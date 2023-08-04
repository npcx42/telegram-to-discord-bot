import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import requests
import asyncio

bot_token = 'put your token here'
channel_url = 'your tg channel url'
discord_channel_id = channel id
discord_bot_id = your bot id

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
intents.members = True
intents.messages = True

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

async def check_channel():
    while True:
        channel = bot.get_channel(discord_channel_id)
        message = get_latest_message(channel_url)
        await channel.send(message[0])
        await asyncio.sleep(3600)

@bot.command(name='check')
async def _check(ctx):
    latest_message = get_latest_message(channel_url)
    await ctx.send(f'Latest message from Telegram channel: {latest_message[0]}')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    bot.loop.create_task(check_channel())

@bot.event
async def on_message(ctx: discord.Message):
    channelId = ctx.channel.id
    userId = ctx.author.id
    bot = ctx.author.bot

    # Тут просто, скрипт проверяет условие того, является ли сообщение от бота или нет.
    if bot and userId == discord_bot_id:
        if channelId == discord_channel_id:
            await ctx.create_thread(
                name = "Комментарий",
                reason = "Allowing to comment in this message"
            )
    else:
        if channelId == discord_channel_id:
            await ctx.delete()

bot.run(bot_token)