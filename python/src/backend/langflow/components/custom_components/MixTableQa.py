from langflow import CustomComponent
from langflow.field_typing import Tool
from langflow.components.custom_components.schemas.mixqa import MixTableQa
from langflow.components.custom_components.utils.qa_node_utils import process_excel_qa_node

class MixTableQa(CustomComponent):
    display_name = "融合问答的表格问答节点"

    def build_config(self):
        return {
            "mix_table_qa": {
                "display_name": "表格问答节点schema",
                "required": False,
                "field_type": "dict"
            }
        }

    def build(self, mix_table_qa: MixTableQa = None) -> Tool:
        # mix_doc_qa =  {
        #     "mode": 0,
        #     ""
        # }
        return process_excel_qa_node(mix_table_qa)