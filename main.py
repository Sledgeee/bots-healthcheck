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


def heartbeat(bot: TeleBot, name: str):
    last_message = db.get(name)
    if last_message:
        bot.delete_message(HEARTBEAT_CHAT_ID, last_message["last_message_id"])

    msg = bot.send_message(HEARTBEAT_CHAT_ID, "tick")
    status = "Online" if msg.message_id else "Offline"
    db.put({
        "status": status,
        "last_message_id": msg.message_id,
        "last_update": int(datetime.now(tz=timezone("Europe/Kiev")).timestamp())
    }, name)


@app.get("/")
async def root():
    return "OK"


@app.lib.run()
@app.lib.cron()
def start_cron(event):
    heartbeat(helper_bot, "helper")
    heartbeat(admin_bot, "admin")
