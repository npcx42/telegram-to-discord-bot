from discord.ext import commands
from discord import Intents
from bs4 import BeautifulSoup
import aiocron
import discord
import requests
import configparser

configure_get = configparser.ConfigParser()
configure_get.read('config.ini', encoding = 'utf-8')
settings = configure_get['BOT_SETTINGS']

TOKEN_BOT = settings['token_bot']
CHANNEL_URL = settings['channel_url']
DISCORD_CHANNEL_ID = int(settings['discord_channel_id'])
DISCORD_BOT_ID = int(settings['discord_bot_id'])
DISCORD_THREAD_NAME = settings['discord_thread_name']
DISCORD_DEBUG_ACCESS = settings['discord_debug_access_uid'].split(',')

print(DISCORD_DEBUG_ACCESS)

class cronjobs():
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        # * * * * * */20 - 20 seconds
        # 0 */1 * * * - 1 hour
        @aiocron.crontab('0 */1 * * *')
        async def get_channel_post():
            new_message = get_latest_message(CHANNEL_URL)
            await bot.get_channel(DISCORD_CHANNEL_ID).send(f'{new_message[0]}')
            print(f'Sended post from \'{CHANNEL_URL}\' with content: {new_message[0]}')

class tgToDiscord(commands.Bot):
    def __init__(self, intents):
        super().__init__(
            command_prefix = '!',
            intents = intents
        )

    async def setup_hook(self):
        cron = cronjobs(self)

    async def close(self):
        await super().close()

intents = Intents.all()
bot = tgToDiscord(intents)
intents.members = True
intents.messages = True
intents.message_content = True

last_message = None

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

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

@bot.event
async def on_message(ctx: discord.Message):
    channelId = ctx.channel.id
    userId = ctx.author.id
    bot = ctx.author.bot

    # Тут просто, скрипт проверяет условие того, является ли сообщение от бота или нет.
    if bot and userId == DISCORD_BOT_ID:
        if channelId == DISCORD_CHANNEL_ID:
            await ctx.create_thread(
                name = DISCORD_THREAD_NAME,
                reason = "Allowing to comment in this message"
            )
    else:
        if channelId == DISCORD_CHANNEL_ID:
            await ctx.delete()
        else:
            pass

    # По непонятной причине, @bot.command() вообще не работает, хотя я ставил intents.message_content = True :/
    if ctx.content.startswith('!debug'):
        latest_message = get_latest_message(CHANNEL_URL)
        await ctx.channel.send(f'If you see this message, it means that the bot is alive\nLatest message from Telegram channel (<{CHANNEL_URL}>): {latest_message[0]}\nCurrent channed id: {DISCORD_CHANNEL_ID}')

    elif ctx.content.startswith('!getmsg'):
        target = ctx.author
        if str(target.id) in DISCORD_DEBUG_ACCESS:
            latest_message = get_latest_message(CHANNEL_URL)
            await ctx.channel.send(f'{latest_message[0]}')

bot.run(TOKEN_BOT)