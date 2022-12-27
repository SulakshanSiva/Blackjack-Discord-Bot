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
async def profile(ctx, member:discord.Member = None):
    if member == None:  
        member = ctx.author

    name = member.display_name
    pfp = member.display_avatar

    embed = discord.Embed(title="Profile", description="Player Stats", colour=discord.Colour.random())
    embed.set_author(name=f"{name}")
    embed.set_thumbnail(url=f"{pfp}")
    embed.add_field(name="Coins", value="test", inline=False)
    embed.add_field(name="Wins", value="test", inline=True)
    embed.add_field(name="Losses", value="test", inline=True)

    await ctx.send(embed=embed)


bot.run(token)




