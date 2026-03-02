import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# -----------------------------
# MAIN GENERATION FUNCTION
# -----------------------------
def generate_content(title, summary, category="football", context="general"):

    prompt = f"""
You are GAMETRAIT — a modern football intelligence system.

Tone:
- Sharp
- Insightful
- No clichés

Write:

OVERLAY:
Max 10–12 words. Insight only.

SHORT:
2 lines.

LONG:
4–5 lines.

ARTICLE:
200 words.

Context: {context}
Title: {title}
Summary: {summary}

If preview:
- Add prediction
- Mention tactical edge

If news:
- Focus on implications, not repetition
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=700,
        )

        text = response.choices[0].message.content.strip()

        print("\n--- RAW AI OUTPUT ---\n", text)

        overlay, short, long, article = parse(text)

        # -----------------------------
        # FALLBACK SAFETY
        # -----------------------------
        if not overlay:
            overlay = title[:80]

        if not short:
            short = title

        if not long:
            long = summary

        if not article:
            article = summary

        return overlay, short, long, article

    except Exception as e:
        print("OpenAI error:", e)

        # HARD FALLBACK (NEVER FAIL)
        return (
            title[:80],
            title,
            summary,
            summary
        )


# -----------------------------
# ROBUST PARSER
# -----------------------------
def parse(text):
    overlay, short, long, article = "", "", "", ""

    try:
        lines = text.split("\n")
        current = None

        for line in lines:
            clean = line.strip()

            if clean.startswith("OVERLAY"):
                current = "overlay"
                overlay = clean.replace("OVERLAY:", "").strip()

            elif clean.startswith("SHORT"):
                current = "short"
                short = clean.replace("SHORT:", "").strip()

            elif clean.startswith("LONG"):
                current = "long"
                long = clean.replace("LONG:", "").strip()

            elif clean.startswith("ARTICLE"):
                current = "article"
                article = clean.replace("ARTICLE:", "").strip()

            else:
                if current == "overlay":
                    overlay += " " + clean
                elif current == "short":
                    short += " " + clean
                elif current == "long":
                    long += " " + clean
                elif current == "article":
                    article += " " + clean

    except Exception as e:
        print("Parse error:", e)

    return overlay.strip(), short.strip(), long.strip(), article.strip()