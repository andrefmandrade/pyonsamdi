import atexit
import json
import logging
from datetime import datetime, timedelta
from io import BytesIO
from typing import Dict, List, Tuple

from matplotlib import pyplot as plt

from settings import DEBUG

logger = logging.getLogger(__name__)
JSON_FILENAME = "bosses.json"

MINI_CLOSED_WINDOW = 12
MINI_OPEN_WINDOW = 12
MAIN_CLOSED_WINDOW = 24
MAIN_OPEN_WINDOW = 24

BOSSES = {
    "Aegis High Priestess": "Aegis",
    "Behemoth Basilisk": "Cavernam",
    "Emperor Dragon": "Nusero",
    "The Forgotten King": "Ossuary",
    "Gatekeeper": "Mausoleum",
    "Great Sunken Serpent": "Pulma",
    "Infernus": "Inferno",
    "Lord Bile": "Darkmire",
    "Terathan Goliath": "Petram",
    "Gargoyle Primogen": "Cathedral",
}

MINI_BOSSES = {
    "Sanguineous": "Aegis",
    "Great Abyssal Hornbeast": "Cavernam",
    "Pit Dragon": "Nusero",
    "Speaker For The Dead": "Ossuary",
    "Cistern Gorgon": "Mausoleum",
    "Ancient Drowned Dragon": "Pulma",
    "Heart Of The Mountain": "Inferno",
    "The Terrorwood": "Darkmire",
    "Lodestone": "Petram",
    "Gargoyle Archon": "Cathedral",
}


class Boss:
    def __init__(self):
        logger.info("Initializing bosses")
        atexit.register(self.save)
        with open(JSON_FILENAME, "r") as f:
            self.bosses = json.load(f)
        self.mini = self.bosses["mini"]
        self.main = self.bosses["main"]

    def save(self) -> None:
        if not DEBUG:
            logger.info("Saving bosses.json")
            with open(JSON_FILENAME, "w") as f:
                json.dump(self.bosses, f)
        else:
            logger.info("Dry-run saving bosses.json")

    def update(self, boss_type: str, dungeon: str, time: int) -> str:
        boss_type = boss_type.lower()
        dungeon = dungeon.title()

        if boss_type not in ["mini", "main"]:
            return "Unknown boss type, please use `mini` or `main` (case insensitive!)"

        bosses = self.mini if boss_type == "mini" else self.main

        if dungeon not in bosses:
            return "Unknown dungeon, please use same name as in `!status` (case insensitive!)"

        if time == 0:
            reported = datetime.now()
        else:
            hour, minute = divmod(time, 60)
            reported = datetime.now() - timedelta(hours=hour, minutes=minute)
        logger.info(f"Reported: {boss_type} {dungeon} died at {reported}")
        previous = datetime.fromtimestamp(bosses[dungeon])
        bosses[dungeon] = int(reported.timestamp())

        self.save()
        return f"Updated {boss_type} {dungeon} last killed at {reported}. Previous date was {previous}"

    def get_xy_and_colors(self, dungeon_times: Dict, closed_window: int, open_window: int) -> Tuple[Dict, List]:
        xy = {}
        colors = []
        now = datetime.now()

        for dungeon, last_time in dungeon_times.items():
            hours = (now - datetime.fromtimestamp(last_time)).total_seconds() / 3600
            hours = int(round(hours, 2)) - closed_window
            xy[dungeon] = (hours / open_window) * 100
            logger.info(f"Diffhours: {hours} [{xy[dungeon]}%] saved: {datetime.fromtimestamp(last_time)}  now: {now}")

            if xy[dungeon] < 25:
                colors.append("green")
            elif xy[dungeon] < 50:
                colors.append("yellow")
            elif xy[dungeon] < 75:
                colors.append("orange")
            elif xy[dungeon] < 100:
                colors.append("red")
            else:
                colors.append("grey")

        return xy, colors

    def status_plot(self) -> BytesIO:
        logger.info("Fetching mini bosses")
        mini_frame, mini_colors = self.get_xy_and_colors(self.mini, MINI_CLOSED_WINDOW, MINI_OPEN_WINDOW)
        mini_x = list(mini_frame.keys())
        mini_y = list(mini_frame.values())

        logger.info("Fetchin main bosses")
        main_frame, main_colors = self.get_xy_and_colors(self.main, MAIN_CLOSED_WINDOW, MAIN_OPEN_WINDOW)
        main_x = list(main_frame.keys())
        main_y = list(main_frame.values())

        f, axarr = plt.subplots(2, sharex=True)
        axarr[0].barh(mini_x, mini_y, color=mini_colors)
        axarr[1].barh(main_x, main_y, color=main_colors)
        axarr[0].set_title("MINI")
        axarr[1].set_title("MAIN")
        axarr[0].grid()
        axarr[1].grid()
        axarr[0].set_xlim(0, 100)
        axarr[1].set_xlim(0, 100)
        axarr[0].invert_yaxis()
        axarr[1].invert_yaxis()
        f.set_canvas(plt.gcf().canvas)
        buffer = BytesIO()
        f.savefig(buffer)
        plt.close("all")
        buffer.seek(0)
        return buffer

    def status_detailed(self) -> str:
        now = datetime.now()
        msg = "```apache\n. LAST REPORTS\n"
        for dungeon, time in self.mini.items():
            time = datetime.fromtimestamp(time)
            delta = int((now - time).total_seconds() // 60)
            hour, minute = divmod(delta, 60)
            msg += f"Mini {dungeon} - {time.strftime('%d %b %H:%M')} - {hour}h{minute}min ago\n"
        for dungeon, time in self.main.items():
            time = datetime.fromtimestamp(time)
            delta = int((now - time).total_seconds() // 60)
            hour, minute = divmod(delta, 60)
            msg += f"\nMain {dungeon} - {time.strftime('%d %b %H:%M')} - {hour}h{minute}min ago\n"
        return msg + '\n```'


boss = Boss()
