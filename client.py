import discord
import sqlite3
import dotenv
import os
from datetime import datetime

dotenv.load_dotenv()

client = discord.Client()
db_name = "bot_data.db"
bot_prefix = "!"


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS commands (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        author TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at DATETIME NOT NULL 
    )
    """)

    conn.commit()
    conn.close()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!input"):
        conn = sqlite3.connect(db_name)
        c = conn.cursor()

        message_content = message.content.replace(f"{bot_prefix}input", "").strip()
        message_author = str(message.author)

        c.execute("""
        INSERT INTO commands VALUES (NULL,:author,:message,:created_at)
        """, {'author': message_author, 'message': message_content,
              'created_at': datetime.now().strftime("%d-%m-%Y %H:%M:%S")})

        conn.commit()
        conn.close()

        if c.lastrowid > 0:
            await message.channel.send(f"message: ({message_content}) stored!")


client.run(os.getenv("DISCORD_TOKEN"))
