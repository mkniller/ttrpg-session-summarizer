import json
from pathlib import Path
from app.config import OUTPUT_DIR

def save_outputs(result: dict, source_name: str | None = None) -> dict:
    """
    Saves:
      - full JSON result
      - GM recap as Markdown
      - Player story recap as Markdown
    """

    # Base filename
    session_base = source_name.rsplit(".", 1)[0] if source_name else "session_output"

    # --- JSON ----
    json_path = OUTPUT_DIR / f"{session_base}_summary.json"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    # --- GM Markdown ----
    gm_md = f"# GM Recap — {session_base}\n\n" + result.get("gm_final_summary", "")
    gm_path = OUTPUT_DIR / f"{session_base}_gm_recap.md"
    gm_path.write_text(gm_md, encoding="utf-8")

    # --- Player Markdown ----
    player_md = f"# Player Recap — {session_base}\n\n" + result.get("player_final_story", "")
    player_path = OUTPUT_DIR / f"{session_base}_player_recap.md"
    player_path.write_text(player_md, encoding="utf-8")

    return {
        "json": str(json_path),
        "gm_markdown": str(gm_path),
        "player_markdown": str(player_path),
    }
