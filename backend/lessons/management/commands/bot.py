import os
import boto3
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from django.core.management.base import BaseCommand
from django.conf import settings
from lessons.utils.s3 import upload_file
from lessons.models import Audio , PostStatus
from asgiref.sync import sync_to_async

class Command(BaseCommand):
    help = "Run Telegram bot to download forwarded posts and upload to Ceph"

    def handle(self, *args, **options):
        # --- Load Config ---
        BOT_TOKEN = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
        TARGET_CHANNEL_ID = getattr(settings, "TELEGRAM_CHANNEL_ID", None)
        PROXY_URL = settings.PROXY_SOCKS5_URL 

        async def handle_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
            message = update.message

            await message.reply_text("⏳ Processing your file...")
            self.stdout.write(f"Processing message {message.message_id} from {message.chat_id}")
            # self.stdout.write(f"Message content: {message}")
            

            file = None
            title = ""
            
            if message.audio:
                file = await message.audio.get_file()
                title = message.audio.title
                file_name = message.audio.file_name
            # elif message.voice:
            #     file = await message.voice.get_file()
            #     file_name 
            elif message.document:
                file = await message.document.get_file()
                title = message.document.file_name
                file_name = message.document.file_name
            else:
                await message.reply_text("❌ No valid file found in the message.")
                return
            file_name = file_name.replace(" ","_")
            file_path = f"/tmp/{file_name}"
            await file.download_to_drive(file_path)
            await message.reply_text(f"✅ File downloaded locally. file title : {title} ")
            uploaded_path_file=upload_file(file_path)

            await sync_to_async(Audio.objects.create)(
                title=title or file_name,
                status=PostStatus.UPLOAD,
                uploaded_url=uploaded_path_file,
                audio_src="Telegram Bot"
            )

            os.remove(file_path)

            await message.reply_text(f"✅ Uploaded to Ceph!, {uploaded_path_file}")

        # --- Start Bot ---
        app_builder = ApplicationBuilder().token(BOT_TOKEN)
        if PROXY_URL:
            app_builder = app_builder.get_updates_proxy(PROXY_URL).proxy(PROXY_URL)

        app = app_builder.build()
        app.add_handler(MessageHandler(filters.ALL, handle_forward))

        self.stdout.write(self.style.SUCCESS("🤖 Telegram bot started..."))
        app.run_polling()
