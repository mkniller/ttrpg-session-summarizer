# 📜 TTRPG Session Summarizer

*A fully automated ShadowDark-style session recap generator using GPT-4.1*

This project converts raw TTRPG session transcripts into:

- **GM Recap** — factual, structured, system-neutral  
- **Player Recap** — gritty, atmospheric ShadowDark narrative  
- **Canonical Entity Extraction** — characters, aliases, pronouns, NPCs, items, creatures  
- **Timeline Extraction** — strict chronological event list with simultaneous scenes  
- **Chunk-Level Processing** — analytical summaries, narrative digests, action logs  
- **Name & Location Normalization** — PC aliases and misspellings automatically resolved  

Everything is done through a multi-stage FastAPI pipeline backed by GPT-4.1.

---

## 🚀 Features

### ✔ Canon Extraction  

Builds canonical lists of:

- Player characters (with pronouns)
- NPCs  
- Locations  
- Items & artifacts  
- Creatures  

### ✔ Timeline Extraction  

Strict chronological ordering of events from the transcript — zero hallucinations.

### ✔ Complete Recap Generation  

- **GM Recap** → objective and structured  
- **Player Recap** → atmospheric, gritty, in-world narrative  
Both guaranteed to reference only transcript events.

### ✔ Automatic Player-Name → Character-Name Replacement  

Using `characters.json`.

### ✔ Location Normalization  

Fixes misspellings like “elkesh” → “Alkesh”.

### ✔ Multi-Stage Pipeline  

1. Normalize transcript  
2. Extract canon  
3. Extract timeline  
4. Chunk transcript  
5. Analytical summaries  
6. Narrative digests  
7. Action logs  
8. GM synthesis  
9. Player synthesis  
10. QA check  
11. Save output bundle  

---

## 📁 Project Structure

```
app/
  ├── main.py
  ├── routes/upload.py
  ├── pipeline/
  │     ├── summarizer.py
  │     ├── chunking.py
  │     ├── models.py
  │     ├── utils.py
  │     ├── postprocess.py
  │     └── prompts/
  │           ├── canon_extract.txt
  │           ├── timeline_extract.txt
  │           ├── narrative_digest.txt
  │           ├── narrative_synthesis.txt
  │           ├── narrative_action_extract.txt
  │           ├── gm_analytical.txt
  │           ├── gm_synthesis.txt
  │           ├── gm_final.txt
  │           ├── player_story.txt
  │           └── qa_check.txt
  ├── config/
  │     └── characters.json
  └── storage/
        └── output/
```

---

## 🧰 Requirements

- Python **3.11**
- OpenAI API Key  
- macOS / Linux / Windows  

---

## 🔧 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/mkniller/ttrpg-session-summarizer.git
cd ttrpg-summarizer
```

---

## 🐍 Create and Activate a Virtual Environment

### macOS / Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### Windows

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
```

---

## 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Set Your OpenAI API Key

### macOS / Linux

```bash
export OPENAI_API_KEY="your-key-here"
```

### Windows

```powershell
setx OPENAI_API_KEY "your-key-here"
```

Restart the terminal if needed.

---

## 🏃 Run the API Server

```bash
uvicorn app.main:app --reload
```

You should see:

```shell
Uvicorn running on http://127.0.0.1:8000
```

---

## 📤 Uploading a Transcript

### Using curl

```bash
curl -X POST "http://127.0.0.1:8000/upload" \
  -F "file=@session_transcript.txt"
```

### Or use the Swagger UI

```plaintext
http://127.0.0.1:8000/docs
```

---

## 📥 Output Files

All generated content is stored in:

```plaintext
storage/output/{session_filename}/
```

This includes:

- `full_summary.json`
- `gm_recap.md`
- `player_recap.md`
- `canon.json`
- `timeline.json`
- Chunk summaries (analytical, narrative, action logs)

---

## 🔧 Configuration Details

### Character Aliases + Pronouns

Located at:

```plaintext
app/config/characters.json
```

Example:

```json
{
  "characters": {
    "Graak": {
      "aliases": ["Jason", "Grak", "Grok"],
      "pronouns": "he/him"
    },
    "Bahl": {
      "aliases": ["Nicky", "Nic"],
      "pronouns": "he/him"
    },
    "Durl": {
      "aliases": ["Eric", "Durhl"],
      "pronouns": "he/him"
    },
    "Lirel": {
      "aliases": ["Alicia"],
      "pronouns": "she/her"
    }
  }
}
```

This file controls:

- Name normalization  
- Alias matching  
- Pronoun assignment  
- Which PCs exist (even if absent from the session)

---

## 🧪 Development Notes

- Canon extraction uses strict no-hallucination rules  
- Timeline extractor enforces chronological ordering  
- Player recap strictly uses canonical pronouns  
- GM recap replaces real names with PC names  

---

## 🛠 Troubleshooting

### Address already in use

```bash
killall uvicorn
```

### Lirel appearing when she wasn’t at the session 

Make sure her **aliases** don’t appear anywhere in the transcript.

### Pronouns incorrect  

Check:

- `characters.json`
- `canon_extract.txt` prompt placement
- That alias normalization isn’t confusing characters

---

## 🧙 Contributing

Pull requests and feature suggestions are welcome!

Future enhancements could include:

- NPC relationship tracker  
- Loot / treasure tables  
- Statblock extraction  
- VTT export integration  

---

## 🏁 License

MIT License.
