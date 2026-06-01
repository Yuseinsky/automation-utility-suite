# ==========================================
# 📦 Dependencies:
# pip install discord.py google-generativeai
# Optional: pip install charset-normalizer (for advanced encoding detection)
# Compatible with Python 3.9+ and discord.py 2.0+
# ==========================================
# [P1-2] Graceful ImportError handling
try:
    import discord
    from discord.ext import commands
    from discord import app_commands
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
import re

__version__ = "4.0.0"

# Windows console encoding configuration
sys.stdout.reconfigure(errors='replace')

# ==========================================
# 🗝️ Configuration & Authentication Credentials
# ==========================================
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN', 'YOUR_DISCORD_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY')
ADMIN_USER_ID = int(os.environ.get('ADMIN_USER_ID', '0'))  # Fallback to 0 if not set

# [P0-1] Path Jail: restrict all file operations within this directory
SAFE_WORKSPACE = os.environ.get(
    'BRIDGE_WORKSPACE',
    os.path.dirname(os.path.abspath(__file__))
)

# [P0-8] Rate Limit protection: max number of chunks per response
MAX_CHUNKS = 5  # ~20KB of text output per command

# [P1-1] Chat session history warning threshold (number of messages)
HISTORY_WARN_THRESHOLD = 60  # ~30 round-trip exchanges


# ==========================================
# 🛡️ Security Utilities
# ==========================================
def _is_path_safe(target_path: str) -> bool:
    """
    [P0-1] Validate that a resolved absolute path stays within SAFE_WORKSPACE.
    Prevents Path Traversal attacks (e.g. ../../Windows/System32/config/SAM).
    """
    try:
        resolved = os.path.realpath(target_path)
        workspace = os.path.realpath(SAFE_WORKSPACE)
        return os.path.commonpath([resolved, workspace]) == workspace
    except (ValueError, OSError):
        return False


def _safe_read_file(file_path: str) -> str:
    """
    [P0-4][P0-9] Multi-encoding file reader with 3-tier fallback.
    Shared by /read command and system_instruction startup loader.
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


def _sanitize_markdown(text: str) -> str:
    """
    [P0-3] Output Sanitization: prevent Markdown escape hatch injection.
    Inserts zero-width spaces into triple backticks to prevent
    premature code block closure in Discord embeds.
    """
    return text.replace("```", "`\u200b`\u200b`")


def _audit_log(user, action: str, path: str = "", detail: str = ""):
    """
    [P1-4] Print a structured audit trail to the terminal.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[AUDIT] {timestamp} | User: {user} | Action: {action} | Path: {path} | {detail}")


# ==========================================
# 🧠 AI Engine Initialization
# ==========================================
genai.configure(api_key=GEMINI_API_KEY)

# [P0-9] Use _safe_read_file for system instruction to avoid startup encoding crash
base_dir = os.path.dirname(os.path.abspath(__file__))
instruction_path = os.path.join(base_dir, "system_instruction.txt")

if os.path.exists(instruction_path):
    try:
        system_instruction = _safe_read_file(instruction_path)
    except Exception as e:
        print(f"[WARNING] Failed to load system_instruction.txt: {e}")
        print("[WARNING] Using default system instruction.")
        system_instruction = (
            "You are a professional system operations assistant. You are communicating "
            "with the system administrator via Discord to perform operations on the local machine. "
            "Respond clearly and concisely."
        )
else:
    system_instruction = (
        "You are a professional system operations assistant. You are communicating "
        "with the system administrator via Discord to perform operations on the local machine. "
        "Respond clearly and concisely."
    )

model = genai.GenerativeModel('gemini-2.5-pro', system_instruction=system_instruction)


class DiscordBridgeBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        # Shared conversation session for contextual memory
        self.chat_session = model.start_chat(history=[])
        # [Nano] Async lock to prevent concurrent chat state corruption
        self.chat_lock = asyncio.Lock()

bot = DiscordBridgeBot()


# ==========================================
# 🛡️ Access Control Interceptor (Admin Check)
# ==========================================
def is_admin(interaction: discord.Interaction):
    """Only allow the configured administrator ID."""
    return ADMIN_USER_ID != 0 and interaction.user.id == ADMIN_USER_ID


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """
    [P0-7] Fixed: checks interaction.response.is_done() before responding,
    preventing InteractionResponded crash when commands have already been deferred.
    """
    if isinstance(error, app_commands.CheckFailure):
        embed = discord.Embed(
            title="⛔ Zone Defense: Access Denied",
            description="Unauthorized access. This command can only be executed by the administrator.",
            color=0xff0000
        )
    else:
        # [MAMA-FIX] Never expose raw exception to Discord.
        # Log details to terminal for admin debugging.
        print(f"[ERROR] Unhandled command error: {type(error).__name__}: {error}")
        embed = discord.Embed(
            title="🚨 Bridge Error",
            description="An unexpected error occurred. Please check the server terminal logs for details.",
            color=0xff0000
        )

    if interaction.response.is_done():
        await interaction.followup.send(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ==========================================
# 📤 Output Utilities
# ==========================================
async def chunk_and_send(interaction, text: str, embed_color: int, title: str, code_wrap: bool = False):
    """
    [P0-8] Enhanced: enforces MAX_CHUNKS limit to prevent Rate Limit death queue.
    [Nano-Markdown] When code_wrap=True, each chunk is independently wrapped in
    a code block to prevent Markdown fracture across pages.
    Discord Embed description limit is 4096 characters.
    """
    # [Nano] Prevent silent freeze if text is empty (e.g., reading a 0-byte file)
    if not text:
        text = "[Empty Content / 0 Bytes]"

    # Use smaller chunk size when code_wrap is enabled to account for wrapper overhead
    chunk_size = 3800 if code_wrap else 3900
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    total_chunks = len(chunks)

    # Enforce hard limit
    if total_chunks > MAX_CHUNKS:
        chunks = chunks[:MAX_CHUNKS]
        chunks.append(
            f"\n\n⚠️ **Output truncated**: Original output was {total_chunks} pages. "
            f"Only the first {MAX_CHUNKS} pages are shown. "
            f"Please access the file directly on the host machine for the full content."
        )

    display_total = len(chunks)
    for i, chunk in enumerate(chunks):
        # [Nano-Markdown] Wrap each chunk independently in a code block
        display_chunk = f"```\n{chunk}\n```" if code_wrap else chunk

        # [Nano] Discord Embed title limit: 256 chars. Truncate to prevent 400 Bad Request.
        raw_title = f"{title} ({i+1}/{display_total})"
        safe_title = raw_title[:256]
        embed = discord.Embed(
            title=safe_title,
            description=display_chunk,
            color=embed_color
        )
        if i == 0:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed)
            else:
                await interaction.response.send_message(embed=embed)
        else:
            await interaction.followup.send(embed=embed)


@bot.event
async def on_ready():
    print('====================================')
    print(f'✨ [Discord Bridge V{__version__}] Online')
    print(f'✨ Logged in as: {bot.user}')
    print(f'✨ Safe Workspace: {SAFE_WORKSPACE}')
    try:
        synced = await bot.tree.sync()
        print(f"✨ Successfully synced {len(synced)} slash commands. Waiting for requests...")
    except Exception as e:
        print(f"❌ Failed to sync slash commands: {e}")
    print('====================================')


# ==========================================
# 🛠️ System Operations: /read
# ==========================================
@bot.tree.command(name="read", description="[Admin Only] Read contents of a local file")
@app_commands.check(is_admin)
async def read_file(interaction: discord.Interaction, file_path: str):
    await interaction.response.defer()
    embed_color = 0x1E90FF  # System Blue

    # Resolve path
    target_path = file_path
    if not os.path.isabs(target_path):
        target_path = os.path.join(SAFE_WORKSPACE, target_path)
    target_path = os.path.realpath(target_path)

    # [P0-1] Path Jail check
    if not _is_path_safe(target_path):
        _audit_log(interaction.user, "READ_BLOCKED", target_path, "Path Traversal attempt")
        await chunk_and_send(
            interaction,
            f"⛔ **Security Error: Path Traversal blocked.**\n"
            f"The requested path escapes the safe workspace.\n"
            f"Allowed workspace: `{SAFE_WORKSPACE}`",
            0xff0000, "🚨 Security Alert"
        )
        return

    _audit_log(interaction.user, "READ", target_path)

    try:
        # [P0-2] Non-blocking I/O via asyncio.to_thread
        # [P0-4] Multi-encoding fallback via _safe_read_file
        content = await asyncio.to_thread(_safe_read_file, target_path)

        # [P0-3] Sanitize markdown backticks
        sanitized = _sanitize_markdown(content)

        # [Nano-Markdown] Pass raw text + code_wrap=True so each page gets its own code block
        await chunk_and_send(
            interaction,
            sanitized,
            embed_color,
            f"📁 File read success: {os.path.basename(target_path)[:200]}",
            code_wrap=True
        )
    except FileNotFoundError:
        await chunk_and_send(
            interaction,
            f"Error: File not found: `{target_path}`",
            embed_color, "❌ File Not Found"
        )
    except Exception as e:
        # [MAMA-FIX] Log raw error to terminal, send sanitized message to Discord
        _audit_log(interaction.user, "READ_ERROR", target_path, f"{type(e).__name__}: {e}")
        await chunk_and_send(
            interaction,
            "A system error occurred while reading the file. Check server logs for details.",
            embed_color, "❌ System Error"
        )


# ==========================================
# 🛠️ System Operations: /write
# ==========================================
@bot.tree.command(name="write", description="[Admin Only] Write/Overwrite contents of a local file")
@app_commands.check(is_admin)
async def write_file(interaction: discord.Interaction, file_path: str, content: str):
    await interaction.response.defer()
    embed_color = 0x1E90FF  # System Blue

    # [P1-3] Empty content protection
    if not content or not content.strip():
        await chunk_and_send(
            interaction,
            "⚠️ **Write aborted**: Content is empty. "
            "To prevent accidental file erasure, please provide at least some content.",
            0xFFA500, "⚠️ Empty Content Warning"
        )
        return

    # Resolve path
    target_path = file_path
    if not os.path.isabs(target_path):
        target_path = os.path.join(SAFE_WORKSPACE, target_path)
    target_path = os.path.realpath(target_path)

    # [P0-1] Path Jail check
    if not _is_path_safe(target_path):
        _audit_log(interaction.user, "WRITE_BLOCKED", target_path, "Path Traversal attempt")
        await chunk_and_send(
            interaction,
            f"⛔ **Security Error: Path Traversal blocked.**\n"
            f"The requested path escapes the safe workspace.\n"
            f"Allowed workspace: `{SAFE_WORKSPACE}`",
            0xff0000, "🚨 Security Alert"
        )
        return

    _audit_log(interaction.user, "WRITE", target_path, f"Content length: {len(content)}")

    try:
        # Reconstruct newline escape sequences
        clean_content = content.replace('\\n', '\n')

        # [P0-2] Non-blocking I/O
        def _sync_write():
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(clean_content)

        await asyncio.to_thread(_sync_write)

        await chunk_and_send(
            interaction,
            f"File successfully written. Size: {len(clean_content)} characters.",
            embed_color,
            f"💾 File write success: {os.path.basename(target_path)[:200]}"
        )
    except Exception as e:
        # [MAMA-FIX] Log raw error to terminal, send sanitized message to Discord
        _audit_log(interaction.user, "WRITE_ERROR", target_path, f"{type(e).__name__}: {e}")
        await chunk_and_send(
            interaction,
            "A system error occurred while writing the file. Check server logs for details.",
            embed_color, "❌ File Write Error"
        )


# ==========================================
# 💬 System Operations: /chat
# ==========================================
@bot.tree.command(name="chat", description="[Admin Only] Interact with the system assistant with context memory")
@app_commands.check(is_admin)
async def chat(interaction: discord.Interaction, message: str):
    await interaction.response.defer()
    embed_color = 0xFF7F50  # Agent Orange

    _audit_log(interaction.user, "CHAT", detail=f"Message length: {len(message)}")

    try:
        # [P1-1] Check history length before sending
        history_len = len(bot.chat_session.history)
        if history_len >= HISTORY_WARN_THRESHOLD:
            warn_embed = discord.Embed(
                title="⚠️ Session Memory Warning",
                description=(
                    f"Chat history has reached **{history_len} messages** "
                    f"(threshold: {HISTORY_WARN_THRESHOLD}).\n"
                    f"This may cause increased API costs and potential token limit errors.\n"
                    f"Use `/clear` to reset the session."
                ),
                color=0xFFA500
            )
            await interaction.followup.send(embed=warn_embed)

        # [Nano] Serialize chat access to prevent Gemini history corruption
        async with bot.chat_lock:
            response = await bot.chat_session.send_message_async(message)
            
        await chunk_and_send(interaction, response.text, embed_color, "💬 Assistant Response")
    except Exception as e:
        # [MAMA-FIX] Log raw error to terminal, send sanitized hint to Discord
        error_text = str(e)
        _audit_log(interaction.user, "CHAT_ERROR", detail=f"{type(e).__name__}: {error_text[:500]}")

        # Provide helpful hints WITHOUT exposing raw exception text
        if "400" in error_text or "invalid" in error_text.lower():
            hint = "This may be caused by a token limit exceeded. Try `/clear` to reset the session."
        elif "429" in error_text or "quota" in error_text.lower():
            hint = "API quota exceeded. Please wait or check your billing settings."
        elif "403" in error_text:
            hint = "API access denied. Please verify your configuration."
        else:
            hint = "An unexpected error occurred. Check the server terminal logs for details."
        await chunk_and_send(
            interaction,
            f"❌ {hint}",
            embed_color, "❌ Connection Error"
        )


# ==========================================
# 🔄 Session Management: /clear
# ==========================================
@bot.tree.command(name="clear", description="[Admin Only] Reset the AI chat session memory")
@app_commands.check(is_admin)
async def clear_session(interaction: discord.Interaction):
    """[P1-1] Allows admin to manually reset the chat session to prevent token explosion."""
    async with bot.chat_lock:
        old_length = len(bot.chat_session.history)
        bot.chat_session = model.start_chat(history=[])

    _audit_log(interaction.user, "CLEAR_SESSION", detail=f"Cleared {old_length} messages")

    embed = discord.Embed(
        title="🔄 Session Reset Complete",
        description=(
            f"Chat memory has been cleared.\n"
            f"**Messages cleared**: {old_length}\n"
            f"A fresh session has been started."
        ),
        color=0x00FF7F
    )
    await interaction.response.send_message(embed=embed)


# ==========================================
# 🚀 Entry Point
# ==========================================
if __name__ == "__main__":
    # [P0-5] Validate DISCORD_TOKEN
    if DISCORD_TOKEN == 'YOUR_DISCORD_TOKEN' or not DISCORD_TOKEN:
        print("[ERROR] DISCORD_TOKEN is not set.")
        print("[FIX]   Set the DISCORD_TOKEN environment variable.")
        sys.exit(1)

    # [P0-5] Validate GEMINI_API_KEY
    if GEMINI_API_KEY == 'YOUR_GEMINI_API_KEY' or not GEMINI_API_KEY:
        print("[ERROR] GEMINI_API_KEY is not set.")
        print("[FIX]   Set the GEMINI_API_KEY environment variable.")
        sys.exit(1)

    # [P0-6] Warn about ADMIN_USER_ID
    if ADMIN_USER_ID == 0:
        print("[WARNING] =========================================")
        print("[WARNING] ADMIN_USER_ID is not set (defaulting to 0).")
        print("[WARNING] ALL commands will be rejected with 'Access Denied'.")
        print("[WARNING] Set the ADMIN_USER_ID environment variable to your Discord User ID.")
        print("[WARNING] =========================================")

    print(f"[INFO] Discord Bridge V{__version__} starting...")
    print(f"[INFO] Safe Workspace: {SAFE_WORKSPACE}")
    bot.run(DISCORD_TOKEN)
