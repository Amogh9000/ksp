"""
Language Identification Module for Crime_AI RAG Pipeline.
Provides reliable discrimination between English (en) and Kannada (kn) inputs
using Meta's FastText language identification model.
"""

import os
import fasttext

# Global model initialization to ensure warm memory caching across API calls
# Resolve path relative to this file so it works regardless of cwd:
#   query/detect_lang.py  →  ../lid.176.ftz  →  <project_root>/lid.176.ftz
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lid.176.ftz")
MODEL_PATH = os.path.normpath(MODEL_PATH)

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"FastText model file 'lid.176.ftz' not found at '{MODEL_PATH}'. "
        "Please download it using:\n"
        "  Invoke-WebRequest -Uri 'https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz' "
        "-OutFile 'lid.176.ftz'"
    )

# Load the compressed FastText model globally.
# Wrapped in try/except: on low-RAM machines the mmap may fail with
# fasttext._ValueError (paging file too small / OOM).
# If loading fails, lang_model stays None and identify_language() falls
# back to returning "en" via its existing catch-all except block.
lang_model = None
try:
    lang_model = fasttext.load_model(MODEL_PATH)
except Exception as _ft_load_exc:
    import logging as _log
    _log.getLogger(__name__).warning(
        "FastText lang-ID model could NOT be loaded — identify_language() will "
        "always return 'en' as fallback. Cause: %s: %s",
        type(_ft_load_exc).__name__, _ft_load_exc,
    )

def identify_language(text: str, confidence_threshold: float = 0.55) -> str:
    """
    Identifies if the input text is English ('en') or Kannada ('kn').
    
    --- LOW-CONFIDENCE FALLBACK RULE ---
    Short queries, highly technical acronyms (e.g., 'FIR', 'OTP'), or heavily 
    code-mixed inputs can dilute statistical language probabilities. 
    
    If the top predicted language score falls BELOW the configured 
    `confidence_threshold` (default: 0.55), the model bypasses the prediction 
    and forcefully defaults to English ('en'). This prevents downstream 
    translation components from executing unnecessarily on malformed strings.
    """
    try:
        # Normalize text to single-line format for optimal FastText execution
        clean_text = text.replace('\n', ' ').strip()
        if not clean_text:
            return "en"

        # Predict top 1 label and probability
        prediction = lang_model.predict(clean_text, k=1)
        lang_code = prediction[0][0].replace('__label__', '')
        confidence = prediction[1][0]
        
        # Apply the low-confidence fallback rule
        if confidence < confidence_threshold:
            return "en"
            
        return lang_code
        
    except Exception:
        # Ultimate fail-safe rule: default to English if inference throws an exception
        return "en"