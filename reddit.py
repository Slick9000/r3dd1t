import aiohttp
import discord
import datetime as dt
from discord.ext import commands
from discord.ext import tasks
import random
import re

intents = discord.Intents.default()

intents.message_content = True

bot = commands.Bot(command_prefix="r-", intents=intents, case_insensitive=True)

bot.remove_command("help")

statuses = ['stupid comments r-help', 'ai take over r-help', 
            'children arguing r-help', 'the internet r-help', 'scary videos r-help',
            'cat videos r-help', 'something r-help', 'you read these? r-help',
            'slick sleep r-help', 'twitch.tv r-help', 'the world spin r-help']

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
            name=random.choice(statuses), type=discord.ActivityType.watching
        )
    )

    print(f"Logged in on {len(bot.guilds)} servers")

@tasks.loop(seconds=40)
async def change_presence():

    await bot.change_presence(discord.Activity(
            name=random.choice(statuses), type=discord.ActivityType.watching
    ))

@bot.event
async def on_message(msg):

    channel = msg.channel

    if msg.author == bot.user:

        return

    if msg.author.bot:

        return

    if msg.content.startswith("r/"):
            
        sub = msg.content.split("/")[1]

        listings = ["best", "hot", "new", "rising", "top"]

        async with aiohttp.ClientSession() as cs:

            async with cs.get(f"https://api.reddit.com/r/{sub}/{random.choice(listings)}") as r:

                info = await r.json()

                try:

                    data = info[0]

                except:

                    data = info

                try:
                    
                    post = random.choice(data["data"]["children"])

                except KeyError:

                    error = discord.Embed(color=color)

                    error.add_field(
                        name="Subreddit Error", value="Subreddit was not found."
                    )

                    await channel.send(embed=error)

                    return
                
                except IndexError:

                    error = discord.Embed(color=color)

                    error.add_field(
                        name="Subreddit Error", value="Subreddit was not found."
                    )

                    await channel.send(embed=error)

                    return

                url = post["data"]["url"]
                subreddit = post["data"]["subreddit"]
                timestamp = dt.datetime.fromtimestamp(
                    post["data"]["created_utc"]
                )
                author = post["data"]["author"]
                permalink = post["data"]["permalink"]
                title = post["data"]["title"]
                text = post["data"]["selftext"]
                nsfw = post["data"]["over_18"]
                link = f"https://www.reddit.com{permalink}"
                media = post["data"]["secure_media"]

                #print(media)
                

                embed = discord.Embed(
                    title=subreddit, url=link, timestamp=timestamp, color=color
                )

                try:
                    
                    if media["type"]:

                        direct_video = re.search(r'https.*\?',media["oembed"]["html"]).group(0)

                        embed.add_field(
                            name="Video Title",
                            value="[{}]({})".format(media["oembed"]["title"], url),
                        )

                        embed.add_field(
                            name="Direct Video",
                            value="[{}]({})".format("Video", direct_video)
                        )

                        embed.set_footer(text=f'Author: {post["data"]["author_fullname"]}')

                        embed.set_image(url=media["oembed"]["thumbnail_url"])

                except:

                    if media:

                        direct_video = media["reddit_video"]["scrubber_media_url"]

                        embed.add_field(
                            name="Video Title",
                            value="[{}]({})".format(post["data"]["title"], url),
                        )

                        embed.add_field(
                            name="Direct Video",
                            value="[{}]({})".format("Video", direct_video)
                        )

                        embed.set_footer(text=f'Author: {post["data"]["author_fullname"]}')

                        embed.set_image(url=post["data"]["thumbnail"])
                    
                    else:

                        embed.add_field(name="Title", value=title, inline=False)

                        embed.set_footer(text=f"Author: {author}")

                        if len(text) > 1024 and text != "":

                            text = f"Content is too large...\n{link}"

                            embed.add_field(name="Content", value=text)

                        if url.endswith((".png", ".jpg", ".jpeg", ".gif")):

                            embed.set_image(url=url)

                        if url.startswith("https://imgur.com"):

                            url = media["thumbnail_url"]

                            embed.set_image(url=url)

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

                        info.add_field(
                            name="NSFW Content",
                            value="The content from this subreddit happens to be NSFW content, "
                            "and no NSFW channel exists on this server, therefore we assume it is not allowed.\n\n"
                            "Feel free to access this in another guild or in DM.",
                        )

                        info.set_footer(
                            text="*Protecting the world one command at a time!*"
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

    elif msg.content.startswith("u/"):

        username = msg.content.split("/")[1]

        async with aiohttp.ClientSession() as cs:

            async with cs.get(f"https://api.reddit.com/user/{username}/about") as r:

                data = await r.json()

                try:

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

    if len(feedback) < 1:

        content = discord.Embed(color=color)

        content.add_field(
            name="User Feedback", value="No feedback provided!"
        )

        await ctx.send(embed=content)

        return

    owner = await bot.fetch_user("357641367507435531")

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
                    "This bot essentially gets images from any subreddit you specify. Made by Slick9000#2237\n"
                    "Try `r/woooosh` or `r/ProgrammerHumor`.",
                )

                embed.add_field(
                    name="User lookup",
                    value="R3dd1t has a user lookup command to view a user's information.\n"
                    "Try `u/reddit` or `u/(username)`.",
                )

                embed.add_field(
                    name="Bot Invite:",
                    value=f"[Invite](https://discordapp.com/oauth2/authorize?client_id={bot.user.id}"
                    f"&scope=bot&permissions=18432)",
                )

                embed.add_field(
                    name="NSFW Content Checks",
                    value="There's no need to worry about accidental NSFW content in #general.\n"
                    "If R3dd1t detects the content is NSFW, it posts it to an NSFW channel.\n"
                    "If no NSFW channel exists, it simply doesn't post it. NSFW content will appear in DM.\n"
                )

                embed.add_field(
                    name="Feedback and Bugs",
                    value="If the bot has any bugs, or if you would like to see a feature added to the bot,\n"
                    "You can feel free to use the `r~feedback` command.\n"
                )

                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/507339242096033792/519655500216926208/885444_news_512x512.png"
                )

                await ctx.send(embed=embed)


token = open("token.txt").read()

if __name__ == '__main__':

   bot.run(token)
