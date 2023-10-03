from dotenv import load_dotenv
load_dotenv()

import os
import logging
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
import openai
import json
import db

openai.api_key = os.getenv("OPENAI_API_KEY")

chat_system_prompt = { "role": "system", "content": """You are my family's sassy and sarcastic assistant
"""}

summary_prompt = { "role": "user", "content": "Please sumamrize the chat to date" }

chats: db.Chat = None
bots: db.Bot = None

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def debug(str):
    if 'DEV' in os.environ:
        print(str)

def summarise(id, items):
    logging.info("Summarising %d messages in chat id {}".format(len(items), id))

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=items + [summary_prompt],
        temperature=0.5,
        max_tokens=256
    )

    message = response["choices"][0]["message"]
    debug(message)
    return message["content"]

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        chat_system_prompt["content"] = " ".join(context.args)
        chats.update_or_create(update.message.id, [])
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Bot reset with new role")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="usage: /reset new role")

async def role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=chat_system_prompt["content"])

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = chats.get(update.message.id) or []
    session.append({"role": "user", "content": update.message.text})

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[chat_system_prompt] + session,
        temperature=0.5,
        max_tokens=256
    )

    message = response["choices"][0]["message"]

    debug(message)
    session.append(message)

    if (len(session) > 20):
        session = [summarise(update.message.id, session[0:10])] + session[11:]
    chats.update_or_create(update.message.id, session)

    if "content" in message and message["content"] == "I'm sorry, but I can't assist with that.":
        logging.error("Wtf? Why can't the agent help?")
        pass
    if "content" in message and message['content']:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message["content"])
    if "function_call" in message:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=json.dumps(message["function_call"], indent=2))

if __name__ == '__main__':
    # model setup
    conn = db.connect_db(os.environ['DATABASE_URL'])
    chats = db.Chat(conn)
    bot = db.Bot(conn)
    
    # TODO: Pull this from bot. Need to iterate over every bot, to create a handler per bot
    application = ApplicationBuilder().token(os.environ['TELEGRAM_BOT_API_KEY']).build()
    application.bot_data
    
    role_handler = CommandHandler('role', role)
    application.add_handler(role_handler)

    reset_handler = CommandHandler('reset', reset)
    application.add_handler(reset_handler)

    chat_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), chat)
    application.add_handler(chat_handler)

    application.run_polling()
