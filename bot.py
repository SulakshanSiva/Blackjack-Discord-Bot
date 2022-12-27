import discord
from discord.ext import commands
import os
from dotenv import load_dotenv 

load_dotenv('.env')

token = os.getenv('TUTORIAL_BOT_TOKEN')

bot = commands.Bot(command_prefix = "!", intents=discord.Intents.all())

bot.remove_command('help')


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

@bot.command()
async def rules(ctx):
    lineOne = "This game will be you against a dealer. The goal of the game is to have a hand that totals higher than the dealer's, but doesn't total to higher than 21.\n"
    lineTwo = "You and the dealer will start off with 2 cards each. You can stay with your hand or recieve a card, called a hit.\n"
    lineThree = "To start the game use the following command: TODO\n"
    lineFour = "Odds are x2.\n"
    winOne = "If your total or the dealer's total is higher than 21, you have 'bust' which is an automatic loss.\n"
    winTwo = "If your total is higher then the dealer's, you have won.\n"
    winThree = "If the dealer's total is higher then your's, you have lost.\n"
    winFour = "If both you and the dealer have 'bust', then you have lost.\n"
    winFive = "If both you and the dealer have an equal score, then you have lost.\n"

    embed = discord.Embed(
        title="How To Play!", description="Welcome to Blackjack!", colour=discord.Colour.red())
    embed.add_field(name="Rules", value=f"{lineOne}{lineTwo}{lineThree}{lineFour}", inline=False)

    embed.add_field(name="Win Conditions",
                    value=f"{winOne}{winTwo}{winThree}{winFour}{winFive}", inline=False)
    

    await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    paragraph = "hi"
    embed = discord.Embed(
        title="Help", description="Command List", colour=discord.Colour.purple())

    await ctx.send(embed=embed)

bot.run(token)




