from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from PIL import Image, ImageDraw, ImageFont
import random
import os
import re
from io import BytesIO

image_paths = [
    "1.jpg",
    "2.jpg",
    "3.jpg",
    "4.jpg",
    "5.jpg",
]
font_path = "Roboto-Black.ttf"
instagram_pattern = re.compile(r'https://(?:www\.)?instagram\.com/[^ ]+')

def wrap_text(text, font, max_width):
    lines = []
    words = text.split(" ")

    current_line = words[0]

    for word in words[1:]:
        test_line = f"{current_line} {word}"
        text_width, _ = ImageDraw.Draw(Image.new("RGB", (max_width, 0))).textbbox((0, 0), test_line, font=font)[2:4]
        if text_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

async def handle_message(update: Update, context: CallbackContext):
    message_text = update.message.text

    matches = instagram_pattern.findall(message_text)
    for match in matches:
        new_link = match.replace("https://www.instagram.com", "https://www.ddinstagram.com")
        user_mention = f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.full_name}</a>'
        await update.message.reply_text(
            f"Ссылка изменена: {new_link}\n\n"
            f"Отправлено пользователем: {user_mention}",
            parse_mode='HTML'
        )
        await update.message.delete()

    if update.message.reply_to_message and 'цитата' in message_text.lower():
        forwarded_text = update.message.reply_to_message.text

        image_path = random.choice(image_paths)
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)

        def get_position_for_image(image_name):
            # Словарь с настройками для разных изображений
            positions = {
                '1.jpg': {'x': 50, 'y': 50, 'color': 'black', 'size': 30, 'c': '© Стетхем'},
                '2.jpg': {'x': 150, 'y': 200, 'color': 'white', 'size': 60, 'c': '© Дон Корлеоне'},
                '3.jpg': {'x': 850, 'y': 150, 'color': 'white', 'size': 60, 'c': '© Саруман Белый'},
                '4.jpg': {'x': 465, 'y': 80, 'color': 'white', 'size': 35, 'c': '© Конфуцций'},
                '5.jpg': {'x': 30, 'y': 30, 'color': 'white', 'size': 28, 'c': '© Джордж Карлин'},
            }
            return positions.get(image_name, {'x': 20, 'y': 20, 'color': 'white', 'size': 35})

        position = get_position_for_image(image_path)

        x_position = position['x']
        y_position = position['y']

        try:
            font = ImageFont.truetype(font_path, size=position['size'])
        except IOError:
            font = ImageFont.load_default()
        image_width, image_height = image.size
        max_width = int((image_width / 2) - 40)
        lines = wrap_text(forwarded_text, font, max_width)
        total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] for line in lines)
        y_position2 = int((image_height - total_text_height) / 2)
        for line in lines:
            text_width, text_height = draw.textbbox((0, 0), line, font=font)[2:4]
            draw.text((x_position, y_position2), line, font=font, fill=position['color'])
            y_position2 += text_height

        y_position2 += text_height
        draw.text((x_position, y_position2), position['c'], font=font, fill=position['color'])
        byte_io = BytesIO()
        image.save(byte_io, format="JPEG")
        byte_io.seek(0)

        await update.message.reply_photo(photo=byte_io)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет! Я бот, который изменяет ссылки на Instagram. Просто отправь ссылку на Instagram, и я добавлю префикс 'dd'. Также, если ты хочешь создать цитату, напиши 'цитата' в ответ на цитируемое сообщение.")

def main():
    token = ""
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
