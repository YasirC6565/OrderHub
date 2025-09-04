
from .client import client
from rapidfuzz import fuzz, process
from metaphone import doublemetaphone


def suggest_product_ai(word: str, product_db: list[str]) -> str | None:
    """ Use OpenAI to find the closest product in the catalog. """
    product_list_str = "\n".join(f"- {p}" for p in product_db)

    prompt = f"""
    You are a product matcher. 
The customer typed: "{word}"

Valid catalog:
{product_list_str}

Rules:
- Return the single closest product name from the catalog.
- Always prefer a close match over "None" if spelling is slightly off.
- Be tolerant of typos and missing letters:
  Examples:
  - "chiken" -> "chicken"
  - "brocoli" -> "broccoli"
  - "onoin" -> "onion"
- Only return EXACTLY one product name from the catalog, nothing else.
- If the word is completely unrelated (e.g., "carpet"), return "None".
- if all letters are matching but 2 or 3 are not matching, then return the matched product.

    
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",   # fast + cheap
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20,
        temperature=0
    )

    suggestion = response.choices[0].message.content.strip()
    return None if suggestion.lower() == "none" else suggestion

def suggest_product_fuzzy(word: str, product_db: list[str], score_cutoff: int = 25) -> str | None:
    """
    Use RapidFuzz to find the closest product in the catalog.
    """
    word_clean = word.strip().lower()
    db_clean = [p.strip().lower() for p in product_db]

    match = process.extractOne(word_clean, db_clean, scorer=fuzz.WRatio, score_cutoff=score_cutoff)
    if match:
        original_index = db_clean.index(match[0])
        return product_db[original_index]
    return None

def phonetic_match(word: str, product_db: list[str]) -> str | None:
    word_code = doublemetaphone(word)[0]
    for p in product_db:
        if doublemetaphone(p)[0] == word_code:
            return p
    return None

