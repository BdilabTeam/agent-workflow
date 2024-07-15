from langflow import CustomComponent
from langflow.field_typing import Tool
from langflow.components.custom_components.schemas.mixqa import MixDataQa
from langflow.components.custom_components.utils.qa_node_utils import process_data_qa_node

class MixDataQa(CustomComponent):
    display_name = "融合问答的数据问答节点"

    def build_config(self):
        return {
            "mix_data_qa": {
                "display_name": "数据问答节点schema",
                "required": False,
                "field_type": "dict"
            }
        }

    def build(self, mix_data_qa: MixDataQa = None) -> Tool:
        # mix_doc_qa =  {
        #     "mode": 0,
        #     ""
        # }
        return process_data_qa_node(mix_data_qa)