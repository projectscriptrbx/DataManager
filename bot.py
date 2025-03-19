import discord
import requests
import os

# Load environment variables (Secure way)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "projectscriptrbx/ProjectSData"  # Change this to your GitHub repo
PREMIUM_FILE = "PremiumUsers.lua"
BLACKLIST_FILE = "BlacklistUsers.lua"
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Discord Bot Setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

# Function to get user list from GitHub
def get_users(file_name):
    url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{file_name}"
    response = requests.get(url)
    if response.status_code == 200:
        text = response.text.strip().replace("return {", "").replace("}", "").strip()
        users = [user.strip().strip('"') for user in text.split(",") if user.strip()]
        return users
    return []

# Function to update user list on GitHub
def update_users(file_name, user_list):
    new_content = 'return {\n  ' + ',\n  '.join(f'"{user}"' for user in user_list) + '\n}'

    get_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_name}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    response = requests.get(get_url, headers=headers)
    if response.status_code == 200:
        sha = response.json()["sha"]
    else:
        return False

    update_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_name}"
    data = {
        "message": f"Updated {file_name}",
        "content": new_content.encode("utf-8").decode("utf-8"),
        "sha": sha
    }
    return requests.put(update_url, headers=headers, json=data).status_code == 200

@client.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip()
    
    if content.startswith("!addpremium "):
        username = content.split(" ", 1)[1].strip()
        users = get_users(PREMIUM_FILE)
        if username in users:
            await message.channel.send(f"❌ {username} is already in the premium list!")
        else:
            users.append(username)
            if update_users(PREMIUM_FILE, users):
                await message.channel.send(f"✅ {username} added to the premium list!")
            else:
                await message.channel.send("❌ Failed to update the list.")

    elif content.startswith("!removepremium "):
        username = content.split(" ", 1)[1].strip()
        users = get_users(PREMIUM_FILE)
        if username not in users:
            await message.channel.send(f"❌ {username} is not in the premium list!")
        else:
            users.remove(username)
            if update_users(PREMIUM_FILE, users):
                await message.channel.send(f"✅ {username} removed from the premium list!")
            else:
                await message.channel.send("❌ Failed to update the list.")

    elif content.startswith("!addblacklist "):
        username = content.split(" ", 1)[1].strip()
        users = get_users(BLACKLIST_FILE)
        if username in users:
            await message.channel.send(f"❌ {username} is already in the blacklist!")
        else:
            users.append(username)
            if update_users(BLACKLIST_FILE, users):
                await message.channel.send(f"✅ {username} added to the blacklist!")
            else:
                await message.channel.send("❌ Failed to update the list.")

    elif content.startswith("!removeblacklist "):
        username = content.split(" ", 1)[1].strip()
        users = get_users(BLACKLIST_FILE)
        if username not in users:
            await message.channel.send(f"❌ {username} is not in the blacklist!")
        else:
            users.remove(username)
            if update_users(BLACKLIST_FILE, users):
                await message.channel.send(f"✅ {username} removed from the blacklist!")
            else:
                await message.channel.send("❌ Failed to update the list.")

client.run(DISCORD_TOKEN)