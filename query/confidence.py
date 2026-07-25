def evaluate_confidence(chunks: list, threshold: float = 0.40) -> dict:
    """
    Evaluates confidence metrics from a database retrieval result set.
    
    Signals tracked:
    1. Top similarity score inside the set.
    2. Count of records crossing the relevance threshold.

    NOTE: Thresholds are calibrated for LaBSE (sentence-transformers/LaBSE) cosine
    similarity distributions, which are significantly lower than OpenAI embedding
    scores. A LaBSE score of ~0.50+ typically represents a strong semantic match.
    
    Returns:
        dict: {"level": "HIGH"|"MEDIUM"|"LOW", "matching_records": int}
    """
    if not chunks:
        return {
            "level": "LOW",
            "matching_records": 0
        }
        
    scores = [chunk["score"] for chunk in chunks]
    top_score = max(scores)
    valid_count = sum(1 for s in scores if s >= threshold)
    
    # Mathematical classification tiers — calibrated for LaBSE score distribution.
    # LaBSE cosine scores are naturally compressed vs. OpenAI models:
    #   >= 0.50  → HIGH   (strong semantic match)
    #   >= 0.40  → MEDIUM (acceptable relevance)
    #   <  0.40  → LOW    (weak or no match → guardrail fires)
    if top_score >= 0.50 and valid_count >= 1:
        level = "HIGH"
    elif top_score >= 0.40 and valid_count >= 1:
        level = "MEDIUM"
    else:
        level = "LOW"
        
    return {
        "level": level,
        "matching_records": valid_count
    }