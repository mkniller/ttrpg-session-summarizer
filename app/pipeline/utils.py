import re
from pathlib import Path
from app.config import BASE_DIR
from app.config import CHARACTER_ALIASES
from app.config import PROTECTED_WORDS
from rapidfuzz import fuzz, process
from collections import Counter
from difflib import SequenceMatcher

def get_prompts_dir() -> Path:
    return BASE_DIR / "pipeline" / "prompts"


def load_prompt(name: str) -> str:
    path = get_prompts_dir() / name
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def format_prompt(template: str, **kwargs) -> str:
    return template.format(**kwargs)

# -------------------------
# STEP 1 — Prepare alias map
# -------------------------
ALIAS_MAP = {}
SHORT_ALIASES = set()

for character, aliases in CHARACTER_ALIASES.items():
    for alias in aliases:
        if len(alias) <= 3:
            SHORT_ALIASES.add(alias.lower())
        else:
            ALIAS_MAP[alias] = character


# -------------------------
# STEP 2 — Words that must NEVER be replaced
# These can be expanded dynamically later.
# -------------------------
HARDCODE_PROTECTED = {
    "alkesh", "larry",  
    "scorpion", "hyenas", "beetles",
    "ruins", "desert", "tomb",
    "trapdoor", "infant", "mummy", "banners"
}


# -------------------------
# STEP 3 — Heuristic location classifier
# -------------------------
LOCATION_HINTS = {
    "north", "south", "east", "west",
    "room", "door", "chamber", "hall", "corridor",
    "sand", "desert", "ruins", "vault",
    "basin", "altar"
}


def looks_like_location(token: str, prev: str = "", next_: str = "") -> bool:
    lower = token.lower()

    if lower in HARDCODE_PROTECTED:
        return True

    # Adjacent to known location context
    if prev.lower() in LOCATION_HINTS or next_.lower() in LOCATION_HINTS:
        return True

    # Lowercase nouns are almost never names
    if token[0].islower():
        return True

    # Multi-word nouns, e.g., 'Silver' + 'Bengal'
    if "-" in token:
        return True

    return False


# -------------------------
# STEP 4 — Fuzzy replacer
# -------------------------
FUZZ_THRESHOLD = 88  # was 80; now stricter


def fuzzy_replace_real_names_with_characters(text: str) -> str:
    tokens = re.findall(r"\b[\w#'-]+\b", text)
    new_tokens = []
    length = len(tokens)

    for i, tok in enumerate(tokens):
        lower = tok.lower()
        prev_tok = tokens[i - 1] if i > 0 else ""
        next_tok = tokens[i + 1] if i + 1 < length else ""

        # → Rule: protect non-names
        if looks_like_location(tok, prev_tok, next_tok):
            new_tokens.append(tok)
            continue

        # → Rule: exact short alias match
        if lower in SHORT_ALIASES:
            # Only replace if the word is capitalized (real name)
            if tok[0].isupper():
                # find correct mapping
                for character, aliases in CHARACTER_ALIASES.items():
                    if lower in [a.lower() for a in aliases]:
                        new_tokens.append(character)
                        break
                else:
                    new_tokens.append(tok)
            else:
                new_tokens.append(tok)
            continue

        # → Rule: fuzzy match only if token looks like a name
        if not tok[0].isupper():
            new_tokens.append(tok)
            continue

        if len(tok) < 3:
            new_tokens.append(tok)
            continue

        # Perform fuzzy lookup
        match, score, _ = process.extractOne(
            tok,
            list(ALIAS_MAP.keys()),
            scorer=fuzz.WRatio
        )

        if score >= FUZZ_THRESHOLD:
            new_tokens.append(ALIAS_MAP[match])
        else:
            new_tokens.append(tok)

    return " ".join(new_tokens)

LOCATION_PATTERNS = [
    r"\bthe ([A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)*)\b",
    r"\bin ([A-Z][a-zA-Z]+)\b",
    r"\bat ([A-Z][a-zA-Z]+)\b",
    r"\b([A-Z][a-zA-Z]+ Room)\b",
    r"\b([A-Z][a-zA-Z]+ Chamber)\b",
    r"\b([A-Z][a-zA-Z]+ Hall)\b",
]

def extract_location_candidates(transcript: str, character_names: list[str]) -> list[str]:
    raw_candidates = []

    for pat in LOCATION_PATTERNS:
        for match in re.findall(pat, transcript):
            if isinstance(match, tuple):
                match = match[0]
            if match not in character_names:
                raw_candidates.append(match)

    # Count occurrences
    counts = Counter(raw_candidates)

    # Keep candidates that appear at least twice (filters noise)
    candidates = [loc for loc, c in counts.items() if c >= 1]

    return sorted(set(candidates))

def similar(a: str, b: str, threshold: float = 0.72) -> bool:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold

def cluster_locations(locations: list[str]) -> dict[str, list[str]]:
    clusters = {}
    used = set()

    for loc in locations:
        if loc in used:
            continue

        clusters[loc] = [loc]
        used.add(loc)

        for other in locations:
            if other in used:
                continue
            if similar(loc, other):
                clusters[loc].append(other)
                used.add(other)

    return clusters

def pick_canonical_name(cluster: list[str], transcript: str) -> str:
    # Pick the version with the highest frequency in transcript
    counts = {name: transcript.count(name) for name in cluster}
    return max(counts, key=counts.get)

def normalize_locations(transcript: str, character_names: list[str]) -> tuple[str, dict]:
    # Step 1: extract candidates
    candidates = extract_location_candidates(transcript, character_names)

    # Step 2: cluster similar names
    clusters = cluster_locations(candidates)

    canon_map = {}

    # Step 3: choose canonical form
    for base, variants in clusters.items():
        canonical = pick_canonical_name(variants, transcript)
        for v in variants:
            canon_map[v] = canonical

    # Step 4: apply replacements
    normalized = transcript
    for old, new in canon_map.items():
        normalized = re.sub(rf"\b{old}\b", new, normalized)

    return normalized, canon_map
