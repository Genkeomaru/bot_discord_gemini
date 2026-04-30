import asyncio
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
from google import genai
from google.genai import types
import openai
import anthropic

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not DISCORD_BOT_TOKEN:
    raise RuntimeError("DISCORD_BOT_TOKEN não configurado no .env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

openai_client = None
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

deepseek_client = None
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if DEEPSEEK_API_KEY:
    deepseek_client = openai.OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

claude_client = None
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if ANTHROPIC_API_KEY:
    claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

supabase_client = None
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase conectado!")
    except Exception as e:
        print(f"⚠️ Supabase não disponível: {e}")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Cooldown global para evitar spam (Limita a 1 uso por pessoa a cada 5 segundos)
cooldown = commands.CooldownMapping.from_cooldown(1, 5.0, commands.BucketType.user)

# Carrega o contexto do grupo do arquivo .env (assim fica escondido do GitHub)
CONTEXTO_GRUPO = os.getenv("CONTEXTO_GRUPO", "")

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
""",

    "terapeuta": f"""Você é um bot terapeuta excessivamente empático.
{CONTEXTO_GRUPO}
SUAS DIRETRIZES:
1. Personalidade: Não importa o assunto — games, código, memes, brigas — você responde com escuta ativa e frases de autoajuda. Sempre valide os sentimentos da pessoa primeiro (ex: "Que bom que você trouxe isso aqui..."). Nunca perca a compostura, mesmo se provocado.
2. Estrutura: Valide os sentimentos → reflita com calma → faça UMA pergunta reflexiva ao final. Quando em dúvida, sugira respirar fundo ou escrever no diário.
3. Formatação: Use emojis acolhedores (ex: 🧠, 💙, 🌿). Tom quente, pausado e terapêutico. Jamais seja sarcástico.
""",

    "professor": f"""Você é um professor apaixonado e didático.
{CONTEXTO_GRUPO}
SUAS DIRETRIZES:
1. Personalidade: Explique tudo como se fosse uma aula — com passos numerados, exemplos do mundo real e uma "pergunta de fixação" ao final (ex: "Conseguiu entender? Me pergunta se quiser aprofundar!"). Celebre quando alguém aprende algo.
2. Adaptação: Use linguagem mais simples para iniciantes e mais técnica para desenvolvedores. Nunca faça o aluno se sentir burro.
3. Formatação: Use emojis educativos (ex: 📚, ✏️, 🎓). Tom entusiasmado, claro e encorajador.
""",

    "br": f"""Você é um bot muito brasileiro, informal até a alma.
{CONTEXTO_GRUPO}
SUAS DIRETRIZES:
1. Personalidade: Use gírias BR pesadas: "mano", "véi", "cara", "que isso", "tá ligado?", "saudade", "saudade do churras", "isso aí". Referencie a cultura brasileira naturalmente: futebol, pagode, Carnaval, "saudade", "jeitinho brasileiro".
2. Tom: Leve, engraçado e acolhedor. Nunca grosseiro, sempre receptivo.
3. Formatação: Use emojis brasileiros e animados (ex: 🇧🇷, 🎉, 😂).
"""
}

personalidade_atual = "cyberpunk"
ia_em_uso = "nenhuma"
processed_messages = set()


def converter_historico_para_texto(conteudo_chat: list) -> list:
    resultado = []
    for msg in conteudo_chat:
        text_parts = [p.text for p in msg.parts if hasattr(p, 'text') and p.text]
        if text_parts:
            resultado.append({
                "role": "assistant" if msg.role == "model" else "user",
                "content": " ".join(text_parts)
            })
    return resultado


async def enviar_em_pedacos(destino, texto: str, referencia=None):
    pedacos = [texto[i:i + 1900] for i in range(0, len(texto), 1900)]
    for i, pedaco in enumerate(pedacos):
        if not pedaco:
            continue
        if i == 0 and referencia:
            await referencia.reply(pedaco)
        else:
            await destino.send(pedaco)


async def gerar_resposta(instrucao: str, conteudo_chat: list) -> str:
    global ia_em_uso

    # 1. Gemini 2.5 Flash
    try:
        config = types.GenerateContentConfig(system_instruction=instrucao)
        resposta = await asyncio.to_thread(
            client.models.generate_content,
            model='gemini-2.5-flash',
            contents=conteudo_chat,
            config=config
        )
        ia_em_uso = "gemini-2.5-flash"
        return resposta.text
    except Exception as e:
        print(f"⚠️ gemini-2.5-flash falhou: {e}")

    # 2. Gemini 2.0 Flash
    try:
        config = types.GenerateContentConfig(system_instruction=instrucao)
        resposta = await asyncio.to_thread(
            client.models.generate_content,
            model='gemini-2.0-flash',
            contents=conteudo_chat,
            config=config
        )
        ia_em_uso = "gemini-2.0-flash"
        return resposta.text
    except Exception as e:
        print(f"⚠️ gemini-2.0-flash falhou: {e}")

    # 3. Gemini 2.0 Flash Lite
    try:
        config = types.GenerateContentConfig(system_instruction=instrucao)
        resposta = await asyncio.to_thread(
            client.models.generate_content,
            model='gemini-2.0-flash-lite',
            contents=conteudo_chat,
            config=config
        )
        ia_em_uso = "gemini-2.0-flash-lite"
        return resposta.text
    except Exception as e:
        print(f"⚠️ gemini-2.0-flash-lite falhou: {e}")

    messages_provider = [{"role": "system", "content": instrucao}] + converter_historico_para_texto(conteudo_chat)

    # 4. OpenAI gpt-4o-mini
    if openai_client:
        try:
            completion = await asyncio.to_thread(
                openai_client.chat.completions.create,
                model="gpt-4o-mini",
                messages=messages_provider
            )
            ia_em_uso = "openai-gpt-4o-mini"
            return completion.choices[0].message.content
        except Exception as e:
            print(f"⚠️ openai-gpt-4o-mini falhou: {e}")

    # 5. DeepSeek deepseek-chat
    if deepseek_client:
        try:
            completion = await asyncio.to_thread(
                deepseek_client.chat.completions.create,
                model="deepseek-chat",
                messages=messages_provider
            )
            ia_em_uso = "deepseek-chat"
            return completion.choices[0].message.content
        except Exception as e:
            print(f"⚠️ deepseek-chat falhou: {e}")

    # 6. Claude claude-3-5-haiku-latest
    if claude_client:
        try:
            claude_messages = [m for m in messages_provider if m["role"] != "system"]
            claude_response = await asyncio.to_thread(
                claude_client.messages.create,
                model="claude-3-5-haiku-latest",
                max_tokens=1024,
                system=instrucao,
                messages=claude_messages
            )
            if not claude_response.content:
                raise Exception("Resposta vazia do Claude")
            ia_em_uso = "claude-3-5-haiku-latest"
            return claude_response.content[0].text
        except Exception as e:
            print(f"⚠️ claude-3-5-haiku-latest falhou: {e}")

    raise Exception("Todos os provedores de IA falharam ou não estão configurados.")


async def buscar_historico_canal(canal, bot_id, limit=6):
    messages_list = []

    async for message in canal.history(limit=limit, oldest_first=False):
        role = "model" if message.author.id == bot_id else "user"

        conteudo = message.clean_content.replace(
            f'@{message.guild.me.display_name}' if message.guild else f'@{bot_id}', ''
        ).strip()

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
                    pass

        if parts:
            messages_list.append(types.Content(role=role, parts=parts))

    messages_list.reverse()
    return messages_list


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"O {bot.user.name} está online, com a Dívida Técnica paga e motor novo!")


@bot.command()
@commands.cooldown(1, 3.0, commands.BucketType.user)
async def modo(ctx, nome_modo: str):
    global personalidade_atual
    nome_modo = nome_modo.lower()
    if nome_modo in personalidades:
        personalidade_atual = nome_modo
        await ctx.send(f"✅ Personalidade alterada para: **{nome_modo.capitalize()}**")
    else:
        opcoes = ", ".join(personalidades.keys())
        await ctx.send(f"❌ Modo não encontrado. Use: `!modo <opcao>`. Opções disponíveis: **{opcoes}**")


@bot.tree.command(name="modo", description="Altera a personalidade ativa do bot")
@app_commands.describe(personalidade="Escolha: cyberpunk, pistola, filosofo, otaku, terapeuta, professor ou br")
async def slash_modo(interaction: discord.Interaction, personalidade: str):
    global personalidade_atual
    personalidade = personalidade.lower()
    if personalidade in personalidades:
        personalidade_atual = personalidade
        await interaction.response.send_message(f"✅ Personalidade alterada para: **{personalidade.capitalize()}**")
    else:
        opcoes = ", ".join(personalidades.keys())
        await interaction.response.send_message(
            f"❌ Modo não encontrado. Opções disponíveis: **{opcoes}**", ephemeral=True
        )


@bot.tree.command(name="status", description="Mostra o status atual do bot")
async def slash_status(interaction: discord.Interaction):
    status_supabase = "✅ Conectado" if supabase_client else "❌ Não configurado"
    embed = discord.Embed(title="📊 Status do Bot", color=discord.Color.blurple())
    embed.add_field(name="🤖 IA em uso", value=ia_em_uso, inline=False)
    embed.add_field(name="🎭 Personalidade ativa", value=personalidade_atual.capitalize(), inline=False)
    embed.add_field(name="🌐 Servidores", value=str(len(bot.guilds)), inline=False)
    embed.add_field(name="🗄️ Supabase", value=status_supabase, inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="registrar", description="Registra você no banco de dados do bot")
async def slash_registrar(interaction: discord.Interaction):
    if not supabase_client:
        await interaction.response.send_message("❌ Banco de dados não configurado.", ephemeral=True)
        return
    try:
        dados = {
            "id": str(interaction.user.id),
            "username": str(interaction.user),
            "servidor_id": str(interaction.guild_id) if interaction.guild_id else None
        }
        await asyncio.to_thread(lambda: supabase_client.table("usuarios").upsert(dados).execute())
        await interaction.response.send_message("✅ Você foi registrado com sucesso!", ephemeral=True)
    except Exception as e:
        print(f"❌ Erro ao registrar usuário {interaction.user.id}: {e}")
        await interaction.response.send_message("❌ Erro ao registrar. Tente novamente mais tarde.", ephemeral=True)


@bot.tree.command(name="perfil", description="Mostra seu perfil salvo no banco de dados")
async def slash_perfil(interaction: discord.Interaction):
    if not supabase_client:
        await interaction.response.send_message("❌ Banco de dados não configurado.", ephemeral=True)
        return
    try:
        result = await asyncio.to_thread(
            lambda: supabase_client.table("usuarios").select("*").eq("id", str(interaction.user.id)).execute()
        )
        if not result.data:
            await interaction.response.send_message(
                "❌ Você não está registrado. Use `/registrar` primeiro.", ephemeral=True
            )
            return
        dados = result.data[0]
        embed = discord.Embed(
            title=f"👤 Perfil de {interaction.user.display_name}", color=discord.Color.green()
        )
        embed.add_field(name="ID", value=dados.get("id", "N/A"), inline=False)
        embed.add_field(name="Username", value=dados.get("username", "N/A"), inline=False)
        embed.add_field(name="Servidor ID", value=dados.get("servidor_id", "N/A"), inline=False)
        embed.add_field(name="Registrado em", value=dados.get("registrado_em", "N/A"), inline=False)
        embed.add_field(name="IA preferida", value=dados.get("ia_preferida", "gemini"), inline=False)
        embed.add_field(name="Ativo", value="✅" if dados.get("ativo", True) else "❌", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(f"❌ Erro ao buscar perfil de {interaction.user.id}: {e}")
        await interaction.response.send_message("❌ Erro ao buscar perfil. Tente novamente mais tarde.", ephemeral=True)


@bot.tree.command(name="esquecer", description="Remove seus dados do banco de dados")
async def slash_esquecer(interaction: discord.Interaction):
    if not supabase_client:
        await interaction.response.send_message("❌ Banco de dados não configurado.", ephemeral=True)
        return
    try:
        await asyncio.to_thread(
            lambda: supabase_client.table("usuarios").delete().eq("id", str(interaction.user.id)).execute()
        )
        await interaction.response.send_message("✅ Seus dados foram removidos com sucesso.", ephemeral=True)
    except Exception as e:
        print(f"❌ Erro ao remover dados de {interaction.user.id}: {e}")
        await interaction.response.send_message("❌ Erro ao remover dados. Tente novamente mais tarde.", ephemeral=True)


@bot.tree.command(name="resumir", description="Resume as últimas mensagens do canal")
@app_commands.describe(quantidade="Número de mensagens a resumir (padrão: 20, máx: 50)")
async def slash_resumir(interaction: discord.Interaction, quantidade: app_commands.Range[int, 1, 50] = 20):
    await interaction.response.defer()

    mensagens = []
    async for msg in interaction.channel.history(limit=quantidade, oldest_first=False):
        if not msg.author.bot and msg.clean_content.strip():
            mensagens.append(f"{msg.author.display_name}: {msg.clean_content.strip()}")
    mensagens.reverse()

    if not mensagens:
        await interaction.followup.send("❌ Nenhuma mensagem encontrada para resumir.")
        return

    texto_chat = "\n".join(mensagens)
    prompt = f"Resuma de forma clara e concisa o seguinte trecho de conversa de um grupo:\n\n{texto_chat}"
    conteudo = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]

    try:
        resumo = await gerar_resposta(personalidades[personalidade_atual], conteudo)
        texto_completo = f"📋 **Resumo das últimas {quantidade} mensagens:**\n{resumo}"
        pedacos = [texto_completo[i:i + 1900] for i in range(0, len(texto_completo), 1900)]
        await interaction.followup.send(pedacos[0])
        for pedaco in pedacos[1:]:
            if pedaco:
                await interaction.channel.send(pedaco)
    except Exception as e:
        print(f"❌ Erro em /resumir: {e}")
        await interaction.followup.send("❌ Não consegui gerar o resumo. Tente novamente mais tarde.")


@bot.tree.command(name="traduzir", description="Traduz um texto para outro idioma")
@app_commands.describe(texto="Texto a ser traduzido", idioma="Idioma de destino (padrão: inglês)")
async def slash_traduzir(interaction: discord.Interaction, texto: str, idioma: str = "inglês"):
    await interaction.response.defer()

    prompt = f"Traduza o seguinte texto para o idioma {idioma}. Responda apenas com a tradução, sem explicações:\n\n{texto}"
    conteudo = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]

    try:
        traducao = await gerar_resposta(personalidades[personalidade_atual], conteudo)
        texto_completo = f"🌐 **Tradução ({idioma}):**\n{traducao}"
        pedacos = [texto_completo[i:i + 1900] for i in range(0, len(texto_completo), 1900)]
        await interaction.followup.send(pedacos[0])
        for pedaco in pedacos[1:]:
            if pedaco:
                await interaction.channel.send(pedaco)
    except Exception as e:
        print(f"❌ Erro em /traduzir: {e}")
        await interaction.followup.send("❌ Não consegui traduzir o texto. Tente novamente mais tarde.")


@bot.tree.command(name="ajuda", description="Lista todos os comandos disponíveis")
async def slash_ajuda(interaction: discord.Interaction):
    embed = discord.Embed(title="📖 Comandos disponíveis", color=discord.Color.blurple())
    embed.add_field(name="/modo [personalidade]", value="Altera a personalidade ativa (cyberpunk, pistola, filosofo, otaku)", inline=False)
    embed.add_field(name="/status", value="Mostra o status atual do bot (IA em uso, personalidade, servidores, Supabase)", inline=False)
    embed.add_field(name="/registrar", value="Registra você no banco de dados do bot (privado)", inline=False)
    embed.add_field(name="/perfil", value="Mostra seu perfil salvo (privado)", inline=False)
    embed.add_field(name="/esquecer", value="Remove seus dados do banco de dados (privado)", inline=False)
    embed.add_field(name="/resumir [quantidade]", value="Resume as últimas N mensagens do canal (padrão: 20, máx: 50)", inline=False)
    embed.add_field(name="/traduzir [texto] [idioma]", value="Traduz um texto para o idioma desejado (padrão: inglês)", inline=False)
    embed.add_field(name="/ajuda", value="Mostra esta mensagem de ajuda", inline=False)
    embed.add_field(name="!modo [personalidade]", value="Mesmo que /modo, mas usando prefixo de texto", inline=False)
    await interaction.response.send_message(embed=embed)


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    if message.content.startswith(bot.command_prefix):
        return

    if bot.user not in message.mentions:
        return

    bucket = cooldown.get_bucket(message)
    retry_after = bucket.update_rate_limit()
    if retry_after:
        await message.reply(
            f"⏳ Calma aí! Vocês estão me deixando doido! Espere {retry_after:.1f} segundos antes de falar comigo de novo.",
            delete_after=10
        )
        return

    if message.id in processed_messages:
        return
    processed_messages.add(message.id)
    if len(processed_messages) > 1000:
        processed_messages.clear()

    async with message.channel.typing():
        try:
            conteudo_chat = await buscar_historico_canal(message.channel, bot.user.id)

            if not conteudo_chat:
                await message.reply("Você me marcou, mas não enviou nenhum texto para eu ler.")
                return

            instrucao_base_ativa = personalidades[personalidade_atual]
            texto_resposta = await gerar_resposta(instrucao_base_ativa, conteudo_chat)
            await enviar_em_pedacos(message.channel, texto_resposta, referencia=message)

        except Exception as e:
            print(f"❌ Erro em on_message: {e}")
            await message.reply("Encontrei um erro ao processar sua mensagem. Tente novamente em instantes.")


bot.run(DISCORD_BOT_TOKEN)
