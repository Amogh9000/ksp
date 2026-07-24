"""
rebuild_translated_log.py
-------------------------
Reads the existing audit_log.jsonl, re-translates any Kannada entry whose
translated_query is missing, None, garbage (dots), or identical to the
raw_query, and writes a clean copy to translated_audit_log.jsonl.

Run once:
    python rebuild_translated_log.py

Safe to re-run — it overwrites translated_audit_log.jsonl from scratch each time.
"""

import sys
import io
import json
import logging
import re
import os

# UTF-8 console output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# Paths relative to project root (where this script lives)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_LOG    = os.path.join(SCRIPT_DIR, "audit_log.jsonl")
DEST_LOG   = os.path.join(SCRIPT_DIR, "translated_audit_log.jsonl")

# Regex to detect "garbage" translations: only dots / dashes / spaces / asterisks
_GARBAGE_RE = re.compile(r"^[\.\-\s\*]+$")


def _is_bad_translation(raw: str, translated: object) -> bool:
    """Return True if translated_query is missing, garbage, or same as raw."""
    if not translated:
        return True
    if not isinstance(translated, str):
        return True
    if _GARBAGE_RE.match(translated.strip()):
        return True
    # Same as raw Kannada (fallback was triggered)
    if translated.strip() == raw.strip():
        return True
    return False


def main():
    # Add query/ to path so translate imports work
    query_dir = os.path.join(SCRIPT_DIR, "query")
    if query_dir not in sys.path:
        sys.path.insert(0, query_dir)

    logger.info("Loading IndicTrans2 KN->EN model (this takes ~30s)...")
    from translate import translate_kn_to_en

    logger.info("Reading %s ...", SRC_LOG)
    entries = []
    with open(SRC_LOG, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))

    logger.info("Total entries: %d", len(entries))

    fixed   = 0
    kept    = 0
    skipped = 0

    with open(DEST_LOG, "w", encoding="utf-8") as out:
        for i, entry in enumerate(entries, 1):
            raw        = entry.get("raw_query", "")
            lang       = entry.get("detected_language", "")
            translated = entry.get("translated_query")

            if lang == "kn" and _is_bad_translation(raw, translated):
                logger.info("[%d/%d] Re-translating: %r...", i, len(entries), raw[:60])
                try:
                    new_translation = translate_kn_to_en(raw)
                    entry["translated_query"] = new_translation
                    fixed += 1
                    logger.info("  -> %r", new_translation[:80])
                except Exception:
                    logger.error("  Translation failed -- keeping original", exc_info=True)
                    skipped += 1
            elif lang != "kn":
                # English queries -- not applicable
                entry["translated_query"] = None
                kept += 1
            else:
                # Already has a good translation
                kept += 1

            out.write(json.dumps(entry, ensure_ascii=False) + "\n")

    logger.info("Done.  Fixed: %d | Kept as-is: %d | Skipped (error): %d",
                fixed, kept, skipped)
    logger.info("Clean log written to: %s", DEST_LOG)


if __name__ == "__main__":
    main()
