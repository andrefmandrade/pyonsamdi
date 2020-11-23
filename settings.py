import dotenv
import os

dotenv.load_dotenv()

DEBUG = True if os.getenv("DEBUG") else False

ADMINS = os.getenv("ADMINS", "").split(",")
DISCORD_TOKEN = os.getenv("DEBUG_TOKEN", "") if DEBUG else os.getenv("DISCORD_TOKEN", "")
