import discord
import os
import random
from flask import Flask
from threading import Thread
import time

# Flaskのアプリケーションインスタンスを作成
app = Flask(__name__) 

# 【重要】Botの起動状態を追跡するためのグローバル変数
# これを各プロセス（ワーカー）がチェックし、Botの多重起動を防ぎます。
bot_start_attempted = False

# -----------------
# Discord Bot本体の起動関数
# -----------------
def run_discord_bot():
    # ランダムに選択する応答メッセージリスト
    RANDOM_RESPONSES = [
    "「ちょっと待ったぁーーーーー！！！！！！！！！」﻿",
    "「行くぞ、シャローーーー！！」",
    "「特殊部隊に推薦できる腕前だー！」",
    "「これでも食らえー！」﻿",
    "「いつも一緒にいるだけが、友達じゃないだろ？」﻿",
    "「物理部好きだろ？」"
    ]

    TOKEN = os.getenv("DISCORD_TOKEN") 
    intents = discord.Intents.default()
    intents.message_content = True 
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print('---------------------------------')
        print(f'Botがログインしました: {client.user.name}')
        print('---------------------------------')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
            
        # メンションされた場合のみ応答
        if client.user.mentioned_in(message):
            response = random.choice(RANDOM_RESPONSES)
            await message.channel.send(f'{message.author.mention} {response}')
            return # 応答したら必ずここで処理を終了

    if TOKEN:
        try:
            # Botを実行
            client.run(TOKEN)
        except Exception as e:
            print(f"Discord Bot 起動失敗: {e}")
    else:
        print("エラー: Botトークンが設定されていません。")

# -----------------
# Webサーバーのエンドポイント (gunicornがアクセスする場所)
# -----------------
@app.route('/')
def home():
    global bot_start_attempted
    
    # 【重要】Botがまだ起動を試みていない場合のみ処理
    if not bot_start_attempted:
        print("Webアクセスを検知。Discord Botの起動を試みます...")
        
        # フラグを立て、他のプロセス/スレッドが重複起動しないようにする
        bot_start_attempted = True
        
        # Botを別スレッドで起動
        Thread(target=run_discord_bot).start()
        
        # Webサーバーは即座にレスポンスを返す
        return "Discord Bot is initializing..."
        
    # Botが起動済みの場合は、Renderのヘルスチェックに応答
    return "Bot is alive!"
