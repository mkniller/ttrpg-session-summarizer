from typing import Dict, List
import json

from app.pipeline.postprocess import save_outputs
from app.pipeline.utils import (
    fuzzy_replace_real_names_with_characters,
    load_prompt,
    format_prompt,
    normalize_locations
)
from app.config import (
    MODEL_ANALYTICAL,
    MODEL_NARRATIVE,
    MODEL_SYNTHESIS,
    MODEL_GM_FINAL,
    MODEL_PLAYER_FINAL,
    MODEL_QA,
    CHARACTER_ALIASES,  # from your existing config / characters.json
    CHARACTER_PRONOUNS,
    CHARACTER_DATA,
)
from app.pipeline.chunking import chunk_text
from app.pipeline.models import chat_completion

def replace_real_names_with_characters(text: str) -> str:
    for canonical, info in CHARACTER_DATA["characters"].items():
        aliases = info.get("aliases", [])
        for alias in aliases:
            text = text.replace(alias, canonical)
    return text

# --- Chunk-level steps ---

def summarize_chunk_analytical(chunk: str) -> str:
    template = load_prompt("gm_analytical.txt")
    prompt = format_prompt(template, chunk=chunk)
    return chat_completion(MODEL_ANALYTICAL, prompt, temperature=0.2)


def summarize_chunk_narrative(chunk: str) -> str:
    template = load_prompt("narrative_digest.txt")
    prompt = format_prompt(template, chunk=chunk)
    return chat_completion(MODEL_NARRATIVE, prompt, temperature=0.5)


def extract_actions(chunk_digest: str) -> str:
    template = load_prompt("narrative_action_extract.txt")
    prompt = format_prompt(template, chunk_digest=chunk_digest)
    return chat_completion(MODEL_NARRATIVE, prompt, temperature=0.3)

def safe_json_loads(text: str):
    if not text or not text.strip():
        raise ValueError("Empty response from model.")

    cleaned = text.strip()

    # Remove Markdown code fences like ```json ... ```
    if cleaned.startswith("```"):
        # Strip first ```... and last ```
        cleaned = cleaned.split("```", 2)
        if len(cleaned) >= 2:
            cleaned = cleaned[1]
        cleaned = cleaned.replace("json", "", 1).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        raise ValueError(f"Model did not return valid JSON. Received:\n{text[:300]}")

# --- New: canon & timeline extraction ---

def extract_canon(transcript: str) -> dict:
    template = load_prompt("canon_extract.txt")
    hints = json.dumps({
    "aliases": CHARACTER_ALIASES,
    "pronouns": CHARACTER_PRONOUNS
}, ensure_ascii=False)
    prompt = format_prompt(
        template,
        raw_transcript=transcript,
        character_hints=hints,
    )
    response = chat_completion(MODEL_ANALYTICAL, prompt, temperature=0.0)

    try:
        return safe_json_loads(response)
    except Exception:
        print("Canon extractor raw output:", response)
        raise

def extract_timeline(transcript: str, canon: dict) -> dict:
    """
    Use the full transcript and canonical entities to build a factual timeline.
    """
    template = load_prompt("timeline_extract.txt")
    canon_json = json.dumps(canon, ensure_ascii=False)
    prompt = format_prompt(
        template,
        raw_transcript=transcript,
        canon=canon_json,
    )
    response = chat_completion(MODEL_ANALYTICAL, prompt, temperature=0.0)
    return safe_json_loads(response)

# --- Synthesis & finals ---

def synthesize_gm_document(analytical_summaries: List[str]) -> str:
    combined = "\n\n".join(analytical_summaries)
    template = load_prompt("gm_synthesis.txt")
    prompt = format_prompt(template, analytical_summaries=combined)
    return chat_completion(MODEL_SYNTHESIS, prompt, temperature=0.2)


def synthesize_narrative_document(
    timeline: List[str],
    simultaneous_events: dict,
    narrative_digests: List[str],
    action_logs: List[str],
    canon: dict,
) -> str:
    timeline_text = "\n".join(timeline)
    simultaneous_text = json.dumps(simultaneous_events, ensure_ascii=False)
    digests_text = "\n\n".join(narrative_digests)
    actions_text = "\n\n".join(action_logs)
    canon_text = json.dumps(canon, ensure_ascii=False)

    template = load_prompt("narrative_synthesis.txt")
    prompt = format_prompt(
        template,
        timeline=timeline_text,
        simultaneous_events=simultaneous_text,
        narrative_digests=digests_text,
        action_logs=actions_text,
        canon_entities=canon_text,
    )
    return chat_completion(MODEL_SYNTHESIS, prompt, temperature=0.3)


def produce_gm_final(gm_synthesis: str) -> str:
    template = load_prompt("gm_final.txt")
    prompt = format_prompt(template, gm_synthesis=gm_synthesis)
    return chat_completion(MODEL_GM_FINAL, prompt, temperature=0.2)


def produce_player_story(narrative_synthesis: str) -> str:
    template = load_prompt("player_story.txt")
    prompt = format_prompt(template, narrative_synthesis=narrative_synthesis)
    return chat_completion(MODEL_PLAYER_FINAL, prompt, temperature=0.8)


def qa_check(
    gm_final: str,
    player_final: str,
    analytical_summaries: List[str],
    narrative_digests: List[str],
) -> str:
    analytical_combined = "\n\n".join(analytical_summaries)
    narrative_combined = "\n\n".join(narrative_digests)
    template = load_prompt("qa_check.txt")
    prompt = format_prompt(
        template,
        gm_final=gm_final,
        player_final=player_final,
        analytical_summaries=analytical_combined,
        narrative_digests=narrative_combined,
    )
    return chat_completion(MODEL_QA, prompt, temperature=0.0)


def run_pipeline(transcript: str, source_name: str | None = None) -> Dict:
    # Step 0: normalize character names first
    transcript = fuzzy_replace_real_names_with_characters(transcript)

    character_names = list(CHARACTER_ALIASES.keys())

    # 1) Normalize names (uses characters.json via CHARACTER_ALIASES)
    transcript, location_map = normalize_locations(transcript, character_names)

    # 2) Extract canon (characters, locations, items, creatures) from full transcript
    canon = extract_canon(transcript)


    # 3) Extract timeline from full transcript using canon
    timeline_data = extract_timeline(transcript, canon)
    timeline = timeline_data.get("timeline", [])
    simultaneous_events = timeline_data.get("simultaneous_events", {})

    # 4) Chunk for per-piece analysis/summaries
    chunks = chunk_text(transcript)

    analytical: List[str] = []
    action_logs: List[str] = []
    narrative_digests: List[str] = []

    for ch in chunks:
        analytical.append(summarize_chunk_analytical(ch))

        digest = summarize_chunk_narrative(ch)
        narrative_digests.append(digest)

        actions = extract_actions(digest)
        action_logs.append(actions)

    # 5) GM synthesis from analytical summaries
    gm_synth = synthesize_gm_document(analytical)

    # 6) Narrative synthesis from timeline + canon + chunk outputs
    narrative_synth = synthesize_narrative_document(
        timeline=timeline,
        simultaneous_events=simultaneous_events,
        narrative_digests=narrative_digests,
        action_logs=action_logs,
        canon=canon,
    )

    # 7) Final outputs
    gm_final_raw = produce_gm_final(gm_synth)
    gm_final = replace_real_names_with_characters(gm_final_raw)
    player_final = produce_player_story(narrative_synth)
    qa = qa_check(gm_final, player_final, analytical, narrative_digests)

    result = {
        "source": source_name,
        "chunk_count": len(chunks),
        "canon": canon,
        "timeline": timeline,
        "simultaneous_events": simultaneous_events,
        "chunk_analytical_summaries": analytical,
        "chunk_narrative_digests": narrative_digests,
        "chunk_action_logs": action_logs,
        "gm_synthesis": gm_synth,
        "player_synthesis": narrative_synth,
        "gm_final_summary": gm_final,
        "player_final_story": player_final,
        "qa_report": qa,
    }

    save_outputs(result, source_name)
    return result
