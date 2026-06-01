# ==========================================
# 📦 Dependencies:
# pip install discord.py google-generativeai python-dotenv
# Optional: pip install charset-normalizer (for advanced encoding detection)
# Compatible with Python 3.9+ and discord.py 2.0+
# ==========================================
# [P2-12] Graceful ImportError handling
try:
    import discord
except ImportError:
    print("[ERROR] Missing dependency: discord.py")
    print("[FIX]   Run: pip install discord.py")
    import sys
    sys.exit(1)

try:
    import google.generativeai as genai
except ImportError:
    print("[ERROR] Missing dependency: google-generativeai")
    print("[FIX]   Run: pip install google-generativeai")
    import sys
    sys.exit(1)

import os
import sys
import asyncio
import datetime

__version__ = "4.0.0"

# Windows console encoding configuration
sys.stdout.reconfigure(errors='replace')

# ==========================================
# 🗝️ Configuration & Authentication Credentials
# ==========================================
# [P2-12] dotenv with graceful fallback
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    print("[WARNING] python-dotenv not installed. Using system environment variables only.")
    print("[FIX]    Run: pip install python-dotenv")

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN', '')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# [P1-7] Admin authentication via immutable User ID (not spoofable username)
ADMIN_USER_ID = int(os.environ.get('ADMIN_USER_ID', '0'))

# [P2-15] Safe parsing for ALLOWED_CHANNEL_ID
try:
    ALLOWED_CHANNEL_ID = int(os.environ.get('ALLOWED_CHANNEL_ID', '0'))
except (ValueError, TypeError):
    print("[WARNING] ALLOWED_CHANNEL_ID is not a valid integer. Defaulting to 0 (all channels).")
    ALLOWED_CHANNEL_ID = 0

# [P1-9] Rate Limit protection: max number of message chunks per response
MAX_CHUNKS = 5

# [P1-10] Backlog memory leak prevention
MAX_BACKLOG = 15

# [MAMA-FIX] Image size limit to prevent OOM Image Bomb (5MB)
MAX_IMAGE_BYTES = 5 * 1024 * 1024

# Auto archive threshold (number of history entries)
AUTO_ARCHIVE_THRESHOLD = 80  # 1 user + 1 assistant = 2; 80 = 40 exchanges


# ==========================================
# 🛡️ Security & Encoding Utilities
# ==========================================
def _safe_read_file(file_path: str) -> str:
    """
    [P2-13] Multi-encoding file reader with 3-tier fallback.
    1. UTF-8
    2. charset_normalizer auto-detection
    3. chardet auto-detection
    4. UTF-8 with errors='replace' (last resort)
    """
    # Tier 1: UTF-8
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        pass

    # Tier 2: charset_normalizer
    try:
        import charset_normalizer
        raw = open(file_path, "rb").read()
        result = charset_normalizer.from_bytes(raw).best()
        if result:
            return str(result)
    except ImportError:
        pass
    except Exception:
        pass

    # Tier 3: chardet
    try:
        import chardet
        raw = open(file_path, "rb").read()
        detected = chardet.detect(raw)
        if detected and detected.get("encoding"):
            return raw.decode(detected["encoding"], errors="replace")
    except ImportError:
        pass
    except Exception:
        pass

    # Tier 4: Last resort
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _audit_log(user, action: str, detail: str = ""):
    """Print a structured audit trail to the terminal."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_str = f"{user.name}#{user.id}" if hasattr(user, 'id') else str(user)
    print(f"[AUDIT] {timestamp} | User: {user_str} | Action: {action} | {detail}")


# ==========================================
# 🧠 AI Engine Initialization
# ==========================================
genai.configure(api_key=GEMINI_API_KEY)

# [P2-13] Use _safe_read_file for system instruction to avoid startup encoding crash
base_dir = os.path.dirname(os.path.abspath(__file__))
instruction_path = os.path.join(base_dir, "system_instruction.txt")

if os.path.exists(instruction_path):
    try:
        system_instruction = _safe_read_file(instruction_path)
    except Exception as e:
        print(f"[WARNING] Failed to load system_instruction.txt: {e}")
        system_instruction = (
            "You are a helpful and polite Discord chatbot agent. "
            "Maintain a friendly tone and assist users. "
            "Keep your responses concise and within 700 characters."
        )
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
# [P1-8] Per-channel async locks to prevent concurrent state corruption
channel_locks = {}


def _get_channel_lock(channel_id: int) -> asyncio.Lock:
    """Get or create an asyncio.Lock for a specific channel."""
    if channel_id not in channel_locks:
        channel_locks[channel_id] = asyncio.Lock()
    return channel_locks[channel_id]


# ==========================================
# 💎 Memory Consolidation & Archiving System
# ==========================================
async def perform_archive(message, chat, channel_id, is_auto=False):
    trigger_type = "【Auto Archive】" if is_auto else "【Manual Archive】"
    await message.channel.send(f"✨ [System] Triggered {trigger_type}. Consolidating memory buffer, please wait...")
    _audit_log(message.author, "ARCHIVE", f"Type: {trigger_type}, Channel: {channel_id}")

    # 1. Summarize the conversation history
    summary_prompt = (
        "Summarize the conversation history from this session into a structured markdown log. "
        "Include the key topics discussed, performance/response summary, and action items."
    )
    try:
        # [P0-1] Non-blocking async API call
        summary_response = await chat.send_message_async(summary_prompt)
        summary_text = summary_response.text
    except Exception as e:
        summary_text = f"Failed to generate summary: {e}"

    # 2. Archive to disk (dual track: summary file and raw transcript)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = os.path.join(base_dir, "Memory_Archives")
    raw_dir = os.path.join(base_dir, "Raw_Transcripts")

    # [P2-14] Non-blocking directory creation and file writes
    def _sync_archive():
        os.makedirs(archive_dir, exist_ok=True)
        os.makedirs(raw_dir, exist_ok=True)

        # [MAMA-FIX] Include channel_id in filename to prevent multi-channel collision
        summary_file = os.path.join(archive_dir, f"Summary_{channel_id}_{timestamp}.md")
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary_text)

        # [MAMA-FIX] Include channel_id in filename to prevent multi-channel collision
        raw_file = os.path.join(raw_dir, f"Raw_Transcript_{channel_id}_{timestamp}.md")
        raw_transcript = f"# Raw Chat Transcript\n*   **Archived At:** {timestamp}\n\n---\n\n"
        for msg in chat.history:
            speaker = "User" if msg.role == 'user' else "Assistant"
            text = "".join([getattr(part, 'text', '') for part in msg.parts])
            if not text.strip():
                text = "(Attachment/Multimodal data)"
            raw_transcript += f"**[{speaker}]**\n{text}\n\n---\n"

        with open(raw_file, "w", encoding="utf-8") as f:
            f.write(raw_transcript)

        return os.path.basename(summary_file), os.path.basename(raw_file)

    summary_name, raw_name = await asyncio.to_thread(_sync_archive)

    # [P1-11] Only show filenames, not full paths (prevents directory structure leakage)
    await message.channel.send(
        f"✅ Memory successfully archived!\n"
        f"📂 **Summary:** `{summary_name}`\n"
        f"📜 **Transcript:** `{raw_name}`\n"
        f"Session memory has been reset."
    )

    # 3. Reset the chat session and seed with the summary for continuity
    new_chat = model.start_chat(history=[])
    seed_prompt = (
        f"[SYSTEM] The conversation memory has been cleared and archived. "
        f"Here is a summary of the previous session for context: \n\n{summary_text}\n\n"
        f"Please acknowledge by saying: 'Context synchronized.'"
    )
    # [P0-5] Seed wrapped in try/except to prevent archive death loop.
    # Even if seed fails, session MUST be reset to break the >=80 threshold cycle.
    try:
        # [P0-2] Non-blocking async API call
        await new_chat.send_message_async(seed_prompt)
    except Exception as e:
        print(f"[WARNING] Context seed injection failed: {e}")
        print("[WARNING] Session reset without context continuity.")

    # Always reset, regardless of seed success
    chat_sessions[channel_id] = new_chat


@client.event
async def on_ready():
    print('====================================')
    print(f'✨ [Discord Chatbot V{__version__}] Online')
    print(f'✨ Logged in as: {client.user}')
    if ALLOWED_CHANNEL_ID != 0:
        print(f'✨ Restricted to channel: {ALLOWED_CHANNEL_ID}')
    else:
        print(f'✨ Listening on all channels')
    print('====================================')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Restrict to allowed channel if configured
    if ALLOWED_CHANNEL_ID != 0 and message.channel.id != ALLOWED_CHANNEL_ID:
        return

    # [P0-6] Support pure-image messages (multimodal illusion fix)
    if message.content or message.attachments:
        try:
            channel_id = message.channel.id

            # Initialize chat session if first message in this channel
            if channel_id not in chat_sessions:
                chat_sessions[channel_id] = model.start_chat(history=[])

            chat = chat_sessions[channel_id]

            # [P1-7] Admin check via immutable User ID (must be BEFORE !archive)
            is_admin_user = (ADMIN_USER_ID != 0 and message.author.id == ADMIN_USER_ID)

            # ==========================================
            # 💎 Manual Archive Command (Admin Only)
            # ==========================================
            # [MAMA-FIX-1] Archive requires admin. Without this gate,
            # any user can spam !archive to burn Gemini API quota
            # (Denial of Wallet attack) and flood the disk with files.
            if message.content and message.content.startswith("!archive"):
                if not is_admin_user:
                    await message.channel.send("❌ [Access Denied] Archive is restricted to the administrator.")
                    _audit_log(message.author, "ARCHIVE_DENIED", f"Channel: {channel_id}")
                    return
                async with _get_channel_lock(channel_id):
                    await perform_archive(message, chat, channel_id, is_auto=False)
                return

            # ==========================================
            # 💬 Conversation Flow Handler (Smart Backlog Listening)
            # ==========================================
            if channel_id not in channel_backlogs:
                channel_backlogs[channel_id] = []

            # Check if chatbot is being addressed
            msg_lower = (message.content or "").lower()
            bot_mentioned = client.user in message.mentions or any(
                name in msg_lower for name in ["bot", "assistant", "system"]
            )

            is_reply_to_bot = False
            if message.reference and hasattr(message.reference, 'resolved'):
                if hasattr(message.reference.resolved, 'author') and message.reference.resolved.author == client.user:
                    is_reply_to_bot = True

            # [MAMA-FIX-2] Removed is_admin_user and has_attachments from should_reply.
            # Reason: Admin's casual chat would trigger AI on every message (token burn).
            # Reason: Any user posting memes/photos would trigger expensive multimodal API.
            # To use multimodal, users MUST @mention the bot or include a trigger keyword.
            should_reply = bot_mentioned or is_reply_to_bot

            if not should_reply:
                # Add to background backlog context
                channel_backlogs[channel_id].append(f"[{message.author.name}]: {message.content}")
                # [P1-10] Enforce backlog size limit to prevent memory leak
                if len(channel_backlogs[channel_id]) > MAX_BACKLOG:
                    channel_backlogs[channel_id] = channel_backlogs[channel_id][-MAX_BACKLOG:]
                return

            # [P1-8] Acquire per-channel lock to prevent concurrent state corruption
            async with _get_channel_lock(channel_id):
                # Retrieve background conversation backlog context
                backlog = channel_backlogs[channel_id]
                context_str = ""
                if backlog:
                    context_str = "[Background Conversation Context]\n" + "\n".join(backlog) + "\n\n"
                    channel_backlogs[channel_id] = []  # Clear backlog

                prompt = f"{context_str}[{message.author.name}]: {message.content or '(Image attached)'}"

                # Handle image attachments (Multimodal)
                if message.attachments:
                    attachment = message.attachments[0]
                    if attachment.content_type and attachment.content_type.startswith('image'):
                        # [MAMA-FIX] OOM Image Bomb protection: reject files > 5MB
                        if attachment.size and attachment.size > MAX_IMAGE_BYTES:
                            size_mb = attachment.size / (1024 * 1024)
                            await message.channel.send(
                                f"⚠️ Image too large ({size_mb:.1f}MB). "
                                f"Maximum allowed: {MAX_IMAGE_BYTES // (1024*1024)}MB."
                            )
                            _audit_log(message.author, "IMAGE_REJECTED", f"Size: {size_mb:.1f}MB")
                            return
                        await message.channel.send("✨ [System] Processing uploaded image...")
                        image_bytes = await attachment.read()

                        # [P0-3] Non-blocking async API call
                        response = await chat.send_message_async([
                            prompt,
                            {"mime_type": attachment.content_type, "data": image_bytes}
                        ])
                    else:
                        # [P0-4] Non-blocking async API call
                        response = await chat.send_message_async(prompt)
                else:
                    # [P0-4] Non-blocking async API call
                    response = await chat.send_message_async(prompt)

                # [P1-9] Split messages with MAX_CHUNKS rate limit guard
                reply_text = response.text
                chunks = [reply_text[i:i + 1950] for i in range(0, len(reply_text), 1950)]
                total_chunks = len(chunks)

                if total_chunks > MAX_CHUNKS:
                    chunks = chunks[:MAX_CHUNKS]
                    chunks.append(
                        "⚠️ **Output truncated**: Response exceeded safe page limit. "
                        f"Original was {total_chunks} pages, showing first {MAX_CHUNKS}."
                    )

                for chunk in chunks:
                    await message.channel.send(chunk)

                # ==========================================
                # 💎 Auto Archive Trigger (History threshold check)
                # ==========================================
                if len(chat.history) >= AUTO_ARCHIVE_THRESHOLD:
                    await perform_archive(message, chat, channel_id, is_auto=True)

        except Exception as e:
            # [MAMA-FIX-3] Never expose raw exception to Discord!
            # str(e) may contain API keys in request URLs, server paths,
            # or internal architecture details. Log to terminal only.
            _audit_log(message.author, "ERROR", f"Channel: {channel_id} | {type(e).__name__}: {e}")
            await message.channel.send(
                "❌ An unexpected error occurred. Please contact the administrator to check the server logs."
            )


if __name__ == "__main__":
    # Startup validation
    if not DISCORD_TOKEN:
        print("[ERROR] DISCORD_TOKEN is not set.")
        print("[FIX]   Set the DISCORD_TOKEN environment variable or add it to .env file.")
        sys.exit(1)

    if not GEMINI_API_KEY:
        print("[ERROR] GEMINI_API_KEY is not set.")
        print("[FIX]   Set the GEMINI_API_KEY environment variable or add it to .env file.")
        sys.exit(1)

    if ADMIN_USER_ID == 0:
        print("[WARNING] =========================================")
        print("[WARNING] ADMIN_USER_ID is not set (defaulting to 0).")
        print("[WARNING] Admin-only features will be disabled.")
        print("[WARNING] Set ADMIN_USER_ID to your Discord User ID.")
        print("[WARNING] =========================================")

    print(f"[INFO] Discord Chatbot V{__version__} starting...")
    print(f"[INFO] Max Backlog: {MAX_BACKLOG} | Max Chunks: {MAX_CHUNKS} | Archive Threshold: {AUTO_ARCHIVE_THRESHOLD}")
    client.run(DISCORD_TOKEN)
