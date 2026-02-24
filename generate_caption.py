import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_caption(title, summary, category, style="insider"):
    prompt = f"""
You are writing for a sharp football page.

SPORT: {category}

Your voice:
- Insider analysis
- Observational, not emotional
- Slightly critical
- Confident tone
- No clichés

Write a 3-line caption.

RULES:
- Each line on a new line
- First line under 8 words
- Mention teams/players from title
- No generic statements
- No hashtags
- No emojis

EXTRA:
- If it is a match preview, predict what could happen
- If it is a result, explain WHY it happened
- If it is a transfer, question the logic or impact
- Add a subtle opinion or edge

NEWS:
Title: {title}
Summary: {summary}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9
    )

    return response.choices[0].message.content.strip()


# -----------------------------
# TEST
# -----------------------------
if __name__ == "__main__":
    caption = generate_caption(
        "Manchester City vs Arsenal preview",
        "City host Arsenal in a top-of-the-table clash.",
        "football"
    )

    print(caption)
