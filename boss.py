import atexit
import json
import logging

from matplotlib import pyplot as plt
from datetime import datetime, timedelta
from io import BytesIO
from typing import Dict, List

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
JSON_FILENAME = "bosses.json"


class Boss:
    def __init__(self):
        logger.info(f"Initializing bosses")
        atexit.register(self.save)
        with open(JSON_FILENAME, "r") as f:
            self.bosses = json.load(f)
        self.mini = self.bosses["mini"]
        self.main = self.bosses["main"]

    def save(self) -> None:
        logger.info(f"Saving bosses.json")
        with open(JSON_FILENAME, "w") as f:
            json.dump(self.bosses, f)

    def update(self, boss_type: str, dungeon: str, time: int) -> str:
        boss_type = boss_type.lower()
        dungeon = dungeon.title()

        if not boss_type in ["mini", "main"]:
            return "Unknown boss type, please use `mini` or `main` (case insensitive!)"

        if boss_type == "mini":
            bosses = self.mini
        else:
            bosses = self.main

        if dungeon not in bosses:
            return "Unknown dungeon, please use same name as in `!status` (case insensitive!)"

        if time == 0:
            reported = datetime.now()
        else:
            hour, minute = divmod(time, 60)
            reported = datetime.now() - timedelta(hours=hour, minutes=minute)
        print(f"Reported: {boss_type} {dungeon} died at {reported}")
        previous = datetime.fromtimestamp(bosses[dungeon])
        bosses[dungeon] = int(reported.timestamp())

        return f"Updated {boss_type} {dungeon} last killed at {reported}. Previous date was {previous}"

    def get_plot(self) -> BytesIO:
        mini_frame, mini_colors = self.get_plot_mini()
        mini_x = list(mini_frame.keys())
        mini_y = list(mini_frame.values())

        main_frame, main_colors = self.get_plot_main()
        main_x = list(main_frame.keys())
        main_y = list(main_frame.values())

        f, axarr = plt.subplots(2, sharex=True)
        axarr[0].barh(mini_x, mini_y, color=mini_colors)
        axarr[1].barh(main_x, main_y, color=main_colors)
        axarr[0].set_title("MINI"); axarr[1].set_title("MAIN")
        axarr[0].grid(); axarr[1].grid()
        axarr[0].set_xlim(0, 100); axarr[1].set_xlim(0, 100)
        axarr[0].invert_yaxis(); axarr[1].invert_yaxis()
        f.set_canvas(plt.gcf().canvas)
        buffer = BytesIO()
        f.savefig(buffer)
        plt.close("all")
        buffer.seek(0)
        return buffer

    def get_plot_mini(self) -> BytesIO:
        now = datetime.now()
        calculated_frame = {}
        colors = []
        for dungeon, last_time in self.mini.items():
            hours = (now - datetime.fromtimestamp(last_time)).total_seconds() / 3600
            hours = int(round(hours, 2)) - 12
            print(f"Mini|{dungeon}Diffhours: {hours}  saved: {datetime.fromtimestamp(last_time)}  now: {now}")
            if hours < 3:
                colors.append("green")
            elif hours < 6:
                colors.append("yellow")
            elif hours < 9:
                colors.append("orange")
            else:
                colors.append("red")

            calculated_frame[dungeon] = (hours / 12) * 100

        return calculated_frame, colors

    def get_plot_main(self) -> BytesIO:
        now = datetime.now()
        calculated_frame = {}
        colors = []
        for dungeon, last_time in self.main.items():
            hours = (now - datetime.fromtimestamp(last_time)).total_seconds() / 3600
            hours = int(round(hours, 2)) - 72
            print(f"Main|{dungeon} Diffhours: {hours}  saved: {datetime.fromtimestamp(last_time)}  now: {now}")
            if hours < 12:
                colors.append("green")
            elif hours < 24:
                colors.append("yellow")
            elif hours < 36:
                colors.append("orange")
            else:
                colors.append("red")

            calculated_frame[dungeon] = (hours / 48) * 100

        return calculated_frame, colors


boss = Boss()
