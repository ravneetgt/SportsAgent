import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_caption(title, summary, category, style="general"):
    prompt = f"""
You are writing for a sports page.

SPORT: {category}

Write a sharp 3-line caption.

STRICT RULES:
- Must stay within the sport context
- Must reference the teams/players in the title
- No generic or unrelated commentary
- No crossover (cricket vs football etc.)
- Avoid clichés

STYLE:
- Insightful
- Slightly critical
- Observational

NEWS:
Title: {title}
Summary: {summary}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )

    return response.choices[0].message.content.strip()


# test
if __name__ == "__main__":
    caption = generate_caption(
    "India wins thriller against Australia",
    "India chased down 280 in a last-over finish.",
    "cricket",
    "analytical_india"
    )

    print(caption)
