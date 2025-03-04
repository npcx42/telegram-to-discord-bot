# TeleRelayBot  

### ⚠️ First update in a long time!  

## 📌 Description  
This bot automatically forwards messages from a Telegram channel to your Discord server.  

## 🔧 Installation  

### ❗ Requirements:  
✅ **Your Telegram channel must be public**  

### 1️⃣ Install Python and dependencies  
- The bot works with **Python 3.10 and later**. You can download it [here](https://www.python.org/downloads/).  
- **Check "Add to PATH"** during installation, or the script won’t work.  
- **Restart your computer** after installation (recommended).  

### 2️⃣ Install dependencies  
Open a terminal in the script’s folder and run:  
```sh
pip install -r requirements.txt
```  

### 3️⃣ Configure the bot  
Open `config.json` and enter your details:  
```json
{
  "TOKEN_BOT": "Your_Bot_Token",
  "CHANNEL_URL": "https://t.me/s/yourchannel",
  "DISCORD_CHANNEL_ID": "Your_Discord_Channel_ID",
  "DISCORD_BOT_ID": "Your_Discord_Bot_ID"
  "discord_debug_access_uid": ["your id", "your friend id"]

}
```  
Now you can start the script and enjoy! 🚀  

## ❓ Support  
If the bot isn’t working, create an issue on GitHub: [click here](https://github.com/npcx42/telegram-to-discord-bot/issues/new).  
~~Discord support is temporarily unavailable.~~