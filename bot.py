import discord
from discord.ext import commands
import os
from dotenv import load_dotenv 

load_dotenv('.env')

token = os.getenv('TUTORIAL_BOT_TOKEN')

bot = commands.Bot(command_prefix = "!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot is online")

@bot.command()
async def ping(ctx):
    await ctx.reply("Hi")


bot.run(token)




