from collections import UserList
from pydoc import describe
import discord
from discord.ext import commands
import os
import json
import random


os.chdir("C:\\Users\\jacks\\Desktop\\uwu\\Ecconamy")

client = commands.Bot(command_prefix = "d!", intents=discord.Intents.all())

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(title= "**You are on cooldown**, Please try again in 1 hour!", color=0xC32A07)
        await ctx.reply(embed=embed)


@client.event 
async def on_ready():
    print("Logged in as {0.user}". format(client))
    await client.change_presence(status=discord.Status.online, activity=discord.Game("d!help d!bal"))

@client.command(aliases = ["bal"])
async def balance(ctx):
    await open_account(ctx.author)
    
    
    user = ctx.author
    users = await get_bank_data()

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"] 

    balanceem = discord.Embed(title = f"{ctx.author.name}'s Balance", color=0x07a0c3)
    balanceem.add_field(name = ":moneybag: Wallet", value = wallet_amt)
    balanceem.add_field(name = ":bank: Bank", value = bank_amt)
    await ctx.reply(embed = balanceem)

@client.command(aliases = ["checkbal"])
async def checkbalance(ctx, member:discord.Member):
    await open_account(ctx.author)
    
    
    user = member
    users = await get_bank_data()

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"] 

    balanceem = discord.Embed(title = f"{member.display_name}'s Balance", color=0x07a0c3)
    balanceem.add_field(name = ":moneybag: Wallet", value = wallet_amt)
    balanceem.add_field(name = ":bank: Bank", value = bank_amt)
    await ctx.reply(embed = balanceem)    

@client.command()
@commands.cooldown(1,3600, commands.BucketType.user)
async def work(ctx):
    
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    earnings = random.randrange(10, 200)

    workemb = discord.Embed(title= f"{ctx.author.name}, You have worked for {earnings} dabs", color=0x07a0c3)


    await ctx.reply(embed= workemb)


    users[str(user.id)]["wallet"] += earnings

    with open("mainbank.json", "w") as f:
        json.dump(users,f)

@client.command()
async def withdraw(ctx,amount = None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)
    amount = int(amount)
    if amount>bal[1]:
        await ctx.send("You don't have that many dabs")
        return

    await update_bank(ctx.author, amount)
    await update_bank(ctx.author, -1*amount, "bank")
    await ctx.send("You withdrew {amount} Dabs!".format(amount = amount))
 
@client.command(aliases = ["lb"])
async def leaderboard(ctx,x = 10):
    users = await get_bank_data()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["wallet"] + users[user]["bank"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total,reverse=True)    

    em = discord.Embed(title = f"Top {x} Richest People" , description = "This is decided on the basis of raw money in the bank and wallet",color = discord.Color(0x07a0c3))
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = client.get_user(id_)
        name = member.name
        em.add_field(name = f"{index}. {name}" , value = f"{amt}",  inline = False)
        if index == x:
            break
        else:
            index += 1

    await ctx.reply(embed = em)

@client.command()
async def send(ctx,member:discord.Member,amount = None):
    await open_account(ctx.author)
    await open_account(member)

    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)
    amount = int(amount)
    if amount>bal[1]:
        await ctx.send("You don't have that many dabs")
        return

    await update_bank(ctx.author, -1*amount)
    await update_bank(ctx.author,amount, "bank")
    await ctx.send("You gave {amount} Dabs!".format(amount = amount))

@client.command()
@commands.has_role("Owners")
async def addmoney(ctx,member:discord.Member,amount = None):
    await open_account(ctx.author)
    await open_account(member)

    if amount == None:
        await ctx.send("Please enter the amount")
        return

    amount = int(amount)

    await update_bank(member,amount, "bank")
    addmoneyem = discord.Embed(title= f":white_check_mark: Added {amount} Dabs To {member.display_name}'s Pocket", color = discord.Color(0x07a0c3))
    await ctx.reply(embed=addmoneyem)


###

@client.command()
async def deposit(ctx,amount = None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)
    amount = int(amount)
    if amount>bal[0]:
        await ctx.send("You don't have that many dabs")
        return

    await update_bank(ctx.author, -1*amount)
    await update_bank(ctx.author,amount, "bank")
    await ctx.send("You desposited {amount} Dabs!".format(amount = amount))



async def open_account(user):

    users = await get_bank_data()
        
    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}     
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0 


        with open("mainbank.json", "w") as f:
            json.dump(users,f)
        return True

async def update_bank(user, change = 0, mode = "wallet"):
    users = await get_bank_data()
    users[str(user.id)][mode] +=  change

    with open("mainbank.json", "w") as f:
        json.dump(users,f)
    bal = [users[str(user.id)]["wallet"],users[str(user.id)]["bank"]]
    return bal

async def get_bank_data():
    with open("mainbank.json", "r") as f:
        users = json.load(f)

    return users



client.run("token")