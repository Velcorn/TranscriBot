import logging
import os
import subprocess
from config import config
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


# Load bot token from config
BOT_TOKEN = config()['bot_token']
# Choose your WhisperX model. "base" is fast, "large-v2" is more accurate.
WHISPER_MODEL = "large-v2"
# Optional: Set this to your Telegram user ID to make the bot private
ALLOWED_USER_ID = None

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_html(
        "Hello! I'm your personal transcription bot.\n\n"
        "Forward any voice message or audio file to me, and I'll transcribe it for you using WhisperX."
    )


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles voice messages and audio files for transcription."""
    # Check if the user is allowed (if privacy is enabled)
    if ALLOWED_USER_ID and update.message.from_user.id != ALLOWED_USER_ID:
        logger.warning(f"Unauthorized access denied for {update.message.from_user.id}.")
        return

    # Let the user know the bot is working on it
    processing_message = await update.message.reply_text("Downloading and processing... Please wait.")

    input_audio_path = None # Define here to ensure it's available in 'finally'
    try:
        file_id = None
        file_extension = ".tmp" # Default extension
        if update.message.voice:
            file_id = update.message.voice.file_id
            file_extension = ".ogg"
        elif update.message.audio:
            file_id = update.message.audio.file_id
            if update.message.audio.file_name:
                # Use Path to get the suffix from the original filename
                file_extension = Path(update.message.audio.file_name).suffix

        if not file_id:
            await processing_message.edit_text("Sorry, I couldn't find an audio file in that message.")
            return

        input_audio_path = Path(f"input_{file_id}{file_extension}")
        
        audio_file = await context.bot.get_file(file_id)
        await audio_file.download_to_drive(input_audio_path)
        logger.info(f"Downloaded audio file to {input_audio_path}")

        await processing_message.edit_text("Transcribing with WhisperX... this may take a moment.")
        
        # Run WhisperX using subprocess
        command = [
            "whisperx",
            str(input_audio_path),
            "--model", WHISPER_MODEL,
            "--compute_type", "int8",
            "--language", "de"
        ]
        
        process = subprocess.run(command, capture_output=True, text=True, check=False)

        if process.returncode != 0:
            logger.error(f"WhisperX Error: {process.stderr}")
            await processing_message.edit_text(f"An error occurred during transcription.\n\n<pre>{process.stderr}</pre>", parse_mode='HTML')
            return

        # Read the transcription result
        transcription_file_path = input_audio_path.with_suffix(".txt")
        
        if transcription_file_path.exists():
            transcription = transcription_file_path.read_text(encoding='utf-8')
            logger.info("Transcription successful.")
            await processing_message.edit_text(transcription, parse_mode='Markdown')
        else:
            await processing_message.edit_text("Could not find the transcription output file.")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        await processing_message.edit_text(f"An unexpected error occurred: {e}")
    
    finally:
        if input_audio_path and input_audio_path.exists():
            # Get the base name of the file without any extension (e.g., "input_123")
            file_stem = input_audio_path.stem
            parent_dir = input_audio_path.parent

            # Find and delete all files starting with that same base name
            logger.info(f"Cleaning up files matching pattern: {file_stem}*")
            for file_to_remove in parent_dir.glob(f"{file_stem}*"):
                try:
                    if file_to_remove.is_file():
                        file_to_remove.unlink()
                        logger.info(f"Removed: {file_to_remove}")
                except Exception as e:
                    logger.error(f"Error removing file {file_to_remove}: {e}")


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_audio))

    # Start the Bot
    logger.info("Bot is starting...")
    application.run_polling()


if __name__ == '__main__':
    main()
