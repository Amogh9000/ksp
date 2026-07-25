"""
translate.py
------------
Standalone translation module for the RAG pipeline.
Supports two translation directions:
  • Kannada → English  (ai4bharat/indictrans2-indic-en-dist-200M)
  • English → Kannada  (ai4bharat/indictrans2-en-indic-dist-200M)

Both models use the tokenizer's built-in src_lang / forced_bos_token_id API
so IndicTransToolkit (which requires a C++ compiler to build) is NOT required.
Pre/post-processing follows the same IndicProcessor-equivalent steps inline.
"""

import logging
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
try:
    from indic_transliteration.sanscript import transliterate, KANNADA, DEVANAGARI
    _TRANSLIT_OK = True
except ImportError:
    _TRANSLIT_OK = False
    logger_tmp = logging.getLogger(__name__)
    logger_tmp.warning(
        "indic-transliteration not found. Install with: pip install indic-transliteration\n"
        "Without it, IndicTrans2 tokenization will be incorrect (model was trained on "
        "Devanagari-unified text)."
    )
# NOTE: google.cloud.translate_v2 is intentionally NOT imported at module level.
# Importing it at startup causes a protobuf VersionError because google-cloud-translate
# requires protobuf < 6.0 while TensorFlow 2.21 requires protobuf >= 6.0.
# It is imported lazily inside the GCP fallback block only when actually needed.

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants  (FLORES-200 / IndicTrans2 language codes)
# ---------------------------------------------------------------------------
# KN → EN model
MODEL_NAME = "ai4bharat/indictrans2-indic-en-dist-200M"
SRC_LANG   = "kan_Knda"   # Kannada
TGT_LANG   = "eng_Latn"   # English

# EN → KN model
EN_INDIC_MODEL_NAME = "ai4bharat/indictrans2-en-indic-dist-200M"
EN_SRC_LANG         = "eng_Latn"   # English
EN_TGT_LANG         = "kan_Knda"   # Kannada

# ---------------------------------------------------------------------------
# Device selection — CUDA when available, CPU otherwise
# ---------------------------------------------------------------------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
logger.info("IndicTrans2 | device: %s", DEVICE)

# ---------------------------------------------------------------------------
# Global singletons — loaded once at import time so they stay warm across
# every API call (avoids multi-second cold-start per request).
#
# Wrapped in try/except: on low-RAM / small-paging-file machines the
# safetensors mmap call raises OSError 1455 ("paging file too small").
# If loading fails the server still starts; translate_kn_to_en() will
# fall back to Google Cloud Translation automatically.
# ---------------------------------------------------------------------------
tokenizer          = None
model              = None
_tgt_lang_token_id = None

try:
    logger.info("IndicTrans2 | loading tokenizer from '%s' ...", MODEL_NAME)
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        src_lang=SRC_LANG,
    )

    logger.info("IndicTrans2 | loading model from '%s' ...", MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
    ).to(DEVICE)
    model.eval()

    # The forced_bos_token_id mechanism is NOT used for the KN→EN model.
    # Investigation shows that 'eng_Latn' is NOT in the decoder's tgt_encoder
    # vocabulary — the decoder for this direction is a plain English SPM vocab.
    # The encoder's context (from the prepended "kan_Knda eng_Latn" source tags)
    # already drives the decoder to generate English.  Forcing a wrong token ID
    # from src_encoder caused garbage output (ID 4 → nonsense decoder token).
    _tgt_lang_token_id = None   # do not use forced_bos; encoder context suffices
    logger.info(
        "IndicTrans2 | forced_bos_token_id for '%s': %s (not used — not in tgt_encoder)",
        TGT_LANG,
        _tgt_lang_token_id,
    )
    logger.info("IndicTrans2 | KN→EN translation module ready.")

except Exception as _kn_en_load_exc:
    logger.warning(
        "IndicTrans2 | KN→EN model could NOT be loaded — server will still start.\n"
        "  Cause : %s: %s\n"
        "  Effect: translate_kn_to_en() will fall back to Google Cloud Translation.\n"
        "  Fix   : increase the Windows paging file size, or free RAM before starting.",
        type(_kn_en_load_exc).__name__,
        _kn_en_load_exc,
    )
    tokenizer = None
    model     = None

# ---------------------------------------------------------------------------
# EN → KN global singletons — always loaded on CPU to avoid VRAM contention
# with the primary KN→EN model.
# Wrapped in try/except: the HuggingFace repo is gated (requires access
# approval). If the download fails (403, network error, missing token),
# the module still loads and translate_en_to_kn() falls back gracefully.
# ---------------------------------------------------------------------------
en_kn_tokenizer   = None
en_kn_model       = None
_kn_lang_token_id = None

try:
    logger.info("IndicTrans2 | loading EN→KN tokenizer from '%s' ...", EN_INDIC_MODEL_NAME)
    en_kn_tokenizer = AutoTokenizer.from_pretrained(
        EN_INDIC_MODEL_NAME,
        trust_remote_code=True,
    )

    logger.info("IndicTrans2 | loading EN→KN model from '%s' ...", EN_INDIC_MODEL_NAME)
    en_kn_model = AutoModelForSeq2SeqLM.from_pretrained(
        EN_INDIC_MODEL_NAME,
        trust_remote_code=True,
    ).to("cpu")
    en_kn_model.eval()

    # For EN→KN: 'kan_Knda' may or may not be in tgt_encoder.
    # The same pattern applies: tgt_encoder is the Indic SPM vocab.
    # Check tgt_encoder first; if absent, forced_bos is not used.
    _kn_lang_token_id = en_kn_tokenizer.tgt_encoder.get(EN_TGT_LANG)
    logger.info(
        "IndicTrans2 | forced_bos_token_id for '%s' (EN→KN): %s",
        EN_TGT_LANG,
        _kn_lang_token_id,
    )
    logger.info("IndicTrans2 | EN→KN translation module ready.")

except Exception as _en_kn_load_exc:
    logger.warning(
        "IndicTrans2 | EN→KN model could NOT be loaded — translate_en_to_kn() will "
        "return the original English text as a fallback. "
        "If this is a gated-repo error, visit https://huggingface.co/%s and request access, "
        "then run: huggingface-cli login\n  Error: %s",
        EN_INDIC_MODEL_NAME,
        _en_kn_load_exc,
    )
    # Ensure singletons stay None so the guard in translate_en_to_kn() triggers.
    en_kn_tokenizer   = None
    en_kn_model       = None
    _kn_lang_token_id = None


# ---------------------------------------------------------------------------
# Transliteration helpers
# ---------------------------------------------------------------------------

def _kn_to_deva(text: str) -> str:
    """Transliterate Kannada script to Devanagari.

    IndicTrans2's SentencePiece model (model.SRC) was trained on text where
    all Indic scripts are unified into Devanagari.  Raw Kannada Unicode is
    out-of-distribution for the SPM and produces garbage tokenisation.
    This step mirrors what IndicProcessor.preprocess_batch() does internally.
    """
    if _TRANSLIT_OK:
        return transliterate(text, KANNADA, DEVANAGARI)
    return text   # fallback: pass raw Kannada (will still crash SPM)


def _deva_to_kn(text: str) -> str:
    """Transliterate Devanagari back to Kannada script.

    The EN→KN model outputs Devanagari-unified Kannada.  This converts it
    back to the Kannada script expected by callers.
    """
    if _TRANSLIT_OK:
        return transliterate(text, DEVANAGARI, KANNADA)
    return text


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def translate_kn_to_en(text: str) -> str:
    """Translate a Kannada string to English using IndicTrans2.

    The model and tokenizer are loaded globally at import time and remain
    warm across all calls — safe for concurrent FastAPI / Uvicorn workers
    as long as each worker process loads its own copy.

    Parameters
    ----------
    text : str
        Input text in Kannada script.

    Returns
    -------
    str
        English translation, or the original *text* if translation fails
        (network error, out-of-memory, unexpected runtime exception, etc.).
    """
    try:
        # ------------------------------------------------------------------
        # 1. Pre-process: transliterate Kannada → Devanagari.
        #
        # IndicTrans2's SentencePiece (model.SRC) was trained on
        # Devanagari-unified text.  Raw Kannada Unicode is out-of-domain
        # and produces garbage tokenisation / translation.
        # Language tags ("kan_Knda", "eng_Latn") stay as ASCII — they are
        # parsed by _src_tokenize before the SPM sees the text.
        # ------------------------------------------------------------------
        deva_text  = _kn_to_deva(text)
        tagged_text = f"{SRC_LANG} {TGT_LANG} {deva_text}"

        # ------------------------------------------------------------------
        # 2. Tokenise — inputs are moved to DEVICE explicitly.
        # ------------------------------------------------------------------
        inputs = tokenizer(
            tagged_text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=256,
        )
        # Ensure every tensor is on the same device as the model.
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

        # ------------------------------------------------------------------
        # 3. Generate
        #
        # NOTE 1: use_cache=False is required. The IndicTrans2 custom decoder
        #   (modeling_indictrans.py:1360) accesses past_key_values[0][0]
        #   without guarding against None, crashing beam search with cache.
        #
        # NOTE 2: num_beams=1 (greedy). Beam search with use_cache=False on
        #   this model is unstable on CPU and produces hallucinations or
        #   wrong-language output. Greedy is reliable and fast for RAG queries.
        #
        # NOTE 3: No forced_bos_token_id. The tgt_encoder is pure English;
        #   eng_Latn is absent. The decoder_start_token_id=2 (</s>) from the
        #   model's generation_config drives correct English output.
        # ------------------------------------------------------------------
        with torch.no_grad():
            generated_tokens = model.generate(
                **inputs,
                use_cache=False,
                num_beams=1,              # greedy — stable on CPU
                num_return_sequences=1,
                min_length=0,
                max_length=256,
                repetition_penalty=1.2,
                no_repeat_ngram_size=2,
            )

        # Move output back to CPU for decoding.
        generated_tokens = generated_tokens.cpu()

        # ------------------------------------------------------------------
        # 3. Decode
        # ------------------------------------------------------------------
        translated_text = tokenizer.batch_decode(
            generated_tokens,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True,
        )[0].strip()

        logger.debug("KN->EN | in=%r | out=%r", text, translated_text)
        return translated_text

    except Exception as exc:
        # Log the FULL stack trace so the root cause is always visible.
        logger.error(
            "KN->EN failed for input %r — falling back to Google Cloud Translation.",
            text,
            exc_info=True,
        )

        # --------------------------------------------------------------
        # Fallback: Google Cloud Translation API  (lazy import to avoid
        # the protobuf version conflict at module load time)
        # --------------------------------------------------------------
        try:
            from google.cloud import translate_v2  # noqa: PLC0415  (intentional lazy import)
            translate_client = translate_v2.Client()
            result = translate_client.translate(text, target_language="en")
            translated_text = result["translatedText"]
            logger.info(
                "Google Cloud Translation succeeded for input %r -> %r",
                text,
                translated_text,
            )
            return translated_text
        except Exception as gcp_exc:
            # Final fail-safe: both translation engines have failed.
            logger.error(
                "Google Cloud Translation also failed for input %r. "
                "Returning original text.",
                text,
                exc_info=True,
            )
            return text


# ---------------------------------------------------------------------------
# EN → KN public API
# ---------------------------------------------------------------------------

def translate_en_to_kn(text: str) -> str:
    """Translate an English string to Kannada using IndicTrans2.

    The EN→KN model and tokenizer are loaded globally at import time and
    pinned to CPU to avoid VRAM contention with the primary KN→EN model.
    Pre/post-processing mirrors the IndicProcessor pipeline inline, using
    the tokenizer's built-in src_lang / forced_bos_token_id mechanism.

    Parameters
    ----------
    text : str
        Input text in English.

    Returns
    -------
    str
        Kannada translation, or the original *text* if translation fails
        (model error, out-of-memory, unexpected runtime exception, etc.).
    """
    try:
        # ------------------------------------------------------------------
        # 0. Guard: abort early if the EN→KN model failed to load at startup
        #    (e.g. gated repo, missing HF token, network error).
        # ------------------------------------------------------------------
        if en_kn_model is None or en_kn_tokenizer is None:
            logger.warning(
                "EN→KN model is unavailable (failed to load at startup). "
                "Returning original English text for: %r",
                text,
            )
            return text

        # ------------------------------------------------------------------
        # 1. Tokenise.
        #
        # CRITICAL: This IndicTrans2 tokenizer requires the input to be
        # prefixed with "eng_Latn kan_Knda ". Its _src_tokenize() method
        # splits the string on the first two spaces to extract language tags:
        #     src_lang, tgt_lang, text = text.split(" ", 2)
        # English text does NOT need Devanagari transliteration (it's already
        # Latin script compatible with the EN→KN model's source SPM).
        # ------------------------------------------------------------------
        tagged_text = f"{EN_SRC_LANG} {EN_TGT_LANG} {text}"
        inputs = en_kn_tokenizer(
            tagged_text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=256,
        ).to("cpu")

        # ------------------------------------------------------------------
        # 2. Generate — beam search, no gradient
        # NOTE: use_cache=False avoids the IndicTrans2 past_key_values bug.
        # forced_bos_token_id is used only if kan_Knda is in tgt_encoder.
        # ------------------------------------------------------------------
        with torch.no_grad():
            gen_kwargs = dict(
                use_cache=False,
                num_beams=1,              # greedy — stable on CPU
                num_return_sequences=1,
                min_length=0,
                max_length=256,
                repetition_penalty=1.2,
                no_repeat_ngram_size=2,
            )
            if _kn_lang_token_id is not None:
                gen_kwargs["forced_bos_token_id"] = _kn_lang_token_id
            generated_tokens = en_kn_model.generate(**inputs, **gen_kwargs)

        # ------------------------------------------------------------------
        # 3. Decode and post-process
        #    (mirrors IndicProcessor.postprocess_batch for single strings)
        # ------------------------------------------------------------------
        translated_text = en_kn_tokenizer.batch_decode(
            generated_tokens,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True,
        )[0].strip()

        # Post-process: the EN→KN model outputs Devanagari-unified Kannada.
        # Transliterate back to Kannada script for the caller.
        translated_text = _deva_to_kn(translated_text)

        logger.debug("EN→KN | in=%r | out=%r", text, translated_text)
        return translated_text

    except Exception as exc:
        logger.error(
            "EN→KN translation failed for input %r -- returning original text. "
            "Error: %s",
            text,
            exc,
            exc_info=True,
        )
        # Graceful degradation: return the English original so the
        # caller (RAG response formatter) can still surface an answer.
        return text


# ---------------------------------------------------------------------------
# Quick smoke-test — run directly with:  python query/translate.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import io

    # Reconfigure stdout to UTF-8 so Kannada characters print correctly
    # on Windows (which defaults to cp1252).
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        stream=sys.stdout,
    )

    test_kn = "ಹಾಸನ ಜಿಲ್ಲೆಯಲ್ಲಿ ದಾಖಲಾಗಿರುವ ಇತ್ತೀಚಿನ ಅಪರಾಧ ಪ್ರಕರಣಗಳು"
    print("Testing KN -> EN...")
    res = translate_kn_to_en(test_kn)
    print(f"Result: {res}")
