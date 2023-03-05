import os 
import openai
import discord
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
discord_token = os.getenv("DISCORD_TOKEN_KEY")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

chat_messages = {}

enable_channels = set()

help_message = """$start: 指定したテキストチャンネルの発言にbotが反応するようにする
$stop: 指定したテキストチャンネルの発言にbotが反応しないようにする
$set_settings: ChatGPTに渡す設定を指定する (参考: https://note.com/fladdict/n/neff2e9d52224 )
$reset: ChatGPTに渡す設定、会話ログをリセットする
$help: このヘルプを表示する"""

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith("$help"):
        return await message.channel.send(help_message)
    
    if not message.channel.id in enable_channels:
        if message.content.startswith("$start"):
            enable_channels.add(message.channel.id)
            chat_messages[message.channel.id] = []
            await message.channel.send("started.")
        return

    if message.content.startswith("$stop"):
        enable_channels.discard(message.channel.id)
        chat_messages.pop(message.channel.id, None)
        return await message.channel.send("stopped.")
    
    if message.content.startswith("$reset"):
        chat_messages[message.channel.id].clear()
        return await message.channel.send("reset log.")
    
    if message.content.startswith("$set_settings "):
        chat_messages[message.channel.id].clear()
        system_settings = message.content.replace("$set_settings ", "")
        chat_messages[message.channel.id].append({"role": "system", "content": system_settings})
        return await message.channel.send("set settings.")
    
    chat_messages[message.channel.id].append({"role": "user", "content": message.content})
    
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_messages[message.channel.id],
        max_tokens=1024,
        temperature=0.6
    )
    
    chat_messages[message.channel.id].append({"role": "assistant", "content": res.choices[0].message.content})
    
    await message.channel.send(res.choices[0].message.content)

client.run(discord_token)