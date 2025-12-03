import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Models
MODEL_ANALYTICAL = "gpt-4.1-mini"
MODEL_NARRATIVE = "gpt-4.1-mini"
MODEL_SYNTHESIS = "gpt-4.1"
MODEL_GM_FINAL = "gpt-4.1"
MODEL_PLAYER_FINAL = "gpt-4.1"
MODEL_QA = "gpt-4.1-mini"

# Storage dirs
STORAGE_DIR = BASE_DIR / "storage"
OUTPUT_DIR = STORAGE_DIR / "output"

# Maximum number of tokens per transcript chunk
MAX_CHUNK_TOKENS = 12000

# --- CHARACTER ALIAS CONFIG -----------------------------------------------

CHARACTER_MAP_FILE = BASE_DIR / "config" / "characters.json"

# Load new-format characters.json
# Expected structure:
# {
#   "characters": {
#       "Graak": { "aliases": [...], "pronouns": "he/him" },
#       "Bahl":  { "aliases": [...], "pronouns": "she/her" }
#   }
# }
CHARACTER_DATA = json.loads(CHARACTER_MAP_FILE.read_text(encoding="utf-8"))

# Build alias map (canonical → aliases)
CHARACTER_ALIASES = {
    canonical: data["aliases"]
    for canonical, data in CHARACTER_DATA["characters"].items()
}

# Build pronoun map (canonical → pronouns)
CHARACTER_PRONOUNS = {
    canonical: data.get("pronouns", "")
    for canonical, data in CHARACTER_DATA["characters"].items()
}

# Words that should NEVER be normalized away
PROTECTED_WORDS = [
    "Alkesh",
    "Al'kesh",
    "Al-Kesh",
    "Al Kesh",
    "Al Kash",
]

# No legacy merging of old format needed anymore
# The old block using `info["role"]` is removed entirely.


# import json
# from pathlib import Path

# BASE_DIR = Path(__file__).resolve().parent

# # Models
# MODEL_ANALYTICAL = "gpt-4.1-mini"
# MODEL_NARRATIVE = "gpt-4.1-mini"
# MODEL_SYNTHESIS = "gpt-4.1"
# MODEL_GM_FINAL = "gpt-4.1"
# MODEL_PLAYER_FINAL = "gpt-4.1"
# MODEL_QA = "gpt-4.1-mini"

# # Storage dirs
# STORAGE_DIR = BASE_DIR / "storage"
# OUTPUT_DIR = STORAGE_DIR / "output"

# # Maximum number of tokens per transcript chunk
# MAX_CHUNK_TOKENS = 12000

# # --- CHARACTER ALIAS CONFIG -----------------------------------------------

# CHARACTER_MAP_FILE = BASE_DIR / "config" / "characters.json"

# CHARACTER_DATA = json.loads(Path("app/config/characters.json").read_text())

# CHARACTER_ALIASES = {
#     canonical: data["aliases"]
#     for canonical, data in CHARACTER_DATA["characters"].items()
# }

# CHARACTER_PRONOUNS = {
#     canonical: data.get("pronouns", "")
#     for canonical, data in CHARACTER_DATA["characters"].items()
# }

# PROTECTED_WORDS = [
#     "Alkesh", 
#     "Al'kesh",
#     "Al-Kesh",
#     "Al Kesh",
#     "Al Kash"
# ]

# if CHARACTER_MAP_FILE.exists():
#     raw = json.loads(CHARACTER_MAP_FILE.read_text(encoding="utf-8"))

#     # raw looks like:
#     # {
#     #   "Jason": { "role": "Graak", "aliases": ["Jason", "J", ...] },
#     #   "Nicky": { "role": "Bahl", "aliases": [...] }
#     # }
    
#     for real_name, info in raw.items():
#         character = info["role"]
#         aliases = info.get("aliases", [])

#         # Each character gets its full alias list
#         CHARACTER_ALIASES[character] = aliases

# else:
#     CHARACTER_ALIASES = {}
