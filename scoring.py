from rapidfuzz import fuzz
import jellyfish

def fuzzy_score(name1, name2):
    """Levenshtein-based fuzzy similarity (0–100)."""
    return max(
        fuzz.token_sort_ratio(name1, name2),
        fuzz.token_set_ratio(name1, name2)
    )

def jaro_winkler_score(name1, name2):
    """Jaro-Winkler similarity (0–100)."""
    return jellyfish.jaro_winkler_similarity(name1, name2) * 100

def phonetic_score(name1, name2):
    """Phonetic similarity for English/Latin."""
    try:
        soundex1 = jellyfish.soundex(name1)
        soundex2 = jellyfish.soundex(name2)
        return 100 if soundex1 == soundex2 else 0
    except:
        return 0

def aggregate_scores(scores, weights):
    """Weighted score aggregation."""
    total = sum(scores[k] * weights.get(k, 1) for k in scores)
    weight_sum = sum(weights.values())
    return total / weight_sum if weight_sum > 0 else 0

def dynamic_weights(name):
    """Dynamic weights for fuzzy & Jaro-Winkler based on name length."""
    length = len(name.replace(" ", ""))  # exclude spaces
    if length <= 4:
        return {"fuzzy": 0.3, "jaro_winkler": 0.7, "phonetic": 0.0}
    elif length <= 8:
        return {"fuzzy": 0.5, "jaro_winkler": 0.5, "phonetic": 0.0}
    else:
        return {"fuzzy": 0.7, "jaro_winkler": 0.3, "phonetic": 0.0}
