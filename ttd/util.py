import aiocron
import requests
from bs4 import BeautifulSoup

from discord.ext import commands

last_message = None

class cronjobs():
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        def get_latest_message(channel_url):
            global last_message
            page = requests.get(channel_url)
            soup = BeautifulSoup(page.content, 'html.parser')
            messages = soup.find_all('div', class_='tgme_widget_message_text')
            new_messages = []

            for message in reversed(messages):
                text = message.text
                if text == last_message:
                    break
                new_messages.append(text)

            if new_messages:
                last_message = new_messages[-1]

            return new_messages
        # * * * * * */20 - 20 seconds ||| 0 */1 * * * - 1 hour
        @aiocron.crontab('0 */1 * * *')
        async def get_channel_post():
            new_message = get_latest_message(CHANNEL_URL)
            message_data = new_message[0]
            await bot.get_channel(DISCORD_CHANNEL_ID).send(f'{message_data}')
            print(f'Sended post from \'{CHANNEL_URL}\' with content: {message_data}')