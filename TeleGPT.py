from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

print('Starting TeleGPT')

TOKEN: Final = os.environ.get('TOKEN')
BOT_USERNAME: Final = os.environ.get('BOT')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello there!')

def handle_response(text: str) -> str:
    # Response logic
    processed: str = text.lower()
    prompt=os.environ.get('DETAIL')+processed

    if 'hello' in processed:
        return 'Hey there!'
    
    #Responses by chatGPT
    url = os.environ.get('URL')
    payload = {
	"model": "gpt-3.5-turbo",
	"messages": [
		{
			"role": os.environ.get('UID'),
			"content": prompt
		}
	]
    }
    headers = {
	"content-type": "application/json",
	os.environ.get('API-KEY'):os.environ.get('KEY'),
	os.environ.get('API-HOST'):os.environ.get('HOST')
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    response_dict = json.loads(response.text)
    content = response_dict["choices"][0]["message"]["content"]
    print(content)
    return content


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Basic info of the incoming message
    message_type: str = update.message.chat.type
    text: str = update.message.text

    # Print a log for debugging
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    # React to group messages only if users mention the bot directly
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    # Reply normal if the message is in private
    print('Bot:', response)
    await update.message.reply_text(response)


# Log errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


# Run the program
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    # Commands
    app.add_handler(CommandHandler('start', start_command))
    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    # Log all errors
    app.add_error_handler(error)
    print('Polling...')
    # Run the bot
    app.run_polling(poll_interval=5)