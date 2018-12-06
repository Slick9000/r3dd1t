import aiohttp
import discord
from discord.ext import commands
import os

bot = commands.Bot(command_prefix="~", case_insensitive=True)
bot.remove_command("help")


@bot.event
async def on_ready():

    await bot.change_presence(activity=discord.Game(
        name="on reddit :3 | ~sub"))

    print(f"Logged in on {len(bot.guilds)} servers")


@bot.event
async def on_message(msg):

    if msg.author == bot.user:

        return

    if msg.author.bot:

        return

    await bot.process_commands(msg)

# def for finding an nsfw channel
def find_nsfw(channels):
    for channel in channels:

        if type(channel) == discord.TextChannel and channel.is_nsfw():

            return channel


@bot.command()
async def sub(ctx, sub = None):
    """The reddit command."""

    try:

        color = 0xff4500

        if sub == None:

            owner = discord.utils.get(bot.users, id=357641367507435531)

            embed = discord.Embed(color=color)

            embed.add_field(name="R3dd1t", value="Thanks for inviting R3dd1t to your server!\n"
                                                 "This bot essentially gets images from any subreddit you specify.\n"
                                                 "Try `~sub hamsters` or `~sub ProgrammerHumor`."
                           )

            embed.add_field(name="Author", value=f"This bot was created by {owner.mention} in discord.py.")

            embed.add_field(name="Bot invite:", value=f"https://discordapp.com/oauth2/authorize?client_id={bot.user.id}"
                                                       "&scope=bot&permissions=18432"
                           )

            embed.add_field(name="Embed Errors", value="If the link isn't an image, it will drop the embed and just post the link.\n"
                                 "(Blame reddit API for this :c)"
                           )

            embed.add_field(name="NSFW Content Checks", value="There's no need to worry about NSFW content, ever.\n"
                                                              "If R3dd1t detects the content is NSFW, it posts it to an NSFW channel.\n"
                                                              "If no NSFW channel exists, it simply doesn't post it. Lovely."
                            )

            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/507339242096033792/519655500216926208/885444_news_512x512.png")

            await ctx.send(embed=embed)
            return

        async with aiohttp.ClientSession() as cs:

            async with cs.get(f"https://api.reddit.com/r/{sub}/random") as r:

                data = await r.json()

                # handling all the nsfw content
                if data[0]["data"]["children"][0]["data"]["over_18"]:

                    if data[0]["data"]["children"][0]["data"]["is_self"] == False:

                        image = data[0]["data"]["children"][0]["data"]["url"]
                        embed = discord.Embed(
                            title=data[0]["data"]["children"][0]["data"]["subreddit"],
                            color=color
                            )

                        embed.set_image(url=image)

                        if ctx.channel.is_nsfw() == True:

                            await ctx.send(embed=embed)

                        else:

                            channel = find_nsfw(ctx.guild.channels)

                            if channel == None:

                                embed = discord.Embed(color=color)

                                embed.add_field(name="NSFW Content", value="The content from this subreddit happens to be NSFW content, "
                                                                           "and no NSFW channel exists on this server.\n"
                                                                           "Therefore, no content was posted as a precaution."
                                                )

                                await ctx.send(embed=embed)

                            else:

                                await channel.send(embed=embed)

                                info = discord.Embed(color=color)

                                info.add_field(name="NSFW Content", value="The content from this subreddit happens to be NSFW content, "
                                                                          "and this command wasn't used in an NSFW channel.\n"
                                                                          f"However we posted it to {channel.mention}, an NSFW channel."
                                               )

                                info.set_footer(text="Now can I have my coffee back? :3")

                                await ctx.send(embed=info)


                # is_self checks if it's a text post, which is what we don't want
                elif data[0]["data"]["children"][0]["data"]["is_self"] == False:

                    image = data[0]["data"]["children"][0]["data"]["url"]
                    embed = discord.Embed(
                        title=data[0]["data"]["children"][0]["data"]["subreddit"],
                        color=color
                        )

                    embed.set_image(url=image)

                    await ctx.send(embed=embed)

                else:

                    # if reddit api still gives a text post just post the link
                    link = data[0]["data"]["children"][0]["data"]["url"]

                    await ctx.send(link)

    except KeyError:

            # subreddit unfound
            embed = discord.Embed(color=color)

            embed.add_field(name="Subreddit Error", value="Subreddit was not found.")

            await ctx.send(embed=embed)


            
bot.run(os.environ['TOKEN'])
