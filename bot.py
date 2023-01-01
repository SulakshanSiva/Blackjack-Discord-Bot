import discord
from discord.ext import commands
import os
from dotenv import load_dotenv 
import asyncio
import aiosqlite
import random
import pydealer

blackjack_vals = {
    "values": {
        "King": 10,
        "Queen": 10,
        "Jack": 10,
        "10": 10,
        "9": 9,
        "8": 8,
        "7": 7,
        "6": 6,
        "5": 5,
        "4": 4,
        "3": 3,
        "2": 2,
        "Ace": 1
    }
}

load_dotenv('.env')

token = os.getenv('TUTORIAL_BOT_TOKEN')

bot = commands.Bot(command_prefix = "!", intents=discord.Intents.all())

bot.remove_command('help')

bot.gameState = False
bot.deck = pydealer.Deck(rebuild=True, re_shuffle=True)
bot.dealer = pydealer.Stack()
bot.player = pydealer.Stack()
bot.money = 0

@bot.event
async def on_ready():
    print("Bot is online")
    bot.db = await aiosqlite.connect("bank.db")
    await asyncio.sleep(3)
    async with bot.db.cursor() as cursor:
        await cursor.execute("CREATE TABLE IF NOT EXISTS bank(coins INTEGER, wins INTEGER, loss INTEGER, user INTEGER)")
    await bot.db.commit()
    print("Database ready!")

async def create_stats(user):
    async with bot.db.cursor() as cursor:
        await cursor.execute("INSERT INTO bank VALUES(?, ?, ?, ?)", (100, 0, 0, user.id))
    await bot.db.commit()
    return 

async def get_stats(user):
    async with bot.db.cursor() as cursor:
        await cursor.execute('SELECT coins, wins, loss FROM bank WHERE user = ?', (user.id,))
        data = await cursor.fetchone()
        if data is None: 
            await create_stats(user)
            return 100, 0, 0
        coins, wins, loss = data[0], data[1], data[2]
        return coins, wins, loss 

async def update_coins(user, amount: int):
    coins, wins, loss = await get_stats(user)
    async with bot.db.cursor() as cursor:
        await cursor.execute('SELECT coins FROM bank WHERE user = ?', (user.id,))
        data = await cursor.fetchone()
        if data is None:
            await create_stats(user)
            return 0
        await cursor.execute("UPDATE bank SET coins = ? WHERE user = ?", (coins + amount, user.id))
    await bot.db.commit()
    
async def update_wins(user, amount: int):
    coins, wins, loss = await get_stats(user)
    async with bot.db.cursor() as cursor:
        await cursor.execute('SELECT wins FROM bank WHERE user = ?', (user.id,))
        data = await cursor.fetchone()
        if data is None:
            await create_stats(user)
            return 0
        await cursor.execute("UPDATE bank SET wins = ? WHERE user = ?", (wins + amount, user.id))
    await bot.db.commit()

async def update_loss(user, amount: int):
    coins, wins, loss = await get_stats(user)
    async with bot.db.cursor() as cursor:
        await cursor.execute('SELECT loss FROM bank WHERE user = ?', (user.id,))
        data = await cursor.fetchone()
        if data is None:
            await create_stats(user)
            return 0
        await cursor.execute("UPDATE bank SET loss = ? WHERE user = ?", (loss + amount, user.id))
    await bot.db.commit()

@bot.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def bet(ctx: commands.context, amount):
    coins, wins, loss = await get_stats(ctx.author)
    try:
        amount = int(amount)
    except ValueError:
            pass
    if amount > coins:
        return await ctx.send("You do not have enough coins to place that bet!")
    else:
        bot.money = amount
        #play game
        bot.gameState = True
        bot.deck = pydealer.Deck(rebuild=True, re_shuffle=True)
        bot.deck.shuffle()
        bot.dealer += bot.deck.deal(2)
        bot.player += bot.deck.deal(2)
        userHand = ""
        for card in bot.player:
            userHand += str(card) + " | "
        await ctx.send(f"Dealer's Hand: | {bot.dealer[0]} |\nThis is your hand: {userHand}\n Would you like to hit or stand?")

@bot.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def hit(ctx: commands.context, member: discord.Member = None):
    if member == None:
        member = ctx.author
    if bot.gameState == False:
        await ctx.send("You have not placed a bet yet!")
    else:
        bot.player += bot.deck.deal(1)
        userHand = ""
        for x in bot.player:
            userHand += str(x) + " | "
        await calcHandForHit(ctx, member)
        if(bot.gameState == False):
            bot.player.empty()
            bot.dealer.empty()
        else:
            await ctx.send(f"This is your hand: {userHand}\n Would you like to hit or stand?")
        
@bot.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def stand(ctx: commands.context, member: discord.Member = None):
    if member == None:
        member = ctx.author
    if bot.gameState == False:
        return await ctx.send("You have not placed a bet yet!")
    else:
        await calcHandForStand(ctx, member)
        if bot.gameState == False:
            bot.player.empty()
            bot.dealer.empty()
        else: 
            return
        
async def calcHandForHit(ctx: commands.context, user):
    #sort hands
    bot.player.sort(blackjack_vals)
    bot.dealer.sort(blackjack_vals)

    totalP = 0
    totalD = 0

    for card in bot.player:
        if card.value != "Ace":
            totalP += blackjack_vals["values"][card.value]
        else:
            temp = totalP + 11
            if temp <= 21:
                totalP = temp
            else:
                totalP += 1
                
    for card in bot.dealer:
        if card.value != "Ace":
            totalD += blackjack_vals["values"][card.value]
        else:
            temp = totalD + 11
            if temp <= 21:
                totalD = temp
            else:
                totalD += 1
    
    if(totalP > 21):
        bot.gameState = False
        await ctx.send(f"Bust! You have lost. ${bot.money} has been deducted from your account.")
        await update_coins(user, (bot.money * -1))
        bot.money = 0
        await update_loss(user, 1)
    else: 
        return

async def calcHandForStand(ctx: commands.context, user):
    # sort hands
    bot.player.sort(blackjack_vals)
    bot.dealer.sort(blackjack_vals)

    totalP = 0
    totalD = 0

    for card in bot.player:
        if card.value != "Ace":
            totalP += blackjack_vals["values"][card.value]
        else:
            temp = totalP + 11
            if temp <= 21:
                totalP = temp
            else:
                totalP += 1

    for card in bot.dealer:
        if card.value != "Ace":
            totalD += blackjack_vals["values"][card.value]
        else:
            temp = totalD + 11
            if temp <= 21:
                totalD = temp
            else:
                totalD += 1
    
    if(totalP > totalD):
        bot.gameState = False
        await ctx.send(f"You have won! ${bot.money * 2} has been added to your account.")
        await update_coins(user, (bot.money * 2))
        bot.money = 0
        await update_wins(user, 1)
    else:
        bot.gameState= False
        await ctx.send(f"You have lost! ${bot.money} has been deducted from your account.")
        await update_coins(user, (bot.money * -1))
        bot.money = 0
        await update_loss(user, 1)

    
@bot.command()
async def profile(ctx, member:discord.Member = None):
    if member == None:  
        member = ctx.author
    coins, wins, loss = await get_stats(member)

    name = member.display_name
    pfp = member.display_avatar

    embed = discord.Embed(title="Profile", description="Player Stats", colour=discord.Colour.random())
    embed.set_author(name=f"{name}")
    embed.set_thumbnail(url=f"{pfp}")
    embed.add_field(name="Coins", value=coins, inline=False)
    embed.add_field(name="Wins", value=wins, inline=True)
    embed.add_field(name="Losses", value=loss, inline=True)

    await ctx.send(embed=embed)

@bot.command()
async def rules(ctx):
    lineOne = "This game will be you against a dealer. The goal of the game is to have a hand that totals higher than the dealer's, but doesn't total to higher than 21.\n"
    lineTwo = "You and the dealer will start off with 2 cards each. You can stay with your hand or recieve a card, called a hit.\n"
    lineThree = "To start the game use the following command: !bet {amount} (ex. !bet 50)\n"
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
    commandOne = "!rules - Displays the rules of the game and how to play\n"
    commandTwo = "!profile - Displays the player profile\n"
    commandThree = "!bet {amount} - Starts a game of Blackjack with the amount entered as the bet.\n"
    commandFour = "!hit - User receives another card in their hand. Used while in a game of Blackjack.\n"
    commandFive = "!stand - User ends the game and compares their hand with the dealers. Used while in a game of Blackjack.\n"

    embed = discord.Embed(
        title="Help", colour=discord.Colour.purple())
    embed.add_field(
        name="Commands", value=f"{commandOne}{commandTwo}{commandThree}{commandFour}{commandFive}", inline=False)

    await ctx.send(embed=embed)


bot.run(token)
asyncio.run(bot.db.close())




