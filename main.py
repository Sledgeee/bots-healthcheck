import os
from pytz import timezone
from datetime import datetime
from fastapi import FastAPI
from deta import App, Deta
from telebot import TeleBot

app = App(FastAPI())
helper_bot = TeleBot(os.getenv("HELPER_BOT_TOKEN"))
admin_bot = TeleBot(os.getenv("ADMIN_BOT_TOKEN"))
HEARTBEAT_CHAT_ID = os.getenv("HEARTBEAT_CHAT_ID")
deta = Deta()
db = deta.Base("health")


def check_status(bot: TeleBot):
    msg = bot.send_message(HEARTBEAT_CHAT_ID, "tick")
    return "Online" if msg.message_id else "Offline"


def heartbeat(bot: TeleBot, name: str):
    status = check_status(bot)
    db.put({"status": status, "last_update": int(datetime.now(tz=timezone("Europe/Kiev")).timestamp())}, name)


@app.get("/")
async def root():
    return "OK"


@app.lib.run()
@app.lib.cron()
def start_cron(event):
    heartbeat(helper_bot, "helper")
    heartbeat(admin_bot, "admin")
