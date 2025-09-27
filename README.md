# Telegram WhisperX Transcription Bot

A simple yet powerful Telegram bot that uses the [WhisperX](https://github.com/m-bain/whisperX) model to transcribe any voice message or audio file you send to it.

This bot is designed to be self-hosted, giving you a private and efficient way to convert speech to text.

## Features ✨

-   **High-Quality Transcription**: Leverages the accuracy of the WhisperX `large-v2` model.
-   **Handles Voice & Audio**: Transcribes both Telegram voice notes (`.ogg`) and forwarded audio files (e.g., `.mp3`, `.m4a`).
-   **Private & Secure**: Run the bot for your personal use by setting an allowed user ID.
-   **Automatic Cleanup**: Deletes downloaded audio and transcription files after processing to save space.
-   **Docker Support**: Includes a `Dockerfile` for easy, containerized deployment.

---

## Prerequisites

Before you begin, ensure you have the following installed:
-   [Python](https://www.python.org/downloads/) 3.10+
-   [Git](https://git-scm.com/)
-   [FFmpeg](https://ffmpeg.org/download.html) (WhisperX requires this for audio processing)
-   [Docker](https://www.docker.com/products/docker-desktop/) (Optional, for containerized deployment)

---

## Setup & Installation 🛠️

Follow these steps to get your transcription bot up and running.

### 1. Clone the Repository

First, clone this repository to your local machine or server.

```bash
git clone https://github.com/Velcorn/TranscriBot
cd TranscriBot
```

### 2. Configure the Bot

The bot's configuration is managed in a `config.ini` file. A template is provided.

**Rename the example configuration file:**
```bash
mv config_ex.ini config.ini
```

**Edit `config.ini`:**
Now, open the `config.ini` file and add your Telegram Bot Token.

```ini
[telegram]
bot_token = YOUR_TELEGRAM_BOT_TOKEN_HERE
```
> **How to get a Bot Token?**
> Talk to the [@BotFather](https://t.me/BotFather) on Telegram. Use the `/newbot` command and follow the instructions. BotFather will give you a unique token.

### 3. Install Dependencies

Install the required Python packages. If you are using `uv` (as recommended in the Dockerfile), you can sync the dependencies.

**Using `uv` (recommended):**
```bash
uv sync --locked
```

**Using `pip`:**
Make sure you have a `requirements.txt` file, then run:
```bash
pip install -r requirements.txt
```

---

## Running the Bot 🚀

You can run the bot directly on your machine or as a Docker container.

### Locally

To run the bot directly with Python:

```bash
python main.py
```
The bot will start polling for updates from Telegram.

### With Docker

Using Docker is the recommended way to deploy the bot for continuous operation.

**1. Build the Docker image:**
```bash
docker build -t transcribot:latest .
```

**2. Run the Docker container:**
This command will run the bot in the background and ensure it restarts automatically if it stops.
```bash
docker run -d --restart unless-stopped --name transcribot transcribot:latest
```

---

## Configuration Options

You can customize the bot's behavior by editing these variables at the top of `main.py`:

-   `WHISPER_MODEL`: Change the WhisperX model. `large-v2` is highly accurate but slower. `base` or `medium` are faster alternatives.
-   `ALLOWED_USER_ID`: To make the bot private, set this variable to your numeric Telegram User ID. If you leave it as `None`, the bot will be public and respond to anyone.
    > You can find your User ID by talking to a bot like [@userinfobot](https://t.me/userinfobot).

---

## How to Use the Bot

1.  **Start the Bot**: In your Telegram chat with the bot, send the `/start` command.
2.  **Transcribe**: Simply forward any voice message or audio file to the bot.
3.  **Receive Transcription**: The bot will reply with the transcribed text. Please be patient, as processing for longer files can take a few moments.
