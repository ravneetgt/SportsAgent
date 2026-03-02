import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_content(
    title,
    summary,
    category="football",
    context="general",
    insight=None,
    editorial=None,
    confidence=None,
    narrative=None,
    personality="analyst",
    fmt="standard"
):

    personality_rules = {
        "analyst": "Calm, structured, tactical.",
        "insider": "Subtle, knowing, like dressing-room insight.",
        "contrarian": "Challenge common views.",
        "cultural": "Narrative, cinematic, emotional restraint.",
        "fan": "Raw, emotional, punchy."
    }

    format_rules = {
        "standard": "Balanced output.",
        "quick_take": "Short, sharp, fewer words.",
        "prediction": "Lean on probabilities and match outcome.",
        "breakdown": "More analysis in LONG and ARTICLE."
    }

    prompt = f"""
You are GAMETRAIT.

PERSONALITY:
{personality} → {personality_rules.get(personality)}

FORMAT:
{fmt} → {format_rules.get(fmt)}

DATA:
{insight}

CONFIDENCE:
{confidence}

NARRATIVE:
{narrative}

EDITORIAL:
{editorial}

Title: {title}
Summary: {summary}

Write:

OVERLAY:
Max 10 words.

SHORT:
2 lines.

LONG:
4–5 lines.

ARTICLE:
~200 words.

RULES:
- No clichés
- Insight > description
- Use football understanding
- Match personality tone
- Match format constraints

If prediction format:
- Mention who has edge

If contrarian:
- Challenge obvious narrative

If insider:
- Imply deeper understanding

If fan:
- Keep it punchy

"""

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.0,
            max_tokens=700,
        )

        text = res.choices[0].message.content.strip()

        return parse(text)

    except Exception as e:
        print("AI error:", e)
        return title[:80], title, summary, summary


def parse(text):
    overlay, short, long, article = "", "", "", ""

    text = text.replace("**", "")
    lines = text.split("\n")

    current = None

    for line in lines:
        clean = line.strip()

        if clean.startswith("OVERLAY:"):
            current = "overlay"
            overlay = clean.replace("OVERLAY:", "").strip()

        elif clean.startswith("SHORT:"):
            current = "short"
            short = clean.replace("SHORT:", "").strip()

        elif clean.startswith("LONG:"):
            current = "long"
            long = clean.replace("LONG:", "").strip()

        elif clean.startswith("ARTICLE:"):
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

    return overlay.strip(), short.strip(), long.strip(), article.strip()