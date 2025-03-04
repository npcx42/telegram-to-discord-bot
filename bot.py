import json
import requests
from bs4 import BeautifulSoup
import aiocron
import discord
from discord.ext import commands
from discord import app_commands

# Загрузка конфигурации из JSON файла
with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

TOKEN_BOT = config["token_bot"]
CHANNEL_URL = config["channel_url"]
DISCORD_BOT_ID = int(config["discord_bot_id"])
DISCORD_CHANNEL_ID = int(config["discord_channel_id"])
DISCORD_THREAD_NAME = config["discord_thread_name"]
DISCORD_DEBUG_ACCESS = config["discord_debug_access_uid"]  # список id в виде строк

class MyBot(commands.Bot):
    def __init__(self, command_prefix: str, intents: discord.Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.last_message = None  # Память для последнего отправленного поста

    async def setup_hook(self):
        # Регистрируем slash-команды в дереве команд
        self.tree.add_command(debug_command)
        self.tree.add_command(getmsg_command)
        await self.tree.sync()
        self.start_channel_check()

    def fetch_latest_message(self, channel_url: str) -> str or None:
        """Запрашивает страницу канала и возвращает новый пост (если он отличается от предыдущего)."""
        try:
            response = requests.get(channel_url)
            response.raise_for_status()
        except Exception as e:
            print(f"Ошибка запроса: {e}")
            return None

        soup = BeautifulSoup(response.content, "html.parser")
        messages = soup.find_all("div", class_="tgme_widget_message_text")
        if not messages:
            return None

        new_text = messages[-1].get_text(strip=True)
        if new_text == self.last_message:
            return None

        self.last_message = new_text
        return new_text

    def start_channel_check(self):        # Планировщик, запускаемый по расписанию каждые 5 минут
        @aiocron.crontab("*/5 * * * *")
        async def scheduled_check():
            new_text = self.fetch_latest_message(CHANNEL_URL)
            if new_text:
                channel = self.get_channel(DISCORD_CHANNEL_ID)
                if channel:
                    try:
                        await channel.send(new_text)
                        print(f"Отправлено новое сообщение с {CHANNEL_URL}: {new_text}")
                    except Exception as e:
                        print(f"Ошибка при отправке сообщения: {e}")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_message(self, message: discord.Message):
        channelId = message.channel.id
        userId = message.author.id
        bot = message.author.bot

        # Проверка, является ли сообщение от бота
        if bot and userId == DISCORD_BOT_ID:
            if channelId == DISCORD_CHANNEL_ID:
                await message.create_thread(
                    name=DISCORD_THREAD_NAME,
                    reason="Разрешение на комментарии под сообщением"
                )
        else:
            if channelId == DISCORD_CHANNEL_ID:
                await message.delete()

# Инициализация бота
intents = discord.Intents.all()
bot = MyBot(command_prefix="!", intents=intents)

# Slash-команды

@app_commands.command(name="debug", description="Проверить работу бота и получить последнее сообщение из Telegram")
async def debug_command(interaction: discord.Interaction):
    if str(interaction.user.id) not in DISCORD_DEBUG_ACCESS:
        await interaction.response.send_message("У вас нет прав для выполнения этой команды.", ephemeral=True)
        return
    new_text = bot.fetch_latest_message(CHANNEL_URL)
    if new_text:
        response_msg = (
            f"Бот работает.\nПоследнее сообщение из Telegram:\n{new_text}\n"
            f"ID канала Discord: {DISCORD_CHANNEL_ID}"
        )
        await interaction.response.send_message(response_msg)
    else:
        await interaction.response.send_message("Новых сообщений не найдено.", ephemeral=True)

@app_commands.command(name="getmsg", description="Получить последнее сообщение из Telegram")
async def getmsg_command(interaction: discord.Interaction):
    if str(interaction.user.id) not in DISCORD_DEBUG_ACCESS:
        await interaction.response.send_message("У вас нет прав для выполнения этой команды.", ephemeral=True)
        return
    new_text = bot.fetch_latest_message(CHANNEL_URL)
    if new_text:
        await interaction.response.send_message(new_text)
    else:
        await interaction.response.send_message("Новых сообщений не найдено.", ephemeral=True)

bot.run(TOKEN_BOT)