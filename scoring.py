GOOD = [
    ("sources_named", 10, "Sources are named"),
    ("claims_attributed", 10, "Claims are attributed to people or documents"),
    ("multiple_viewpoints", 10, "More than one viewpoint is included"),
    ("headline_matches_content", 5, "Headline matches the content"),
]

BAD = [
    ("uses_sarcasm_or_insults", 7, "Writer uses sarcasm or insults"),
    ("uses_absolute_language", 5, "Writer uses absolute language"),
    ("emotional_language_by_writer", 5, "Writer uses emotional language"),
]

START = 50


def explain_score(r):
    """Returns (score, list of (reason, points))."""
    checks = r.get("checks", {})
    score = START
    lines = [("Starting point", START)]

    for key, pts, label in GOOD:
        if checks.get(key) is True:
            score += pts
            lines.append((label, pts))

    for key, pts, label in BAD:
        if checks.get(key) is True:
            score -= pts
            lines.append((label, -pts))

    if r.get("article_type") == "opinion":
        score -= 5
        lines.append(("Opinion piece (not neutral news)", -5))

    score = max(0, min(100, score))
    return score, lines


def compute_score(r):
    return explain_score(r)[0]


def grade_from_score(score):
    if score >= 90: return "A"
    if score >= 80: return "B"
    if score >= 70: return "C"
    if score >= 60: return "D"
    return "F"