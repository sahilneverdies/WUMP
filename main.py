import os
import asyncio
import traceback
from threading import Thread
from datetime import datetime

import aiohttp
import discord
from discord.ext import commands

# Local project imports
from core import Context
from core.Cog import Cog
from core.Olympus import Olympus
from utils.Tools import *
from utils.config import *

# Optional: auto-install (not recommended for production)
# os.system("pip install -r requirements.txt")  # REMOVE THIS ON RENDER

# Configure Jishaku behavior
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "False"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"

# Init bot
client = Olympus()
TOKEN = os.getenv("TOKEN")  # Set this in Render's Environment tab

# Keep-alive Flask server for UptimeRobot
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "© Wump Development 2025"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# Bot Events
@client.event
async def on_ready():
    await client.wait_until_ready()
    print("Loaded & Online!")
    print(f"Logged in as: {client.user}")
    print(f"Connected to: {len(client.guilds)} guilds")
    print(f"Connected to: {len(client.users)} users")

    try:
        synced = await client.tree.sync()
        print(f"Synced {len(client.commands)} Commands and {len(synced)} Slash Commands")
    except Exception as e:
        print("Slash sync failed:", e)

@client.event
async def on_command_completion(ctx: commands.Context):
    if ctx.author.id == 1070619070468214824:
        return

    command_name = ctx.command.qualified_name
    webhook_url = "https://discord.com/api/webhooks/1370626354768252958/..."  # REDACTED HERE

    embed = discord.Embed(color=0x000000)
    avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
    embed.set_author(name=f"Executed {command_name}", icon_url=avatar_url)
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(name="Command:", value=command_name, inline=False)
    embed.add_field(name="User:", value=f"{ctx.author} ({ctx.author.id})", inline=False)
    
    if ctx.guild:
        embed.add_field(name="Guild:", value=f"{ctx.guild.name} ({ctx.guild.id})", inline=False)
        embed.add_field(name="Channel:", value=f"{ctx.channel.name} ({ctx.channel.id})", inline=False)

    embed.timestamp = discord.utils.utcnow()
    embed.set_footer(text="Wump Development™", icon_url=client.user.display_avatar.url)

    try:
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(webhook_url, session=session)
            await webhook.send(embed=embed)
    except Exception as e:
        print("Webhook send error:", e)
        traceback.print_exc()

# Async entrypoint
async def main():
    async with client:
        await client.load_extension("jishaku")
        await client.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
