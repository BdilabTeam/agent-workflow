from typing import List, Dict, Union
from langflow.components.custom_components.schemas.workflow import TextProcessingNode
from langflow.components.custom_components.utils.workflow_node_utils import process_textprocessing_node
from langflow import CustomComponent

class TextProcessing(CustomComponent):
    id = "10"    # Unique ID
    display_name = "工作流-文本处理" # Langflow UI节点展示名称
    description = "TextProcessing Node"    # 节点描述

    def build_config(self):
        return {
            "prenode_inputs": {
                "display_name": "前置节点输入",
                "required": False,
            },
            "textprocessing_node_schema": {    # build方法参数名称
                "display_name": "文本节点schemas",   # Langflow UI入参展示名称
                "advanced": False,
                "required": False,
                "field_type": "dict"
            },
        }

    def build(
        self,
        prenode_inputs: List[Dict] = [],
        textprocessing_node_schema: TextProcessingNode = None # 节点参数schema
    ) -> Union[dict, Dict]:
        #字符串拼接
        # textprocessing_node_schema = {
        #     "flow_id": "1",
        #     "node_id": "TextProcessingID",
        #     "node_name": "textprocessing",
        #     "mode_selection": "string_concatenation",
        #     "string_concatenation": "riben{{event}}爬爬爬{{place}}000--++",
        #     "input_schema": {
        #         "inputParameters": [
        #             {
        #                 "name": "event",
        #                 "input": {
        #                     "type": "string",
        #                     "schema": None,
        #                     "value": {
        #                         "type": "literal",
        #                         "content": "分析安全事件"
        #                     }
        #                 }
        #             },
        #
        #             {
        #                 "name": "place",
        #                 "input": {
        #                     "type": "string",
        #                     "schema": None,
        #                     "value": {
        #                         "type": "literal",
        #                         "content": "鄂州"
        #                     }
        #                 }
        #             },
        #             {
        #                 "name": "名字",
        #                 "input": {
        #                     "type": "string",
        #                     "schema": None,
        #                     "value": {
        #                         "type": "literal",
        #                         "content": "小名"
        #                     }
        #                 }
        #             }
        #         ]
        #     },
        # }

        #字符串分隔

        # textprocessing_node_schema = {
        #     "flow_id": "1",
        #     "node_id": "TextProcessingID",
        #     "node_name": "textprocessing",
        #     "mode_selection": "string_separation",
        #     "delimiter": ["line_break", "tab_break", "period", "comma", "semicolon", "space"],
        #     "input_schema": {
        #         "inputParameters": [
        #             {
        #                 "name": "separation",
        #                 "input": {
        #                     "type": "string",
        #                     "schema": None,
        #                     "value": {
        #                         "type": "literal",
        #                         "content": "test ;, 第一;第二,第三 第四\t第五\n第六\t\n第七\t \n;\t,\n第八"
        #                     }
        #                 }
        #             }
        #
        #
        #         ]
        #     },
        # }
        return process_textprocessing_node(prenode_inputs=prenode_inputs, textprocessing_node_schema=textprocessing_node_schema)  # utils.workflow_node_utils.py中实现节点