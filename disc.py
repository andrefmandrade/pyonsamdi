import logging
from io import BytesIO

import discord

from boss import boss
from settings import ADMINS

logger = logging.getLogger(__name__)
client = discord.Client()

USAGE = """
Usage: `!report <boss_type> <dungeon> [minutes ago]`
    e.g. `!report Main Petram 23` (Petram main died 23 minutes ago)
    e.g. `!report Mini Darkmire` (DM mini just died, NO was time specified)
    e.g. `!report Main Mausoleum 331` (Maus mini just died 5 hours and 31 minutes ago)

    For latest status please use `!status`
"""


@client.event
async def on_ready():
    logger.info(f"We have logged in as {client.user}")


async def post_img(message, img: BytesIO) -> None:
    file = discord.File(img, filename="img.png")
    embed = discord.Embed().set_image(url="attachment://img.png")
    await message.channel.send(embed=embed, file=file)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif str(message.author) == "UO Outlands #livefeed-pvm#0000":
        if message.content.startswith("The Shrine") or message.content.startswith("An Omni Realm"):
            await message.channel.send("@here")
    message.content = message.content.lower()

    # !status
    if message.content.startswith("!status"):
        if "detailed" in message.content:
            await message.channel.send(boss.status_detailed())
        else:
            await post_img(message, img=boss.status_plot())

    # !report
    elif message.content.startswith("!report"):
        logger.info(f"user {str(message.author)}: ({message.content})")
        msg = message.content[len("!report ") :].split()
        if len(msg) < 2:
            return await message.channel.send(USAGE)

        boss_type = msg[0]
        dungeon = msg[1]
        if len(msg) == 3:
            try:
                time = int(msg[2])
            except ValueError:
                return await message.channel.send(USAGE)
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
        if str(message.author) in ADMINS:
            await message.channel.send(f"{boss.bosses}")
        else:
            await message.channel.send("Unauthorized")

    # !help
    elif message.content.startswith("!help"):
        await message.channel.send(USAGE)
        return


def run_bot(token: str) -> None:
    client.run(token)
