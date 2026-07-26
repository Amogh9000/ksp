"""
intent_router.py - NLP Intent Router for the Law Enforcement RAG Pipeline
==========================================================================
Classifies a user's English query into one of four strict categories:

  LOOKUP   - Simple fact / FIR record retrieval  -> handled by the RAG pipeline
  PATTERN  - Trend analysis / aggregations / hotspot mapping
  PREDICT  - Forecasting / risk assessment        -> Track 4 Risk Model
  NETWORK  - Suspect connections / crime networks -> Track 4 Graph Model

Design Notes:
  - Uses the same LLM_PROVIDER / API key as the rest of the pipeline (.env).
  - Uses the llama_index .chat() API (not .complete()) with explicit
    system / user ChatMessage roles.  This is required because Groq (and other
    providers) only honour the system prompt reliably through the chat
    message API, not through the constructor system_prompt kwarg.
  - The user turn is prefixed "Classify this query: <query>" to prevent the
    model from treating the text as a real intelligence request.
  - max_tokens=8, temperature=0  -> fast, deterministic, single-label output.
  - Three-tier fallback parser: exact match -> word-boundary scan -> LOOKUP.
  - Lazy singleton via route_query() for efficient reuse across the pipeline.
"""

import os
import re
import logging
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Valid intent labels (single source of truth)
# ---------------------------------------------------------------------------
VALID_INTENTS = {"LOOKUP", "PATTERN", "PREDICT", "NETWORK"}
DEFAULT_INTENT = "LOOKUP"

# ---------------------------------------------------------------------------
# Zero-shot routing system prompt - intentionally strict and minimal
# ---------------------------------------------------------------------------
_ROUTER_SYSTEM_PROMPT = (
    """You are an intent classification engine for a Law Enforcement Intelligence API.
Your ONLY job is to classify the user's query into one of four exact categories: LOOKUP, PATTERN, PREDICT, or NETWORK.

Categories:
1. LOOKUP: Simple retrieval of facts, case summaries, or specific FIR records.
2. PATTERN: Trend analysis, aggregations, or geographic hotspots.
3. PREDICT: Forecasting, likelihood, or risk assessment queries.
4. NETWORK: Finding connections between suspects, gangs, or financial flows.

EXAMPLES:
Query: "Give me the summary of the OTP fraud case near Sami Circle."
Label: LOOKUP

Query: "Who was the victim in FIR 10012003?"
Label: LOOKUP

Query: "Retrieve the details of the stolen motorcycle in Belagavi."
Label: LOOKUP

Query: "What is the most common cyber crime in Hassan this month?"
Label: PATTERN

Query: "Show me a heat map of chain snatchings over the last quarter."
Label: PATTERN

Query: "Are vehicle thefts increasing in the southern district?"
Label: PATTERN

Query: "What is the likelihood of a chain snatching at the bus stand tomorrow?"
Label: PREDICT

Query: "Forecast the crime rate for next week based on current data."
Label: PREDICT

Query: "Where should we deploy patrols tonight to prevent burglaries?"
Label: PREDICT

Query: "Is Quincy Bhardwaj connected to any other bank fraud cases?"
Label: NETWORK

Query: "Show me the gang structure of the Hassan cyber criminals."
Label: NETWORK

Query: "Trace the money flow from the unauthorized bank transaction."
Label: NETWORK

Respond strictly with ONE WORD: the category label. Do not include punctuation or explanations.
"""
)

# ---------------------------------------------------------------------------
# Graceful provider imports (mirrors llm_gateway.py pattern)
# ---------------------------------------------------------------------------
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

try:
    from llama_index.core.llms import ChatMessage, MessageRole
except ImportError:
    ChatMessage = None
    MessageRole = None


# ---------------------------------------------------------------------------
# IntentRouter class
# ---------------------------------------------------------------------------
class IntentRouter:
    """
    Classifies a natural-language query into one of four routing intents.

    Usage
    -----
    >>> router = IntentRouter()
    >>> router.classify("What is the most common theft in Hassan?")
    'PATTERN'

    The router uses the same LLM_PROVIDER / API key set in .env but
    instantiates its own client with a classification-specific system prompt,
    max_tokens=8, and temperature=0 for deterministic single-word output.
    It calls .chat() with explicit ChatMessage roles - this is the only
    reliable way to enforce the system prompt across all supported providers.
    """

    def __init__(self):
        load_dotenv(override=True)
        self.provider = os.getenv("LLM_PROVIDER", "groq").lower()
        self._client = self._build_client()
        logger.info(
            "IntentRouter initialised | provider=%s | valid_intents=%s",
            self.provider.upper(),
            VALID_INTENTS,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_client(self):
        """
        Builds a router-specific LLM client that:
          - Honours the project's configured LLM_PROVIDER from .env
          - Caps max_tokens at 8  (one label word is all that is needed)
          - Sets temperature=0    (fully deterministic output)
        The system prompt is injected at call-time via ChatMessage, not here,
        because constructor-level system_prompt is unreliable on Groq.
        """
        if self.provider == "groq":
            if Groq is None:
                raise ImportError(
                    "Groq provider not installed. Run: "
                    "pip install llama-index-llms-groq"
                )
            return Groq(
                model="llama-3.1-8b-instant",
                api_key=os.getenv("GROQ_API_KEY"),
                max_tokens=8,
                temperature=0.0,
            )

        elif self.provider == "openai":
            if OpenAI is None:
                raise ImportError(
                    "OpenAI provider not installed. Run: "
                    "pip install llama-index-llms-openai"
                )
            return OpenAI(
                model="gpt-4o-mini",
                api_key=os.getenv("OPENAI_API_KEY"),
                max_tokens=8,
                temperature=0.0,
            )

        elif self.provider == "anthropic":
            if Anthropic is None:
                raise ImportError(
                    "Anthropic provider not installed. Run: "
                    "pip install llama-index-llms-anthropic"
                )
            return Anthropic(
                model="claude-3-5-sonnet-20240620",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                max_tokens=8,
            )
            
        elif self.provider == "catalyst":
            class MockCatalystRouter:
                def chat(self, messages):
                    class MockMsg:
                        content = "LOOKUP"
                    class MockResponse:
                        message = MockMsg()
                    return MockResponse()
            return MockCatalystRouter()

        else:
            raise ValueError(
                f"Unsupported LLM_PROVIDER '{self.provider}' in .env. "
                "Valid options: groq, openai, anthropic, catalyst"
            )

    @staticmethod
    def _parse_intent(raw: str) -> str:
        """
        Extracts a valid intent token from the LLM raw response.

        Three-tier strategy:
          Tier 1 - Exact match after stripping whitespace and upper-casing.
          Tier 2 - Word-boundary regex scan for any valid label embedded in
                   the text (handles "LOOKUP." or "The intent is PATTERN").
          Tier 3 - Hardcoded fallback: DEFAULT_INTENT ("LOOKUP"). Never raises.
        """
        cleaned = raw.strip().upper()

        # Tier 1: exact match
        if cleaned in VALID_INTENTS:
            return cleaned

        # Tier 2: embedded label scan
        for label in VALID_INTENTS:
            if re.search(rf"\b{label}\b", cleaned):
                logger.warning(
                    "IntentRouter: non-pure LLM response '%s'; extracted '%s'.",
                    raw.strip(),
                    label,
                )
                return label

        # Tier 3: hardcoded safety fallback
        logger.error(
            "IntentRouter: unrecognised response '%s'. Defaulting to '%s'.",
            raw.strip(),
            DEFAULT_INTENT,
        )
        return DEFAULT_INTENT

    def _build_messages(self, query: str):
        """
        Constructs the [system, user] ChatMessage list for the classification call.
        The user turn is prefixed 'Classify this query:' to unambiguously signal
        to the model that it must classify rather than answer the query.
        """
        if ChatMessage is None or MessageRole is None:
            raise ImportError(
                "llama_index.core.llms not available. "
                "Run: pip install llama-index-core"
            )
        return [
            ChatMessage(role=MessageRole.SYSTEM, content=_ROUTER_SYSTEM_PROMPT),
            ChatMessage(
                role=MessageRole.USER,
                content=f"Classify this query: {query.strip()}",
            ),
        ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify(self, query: str) -> str:
        """
        Classifies *query* into one of: LOOKUP | PATTERN | PREDICT | NETWORK.

        Parameters
        ----------
        query : str
            The user's English search query.

        Returns
        -------
        str
            One of the four intent labels. Always returns a valid label -
            never raises; falls back to LOOKUP on any error.
        """
        if not query or not query.strip():
            logger.warning("IntentRouter: empty query received. Defaulting to LOOKUP.")
            return DEFAULT_INTENT

        q_lower = query.strip().lower()
        if q_lower == "/run-heatmap":
            return "PATTERN"
        elif q_lower == "/query-suspects":
            return "NETWORK"

        try:
            messages = self._build_messages(query)
            response = self._client.chat(messages)
            raw_text: str = response.message.content
            intent = self._parse_intent(raw_text)
            logger.info(
                "IntentRouter: query='%.60s...' -> intent=%s",
                query,
                intent,
            )
            return intent

        except Exception as exc:
            logger.error("IntentRouter: LLM call failed - %s. Using heuristic fallback.", exc)
            if "heatmap" in q_lower or "pattern" in q_lower or "trend" in q_lower:
                return "PATTERN"
            if "predict" in q_lower or "forecast" in q_lower:
                return "PREDICT"
            if "network" in q_lower or "suspect" in q_lower or "connect" in q_lower:
                return "NETWORK"
            return DEFAULT_INTENT


# ---------------------------------------------------------------------------
# Module-level convenience function with lazy singleton
# ---------------------------------------------------------------------------
_router_singleton = None


def route_query(query: str) -> str:
    """
    Module-level convenience wrapper that lazily creates a shared
    IntentRouter instance (avoids re-initialising the LLM client on every call).

    Parameters
    ----------
    query : str
        The user's English search query.

    Returns
    -------
    str
        One of: LOOKUP | PATTERN | PREDICT | NETWORK
    """
    global _router_singleton
    if _router_singleton is None:
        _router_singleton = IntentRouter()
    return _router_singleton.classify(query)


# ---------------------------------------------------------------------------
# Self-test execution block
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import io

    # Force UTF-8 output on Windows terminals
    _enc = getattr(sys.stdout, "encoding", "utf-8") or "utf-8"
    if _enc.lower() != "utf-8" and hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    logging.basicConfig(level=logging.WARNING)

    # One query per expected category
    TEST_CASES = [
        {
            "query": "Give me the summary of the OTP fraud case near Sami Circle.",
            "expected": "LOOKUP",
            "description": "LOOKUP  -- specific FIR / case summary retrieval",
        },
        {
            "query": "What is the most common cyber crime in Hassan this month?",
            "expected": "PATTERN",
            "description": "PATTERN -- trend analysis / frequency aggregation",
        },
        {
            "query": (
                "What is the likelihood of a chain snatching incident "
                "at the bus stand tomorrow?"
            ),
            "expected": "PREDICT",
            "description": "PREDICT -- risk forecast / future event likelihood",
        },
        {
            "query": (
                "Is Quincy Bhardwaj connected to any other bank fraud "
                "cases or organised crime syndicates?"
            ),
            "expected": "NETWORK",
            "description": "NETWORK -- suspect connections / crime network mapping",
        },
    ]

    print("=" * 70)
    print("  IntentRouter -- Self-Test Suite")
    print(f"  Provider : {os.getenv('LLM_PROVIDER', 'groq').upper()}")
    print("=" * 70)

    router = IntentRouter()
    passed = 0

    for i, case in enumerate(TEST_CASES, start=1):
        result = router.classify(case["query"])
        ok = result == case["expected"]
        if ok:
            passed += 1

        print(f"\n[TEST {i}] {case['description']}")
        print(f"  Query    : {case['query']}")
        print(f"  Expected : {case['expected']}")
        print(f"  Got      : {result}")
        print(f"  Status   : {'[OK] PASS' if ok else '[XX] FAIL'}")

    print("\n" + "=" * 70)
    print(f"  Results  : {passed}/{len(TEST_CASES)} tests passed")
    if passed == len(TEST_CASES):
        print("  All routing tests passed -- intent router is operational.")
    else:
        print("  Some tests failed -- review LLM responses above.")
    print("=" * 70)
