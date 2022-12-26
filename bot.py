import discord
from discord.ext import commands

bot = commands.Bot(command_prefix = "!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot is online")

@bot.command()
async def ping(ctx):
    await ctx.reply("Hi")


bot.run("MTA1Njk5ODk5Mjg4NzY5MzQwMw.GQOU5u.fxagf2FxwfqCCNNy19AtN-g_TElRcV11l8f6M0")




