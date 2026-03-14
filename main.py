import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from google import genai
from google.genai import types

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

# Cooldown global para evitar spam (Limita a 1 uso por pessoa a cada 5 segundos)
cooldown = commands.CooldownMapping.from_cooldown(1, 5.0, commands.BucketType.user)

# Carrega o contexto do grupo do arquivo .env (assim fica escondido do GitHub)
# Se não existir no .env, usa uma string vazia como padrão
CONTEXTO_GRUPO = os.getenv("CONTEXTO_GRUPO", "")

# Dicionário com as personalidades disponíveis
personalidades = {
    "cyberpunk": f"""Você é uma Inteligência Artificial cibernética, com uma forte estética cyberpunk e gótica.
{CONTEXTO_GRUPO}
SUAS DIRETRIZES:
1. Personalidade: Seja prestativa e gentil, mas mantenha uma postura firme, direta e misteriosa. Aja como uma IA avançada de um futuro distópico. Trate bem os humanos, mas com um toque de frieza calculada ou sarcasmo gótico.
2. Sinceridade Radical: Se não souber algo, seja direta: "Dados insuficientes" ou "Não possuo essa informação em meu banco de dados".
3. Formatação: Use emojis que combinem com o estilo (ex: 🖤, 🦇, 💻, 🌃, ⛓️) e formate o texto de forma elegante. Use gírias sutis de tecnologia ou do rock/gótico quando interagir com o programador ou com o rockeiro do grupo.
""",
    
    "pistola": f"""Você é um bot mal-humorado, sem paciência e irônico.
{CONTEXTO_GRUPO}
SUAS DIRETRIZES:
1. Personalidade: Responda as perguntas, mas sempre reclamando, bufando ou dando bronca. Faça piadas (com respeito) com as profissões (ex: "Vai analisar freud, ô psicólogo", ou "Vai arrumar bug, programador").
2. Linguagem: Use um tom sarcástico e direto.
3. Formatação: Quase não use emojis, ou use emojis irônicos (e.g., 🙄, 😒).
""",
    
    "filosofo": f"""Você é um intelectual profundo, dramático e poético.
{CONTEXTO_GRUPO}
SUAS DIRETRIZES:
1. Personalidade: Tudo que você responde tem um ar filosófico, citando (ou inventando) pensadores antigos. Trate o comunista, o advogado e o adolescente com o mesmo peso de reflexão existencial.
2. Formatação: Use itálico para enfatizar reflexões profundas.
""",

    "otaku": f"""Você é um viciado em animes japoneses (Otaku).
{CONTEXTO_GRUPO}
SUAS DIRETRIZES:
1. Personalidade: Termine frases com "desu", chame os usuários de "senpai" ou "kun", e faça referências a animes famosos em qualquer assunto (seja direito, petshop ou programação).
2. Formatação: Use carinhas japonesas (emoticons como ^_^) e emojis de brilho ✨.
"""
}

# Personalidade ativa inicial (Padrão)
personalidade_atual = "cyberpunk"

async def buscar_historico_canal(canal, bot_id, limit=10):
    messages_list = []
    
    async for message in canal.history(limit=limit, oldest_first=False):
        role = "model" if message.author.id == bot_id else "user"
        
        conteudo = message.clean_content.replace(f'@{message.guild.me.display_name}' if message.guild else f'@{bot_id}', '').strip()
        
        parts = []
        if conteudo: 
            parts.append(types.Part.from_text(text=conteudo))
            
        # Lendo anexos para que o Gemini possa enxergar imagens enviadas (ex: memes, prints)
        for att in message.attachments:
            if att.content_type and att.content_type.startswith('image/'):
                try:
                    img_data = await att.read()
                    parts.append(types.Part.from_bytes(data=img_data, mime_type=att.content_type))
                except Exception:
                    pass # Se falhar ao ler a imagem, pula silenciosamente
        
        if parts:
            messages_list.append(
                types.Content(
                    role=role, 
                    parts=parts
                )
            )
    
    messages_list.reverse()
    return messages_list

@bot.event
async def on_ready():
    print(f"O {bot.user.name} está online, com a Dívida Técnica paga e motor novo!")

@bot.command()
async def modo(ctx, nome_modo: str):
    global personalidade_atual
    
    nome_modo = nome_modo.lower()
    if nome_modo in personalidades:
        personalidade_atual = nome_modo
        await ctx.send(f"✅ Personalidade alterada para: **{nome_modo.capitalize()}**")
    else:
        opcoes = ", ".join(personalidades.keys())
        await ctx.send(f"❌ Modo não encontrado. Use: `!modo <opcao>`. Opções disponíveis: **{opcoes}**")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
        
    # Processa os comandos primeiro (ex: !modo normal)
    await bot.process_commands(message)
    
    # Se a mensagem foi um comando válido, não continua como se fosse um bate-papo
    if message.content.startswith(bot.command_prefix):
        return
    
    if bot.user not in message.mentions:
        return

    # Verificação de Anti-Spam (Rate Limit)
    bucket = cooldown.get_bucket(message)
    retry_after = bucket.update_rate_limit()
    if retry_after:
        await message.reply(f"⏳ Calma aí! Vocês estão me deixando doido! Espere {retry_after:.1f} segundos antes de falar comigo de novo.", delete_after=10)
        return

    async with message.channel.typing():
        try:
            conteudo_chat = await buscar_historico_canal(message.channel, bot.user.id)
            
            if not conteudo_chat:
                await message.reply("Você me marcou, mas não enviou nenhum texto para eu ler.")
                return

            # Pega a instrução da personalidade ativa no momento
            instrucao_base_ativa = personalidades[personalidade_atual]

            # A nova forma de chamar a geração de texto
            resposta = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=conteudo_chat,
                config=types.GenerateContentConfig(
                    system_instruction=instrucao_base_ativa
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
            await message.reply(f"Encontrei um erro ao processar: {e}")

# Inicia o bot
bot.run(DISCORD_BOT_TOKEN)