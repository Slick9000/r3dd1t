import aiohttp
import datetime as dt
import discord
from discord.ext import commands
import os

bot = commands.Bot(command_prefix="~", case_insensitive=True)
bot.remove_command("help")


@bot.event
async def on_ready():

    await bot.change_presence(activity=discord.Game(name="on reddit :3 | ~sub"))

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
async def sub(ctx, sub=None):
    """The reddit command."""

    color = 0xFF4500

    if sub == None:

        owner = discord.utils.get(bot.users, id=357_641_367_507_435_531)

        embed = discord.Embed(color=color)

        embed.add_field(
            name="R3dd1t",
            value="Thanks for inviting R3dd1t to your server!\n"
            "This bot essentially gets images from any subreddit you specify.\n"
            "Try `~sub hamsters` or `~sub ProgrammerHumor`.",
        )

        embed.add_field(
            name="Author",
            value=f"This bot was created by {owner.mention} in discord.py.",
        )

        embed.add_field(
            name="Bot Invite:",
            value="[Invite](https://discordapp.com/oauth2/authorize?client_id={bot.user.id}"
            "&scope=bot&permissions=18432)",
        )

        embed.add_field(
            name="NSFW Content Checks",
            value="There's no need to worry about NSFW content, ever.\n"
            "If R3dd1t detects the content is NSFW, it posts it to an NSFW channel.\n"
            "If no NSFW channel exists, it simply doesn't post it. Lovely.\n"
            "**Note:** This does not apply to DM channels, in that case it will post.",
        )

        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/507339242096033792/519655500216926208/885444_news_512x512.png"
        )

        await ctx.send(embed=embed)
        return

    async with aiohttp.ClientSession() as cs:

        async with cs.get(f"https://api.reddit.com/r/{sub}/random") as r:

            data = await r.json()

            try:

                try:

                    # TODO: Make this a class of dictionary objects

                    url = data[0]["data"]["children"][0]["data"]["url"]
                    name = data[0]["data"]["children"][0]["data"]["subreddit"]
                    timestamp = dt.datetime.fromtimestamp(
                        data[0]["data"]["children"][0]["data"]["created_utc"]
                    )
                    author = data[0]["data"]["children"][0]["data"]["author"]
                    post = data[0]["data"]["children"][0]["data"]["permalink"]
                    title = data[0]["data"]["children"][0]["data"]["title"]
                    text = data[0]["data"]["children"][0]["data"]["selftext"]
                    nsfw = data[0]["data"]["children"][0]["data"]["over_18"]
                    full_post = f"https://www.reddit.com{post}"
                    media = data[0]["data"]["children"][0]["data"]["media"]["oembed"]

                except TypeError:

                    media = None

                embed = discord.Embed(
                    title=name,
                    url=full_post,
                    timestamp=timestamp,
                    color=color
                )

                embed.add_field(name="Title", value=title, inline=False)

                embed.set_footer(text=f"Author: {author}")

                if text != "":

                    if len(text) > 1024:

                        text = f"Content is too large...\n{full_post}"

                    embed.add_field(name="Content", value=text)

                if url.endswith((".png", ".jpg", ".jpeg", ".gif")):

                    embed.set_image(url=url)

                if url.startswith("https://imgur.com"):

                    url = media["thumbnail_url"]

                    embed.set_image(url=url)

                if media:

                    if media["type"] == "video":

                        embed.add_field(
                            name="Video Title",
                            value="[{}]({})".format(media["title"], url),
                        )

                        embed.add_field(
                            name="Channel",
                            value="[{}]({})".format(
                                media["author_name"], media["author_url"]
                            ),
                        )

                        embed.set_image(url=media["thumbnail_url"])

                if not nsfw:

                    await ctx.send(embed=embed)

                elif nsfw and ctx.channel.is_nsfw():

                    await ctx.send(embed=embed)

                else:

                    channel = find_nsfw(ctx.guild.channels)

                    if channel == None:

                        embed = discord.Embed(color=color)

                        embed.add_field(
                            name="NSFW Content",
                            value="The content from this subreddit happens to be NSFW content, "
                            "and no NSFW channel exists on this server.\n"
                            "Therefore, no content was posted as a precaution.",
                        )

                        await ctx.send(embed=embed)

                    else:

                        await channel.send(embed=embed)

                        info = discord.Embed(color=color)

                        info.add_field(
                            name="NSFW Content",
                            value="The content from this subreddit happens to be NSFW content, "
                            "and this command wasn't used in an NSFW channel.\n"
                            f"However we posted it to {channel.mention}, an NSFW channel.",
                        )

                        info.set_footer(text="Now can I have my coffee back? :3")

                        await ctx.send(embed=info)

            except KeyError:

                error = discord.Embed(color=color)

                error.add_field(
                    name="Subreddit Error", value="Subreddit was not found."
                )

                await ctx.send(embed=error)



            
bot.run(os.environ['TOKEN'])
