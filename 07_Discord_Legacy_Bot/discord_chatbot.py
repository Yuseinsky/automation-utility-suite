# ==========================================
# 📦 Dependencies:
# pip install discord.py google-generativeai python-dotenv
# Compatible with Python 3.9+ and discord.py 2.0+
# ==========================================
import discord
import google.generativeai as genai
import os
import sys
import datetime

# Windows console encoding configuration
sys.stdout.reconfigure(errors='replace')

# ==========================================
# 🗝️ Configuration & Authentication Credentials
# ==========================================
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN', '')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
ALLOWED_CHANNEL_ID = int(os.environ.get('ALLOWED_CHANNEL_ID', '0'))
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')

if not DISCORD_TOKEN or not GEMINI_API_KEY:
    print("Error: Missing DISCORD_TOKEN or GEMINI_API_KEY in environment variables.")
    sys.exit(1)

# ==========================================
# 🧠 AI Engine Initialization
# ==========================================
genai.configure(api_key=GEMINI_API_KEY)

# Try loading system prompt if available
base_dir = os.path.dirname(os.path.abspath(__file__))
instruction_path = os.path.join(base_dir, "system_instruction.txt")

if os.path.exists(instruction_path):
    with open(instruction_path, "r", encoding="utf-8") as f:
        system_instruction = f.read()
else:
    system_instruction = (
        "You are a helpful and polite Discord chatbot agent. "
        "Maintain a friendly tone and assist users. "
        "Keep your responses concise and within 700 characters."
    )

model = genai.GenerativeModel('gemini-2.5-pro', system_instruction=system_instruction)

# ==========================================
# 👗 Discord Client & Memory Buffers
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Session history maps: channel_id -> chat session
chat_sessions = {}
# Backlog history maps: channel_id -> backlog list
channel_backlogs = {}

# ==========================================
# 💎 Memory Consolidation & Archiving System
# ==========================================
async def perform_archive(message, chat, channel_id, is_auto=False):
    trigger_type = "【Auto Archive】" if is_auto else "【Manual Archive】"
    await message.channel.send(f"✨ [System] Triggered {trigger_type}. Consolidating memory buffer, please wait...")
    
    # 1. Summarize the conversation history
    summary_prompt = (
        "Summarize the conversation history from this session into a structured markdown log. "
        "Include the key topics discussed, performance/response summary, and action items."
    )
    try:
        summary_response = chat.send_message(summary_prompt)
        summary_text = summary_response.text
    except Exception as e:
        summary_text = f"Failed to generate summary: {e}"
    
    # 2. Archive to disk (dual track: summary file and raw transcript)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    archive_dir = os.path.join(base_dir, "Memory_Archives")
    raw_dir = os.path.join(base_dir, "Raw_Transcripts")
    
    os.makedirs(archive_dir, exist_ok=True)
    os.makedirs(raw_dir, exist_ok=True)
    
    # Write summary
    summary_file = os.path.join(archive_dir, f"Summary_{timestamp}.md")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary_text)
        
    # Write raw log transcript
    raw_file = os.path.join(raw_dir, f"Raw_Transcript_{timestamp}.md")
    raw_transcript = f"# Raw Chat Transcript\n*   **Archived At:** {timestamp}\n\n---\n\n"
    for msg in chat.history:
        speaker = "User" if msg.role == 'user' else "Assistant"
        text = "".join([getattr(part, 'text', '') for part in msg.parts])
        if not text.strip():
            text = "(Attachment/Multimodal data)"
        raw_transcript += f"**[{speaker}]**\n{text}\n\n---\n"
        
    with open(raw_file, "w", encoding="utf-8") as f:
        f.write(raw_transcript)
        
    await message.channel.send(
        f"✅ Memory successfully archived!\n"
        f"📂 **Summary:** `{summary_file}`\n"
        f"📜 **Transcript:** `{raw_file}`\n"
        f"Session memory has been reset."
    )
    
    # 3. Reset the chat session and seed with the summary for continuity
    new_chat = model.start_chat(history=[])
    seed_prompt = (
        f"[SYSTEM] The conversation memory has been cleared and archived. "
        f"Here is a summary of the previous session for context: \n\n{summary_text}\n\n"
        f"Please acknowledge by saying: 'Context synchronized.'"
    )
    new_chat.send_message(seed_prompt)
    chat_sessions[channel_id] = new_chat

@client.event
async def on_ready():
    print('====================================')
    print(f'✨ [Discord Chatbot] Online')
    print(f'✨ Logged in as: {client.user}')
    print('====================================')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Restrict to allowed channel if configured
    if ALLOWED_CHANNEL_ID != 0 and message.channel.id != ALLOWED_CHANNEL_ID:
        return

    if message.content: 
        try:
            # Initialize chat session if first message in this channel
            if message.channel.id not in chat_sessions:
                chat_sessions[message.channel.id] = model.start_chat(history=[])
            
            chat = chat_sessions[message.channel.id]

            # ==========================================
            # 💎 Manual Archive Command
            # ==========================================
            if message.content.startswith("!archive"):
                await perform_archive(message, chat, message.channel.id, is_auto=False)
                return

            # ==========================================
            # 💬 Conversation Flow Handler (Smart Backlog Listening)
            # ==========================================
            if message.channel.id not in channel_backlogs:
                channel_backlogs[message.channel.id] = []

            # Check if chatbot is being addressed
            msg_lower = message.content.lower()
            bot_mentioned = client.user in message.mentions or any(name in msg_lower for name in ["bot", "assistant", "system"])
            
            is_reply_to_bot = False
            if message.reference and hasattr(message.reference, 'resolved'):
                if hasattr(message.reference.resolved, 'author') and message.reference.resolved.author == client.user:
                    is_reply_to_bot = True

            is_admin_user = (message.author.name == ADMIN_USERNAME)

            # Reply if mentioned, replied to, or if admin says something without targeting others
            should_reply = bot_mentioned or is_reply_to_bot or is_admin_user

            if not should_reply:
                # Add to background backlog context
                channel_backlogs[message.channel.id].append(f"[{message.author.name}]: {message.content}")
                return

            # Retrieve background conversation backlog context
            backlog = channel_backlogs[message.channel.id]
            context_str = ""
            if backlog:
                context_str = "[Background Conversation Context]\n" + "\n".join(backlog) + "\n\n"
                channel_backlogs[message.channel.id] = []  # Clear backlog

            prompt = f"{context_str}[{message.author.name}]: {message.content}"
            
            # Handle image attachments (Multimodal)
            if message.attachments:
                attachment = message.attachments[0]
                if attachment.content_type and attachment.content_type.startswith('image'):
                    await message.channel.send("✨ [System] Processing uploaded image...")
                    image_bytes = await attachment.read()
                    
                    response = chat.send_message([
                        prompt, 
                        {"mime_type": attachment.content_type, "data": image_bytes}
                    ])
                else:
                    response = chat.send_message(prompt)
            else:
                response = chat.send_message(prompt)
            
            # Split messages exceeding Discord's 2000-character limit
            reply_text = response.text
            for i in range(0, len(reply_text), 1950):
                await message.channel.send(reply_text[i:i+1950])

            # ==========================================
            # 💎 Auto Archive Trigger (History threshold check)
            # ==========================================
            # 1 user message + 1 assistant reply = 2 records. 80 records = 40 exchanges.
            if len(chat.history) >= 80:
                await perform_archive(message, chat, message.channel.id, is_auto=True)
                
        except Exception as e:
            error_msg = str(e)[:1900]
            await message.channel.send(f"An error occurred: \n{error_msg}")

if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
