import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_caption(title, summary, category, style="general"):
    prompt = f"""
You are the voice of a fast-growing sports Instagram page.

STYLE: {style}

GOAL:
Make people stop scrolling and react.

GLOBAL RULES:
- 3 lines only
- Each line on a new line
- First line must be sharp and slightly provocative (max 8 words)
- Second line adds context
- Third line adds tension, doubt, or a strong opinion
- No clichés like "great match" or "statement win"
- No emojis
- No hashtags
- Avoid neutral analysis

STYLE RULES:

analytical_india:
- Focus on pressure, mistakes, and key turning points
- Slightly critical tone
- India-centric perspective
- Highlight weaknesses, not just success

transfer_drama:
- Focus on uncertainty, decline, or big changes
- Slightly dramatic but controlled
- Emphasise what's at stake

OUTPUT STYLE:
Short, sharp, and opinionated. Not safe.

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
