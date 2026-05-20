# ==========================================
# 📦 Dependencies:
# pip install discord.py google-generativeai
# Compatible with Python 3.9+ and discord.py 2.0+
# ==========================================
import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
import os
import sys

# Windows console encoding configuration
sys.stdout.reconfigure(errors='replace')

# ==========================================
# 🗝️ Configuration & Authentication Credentials
# ==========================================
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN', 'YOUR_DISCORD_TOKEN') 
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY')
ADMIN_USER_ID = int(os.environ.get('ADMIN_USER_ID', '0')) # Fallback to 0 if not set

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

bot = DiscordBridgeBot()

# ==========================================
# 🛡️ Access Control Interceptor (Admin Check)
# ==========================================
def is_admin(interaction: discord.Interaction):
    # Only allow the configured administrator ID
    return ADMIN_USER_ID != 0 and interaction.user.id == ADMIN_USER_ID

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        embed = discord.Embed(
            title="⛔ Zone Defense: Access Denied", 
            description="Unauthorized access. This command can only be executed by the administrator.", 
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(f"🚨 Bridge Error: {str(error)}", ephemeral=True)

# Helper function to chunk large outputs
async def chunk_and_send(interaction, text: str, embed_color: int, title: str):
    # Discord Embed description limit is 4096 characters
    chunks = [text[i:i + 3900] for i in range(0, len(text), 3900)]
    
    for i, chunk in enumerate(chunks):
        embed = discord.Embed(title=f"{title} ({i+1}/{len(chunks)})", description=chunk, color=embed_color)
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
    print(f'✨ [Discord Bridge] Online')
    print(f'✨ Logged in as: {bot.user}')
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
    embed_color = 0x1E90FF # System Blue
    
    # Resolve relative paths against working directory
    target_path = file_path
    if not os.path.isabs(target_path):
        target_path = os.path.abspath(target_path)
        
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()
        await chunk_and_send(interaction, f"```markdown\n{content}\n```", embed_color, f"📁 File read success: {os.path.basename(target_path)}")
    except FileNotFoundError:
        await chunk_and_send(interaction, f"Error: File not found: `{target_path}`", embed_color, "❌ File Not Found")
    except Exception as e:
        await chunk_and_send(interaction, f"System error reading file:\n{e}", embed_color, "❌ System Error")

# ==========================================
# 🛠️ System Operations: /write
# ==========================================
@bot.tree.command(name="write", description="[Admin Only] Write/Overwrite contents of a local file")
@app_commands.check(is_admin)
async def write_file(interaction: discord.Interaction, file_path: str, content: str):
    await interaction.response.defer()
    embed_color = 0x1E90FF # System Blue
    
    target_path = file_path
    if not os.path.isabs(target_path):
        target_path = os.path.abspath(target_path)
        
    try:
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            # Reconstruct newline escape sequences
            clean_content = content.replace('\\n', '\n')
            f.write(clean_content)
            
        await chunk_and_send(interaction, f"File successfully written. Size: {len(clean_content)} characters.", embed_color, f"💾 File write success: {os.path.basename(target_path)}")
    except Exception as e:
         await chunk_and_send(interaction, f"Error writing file:\n{e}", embed_color, "❌ File Write Error")

# ==========================================
# 💬 System Operations: /chat
# ==========================================
@bot.tree.command(name="chat", description="[Admin Only] Interact with the system assistant with context memory")
@app_commands.check(is_admin)
async def chat(interaction: discord.Interaction, message: str):
    await interaction.response.defer()
    embed_color = 0xFF7F50 # Agent Orange
    
    try:
        response = await bot.chat_session.send_message_async(message)
        await chunk_and_send(interaction, response.text, embed_color, "💬 Assistant Response")
    except Exception as e:
        await chunk_and_send(interaction, f"API communication error:\n```\n{e}\n```", embed_color, "❌ Connection Error")

if __name__ == "__main__":
    if DISCORD_TOKEN == 'YOUR_DISCORD_TOKEN':
        print("Error: Please set your DISCORD_TOKEN environment variable.")
    else:
        bot.run(DISCORD_TOKEN)
