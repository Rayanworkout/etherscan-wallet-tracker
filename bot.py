import json
import os
import discord
from discord.ext import commands
from discord.ext.commands.errors import (CheckFailure, CommandNotFound,
                                         MissingRequiredArgument)

from utils import get_all_transactions

bot = commands.Bot(command_prefix="!", help_command=None, case_insensitive=True, intents=discord.Intents.all())


#############################################################################################################

@bot.event
async def on_ready():
    print("Wallet Tracker Bot Ready ...")

#############################################################################################################

@bot.event
async def on_command_error(ctx, error):
    """Custom error handler, for the selected exceptions
    not appearing in the terminal, or sending msg when arg is mandatory"""

    if isinstance(error, MissingRequiredArgument):
        embed = discord.Embed(
            description="You need to specify something after the command !  :x:",
            color=discord.Colour.blue(),
        )
        await ctx.reply(embed=embed)
    elif isinstance(error, (CheckFailure, CommandNotFound)):
        pass

@bot.check
async def globally_block_dms(ctx):
    """Preventing anyone to send DM to the Bot"""
    return ctx.guild is not None


def checkAuthorized(ctx):
    """Defining discord IDs authorized for
    admin commands"""
    return ctx.message.author.id in [
        828233789594927115,
    ]

#############################################################################################################

@bot.command()
@commands.check(checkAuthorized)
async def Tags(ctx):
    
    existing_tags = [f"**{folder.upper()}**\n\n" for folder in os.listdir("tracked_accounts")]
    embed = discord.Embed(
    description=f"**:arrow_down: Existing Tags  :arrow_down:**\n\n{''.join(existing_tags)}",
    color=discord.Colour.blue(),
    )
    return await ctx.reply(embed=embed)


@bot.command()
@commands.check(checkAuthorized)
async def track(ctx, *args):
    
    if len(args) != 2:
        embed = discord.Embed(
        description="**You need to specify an Ethereum address and a Tag with this command  :x:**",
        color=discord.Colour.blue(),
        )
        return await ctx.reply(embed=embed)
    
    address = args[0].lower()
    tag = args[1].lower()
    
    
    
    data = get_all_transactions(address)
    
    if data in ["error getting transactions for this account", "no transaction found for this account"]:
        embed = discord.Embed(
        description=f"**{data}  :x:**",
        color=discord.Colour.blue(),
            )
        
        return await ctx.reply(embed=embed)
    
    for folder in os.listdir("tracked_accounts"):
        for accounts in os.listdir(f"tracked_accounts/{folder}"):
            if f"{address}.json" == accounts:
                embed = discord.Embed(
                description=f'**"{address}"\n\nis already tracked  :x:**',
                color=discord.Colour.blue(),
                    )
            
                return await ctx.reply(embed=embed)
    
    
    if not os.path.isdir(f"tracked_accounts/{tag}"):
        os.mkdir(f"tracked_accounts/{tag}")
        
    with open(f"tracked_accounts/{tag}/{address}.json", "w") as f:
        json.dump(data, f, indent=4)

    embed = discord.Embed(
    description=f'**:white_check_mark: NOW TRACKING\n\n{address}\n\nas "{tag.upper()}"**',
    color=discord.Colour.blue(),
        )
    
    return await ctx.reply(embed=embed)


@bot.command()
@commands.check(checkAuthorized)
async def untrack(ctx, arg):
    
    arg = arg.lower()    
    
    for folder in os.listdir("tracked_accounts"):
        for accounts in os.listdir(f"tracked_accounts/{folder}"):
            if f"{arg}.json" == accounts:
                os.remove(f"tracked_accounts/{folder}/{accounts}")
                embed = discord.Embed(
                description=f"**{arg} is no longer tracked  :white_check_mark: **",
                color=discord.Colour.blue(),
                    )
            
                return await ctx.reply(embed=embed)
    
    else:
        embed = discord.Embed(
        description=f"**{arg} is not tracked  :x: **",
        color=discord.Colour.blue(),
            )
        
        return await ctx.reply(embed=embed)
 


if not os.path.isdir("tracked_accounts"):
    os.mkdir("tracked_accounts")

bot.run("MTAzODY1NDYyOTg0MTQ3MzU3OA.GlqVNV.O18rha9lCJnF4LyvAohkeykWQqjUZntNxON0rE")
