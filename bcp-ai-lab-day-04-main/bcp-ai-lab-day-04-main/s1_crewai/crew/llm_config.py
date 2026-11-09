"""Configuración del proveedor LLM de S1."""
import os
from dotenv import load_dotenv
from crew.copilot_llm import CopilotLLM

load_dotenv()


def get_llm() -> CopilotLLM:
    """Return the only supported provider for the lab."""
    return CopilotLLM(model=os.getenv("COPILOT_MODEL", "gpt-6-luna"))


llm = get_llm()
