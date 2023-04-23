import os
import openai
import telebot
from telebot.types import Message, BotCommand, InputMediaPhoto
from PIL import Image
import io


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


# Handler function to edit an image
@bot.message_handler(commands=['edit_image'])
def edit_image_handler(message: Message):
    prompt = message.text
    prompt = prompt.replace('/edit_image', '')
    prompt = prompt.strip()

    bot.reply_to(message, "Please upload an image to edit.")
    bot.register_next_step_handler(message, process_image, prompt)


# Function to process the uploaded image and apply filters to it
def process_image(message: Message, prompt: str):
    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        jpg_img = Image.open(io.BytesIO(downloaded_file))
        img_size = jpg_img.size
        rgba_img = jpg_img.convert('RGBA')
        png_io = io.BytesIO()
        rgba_img.save(png_io, format='PNG')
        png_bytes = png_io.getvalue()

        transparent_img = Image.new('RGBA', img_size, (0, 0, 0, 0))
        transparent_png_io = io.BytesIO()
        transparent_img.save(transparent_png_io, format='PNG')
        transparent_png_bytes = transparent_png_io.getvalue()

        print(prompt)
        response = openai.Image.create_edit(
                image=png_bytes,
                mask=transparent_png_bytes,
                prompt=prompt,
                n=1,
                size='{}x{}'.format(img_size[0], img_size[1])
            )
        filtered_image_url = response['data'][0]['url']
        bot.send_photo(message.chat.id, filtered_image_url)
    except:
        bot.reply_to(message, "Sorry, something went wrong. Please try again.")


def main():
    command_list = []
    command_list.append(BotCommand('/start', 'Displays a welcome message.'))
    command_list.append(BotCommand('/generate_image', 'Generates an image based on the prompt you provide. For example, "/generate_image red apple".'))
    command_list.append(BotCommand('/edit_image', 'Upload an image and apply filters to it.'))

    # Set bot commands
    bot.set_my_commands(command_list)

    # Run the bot
    bot.polling()


if __name__ == '__main__':
    main()