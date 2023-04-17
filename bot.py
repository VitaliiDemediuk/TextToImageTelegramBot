import os
import openai
import telebot
from telebot.types import Message, BotCommand


# Set up OpenAI API key
openai.api_key = os.environ.get('OPENAI_API_KEY')


# Initialize Telegram bot
bot = telebot.TeleBot(os.environ.get('TELEGRAM_BOT_TOKEN'))


# Function to generate image using OpenAI's DALL-E API
def generate_image(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return response['data'][0]['url']


# Handler function to generate image in response to a message
@bot.message_handler(commands=['generate_image'])
def generate_image_handler(message: Message):
    prompt = message.text
    prompt = prompt.replace('/generate_image', '')
    prompt = prompt.strip()
    print (prompt)
    if prompt:
        image_url = generate_image(prompt)
        bot.send_photo(message.chat.id, image_url)
    else:
        bot.reply_to(message, "Please provide a prompt. For example, '/generate_image red apple'.") 


# Handler function to display welcome message when user starts the bot
@bot.message_handler(commands=['start'])
def welcome_message_handler(message: Message):
    welcome_message = "Hi! I'm an image generation bot powered by OpenAI's DALL-E API. To generate an image, type /generate_image followed by a prompt (e.g. '/generate_image red apple')."
    bot.send_message(message.chat.id, welcome_message)


def main():
    command_list = []
    command_list.append(BotCommand('/start', 'Displays a welcome message.'))
    command_list.append(BotCommand('/generate_image', 'Generates an image based on the prompt you provide. For example, "/generate_image red apple".'))
    bot.set_my_commands(command_list)

    # Run the bot
    bot.polling()


if __name__ == '__main__':
    main()