# Overwatch

An open-source tool that checks news articles for writing quality, sourcing, and manipulation patterns.

**Live app:** (paste your Streamlit link here)

## What it does
- Scrapes an article from a link, or accepts pasted text
- Uses an AI model to analyze sourcing, bias, and manipulation tactics
- Computes a transparent score with a rule you can read (see scoring.py)
- Gives reverse-image-search links to check photos

## Limits
Overwatch grades writing and sourcing only. It does not verify facts and cannot detect deepfakes. Scores can vary by about 10 points between runs. Treat results as a starting point, never a verdict.
![Overwatch screenshot](screenshot.png)