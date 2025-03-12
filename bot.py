import os
import discord
import requests
import base64
from discord.ext import commands
from datetime import datetime

# Environment Variables
TOKEN = os.getenv("MTM0OTI2MTY4MTU2NTYzNDU4Mg.GPu0iz.KH_-gO7Bwj-zw0cUrrjmeg3uIkZ2Jfzc4s7U7I")
GITHUB_TOKEN = os.getenv("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")
REPO_OWNER = os.getenv("projectscriptrbx")  # GitHub username
REPO_NAME = os.getenv("DataManager")  # Repository name
BRANCH = "main"
WEBHOOK_URL = os.getenv("https://discord.com/api/webhooks/1347917180389560361/_z0wm98GkLB0vjN2YH-dLr7TY8a7LMjXpo9XAnex9JntI4vHBT8Xji9TxiROktakiaO4")  # Webhook URL
BOT_OWNER_ID = int(os.getenv("779623222211248138"))  # Bot owner's Discord ID

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# GitHub API headers
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# File mapping for whitelist management
WHITELIST_FILES = {
    "admin": "AdminUsers.lua",
    "premium": "PremiumUsers.lua",
    "blacklist": "BlacklistUsers.lua"
}

# Function to get file content from GitHub
def get_file_content(filename):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{filename}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        content = base64.b64decode(response.json()["content"]).decode("utf-8")
        return content, response.json()["sha"]
    return None, None

# Function to update file content on GitHub
def update_file(filename, new_content, message, sha):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{filename}"
    data = {
        "message": message,
        "content": base64.b64encode(new_content.encode("utf-8")).decode("utf-8"),
        "sha": sha,
        "branch": BRANCH
    }
    
    response = requests.put(url, json=data, headers=HEADERS)
    return response.status_code == 200

# Function to send webhook notifications
def send_webhook(display_name, username, action):
    avatar_url = f"https://www.roblox.com/headshot-thumbnail/image?userId={username}&width=420&height=420&format=png"
    payload = {
        "username": "🪽ProjectS Data",
        "embeds": [{
            "title": "📢 Data Update",
            "description": "Admin updated ProjectS Data.",
            "color": 16766720,
            "fields": [
                {"name": "📛 Display Name", "value": display_name, "inline": True},
                {"name": "👤 Username", "value": "@" + username, "inline": True},
                {"name": "🖥️ Action", "value": action, "inline": False},
                {"name": "🗓️ Date", "value": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"), "inline": False}
            ],
            "thumbnail": {"url": avatar_url},
            "footer": {"text": "Data System | ProjectS HUB"}
        }]
    }

    requests.post(WEBHOOK_URL, json=payload)

# Function to check if user is an admin
def is_admin(user_id):
    content, _ = get_file_content("AdminUsers.lua")
    if content:
        admin_list = [line.strip().strip('"').strip(',') for line in content.strip().split("\n")[1:-1]]
        return str(user_id) in admin_list
    return False

# Command to add user (Admins only)
@bot.command()
async def add(ctx, list_name: str, username: str):
    if not is_admin(ctx.author.id):
        await ctx.send("❌ You don't have permission to use this command!")
        return

    if list_name not in WHITELIST_FILES:
        await ctx.send("❌ Invalid list! Use `admin`, `premium`, or `blacklist`.")
        return
    
    filename = WHITELIST_FILES[list_name]
    content, sha = get_file_content(filename)

    if content is None:
        await ctx.send("❌ Could not fetch file data.")
        return

    # Extract existing usernames
    lines = content.strip().split("\n")[1:-1]
    existing_users = [line.strip().strip('"').strip(',') for line in lines]

    if username in existing_users:
        await ctx.send(f"⚠️ User `{username}` is already in `{list_name}`!")
        return

    existing_users.append(username)
    new_content = 'return {\n  "' + '",\n  "'.join(existing_users) + '"\n}'

    if update_file(filename, new_content, f"Added {username} to {list_name}", sha):
        send_webhook(username, username, f"Added to {list_name}")
        await ctx.send(f"✅ Added `{username}` to `{list_name}`!")
    else:
        await ctx.send("❌ Error updating file!")

# Command to remove user (Admins only)
@bot.command()
async def remove(ctx, list_name: str, username: str):
    if not is_admin(ctx.author.id):
        await ctx.send("❌ You don't have permission to use this command!")
        return

    if list_name not in WHITELIST_FILES:
        await ctx.send("❌ Invalid list! Use `admin`, `premium`, or `blacklist`.")
        return

    filename = WHITELIST_FILES[list_name]
    content, sha = get_file_content(filename)

    if content is None:
        await ctx.send("❌ Could not fetch file data.")
        return

    lines = content.strip().split("\n")[1:-1]
    existing_users = [line.strip().strip('"').strip(',') for line in lines]

    if username not in existing_users:
        await ctx.send(f"⚠️ User `{username}` is not in `{list_name}`!")
        return

    existing_users.remove(username)
    new_content = 'return {\n  "' + '",\n  "'.join(existing_users) + '"\n}'

    if update_file(filename, new_content, f"Removed {username} from {list_name}", sha):
        send_webhook(username, username, f"Removed from {list_name}")
        await ctx.send(f"✅ Removed `{username}` from `{list_name}`!")
    else:
        await ctx.send("❌ Error updating file!")

# Command to add admin (Only bot owner can use)
@bot.command()
async def addaccess(ctx, discord_id: str):
    if ctx.author.id != BOT_OWNER_ID:
        await ctx.send("❌ Only the bot owner can use this command!")
        return

    filename = "AdminUsers.lua"
    content, sha = get_file_content(filename)

    if content is None:
        await ctx.send("❌ Could not fetch file data.")
        return

    lines = content.strip().split("\n")[1:-1]
    existing_admins = [line.strip().strip('"').strip(',') for line in lines]

    if discord_id in existing_admins:
        await ctx.send(f"⚠️ User `{discord_id}` is already an admin!")
        return

    existing_admins.append(discord_id)
    new_content = 'return {\n  "' + '",\n  "'.join(existing_admins) + '"\n}'

    if update_file(filename, new_content, f"Added {discord_id} as an admin", sha):
        await ctx.send(f"✅ Added `{discord_id}` as an admin!")
    else:
        await ctx.send("❌ Error updating file!")

# Run the bot
bot.run(TOKEN)