import re

def clean_text(text):
    text = text.replace("구매", "").strip()
    text = re.split(r"\d", text)[0].strip()
    text = re.sub(r"\s+", " ", text)
    return text
