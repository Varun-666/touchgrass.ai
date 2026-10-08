# 🌿 TouchGrass AI

> **Use AI for 10 seconds. Then put the phone away.**

TouchGrass AI is a local-first outdoor activity companion built for the Hacktoberfest Open-Source AI Challenge — Week 1: **Touch Grass**.

Instead of making another AI app that keeps people talking to a screen, TouchGrass generates a short, practical outdoor mission that the user can take into the real world.

## What it does

Choose a mode and a few preferences:

- 🌿 **Nature** — observation, walking, birding and nature missions
- 🚶 **Explore** — small exploration challenges for parks, neighborhoods and trails
- 🌱 **Garden** — simple gardening and plant-care missions

The local AI creates a structured mission containing:

- a title
- a short reason
- a 3-step activity
- things to look for
- a time-box
- a phone-away instruction
- a safety note

## Open-source AI

The default model is **Qwen/Qwen2.5-0.5B-Instruct**, loaded locally through Hugging Face Transformers.

Model: https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct

License: Apache-2.0

The model is downloaded once and then loaded from the local Hugging Face cache. No paid AI API or API key is required.

### Why this matters

**Privacy:** user preferences stay on the local machine.

**Offline path:** after the model is downloaded, generation itself does not require a cloud AI API.

**Model freedom:** the model can be swapped for another compatible open-weight model.

**Cost:** there are no per-request model API charges.

**Hackability:** prompts, model settings and the application logic are all visible and editable.

## Architecture

```text
Browser
   │
   ▼
FastAPI application
   │
   ├── Mission validation
   ├── Safety rules
   └── Prompt builder
          │
          ▼
   Qwen2.5-0.5B-Instruct
       (local inference)
          │
          ▼
   Structured Outdoor Mission
          │
          ▼
       🌳 Outside
```

## Quick start

### 1. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the app

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

The first generation downloads the model from Hugging Face. Subsequent runs use the local cache.

## Hardware

The default model is intentionally small (~0.5B parameters) so this project is approachable on consumer hardware. Transformers will use a CUDA GPU when available and otherwise CPU.

For a stronger machine, change `MODEL_ID` in `app/ai_engine.py` to another compatible open-weight instruction model.

## Optional environment variables

```text
TOUCHGRASS_MODEL=Qwen/Qwen2.5-0.5B-Instruct
TOUCHGRASS_MAX_NEW_TOKENS=320
TOUCHGRASS_TEMPERATURE=0.75
```

## API

### `GET /api/health`

Returns model status and device information.

### `POST /api/mission`

Example:

```json
{
  "mode": "nature",
  "duration": 30,
  "energy": "low",
  "setting": "park",
  "interests": ["birds", "plants"],
  "goal": "I want something relaxing"
}
```

## Demo flow

For the challenge video, use this sequence:

1. Open TouchGrass AI.
2. Select **Nature**.
3. Choose 30 minutes and low energy.
4. Enter `birds, plants`.
5. Generate a mission.
6. Show the mission for a few seconds.
7. Say: **“Now the app's job is done.”**
8. Put the phone away and actually do the mission outside.
9. Record a short clip/photo of the real-world activity.

## Safety

TouchGrass is not a medical, navigation, emergency or wildlife-identification system. Generated activities should be performed in familiar, safe locations and users should follow local rules. The app explicitly avoids instructions involving entering restricted areas, approaching wildlife, consuming unknown plants, or dangerous terrain.

## Project structure

```text
touchgrass-ai/
├── app/
│   ├── __init__.py
│   ├── ai_engine.py
│   ├── main.py
│   ├── schemas.py
│   └── static/
│       ├── index.html
│       ├── app.js
│       ├── styles.css
│       ├── manifest.json
│       └── sw.js
├── tests/
│   └── test_api.py
├── .gitignore
├── LICENSE
├── requirements.txt
└── README.md
```

## License

MIT for the application code. The AI model remains under its own Apache-2.0 license.
