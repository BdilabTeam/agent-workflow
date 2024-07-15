from langflow import CustomComponent
from langflow.field_typing import Tool
from langflow.components.custom_components.schemas.mixqa import MixDocQa
from langflow.components.custom_components.utils.qa_node_utils import process_doc_qa_node

class MixDocQa(CustomComponent):
    display_name = "融合问答的文档问答节点"

    def build_config(self):
        return {
            "mix_doc_qa": {
                "display_name": "文档问答节点schema",
                "required": False,
                "field_type": "dict"
            }
        }

    def build(self, mix_doc_qa: MixDocQa = None) -> Tool:
        # mix_doc_qa =  {
        #     "mode": 0,
        #     ""
        # }
        return process_doc_qa_node(mix_doc_qa)