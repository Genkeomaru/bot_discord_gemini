# 🤖 Bot de Discord com Google Gemini API

Este é um bot conversacional para Discord construído em Python, integrado com a API oficial do Google Gemini (modelo `gemini-2.5-flash`). Ele atua como um assistente amigável e moderador conversacional para o servidor.

## 🚀 Tecnologias Utilizadas
* **Python 3.x**
* **discord.py:** Integração com a API do Discord.
* **google-genai:** SDK oficial e atualizado do Google para comunicação com a IA.
* **Flask:** Mini-servidor web para manter a aplicação viva (keep-alive) em hospedagens PaaS.
* **Render & UptimeRobot:** Infraestrutura de hospedagem e monitoramento contínuo.

## ⚙️ Funcionalidades
* **Memória de Contexto:** O bot lê o histórico recente do canal para entender o contexto antes de responder.
* **Personalidade Customizável:** Utiliza *System Instructions* do Gemini para manter o tom de voz amigável, sincero e focado em moderação.
* **Fatiador de Mensagens:** Previne travamentos causados pelo limite de 2000 caracteres do Discord, dividindo respostas longas automaticamente.
* **Keep-Alive:** Rota web nativa para evitar que o contêiner entre em modo *sleep* na hospedagem gratuita.

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