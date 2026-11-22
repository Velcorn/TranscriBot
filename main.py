import logging
import os
import tempfile
from pathlib import Path

import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.environ["BOT_TOKEN"]
OVH_API_KEY = os.environ["OVH_API_KEY"]
ALLOWED_USER_ID = int(os.environ["ALLOWED_USER_ID"])
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "whisper-large-v3-turbo")
# Empty = let Whisper auto-detect the language per message (handles German and English).
LANGUAGE = os.environ.get("LANGUAGE", "").strip()
OVH_URL = "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/audio/transcriptions"

# Telegram allows 4096 chars per message; leave some headroom.
CHUNK_SIZE = 4000

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
# httpx logs every request URL at INFO, which includes the bot token for Telegram calls.
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    if update.message.from_user.id != ALLOWED_USER_ID:
        return
    await update.message.reply_html(
        "Hello! I'm your personal transcription bot.\n\n"
        "Forward any voice message or audio file to me, and I'll transcribe it for you "
        "using the OVHcloud Whisper API."
    )


async def transcribe(path: Path) -> str:
    """Sends the audio file to the OVHcloud Whisper endpoint and returns the text."""
    data = {"model": WHISPER_MODEL}
    if LANGUAGE:
        data["language"] = LANGUAGE
    async with httpx.AsyncClient(timeout=300) as client:
        with path.open("rb") as f:
            r = await client.post(
                OVH_URL,
                headers={"Authorization": f"Bearer {OVH_API_KEY}"},
                data=data,
                files={"file": (path.name, f)},
            )
    r.raise_for_status()
    return r.json()["text"].strip()


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles voice messages and audio files for transcription."""
    user_id = update.message.from_user.id
    if user_id != ALLOWED_USER_ID:
        logger.warning("Unauthorized access denied for %s.", user_id)
        return

    processing_message = await update.message.reply_text("Downloading... Please wait.")

    input_audio_path = None
    try:
        file_id = None
        file_extension = ".tmp"
        if update.message.voice:
            file_id = update.message.voice.file_id
            file_extension = ".ogg"
        elif update.message.audio:
            file_id = update.message.audio.file_id
            if update.message.audio.file_name:
                file_extension = Path(update.message.audio.file_name).suffix or file_extension

        if not file_id:
            await processing_message.edit_text("Sorry, I couldn't find an audio file in that message.")
            return

        input_audio_path = Path(tempfile.gettempdir()) / f"input_{file_id}{file_extension}"
        audio_file = await context.bot.get_file(file_id)
        await audio_file.download_to_drive(input_audio_path)
        logger.info("Downloaded audio file to %s", input_audio_path)

        await processing_message.edit_text("Transcribing…")
        text = await transcribe(input_audio_path)
        if not text:
            await processing_message.edit_text("(no speech detected)")
            return

        logger.info("Transcription successful (%d chars).", len(text))
        # Plain text, NOT Markdown: transcripts can contain * _ etc.
        chunks = [text[i:i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]
        await processing_message.edit_text(chunks[0])
        for chunk in chunks[1:]:
            await update.message.reply_text(chunk)

    except httpx.HTTPStatusError as e:
        logger.error(
            "OVH API error: HTTP %s - %s", e.response.status_code, e.response.text[:300]
        )
        await processing_message.edit_text("Transcription failed, see logs.")
    except Exception:
        logger.exception("An unexpected error occurred.")
        await processing_message.edit_text("Transcription failed, see logs.")

    finally:
        if input_audio_path and input_audio_path.exists():
            try:
                input_audio_path.unlink()
                logger.info("Removed: %s", input_audio_path)
            except Exception as e:
                logger.error("Error removing file %s: %s", input_audio_path, e)


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_audio))

    logger.info("Bot is starting...")
    application.run_polling()


if __name__ == "__main__":
    main()
