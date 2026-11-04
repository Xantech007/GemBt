import os
import logging
from dotenv import load_dotenv
from telethon import TelegramClient, events
from google import genai

# Load environment variables
load_dotenv()
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_ID = "gemini-2.5-flash"

# Initialize Telethon Client (session name will save your login state)
bot = TelegramClient('gemini_userbot_session', API_ID, API_HASH)

@bot.on(events.NewMessage(incoming=True))
async def handle_message(event):
    # Ignore messages you send yourself
    if event.out:
        return

    user_message = event.raw_text
    if not user_message:
        return

    # Optional: Restrict interaction. 
    # For example, if you only want it to respond in group chats when someone tags you or replies to you:
    if event.is_group:
        me = await bot.get_me()
        is_reply_to_me = False
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            if reply_msg and reply_msg.sender_id == me.id:
                is_reply_to_me = True
        
        # If not mentioned and not replying to you, ignore the message
        if not event.mentioned and not is_reply_to_me:
            return

    try:
        # Simulate 'typing' status in chat while Gemini generates a reply
        async with event.client.action(event.chat_id, 'typing'):
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=user_message,
            )
            reply_text = response.text

        # Reply directly using your real account
        await event.reply(reply_text)

    except Exception as e:
        logger.error(f"Error communicating with Gemini: {e}")

def main():
    print("Starting UserBot...")
    # This will initiate the login process in the terminal
    bot.start()
    print("UserBot is active and listening for messages...")
    bot.run_until_disconnected()

if __name__ == "__main__":
    main()
