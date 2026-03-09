import discord
import os
import logging
from dotenv import load_dotenv
from discord.ext import commands
from google import genai
from google.genai import types

# Configura o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carrega as variáveis de ambiente
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Inicia o cliente da nova biblioteca oficial do Google
client = genai.Client(api_key=GEMINI_API_KEY)

# Configurações do Discord
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

instrucao_base = """
Você é a Inteligência Artificial que atua como assistente, guia e moderador conversacional deste servidor do Discord.

SUAS DIRETRIZES FUNDAMENTAIS:
1. Personalidade: Seja extremamente amigável, acolhedor e prestativo com todos os membros. Aja como um colega de confiança que também ajuda a manter a ordem na casa.
2. Sinceridade Radical: Se alguém perguntar algo que você não sabe ou não tem certeza, seja 100% honesto. Diga diretamente "Eu não sei" ou "Não tenho essa informação". Nunca invente fatos.
3. Papel de Admin: Oriente os usuários sobre a dinâmica do servidor e tire dúvidas gerais. Se perceber discussões acaloradas, intervenha pedindo calma e respeito.
4. Limitações Técnicas: Você NÃO tem capacidade técnica para aplicar punições (como banir, mutar ou apagar mensagens). Se exigirem isso, explique suas limitações.
5. Formatação: Use a formatação nativa do Discord (negrito, itálico, listas e emojis moderados) para deixar a leitura agradável.
"""

async def buscar_historico_canal(canal, bot_id, limit=10):
    messages_list = []
    
    async for message in canal.history(limit=limit, oldest_first=False):
        role = "model" if message.author.id == bot_id else "user"
        conteudo = message.content.replace(f'<@{bot_id}>', '').replace(f'<@!{bot_id}>', '').strip()
        
        if conteudo: 
            # A nova biblioteca exige a montagem exata deste objeto 'Content'
            messages_list.append(
                types.Content(
                    role=role, 
                    parts=[types.Part.from_text(text=conteudo)]
                )
            )
    
    messages_list.reverse()
    return messages_list

@bot.event
async def on_ready():
    logger.info(f"O {bot.user.name} está online, pronto para uso e com a Dívida Técnica paga!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if bot.user not in message.mentions:
        return

    async with message.channel.typing():
        try:
            conteudo_chat = await buscar_historico_canal(message.channel, bot.user.id)
            
            if not conteudo_chat:
                await message.reply("Você me marcou, mas não enviou nenhum texto para eu ler.")
                return

            # A nova forma de chamar a geração de texto
            resposta = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=conteudo_chat,
                config=types.GenerateContentConfig(
                    system_instruction=instrucao_base
                )
            )
            
            texto_resposta = resposta.text
            limite_discord = 1900 # Usamos 1900 como margem de segurança
            
            # Cria uma lista dividindo o texto gigante em pedaços menores
            pedacos = [texto_resposta[i:i+limite_discord] for i in range(0, len(texto_resposta), limite_discord)]
            
            # Envia cada pedaço sequencialmente
            for pedaco in pedacos:
                await message.reply(pedaco)
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem no canal {message.channel.name} (ID: {message.channel.id}): {e}", exc_info=True)
            await message.reply("Desculpe, encontrei um erro interno ao tentar processar sua mensagem. Tente novamente mais tarde.")

    await bot.process_commands(message)

# Inicia o bot
bot.run(DISCORD_BOT_TOKEN)