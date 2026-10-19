from scraper import scrape_article
from analyzer import analyze
from scoring import compute_score, grade_from_score
def grade_from_score(score):
    if score >= 90: return "A"
    if score >= 80: return "B"
    if score >= 70: return "C"
    if score >= 60: return "D"
    return "F"


url = input("Paste an article link: ").strip()

print("Scraping...")
article = scrape_article(url)
print("Title:", article["title"])
print("Author found by scraper:", article["author"])
print("Analyzing...\n")

r = analyze(article)

score = compute_score(r)
print(f"GRADE: {grade_from_score(score)}  ({score}/100)  confidence: {r['confidence']}")
print("(This grades writing and sourcing only. Facts are not verified.)")
print("\n" + r["summary"])
print("\nSOURCES:", r["source_quality"])
print("\nBIAS:", r["bias_assessment"])

print("\nMANIPULATION FLAGS:")
if not r["manipulation_flags"]:
    print("  none found")
for f in r["manipulation_flags"]:
    print(f"  - {f['type']}: {f['example']}")

print("\nCHECK NEXT:")
for item in r["what_to_check_next"]:
    print("  -", item)