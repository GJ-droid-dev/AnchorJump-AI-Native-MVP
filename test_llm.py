from core.llm_client import LLMClient
from core.config import Config

try:
    client = LLMClient()
    res = client.parse_anchor("London 2024 july", Config.REFERENCE_DATE)
    print("SUCCESS")
    print(res)
except Exception as e:
    print("ERROR:")
    print(e)
