import asyncio
import logging
from io import BytesIO

import discord

from boss import BOSSES, MINI_BOSSES, boss
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


async def scheduled_report():
    channel = client.get_channel(525396277593243648)
    while True:
        file = discord.File(boss.status_plot(), filename="img.png")
        embed = discord.Embed().set_image(url="attachment://img.png")
        await channel.send(embed=embed, file=file)
        await asyncio.sleep(30 * 60)


@client.event
async def on_ready():
    logger.info(f"We have logged in as {client.user}")
    await scheduled_report()


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
    elif str(message.author) == "UltiMon#6131":
        if report_me := next(filter(lambda boss: boss in message.content, BOSSES), None):
            await message.channel.send(boss.update("main", BOSSES[report_me], 0))
        elif report_me := next(filter(lambda boss: boss in message.content, MINI_BOSSES), None):
            await message.channel.send(boss.update("mini", MINI_BOSSES[report_me], 0))

    message.content = message.content.lower()
    # !status
    if message.content.startswith("!status"):
        if "detailed" in message.content:
            await message.channel.send(boss.status_detailed())
        else:
            await post_img(message, img=boss.status_plot())

    # !calc
    if message.content.startswith("!calc"):
        try:
            h, m = message.content[6:].split(":")
        except:
            return await message.channel.send("Usage: e.g. `!calc 5:33`")
        mins = int(h)*60 + int(m)
        await message.channel.send(f"{h}:{m} equal to {mins} minutes")

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

    elif message.content.startswith("!start"):
        await scheduled_report()


def run_bot(token: str) -> None:
    client.run(token)
