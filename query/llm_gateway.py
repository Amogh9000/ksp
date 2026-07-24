import os
import re
from dotenv import load_dotenv

# ---------------------------------------------------------
# GRACEFUL IMPORTS
# ---------------------------------------------------------
try:
    from llama_index.llms.groq import Groq
except ImportError:
    Groq = None

try:
    from llama_index.llms.openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from llama_index.llms.anthropic import Anthropic
except ImportError:
    Anthropic = None


# System prompt that prevents repetition loops and hallucination
_SYSTEM_PROMPT = """You are a precise crime intelligence assistant for Karnataka Police.

Rules you MUST follow:
1. Answer ONLY using the provided CONTEXT. Do not invent facts.
2. Be concise — use plain bullet points with a single dash (-), NOT asterisks (*).
3. If the context does not contain enough information, say: "No matching records found in the available data."
4. STOP immediately after you have conveyed all relevant information. Do NOT repeat yourself.
5. Never produce sequences of repeated symbols, asterisks, or filler characters.
"""

# Regex to detect runaway repetition: 5+ consecutive "* " patterns
_REPETITION_RE = re.compile(r"(\* ){5,}")


def _sanitize(text: str) -> str:
    """Truncate at the first sign of runaway asterisk repetition and clean up."""
    match = _REPETITION_RE.search(text)
    if match:
        # Keep everything before the repetition starts, trim cleanly
        clean = text[:match.start()].rstrip(" -\n*")
        if clean:
            return clean + "\n\n[Note: Response truncated — insufficient data in retrieved records.]"
        return "No matching records found in the available data."
    return text


class LLMGateway:
    """
    Unified Interface for all LLM providers.
    Controlled globally by the 'LLM_PROVIDER' flag in the .env file.
    """
    def __init__(self):
        load_dotenv(override=True)
        # The single source of truth for which AI is active
        self.provider = os.getenv("LLM_PROVIDER", "groq").lower()
        self.client = self._initialize_client()

    def _initialize_client(self):
        """Privately initializes the requested vendor client."""
        if self.provider == "groq":
            if Groq is None:
                raise ImportError("Groq is not installed. Run: pip install llama-index-llms-groq")
            return Groq(
                model="llama-3.1-8b-instant",
                api_key=os.getenv("GROQ_API_KEY"),
                system_prompt=_SYSTEM_PROMPT,
                max_tokens=512,              # hard cap — prevents runaway generation
            )

        elif self.provider == "openai":
            if OpenAI is None:
                raise ImportError("OpenAI is not installed. Run: pip install llama-index-llms-openai")
            return OpenAI(
                model="gpt-4o",
                api_key=os.getenv("OPENAI_API_KEY"),
                system_prompt=_SYSTEM_PROMPT,
                max_tokens=512,
            )

        elif self.provider == "anthropic":
            if Anthropic is None:
                raise ImportError("Anthropic is not installed. Run: pip install llama-index-llms-anthropic")
            return Anthropic(
                model="claude-3-5-sonnet-20240620",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                system_prompt=_SYSTEM_PROMPT,
                max_tokens=512,
            )

        else:
            raise ValueError(f"Unsupported LLM_PROVIDER in .env: {self.provider}")

    def generate(self, prompt: str, context: str) -> str:
        """
        The public method the RAG pipeline calls.
        It has zero knowledge of *which* LLM is actually executing the request.
        """
        final_prompt = (
            f"{prompt}\n\n"
            f"=========================================\n"
            f"CONTEXT (Retrieved Records):\n{context}"
        )

        try:
            response = self.client.complete(final_prompt)
            raw_text = response.text
            # Post-process: strip any runaway asterisk repetition before returning
            return _sanitize(raw_text)
        except Exception as e:
            print(f"Gateway Generation Error [{self.provider.upper()}]: {e}")
            return "ERROR: Synthesis failure."