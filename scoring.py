def grade_from_score(score):
    if score >= 90: return "A"
    if score >= 80: return "B"
    if score >= 70: return "C"
    if score >= 60: return "D"
    return "F"


def compute_score(r):
    score = 85
    if r.get("article_type") == "opinion":
        score -= 10
    score -= 7 * min(len(r["manipulation_flags"]), 4)
    return score