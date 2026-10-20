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
    ("relies_on_anonymous_sources", 5, "Relies on anonymous sources"),
    ("claims_without_evidence", 8, "Makes claims without evidence"),
]

START = 50


def explain_score(r):
    """Returns (score, list of (reason, points))."""
    checks = r.get("checks", {})
    score = START
    lines = [("Starting point", START)]

    for key, pts, label in GOOD:
        level = checks.get(key)
        if isinstance(level, bool):
            level = 2 if level else 0
        if level not in (0, 1, 2):
            level = 0
        earned = round(pts * level / 2)
        if earned > 0:
            score += earned
            suffix = "" if level == 2 else " (partly)"
            lines.append((label + suffix, earned))

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