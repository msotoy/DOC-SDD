import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lab_copilot.chat import CopilotChat

load_dotenv(Path(__file__).parent.parent / ".env", override=True)


def get_llm() -> CopilotChat:
    return CopilotChat()


llm = get_llm()
