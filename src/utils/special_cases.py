import re


SPECIAL_CASES = {
    "donia": "Coriander",
    "tom": "Tomato",
    "green pepper": "Pepper Green",
    "red pepper": "Pepper Red",
    "spring onion": "Onion Spring",
    "spanish onion": "Onion Spanish",
    "potato": "Potato White"
}

def apply_special_cases(word: str) -> str | None:
    """
    Return mapped product if word matches a special case, else None.
    """
    if not word:
        return None

    clean = re.sub(r"^\d+\s*[a-zA-Z]*\s*", "", word.strip().lower())
    return SPECIAL_CASES.get(clean)