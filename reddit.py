import aiohttp
import discord
import os
import datetime as dt
from discord.ext import commands

bot = commands.Bot(command_prefix="r~", case_insensitive=True)
bot.remove_command("help")

color = 0xFF4500

# def for finding an nsfw channel


def find_nsfw(channels):

    for channel in channels:

        if type(channel) == discord.TextChannel and channel.is_nsfw():

            return channel


@bot.event
async def on_ready():

    await bot.change_presence(
        activity=discord.Activity(
            name="reddit :3 | r~help", type=discord.ActivityType.watching
        )
    )

    print(f"Logged in on {len(bot.guilds)} servers")


@bot.event
async def on_message(msg):


    channel = msg.channel

    if msg.author == bot.user:

        return

    if msg.author.bot:

        return

    if msg.content.startswith("r/"):

        sub = msg.content.split("/")[1]

        listings = ["best", "hot", "new", "random", "rising", "top"]

        async with aiohttp.ClientSession() as cs:

            async with cs.get(f"https://api.reddit.com/r/{sub}/random") as r:

                data = await r.json()

                try:

                        # TODO: Make this a class of dictionary objects

                        url = data[0]["data"]["children"][0]["data"]["url"]
                        subreddit = data[0]["data"]["children"][0]["data"]["subreddit"]
                        timestamp = dt.datetime.fromtimestamp(
                            data[0]["data"]["children"][0]["data"]["created_utc"]
                        )
                        author = data[0]["data"]["children"][0]["data"]["author"]
                        permalink = data[0]["data"]["children"][0]["data"]["permalink"]
                        title = data[0]["data"]["children"][0]["data"]["title"]
                        text = data[0]["data"]["children"][0]["data"]["selftext"]
                        nsfw = data[0]["data"]["children"][0]["data"]["over_18"]
                        post = f"https://www.reddit.com{permalink}"
                        media = data[0]["data"]["children"][0]["data"]["media"]
                        post = f"https://www.reddit.com{permalink}"
                        

                        embed = discord.Embed(
                            title=subreddit, url=post, timestamp=timestamp, color=color
                        )

                        embed.add_field(name="Title", value=title, inline=False)

                        embed.set_footer(text=f"Author: {author}")

                        if len(text) > 1024 and text != "":

                            text = f"Content is too large...\n{post}"

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

                        if type(channel) == discord.DMChannel:

                            await channel.send(embed=embed)

                        elif not nsfw:

                            await channel.send(embed=embed)

                        elif nsfw and channel.is_nsfw():

                            await channel.send(embed=embed)

                        else:

                            nsfw_channel = find_nsfw(channel.guild.channels)

                            if nsfw_channel == None:

                                info = discord.Embed(color=color)

                                embed.add_field(
                                    name="NSFW Content",
                                    value="The content from this subreddit happens to be NSFW content, "
                                    "and no NSFW channel exists on this server.\n"
                                    "Therefore, no content was posted as a precaution.",
                                )

                                await channel.send(embed=info)

                            else:

                                await nsfw_channel.send(embed=embed)

                                info = discord.Embed(color=color)

                                info.add_field(
                                    name="NSFW Content",
                                    value="The content from this subreddit happens to be NSFW content, "
                                    "and this command wasn't used in an NSFW channel.\n"
                                    f"However we posted it to {nsfw_channel.mention}, an NSFW channel.",
                                )

                                info.set_footer(
                                    text="Now can I have my coffee back? :3"
                                )

                                await channel.send(embed=info)

                except KeyError:

                    error = discord.Embed(color=color)

                    error.add_field(
                        name="Subreddit Error", value="Subreddit was not found."
                    )

                    await channel.send(embed=error)

    elif msg.content.startswith("u/"):

        username = msg.content.split("/")[1]

        async with aiohttp.ClientSession() as cs:

            async with cs.get(f"https://api.reddit.com/user/{username}/about") as r:

                data = await r.json()

                try:

                    # TODO: Make this a class of dictionary objects

                    name = data["data"]["name"]
                    user = f"https://reddit.com/user/{name}/"
                    employee = data["data"]["is_employee"]
                    premium = data["data"]["is_gold"]
                    avatar = data["data"]["icon_img"].split("?")[0]
                    timestamp = dt.datetime.fromtimestamp(data["data"]["created_utc"])
                    link_karma = data["data"]["link_karma"]
                    comment_karma = data["data"]["comment_karma"]
                    verified = data["data"]["verified"]

                    embed = discord.Embed(
                        title=name, url=user, timestamp=timestamp, color=color
                    )

                    embed.add_field(name="Verified", value=verified)

                    embed.add_field(name="Comment Karma", value=comment_karma)

                    embed.add_field(name="Post Karma", value=link_karma)

                    embed.add_field(name="Employee", value=employee)

                    embed.add_field(name="Premium", value=premium)

                    embed.set_image(url=avatar)

                    embed.set_footer(text="Joined:")

                    await channel.send(embed=embed)

                except KeyError:

                    error = discord.Embed(color=color)

                    error.add_field(
                        name="User Error", value="User was unfound or nonexistant."
                    )

                    await channel.send(embed=error)

    await bot.process_commands(msg)

    
@bot.command()
async def ping(ctx):
    """Test the bot's uptime"""

    await ctx.send("Pong!")

@bot.command()
async def feedback(ctx, *, feedback):
    """Sends a DM via the bot to the bot owner
    And also stores the feedback in a file."""

    owner = discord.utils.get(bot.users, id=357_641_367_507_435_531)

    content = discord.Embed(color=color)

    content.add_field(
        name="User Feedback", value=feedback
    )

    content.set_footer(text=f"Contribution made by {ctx.author}")

    await owner.send(embed=content)
    
@bot.command()
async def help(ctx):
    """The reddit command."""

    async with aiohttp.ClientSession() as cs:

            async with cs.get(f"https://api.reddit.com/r/random") as r:

                data = await r.json()

                embed = discord.Embed(color=color)

                embed.add_field(
                    name="R3dd1t",
                    value="Thanks for inviting R3dd1t to your server!\n"
                    "This bot essentially gets images from any subreddit you specify.\n"
                    f"Try looking at a new sub!",
                )

                embed = discord.Embed(color=color)

                embed.add_field(
                    name="R3dd1t",
                    value="Thanks for inviting R3dd1t to your server!\n"
                    "This bot essentially gets images from any subreddit you specify.\n"
                    "Try `r/woooosh` or `r/ProgrammerHumor`.",
                )

                embed.add_field(
                    name="User lookup",
                    value="R3dd1t also has a user lookup command to view a user's information.\n"
                    "Try `u/reddit` or `u/(username)`.",
                )

                embed.add_field(
                    name="Author",
                    value=f"This bot was created by Slick9000#2237 in discord.py.",
                )

                embed.add_field(
                    name="Bot Invite:",
                    value=f"[Invite](https://discordapp.com/oauth2/authorize?client_id={bot.user.id}"
                    f"&scope=bot&permissions=18432)",
                )

                embed.add_field(
                    name="NSFW Content Checks",
                    value="There's no need to worry about NSFW content, ever.\n"
                    "If R3dd1t detects the content is NSFW, it posts it to an NSFW channel.\n"
                    "If no NSFW channel exists, it simply doesn't post it. Lovely.\n"
                    "**Note:** This does not apply to DM channels. NSFW content will always post in that situation.",
                )

                embed.add_field(
                    name="Feedback and Bugs",
                    value="If the bot has any bugs, or if you would like to see a feature added to the bot,\n"
                    "You can feel free to use the `r~feedback` command.\n"
                    "This sends me whatever feedback you have to my private DM, and is also stored in a database.\n"
                    "Any help would be greatly appreciated!"
                )

                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/507339242096033792/519655500216926208/885444_news_512x512.png"
                )

                await ctx.send(embed=embed)


bot.run(os.environ['TOKEN'])
