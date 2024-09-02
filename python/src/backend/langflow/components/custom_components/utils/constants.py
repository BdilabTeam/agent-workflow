TOOL_CALL_URL = "http://172.22.102.61:48080/admin-api/plugins/tool/external/call/test"
KNOWLEDGE_CALL_URL = "http://172.22.102.61:48080/admin-api/agent/text/langFlowAsk"
QWEN_BASE_URL = "http://10.8.0.14:6006/v1"
WORKFLOW_CALL_URL = "http://172.22.102.61:8060/admin-api/workflow/run/external"

WORKFLOW_CALL_URL_AGENT = "http://172.22.102.61:8060/admin-api/workflow/run/external"
TOOL_CALL_URL_AGENT = "http://172.22.102.61:48080/admin-api/plugins/tool/external/call/test"
KNOWLEDGE_CALL_URL_AGENT = "http://172.22.102.61:48080/admin-api/agent/text/langFlowAskTab"

DOC_QA_URL="http://172.22.102.61:8060/admin-api/agent/text/langFlow"
DATA_QA_URL="http://172.22.102.61:8060"
EXCEL_QA_URL="http://172.22.102.61:8060"

PYTHON_BASIC_TYPES = [str, bool, int, float, tuple, list, dict, set]
DIRECT_TYPES = [
    "str",
    "bool",
    "dict",
    "int",
    "float",
    "Any",
    "prompt",
    "code",
    "NestedDict",
]

OPENAI_MODELS = [
    "text-davinci-003",
    "text-davinci-002",
    "text-curie-001",
    "text-babbage-001",
    "text-ada-001",
]

CHAT_OPENAI_MODELS = [
    "gpt-4-turbo-preview",
    "gpt-4-0125-preview",
    "gpt-4-1106-preview",
    "gpt-4-vision-preview",
    "gpt-3.5-turbo-0125",
    "gpt-3.5-turbo-1106",
]