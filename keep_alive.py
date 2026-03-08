from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot está vivo e operando!"

def run():
    # O Render injeta automaticamente a porta na variável de ambiente PORT
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()