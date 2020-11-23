import discord
import sqlite3
import dotenv
import os
import logging

from datetime import datetime
from io import BytesIO

from boss import boss

dotenv.load_dotenv()

# Setup logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

client = discord.Client()
bot_prefix = "!"

USAGE = """
Usage: `!report <boss_type> <dungeon> [minutes ago]`
    e.g. `!report Main Petram 23` (Petram main died 23 minutes ago)
    e.g. `!report Mini Darkmire` (DM mini just died, NO was time specified)
    e.g. `!report Main Mausoleum 331` (Maus mini just died 5 hours and 31 minutes ago)

    For latest status please use `!status`
"""


@client.event
async def on_ready():
    logger.info("We have logged in as {0.user}".format(client))


async def post_img(message, img: BytesIO) -> None:
    file = discord.File(img, filename="img.png")
    embed = discord.Embed()
    embed.set_image(url="attachment://img.png")
    await message.channel.send(embed=embed, file=file)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    message.content = message.content.lower()

    # !status
    if message.content.startswith("!status"):
        await post_img(message, img=boss.get_plot())

    # !report
    elif message.content.startswith("!report"):
        logger.info(f"user {str(message.author)}: ({message.content})")
        msg = message.content[len("!report ") :].split()
        if len(msg) < 2:
            await message.channel.send(USAGE)
            return
        boss_type = msg[0]
        dungeon = msg[1]
        if len(msg) == 3:
            time = int(msg[2])
        else:
            time = 0

        await message.channel.send(boss.update(boss_type, dungeon, time))

    # !save
    elif message.content.startswith("!save"):
        logger.info(f"user {str(message.author)} saved database!")
        boss.save()
        await message.channel.send("Database saved")

    # !debug
    elif message.content.startswith("!debug"):
        if str(message.author) == "rsprudencio#4854":
            await message.channel.send(f"{boss.bosses}")
        else:
            await message.channel.send("Unauthorized")

    # !help
    elif message.content.startswith("!help"):
        await message.channel.send(USAGE)
        return


def run_bot() -> None:
    client.run(os.getenv("DISCORD_TOKEN"))
