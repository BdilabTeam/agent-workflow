import os
import re
import ast
import json
import tiktoken
from chevron import render
from enum import Enum
from string import Formatter
from typing import Union, List, Dict, Any

from jinja2 import Template
from transformers import PreTrainedTokenizerFast

from langflow.components.custom_components.schemas.workflow import Inputs, NodeData, Outputs, RetrievalResult, TokenAndCost

from langflow.services.deps import get_session
from langflow.services.database.models.workflow.crud import get_workflow_by_id, update_workflow
from langflow.services.database.models.workflow.model import WorkflowUpdate

PARENT_DIR = os.path.dirname(os.path.dirname(__file__))

class NodeType(Enum):
    START = "Start"
    TOOL = "Tool"
    KNOWLEDGE = "Knowledge"
    LLM = "LLM"
    END = "End"
    
class RetrievalResultSourceType(Enum):
    DOC = "doc"
    DATA = "data"

def is_string(s):
    try:
        return isinstance(s, str)
    except (ValueError, SyntaxError):
        return False

def is_int_string(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def is_float_string(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_dict_string(s):
    try:
        parsed = ast.literal_eval(s)
        return isinstance(parsed, dict)
    except (ValueError, SyntaxError):
        return False

def is_bool_string(s):
    if isinstance(s, str):
        value_lower = s.strip().lower()
        if value_lower in ("true", "1", "yes", "on"):
            return True
        elif value_lower in ("false", "0", "no", "off"):
            return False
    raise ValueError(f"Invalid boolean string: {s}")

def is_list_string(s):
    try:
        parsed = ast.literal_eval(s)
        return isinstance(parsed, list)
    except (ValueError, SyntaxError):
        return False

def is_list_of_integers_string(s):
    try:
        parsed = ast.literal_eval(s)
        if isinstance(parsed, list) and all(isinstance(item, int) for item in parsed):
            return True
        return False
    except (ValueError, SyntaxError):
        return False

def is_list_of_strs_string(s):
    try:
        parsed = ast.literal_eval(s)
        if isinstance(parsed, list) and all(isinstance(item, str) for item in parsed):
            return True
        return False
    except (ValueError, SyntaxError):
        return False

def is_list_of_floats_string(s):
    try:
        parsed = ast.literal_eval(s)
        # if isinstance(parsed, list) and all(isinstance(item, float) for item in parsed):
        if isinstance(parsed, list) and all(isinstance(item, float) for item in parsed):
            return True
        return False
    except (ValueError, SyntaxError):
        return False

def is_list_of_dicts_string(s):
    try:
        parsed = ast.literal_eval(s)
        if isinstance(parsed, list) and all(isinstance(item, dict) for item in parsed):
            return True
        return False
    except (ValueError, SyntaxError):
        return False

def validate_dtype(dtype, content):
    type_validate_func_map = {
        "string": is_string,
        "integer": is_int_string,
        "number": is_float_string,
        "list": is_list_string,
        "array": is_list_string,
        "object": is_dict_string,
        "boolean": is_bool_string
    }
    if not (type_validate_func := type_validate_func_map.get(dtype, None)):
        raise ValueError(f"Unsupported data type '{dtype}'. Only the following data types are supported: {list(type_validate_func_map.keys())}")

    return type_validate_func(content)

def get_value_by_key_path(output_dict, key_path):
    """根据给定的键路径获取字典中的值"""
    keys = key_path.split('.')  # 将键路径按照 '.' 分割成键列表
    value = output_dict
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)  # 获取当前键对应的值
        else:
            return None  # 如果当前值不是字典，则返回 None
    return value

def format_input_schemas_to_dict(input_schema: Union[Inputs], prenode_results: List[NodeData] = None):
    """解析输入schema为字典对象"""
    input_param_schemas = input_schema.inputParameters

    input_param_dict = {}
    for input_param_schema in input_param_schemas:
        key = input_param_schema.name
        dtype = input_param_schema.input.type
        content = input_param_schema.input.value.content
        value_source_type = input_param_schema.input.value.type
        
        value = ""
        # TODO 什么场景需要校验类型与字符串表示的值是否匹配？
        if value_source_type == "literal":
            if validate_dtype(dtype=dtype, content=content):    # 校验实际类型与字符串表示是否匹配
                if dtype == "string":
                    value = content
                else:
                    value = ast.literal_eval(content)   # 检验通过即可将字符串表示值解析为实际类型
            else:
                raise TypeError(f"字段: '{key}' 数据类型校验失败")
        elif value_source_type == "ref":
            if ref_source_id := input_param_schema.input.value.content.source_id:
                key_path = input_param_schema.input.value.content.name
                for node_data in prenode_results:
                    if node_data.node_id == ref_source_id:
                        source_output_dict = json.loads(node_data.output)
                        if (value := get_value_by_key_path(source_output_dict, key_path)) is None:
                            raise ValueError(f"从源节点 '{ref_source_id}' 获取关键字 '{key_path}' 的值为空")
                        # TODO 校验引用值与定义的数据类型一致？
            else:
                raise ValueError(f"字段: '{key}' 缺少源ID")
        else:
                raise ValueError("参数值来源类型字段必须是以下之一:['literal'、'ref']")

        input_param_dict.update({key: value})
    
    return input_param_dict

def get_query_value(params_dict):
    if "query" in params_dict:
        return params_dict["query"]
    elif "Query" in params_dict:
        return params_dict["Query"]
    else:
        raise KeyError("The dictionary does not contain 'query' or 'Query' key.")

def format_output_schemas_to_dict(output_schema: Union[Outputs], raw_output) -> dict:
    """解析转换输出schema为字典对象"""
    output_param_schemas = output_schema.outputs
    output_dict = {}
    for output_param_schema in output_param_schemas:
        if not (key := output_param_schema.name):
            raise ValueError("输出参数schema的参数名称字段（name）不能为空")
        # TODO 根据参数类型适配不用输出解析器
        dtype = output_param_schema.type
        
        if validate_dtype(dtype=dtype, content=raw_output):    # 校验实际类型与字符串表示是否匹配
            if dtype == "string":
                value = raw_output
            else:
                value = ast.literal_eval(raw_output)   # 检验通过即可将字符串表示值解析为实际类型
        else:
            raise TypeError(f"输出解析失败, 节点原始输出 '{raw_output}' 无法转换为字段: '{key}' 期望的数据类型 '{dtype}'")
    
        output_dict.update({key: value})
    return output_dict

def format_prenodes_data(prenode_inputs: list):
    all_nodes_data = []
    # 获取所有节点输出，key为节点ID，value为节点原始输出
    node_ids = []
    def get_nodes_result(prenode_inputs):
        for prenode_input in prenode_inputs:
            for k, v in prenode_input.items():
                if k == "prenode_inputs":
                    get_nodes_result(v)
                if k != "prenode_inputs":
                    if v.get("node_id") not in node_ids:
                        node_ids.append(v.get("node_id"))
                        all_nodes_data.append(NodeData(**v))

    get_nodes_result(prenode_inputs=prenode_inputs)
    return all_nodes_data

def format_placeholder_to_str(template):
    """占位符转换为字符串key, 例如{key} -> key"""
    pattern = r'\{([^{}]+)\}'
    matched_keys = re.findall(pattern=pattern, string=template)
    placeholder = {}
    if matched_keys:
        for k in matched_keys:
            placeholder.update({k: f"{k}"})
    formatted_prompt = template.format(**placeholder)
    return formatted_prompt

def safe_format_prompt(template: str, params_dict: Dict[str, Any]):
    """格式化字符串时忽略缺失的占位符"""
    # class SafeFormatter(Formatter):
    #     def get_value(self, key, args, kwargs):
    #         if isinstance(key, str):
    #             return kwargs.get(key, f'{{{key}}}')
    #         else:
    #             return Formatter.get_value(key, args, kwargs)

    # formatter = SafeFormatter()
    # formatted_prompt = formatter.format(template, **params_dict)
    # formatted_template = render(template=template, data=params_dict)
    # return format_placeholder_to_str(formatted_template)  
    
    jinja_template = Template(template)
    formatted_template = jinja_template.render(params_dict)
    return formatted_template

def compute_tokens_by_tiktoken(text) -> int:
    # 加载 GPT-3 的 tokenizer
    enc = tiktoken.get_encoding()
    # 使用 tokenizer 进行 token 化
    tokens = enc.encode(text)
    # 计算 token 数量
    token_count = len(tokens)
    return token_count

def compute_tokens_by_transformers(text) -> int:
    # 指定本地文件路径
    tokenizer_path = os.path.join(PARENT_DIR, "tokenizer")  # 替换为实际文件路径

    # 加载 tokenizer
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_file=f"{tokenizer_path}/qwen1.5-14b-chat-tokenizer.json",
        vocab_file=f"{tokenizer_path}/qwen1.5-14b-chat-vocab.json",
        merges_file=f"{tokenizer_path}/qwen1.5-14b-chat-merges.txt",
        tokenizer_config_file=f"{tokenizer_path}/qwen1.5-14b-chat-tokenizer-config.json"
    )
    # 进行 token 化
    tokens = tokenizer.encode(text)
    # 计算 token 数量
    token_count = len(tokens)
    return token_count

def format_tokens(tokens: int) -> str:
    return f"{tokens} Tokens"

def parse_token_string(token_str):
    # 使用正则表达式匹配数值部分
    match = re.match(r'(\d+)\s*Tokens?', token_str, re.IGNORECASE)
    
    if match:
        # 提取匹配的数值部分并转换为整数
        return int(match.group(1))
    else:
        raise ValueError("Invalid token format")
    
def parse_time_string(time_str):
    # 使用正则表达式匹配数值部分
    match = re.match(r'(\d+(\.\d+)?)s', time_str)
    
    if match:
        # 提取匹配的数值部分并转换为浮点数
        return float(match.group(1))
    else:
        raise ValueError("Invalid time format")

def on_start(workflow_id, node_data: NodeData):
    session = next(get_session())
    if not (workflow_db := get_workflow_by_id(db=session, id=workflow_id)):
        raise ValueError("Workflow not found")
    try:
        node_results = json.loads(workflow_db.node_results)
        # 开始节点，清空当前流执行结果
        if node_data.node_type == NodeType.START.value:
            node_results = []
        # updated_node_results = list(filter(lambda node_data_dict: node_data_dict.get("node_id") != node_data.node_id, node_results))
        node_results.append(node_data.model_dump())
        node_results_json = json.dumps(node_results, ensure_ascii=False)
        workflow_update = WorkflowUpdate(node_results=node_results_json)
        # 开始节点，更新流状态为RUNNING 
        if node_data.node_type == NodeType.START.value:
            workflow_update.execute_status = "RUNNING"
        update_workflow(workflow_db, workflow_update, session)
    except Exception as e:
        raise RuntimeError(f"节点状态同步失败, 具体原因: {e.args[0]}")
    
def on_end(workflow_id, node_data: NodeData):
    session = next(get_session())
    if not (workflow_db := get_workflow_by_id(db=session, id=workflow_id)):
        raise ValueError("Workflow not found")
    try:
        node_results: List[Dict] = json.loads(workflow_db.node_results)
        # on_start已经更新过当前节点数据，on_end时根据节点ID过滤节点数据，并重新更新节点数据
        updated_node_results = list(filter(lambda node_data_dict: node_data_dict.get("node_id") != node_data.node_id, node_results))
        updated_node_results.append(node_data.model_dump())
        
        workflow_exe_cost_str = None
        workflow_token_and_cost_json = None
        # End节点需要计算总耗时和总token消耗
        if node_data.node_type == NodeType.END.value:
            # 计算工作流总耗时
            workflow_exe_cost = 0
            for updated_node_result in updated_node_results:
                node_exe_cost_str = updated_node_result.get("node_exe_cost")
                node_exe_cost = parse_time_string(node_exe_cost_str)
                workflow_exe_cost = workflow_exe_cost + node_exe_cost
            workflow_exe_cost_str = f"{round(workflow_exe_cost, 3)}s"
        
            # TODO 计算工作流token消耗
            workflow_input_tokens = 0
            workflow_output_tokens = 0
            workflow_total_tokens = 0
            for updated_node_result in updated_node_results:
                if updated_node_result.get("node_type") == NodeType.LLM.value:   # 仅对LLM节点计算tokens
                    token_and_cost = updated_node_result.get("token_and_cost")
                    input_tokens_str = token_and_cost.get("input_tokens")
                    input_tokens = parse_token_string(input_tokens_str)
                    workflow_input_tokens = workflow_input_tokens + input_tokens
                    
                    output_tokens_str = token_and_cost.get("output_tokens")
                    output_tokens = parse_token_string(output_tokens_str)
                    workflow_output_tokens = workflow_output_tokens + output_tokens
                    
                    total_tokens_str = token_and_cost.get("total_tokens")
                    total_tokens = parse_token_string(total_tokens_str)
                    workflow_total_tokens = workflow_total_tokens + total_tokens
                
            workflow_token_and_cost = TokenAndCost(
                input_tokens=format_tokens(workflow_input_tokens), 
                output_tokens=format_tokens(workflow_output_tokens), 
                total_tokens=format_tokens(workflow_total_tokens)
            )
            workflow_token_and_cost_json = workflow_token_and_cost.model_dump_json()
        
        node_results_json = json.dumps(updated_node_results, ensure_ascii=False)
        workflow_update = WorkflowUpdate(node_results=node_results_json, )
        
        if workflow_token_and_cost_json is not None:
            workflow_update.token_and_cost = workflow_token_and_cost_json
        if workflow_exe_cost_str is not None:
            workflow_update.workflow_exe_cost = workflow_exe_cost_str
        
        if node_data.node_type == NodeType.END.value and node_data.node_status == "SUCCESS":
            workflow_update.execute_status = "SUCCESS"
        elif node_data.node_type == NodeType.END.value and node_data.node_status == "FAILED":
            workflow_update.execute_status = "FAILED"
        
        update_workflow(workflow_db, workflow_update, session)
    except Exception as e:
        raise RuntimeError(f"节点状态同步失败, 具体原因: {e.args[0]}")
    
def get_top_n_retrieval_results(retrieval_results: List[RetrievalResult], n: int) -> List[RetrievalResult]:
    # 根据 similarity_score 对结果进行排序
    sorted_results = sorted(retrieval_results, key=lambda x: x.similarity_score, reverse=True)
    # 取前 n 个结果
    top_n_results = sorted_results[:n]
    return top_n_results

