import aiohttp
import discord
from discord.ext import commands
import os

bot = commands.Bot(command_prefix="~", case_insensitive=True)
bot.remove_command("help")


@bot.event
async def on_ready():
    
    await bot.change_presence(activity=discord.Game(
        name="On reddit :3 | ~sub")) 
    print(f"Logged in on {len(bot.guilds)} servers")


@bot.event
async def on_message(msg):

    if msg.author == bot.user:
        return
    if msg.author.bot:
        return
    
    await bot.process_commands(msg)


@bot.command()
async def sub(ctx, sub = None):
    """The reddit command."""

    color = 0xff4500
    
    if sub == None:
        
        owner = discord.utils.get(bot.users, id=357641367507435531)
        
        embed = discord.Embed(color=color)
        embed.add_field(name="R3dd1t", value="Thanks for inviting Reddit Bot to your server!\n"
                                             "This bot essentially gets images from any subreddit you specify.\n"
                                             "Try `~sub hamsters` or `~sub JoyconBoyz`."
                        )
        
        embed.add_field(name="Author", value=f"This bot was created by {owner.mention} in discord.py.")
        embed.add_field(name="Bot invite:", value=f"https://discordapp.com/oauth2/authorize?client_id={bot.user.id}"
                                                   "&scope=bot&permissions=18432"
                        )
        embed.add_field(name="Embed Errors", value="If the link isn't an image, it will drop the embed and just post the link.\n"
                              "(Blame reddit API for this :c)"
                        )
        
        embed.set_image(url="https://cdn.discordapp.com/attachments/507339242096033792/519655500216926208/885444_news_512x512.png")
        
        await ctx.send(embed=embed)
        return

    async with aiohttp.ClientSession() as cs:
        async with cs.get(f"https://api.reddit.com/r/{sub}/random") as r:
            data = await r.json()

            # is_self checks if it's a text post, which is what we don't want
            if data[0]["data"]["children"][0]["data"]["is_self"] == False:
                
                image = data[0]["data"]["children"][0]["data"]["url"]
                embed = discord.Embed(
                    title=data[0]["data"]["children"][0]["data"]["subreddit"],
                    color=color
                    )
                
                embed.set_image(url=image)
                
                await ctx.send(embed=embed)
                
            else:

                link = data[0]["data"]["children"][0]["data"]["url"]
                
                await ctx.send(link)
                

bot.run(os.environ['TOKEN'])
