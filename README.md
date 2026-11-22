# TranscriBot

A small private Telegram bot that transcribes voice messages and audio files using the
[OVHcloud AI Endpoints](https://endpoints.ai.cloud.ovh.net/) Whisper API
(`whisper-large-v3-turbo` by default, ≈ €0.046 per hour of audio).

## Features

- Transcribes Telegram voice notes (`.ogg`) and forwarded audio files (`.mp3`, `.m4a`, …).
- Private: only the configured Telegram user ID gets a reply (every transcription costs money).
- Long transcripts are split across several messages (Telegram's 4096-char limit).
- Downloaded audio is deleted after processing.
- No local model: the image is tiny and runs fine on low-power hardware.

Note: Telegram's Bot API only lets bots download files up to 20 MB.

## Setup

1. Create a bot with [@BotFather](https://t.me/BotFather) and copy the token.
2. In the OVH control panel → Public Cloud → AI & Machine Learning → AI Endpoints → API keys,
   create a dedicated key for this bot.
3. Get your numeric Telegram user ID from [@userinfobot](https://t.me/userinfobot).
4. Configure:
   ```bash
   cp .env.example .env && chmod 600 .env
   # fill in BOT_TOKEN, OVH_API_KEY, ALLOWED_USER_ID
   ```

| Variable          | Required | Default                  |
|-------------------|----------|--------------------------|
| `BOT_TOKEN`       | yes      |                          |
| `OVH_API_KEY`     | yes      |                          |
| `ALLOWED_USER_ID` | yes      |                          |
| `WHISPER_MODEL`   | no       | `whisper-large-v3-turbo` |
| `LANGUAGE`        | no       | `de`                     |

If accuracy is poor, try `WHISPER_MODEL=whisper-large-v3`.

## Run

With Docker Compose (recommended):
```bash
docker compose up -d --build
docker logs -f transcribot   # expect "Bot is starting..."
```

Locally:
```bash
uv sync
set -a; . ./.env; set +a
uv run main.py
```

## Usage

Send `/start`, then send or forward any voice message or audio file. The bot replies with the transcript.

Any OpenAI-compatible `/audio/transcriptions` endpoint can be used by changing `OVH_URL` in
`main.py` and `WHISPER_MODEL`.
