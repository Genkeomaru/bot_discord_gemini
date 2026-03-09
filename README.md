# 🤖 Bot de Discord com Google Gemini API

Este é um bot conversacional para Discord construído em Python, integrado com a API oficial do Google Gemini (modelo `gemini-2.5-flash`). Ele atua como um assistente amigável e moderador conversacional para o servidor.

## 🚀 Tecnologias Utilizadas
* **Python 3.x**
* **discord.py:** Integração com a API do Discord.
* **google-genai:** SDK oficial e atualizado do Google para comunicação com a IA.
* **Docker:** Para facilitar a hospedagem em qualquer ambiente (como VPS via GitHub Student Pack).

## ⚙️ Funcionalidades
* **Memória de Contexto:** O bot lê o histórico recente do canal para entender o contexto antes de responder.
* **Personalidade Customizável:** Utiliza *System Instructions* do Gemini para manter o tom de voz amigável, sincero e focado em moderação.
* **Fatiador de Mensagens:** Previne travamentos causados pelo limite de 2000 caracteres do Discord, dividindo respostas longas automaticamente.

## 🔒 Segurança (IMPORTANTE)
As chaves de API (`DISCORD_BOT_TOKEN` e `GEMINI_API_KEY`) **nunca** devem ser comitadas neste repositório. 
Ao rodar localmente, crie um arquivo `.env` na raiz do projeto contendo as chaves. O arquivo `.env` já está declarado no `.gitignore` para sua segurança.

## 🛠️ Como rodar localmente

1. Clone o repositório:
   ```bash
   git clone [https://github.com/Genkeomaru/bot_discord_gemini.git](https://github.com/Genkeomaru/bot_discord_gemini.git)

2. Crie e ative um ambiente virtual:
    ```Bash
    python -m venv .venv
    .\.venv\Scripts\activate

3. Instale as dependências:
    ```Bash
    pip install -r requirements.txt

4. Execute a aplicação:
    ```Bash
    python main.py
    ```

## 🐳 Como rodar com Docker (Recomendado para VPS)

Se você tem uma VPS (como as fornecidas pelo GitHub Student Pack na DigitalOcean, Azure, AWS, etc.), usar o Docker é a maneira mais fácil de manter seu bot rodando 24/7.

1. Clone o repositório na sua VPS:
   ```bash
   git clone https://github.com/Genkeomaru/bot_discord_gemini.git
   cd bot_discord_gemini
   ```

2. Crie o arquivo `.env` com suas chaves:
   ```bash
   nano .env
   # Adicione suas chaves: DISCORD_BOT_TOKEN=... e GEMINI_API_KEY=...
   ```

3. Construa a imagem Docker:
   ```bash
   docker build -t bot-discord-gemini .
   ```

4. Rode o container em segundo plano:
   ```bash
   docker run -d --name bot-gemini --env-file .env --restart unless-stopped bot-discord-gemini
   ```

O bot ficará rodando. Se o servidor reiniciar, o bot voltará automaticamente (`--restart unless-stopped`). Para ver os logs, basta digitar `docker logs -f bot-gemini`.