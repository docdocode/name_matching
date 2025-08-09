import csv
from preprocess import (
    normalize_name, detect_language,
    is_chinese, is_russian,
    chinese_to_pinyin, russian_to_latin
)
from scoring import (
    fuzzy_score, phonetic_score, jaro_winkler_score,
    aggregate_scores, dynamic_weights
)


def compare_name_parts(part1, part2):
    """Compare two name parts with special initial handling."""
    part1 = part1.lower()
    part2 = part2.lower()

    if len(part1) == 1 and part2.startswith(part1):
        return 100  # treat initial as perfect match
    if len(part2) == 1 and part1.startswith(part2):
        return 100

    # fallback to fuzzy scoring for the part
    # Using fuzzy token ratio on parts directly
    from fuzzywuzzy import fuzz
    return fuzz.ratio(part1, part2)


def name_similarity_with_initials(name1, name2):
    """Calculate similarity considering initials as perfect matches."""
    parts1 = name1.split()
    parts2 = name2.split()

    max_len = max(len(parts1), len(parts2))
    total_score = 0

    for i in range(max_len):
        p1 = parts1[i] if i < len(parts1) else ""
        p2 = parts2[i] if i < len(parts2) else ""

        if p1 == "" or p2 == "":
            # if one part missing, score 0 for that part
            part_score = 0
        else:
            part_score = compare_name_parts(p1, p2)

        total_score += part_score

    return total_score / max_len if max_len > 0 else 0


def match_name(input_name, db_file="mock_database.csv", threshold=90):
    results = []
    norm_input = normalize_name(input_name)
    lang = detect_language(norm_input)

    translit_input = norm_input
    if is_chinese(norm_input):
        translit_input = chinese_to_pinyin(norm_input)
    elif is_russian(norm_input):
        translit_input = russian_to_latin(norm_input)

    weights = dynamic_weights(norm_input)

    with open(db_file, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            norm_db_name = normalize_name(row["full_name"])
            translit_db_name = norm_db_name

            if is_chinese(norm_db_name):
                translit_db_name = chinese_to_pinyin(norm_db_name)
            elif is_russian(norm_db_name):
                translit_db_name = russian_to_latin(norm_db_name)

            # Compute similarity with initial handling
            sim_score_orig = name_similarity_with_initials(norm_input, norm_db_name)
            sim_score_translit = name_similarity_with_initials(translit_input, translit_db_name)

            # Compute other scores for phonetic if needed
            phon_score_orig = phonetic_score(norm_input, norm_db_name) if lang == "en" else 0
            phon_score_translit = phonetic_score(translit_input, translit_db_name) if lang == "en" else 0

            orig_scores = {
                "fuzzy": sim_score_orig,
                "jaro_winkler": jaro_winkler_score(norm_input, norm_db_name),
                "phonetic": phon_score_orig
            }
            translit_scores = {
                "fuzzy": sim_score_translit,
                "jaro_winkler": jaro_winkler_score(translit_input, translit_db_name),
                "phonetic": phon_score_translit
            }

            orig_final = aggregate_scores(orig_scores, weights)
            translit_final = aggregate_scores(translit_scores, weights)

            final_score = max(orig_final, translit_final)

            if final_score >= threshold:
                results.append({
                    "id": row["id"],
                    "full_name": row["full_name"],
                    "country": row["country"],
                    "score": round(final_score, 2),
                    "notes": row["notes"]
                })

    return sorted(results, key=lambda x: x["score"], reverse=True)
