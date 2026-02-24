import os
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_content(title, summary, category="football", context="general"):

    prompt = f"""
You are a sharp football analyst.

Write:

SHORT:
3 lines

LONG:
6 lines

ARTICLE:
200 words

Title: {title}
Summary: {summary}
"""

    for _ in range(2):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=700
            )

            text = response.choices[0].message.content.strip()

            short, long, article = parse(text)

            return {
                "short_caption": short,
                "long_caption": long,
                "article": article
            }

        except Exception as e:
            print("OpenAI error:", e)
            time.sleep(2)

    return {
        "short_caption": title,
        "long_caption": summary,
        "article": summary
    }


def parse(text):
    short, long, article = "", "", ""

    try:
        if "SHORT:" in text:
            short = text.split("SHORT:")[1].split("LONG:")[0].strip()

        if "LONG:" in text:
            long = text.split("LONG:")[1].split("ARTICLE:")[0].strip()

        if "ARTICLE:" in text:
            article = text.split("ARTICLE:")[1].strip()

    except Exception as e:
        print("Parse error:", e)
        short = text

    return short, long, article