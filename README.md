# Bot Discord — IA com Múltiplos Provedores

Bot conversacional para Discord feito em Python. Responde quando marcado (`@bot`), tem 7 personalidades trocáveis e usa uma cadeia de fallback com 6 provedores de IA para garantir disponibilidade máxima.

Hospedado no **DigitalOcean** com banco de dados opcional via **Supabase**.

---

## Sumário

- [Funcionalidades](#funcionalidades)
- [Provedores de IA](#provedores-de-ia)
- [Personalidades](#personalidades)
- [Comandos](#comandos)
- [Configuração do .env](#configuração-do-env)
- [Configuração do Supabase](#configuração-do-supabase)
- [Rodando localmente](#rodando-localmente)
- [Deploy no DigitalOcean](#deploy-no-digitalocean)

---

## Funcionalidades

- Responde quando marcado com `@bot` em qualquer canal
- Lê o histórico recente do canal para entender o contexto da conversa
- Lê imagens enviadas como anexos (memes, prints, etc.)
- Divide respostas longas automaticamente (limite de 1900 caracteres por mensagem)
- Anti-spam: limite de 1 requisição por usuário a cada 5 segundos
- 7 personalidades trocáveis em tempo real
- 8 slash commands
- Integração opcional com Supabase para registro de usuários
- Funciona mesmo sem Supabase, OpenAI, DeepSeek ou Claude configurados

---

## Provedores de IA

O bot tenta cada provedor em ordem. Se um falhar (erro de rede, cota, etc.), passa para o próximo automaticamente.

| Ordem | Provedor | Modelo | Variável necessária |
|-------|----------|--------|---------------------|
| 1 | Google Gemini | `gemini-2.5-flash` | `GEMINI_API_KEY` |
| 2 | Google Gemini | `gemini-2.0-flash` | `GEMINI_API_KEY` |
| 3 | Google Gemini | `gemini-2.0-flash-lite` | `GEMINI_API_KEY` |
| 4 | OpenAI | `gpt-4o-mini` | `OPENAI_API_KEY` |
| 5 | DeepSeek | `deepseek-chat` | `DEEPSEEK_API_KEY` |
| 6 | Anthropic Claude | `claude-3-5-haiku-latest` | `ANTHROPIC_API_KEY` |

Apenas `GEMINI_API_KEY` é obrigatória. As demais são opcionais e ampliam a resiliência do bot.

---

## Personalidades

Troque com `/modo [nome]` ou `!modo [nome]`. A personalidade ativa é mantida enquanto o bot estiver rodando.

### cyberpunk *(padrão)*
IA cibernética de estética cyberpunk/gótica. Direta, misteriosa, com toque de sarcasmo frio. Usa emojis 🖤 💻 🌃.

> *"Dados recebidos. Analisando sua consulta... interessante escolha de palavras para alguém que claramente não dormiu."*

### pistola
Bot mal-humorado, sem paciência e irônico. Responde tudo reclamando, com piadas sobre as profissões dos usuários. Emojis irônicos 🙄 😒.

> *"Sério? Você me chamou pra isso? Vai arrumar bug, programador. Mas tá bem, vou responder..."*

### filosofo
Intelectual dramático e poético. Tudo vira reflexão existencial, com citações (reais ou inventadas) de pensadores antigos. Tom solene.

> *"Como diria Heráclito — ou talvez eu mesmo neste instante — a pergunta que você faz já contém sua própria resposta."*

### otaku
Viciado em animes. Termina frases com "desu", chama todos de "senpai" ou "kun", e encaixa referências de anime em qualquer assunto. Emojis ✨ ^_^.

> *"Isso me lembra muito o arco do Chunin no Naruto, senpai! Vou explicar tudo desu~ ✨"*

### terapeuta
Terapeuta excessivamente empático. Valida sentimentos antes de qualquer coisa, faz uma pergunta reflexiva ao final, sugere respirar fundo quando em dúvida. Nunca perde a compostura. Emojis 🧠 💙 🌿.

> *"Que bom que você trouxe isso aqui... Parece que você está carregando muita coisa sozinho. Como você tem se sentido com isso no dia a dia?"*

### professor
Professor apaixonado e didático. Explica tudo em passos numerados com exemplos práticos. Faz uma "pergunta de fixação" ao final. Adapta o nível de linguagem ao interlocutor. Emojis 📚 ✏️ 🎓.

> *"Ótima pergunta! Vamos por partes: 1) O problema é X, 2) A solução é Y porque Z. Conseguiu entender? Me pergunta se quiser aprofundar! 🎓"*

### br
Bot brasileiro raiz. Gírias pesadas ("mano", "véi", "tá ligado?"), referências à cultura do Brasil (futebol, pagode, Carnaval, saudade). Leve, engraçado e acolhedor. Emojis 🇧🇷 🎉 😂.

> *"Cara, que isso mano 😂 Deixa eu te explicar direitinho, tá ligado? É mais simples do que parece, véi!"*

---

## Comandos

### Slash commands (`/`)

| Comando | Descrição |
|---------|-----------|
| `/modo [personalidade]` | Altera a personalidade ativa. Opções: `cyberpunk`, `pistola`, `filosofo`, `otaku`, `terapeuta`, `professor`, `br` |
| `/status` | Mostra o provedor de IA em uso, personalidade ativa, número de servidores e status do Supabase |
| `/registrar` | Salva seu usuário no banco de dados (privado) |
| `/perfil` | Exibe seus dados salvos no banco (privado) |
| `/esquecer` | Remove seus dados do banco permanentemente (privado) |
| `/resumir [quantidade]` | Resume as últimas N mensagens do canal. Padrão: 20, máximo: 50 |
| `/traduzir [texto] [idioma]` | Traduz um texto para o idioma escolhido. Padrão: inglês |
| `/ajuda` | Lista todos os comandos com descrições |

### Comandos de prefixo (`!`)

| Comando | Descrição |
|---------|-----------|
| `!modo [personalidade]` | Mesmo que `/modo`, mantido para compatibilidade |

---

## Configuração do .env

Crie um arquivo `.env` na raiz do projeto copiando o `.env.example`:

```bash
cp .env.example .env
```

Preencha as variáveis:

```env
# Obrigatório
DISCORD_BOT_TOKEN=seu_token_do_discord
GEMINI_API_KEY=sua_chave_gemini

# Opcionais — ampliam a cadeia de fallback
OPENAI_API_KEY=sua_chave_openai
DEEPSEEK_API_KEY=sua_chave_deepseek
ANTHROPIC_API_KEY=sua_chave_anthropic

# Opcional — banco de dados de usuários
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_service_role_key

# Opcional — contexto privado do grupo (não vai pro GitHub)
# Descreva quem são os membros do servidor para personalizar as respostas
CONTEXTO_GRUPO=
```

**Onde obter cada chave:**

- `DISCORD_BOT_TOKEN` → [discord.com/developers/applications](https://discord.com/developers/applications) — crie um app, vá em *Bot* e copie o token
- `GEMINI_API_KEY` → [aistudio.google.com](https://aistudio.google.com) — *Get API key*
- `OPENAI_API_KEY` → [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- `DEEPSEEK_API_KEY` → [platform.deepseek.com](https://platform.deepseek.com)
- `ANTHROPIC_API_KEY` → [console.anthropic.com](https://console.anthropic.com)
- `SUPABASE_URL` e `SUPABASE_KEY` → painel do Supabase → *Project Settings* → *API*

> O `.env` está no `.gitignore`. Nunca commite esse arquivo.

---

## Configuração do Supabase

O Supabase é opcional. Se não configurado, todos os comandos de perfil (`/registrar`, `/perfil`, `/esquecer`) simplesmente informam que o banco não está disponível — o resto do bot funciona normalmente.

**Para ativar:**

1. Crie um projeto em [supabase.com](https://supabase.com)
2. No painel, vá em **SQL Editor → New query**
3. Cole o conteúdo de `setup_supabase.sql` e clique em **Run**
4. Vá em **Project Settings → API** e copie:
   - **Project URL** → `SUPABASE_URL`
   - **service_role** (secret) → `SUPABASE_KEY`

O script `setup_supabase.sql` cria a tabela `usuarios`, habilita Row Level Security e configura a policy para o `service_role` ter acesso total.

**Estrutura da tabela `usuarios`:**

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | TEXT (PK) | ID do usuário no Discord |
| `username` | TEXT | Nome de usuário completo |
| `servidor_id` | TEXT | ID do servidor onde se registrou |
| `registrado_em` | TIMESTAMPTZ | Data de registro (automático) |
| `ia_preferida` | TEXT | Padrão: `gemini` |
| `ativo` | BOOLEAN | Padrão: `true` |

---

## Rodando localmente

```bash
# 1. Clone o repositório
git clone <url-do-repo>
cd <pasta>

# 2. Crie o ambiente virtual
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure o .env (veja seção acima)

# 5. Inicie o bot
python main.py
```

---

## Deploy no DigitalOcean

O bot roda como um processo contínuo no servidor. Para enviar atualizações:

```bash
# 1. No seu ambiente local, commite e envie as mudanças
git add .
git commit -m "descrição da mudança"
git push origin main

# 2. No servidor (via SSH), puxe as mudanças e reinicie o processo
ssh usuario@ip-do-servidor

cd /caminho/do/bot
git pull origin main

# Se usar systemd
sudo systemctl restart nome-do-servico

# Se usar screen/tmux, encerre o processo e reinicie manualmente
python main.py
```

**Para verificar se o bot está rodando (systemd):**

```bash
sudo systemctl status nome-do-servico
```

**Para ver os logs em tempo real:**

```bash
# systemd
sudo journalctl -u nome-do-servico -f

# ou direto no terminal se estiver rodando em foreground
# os prints de erro aparecem no stdout
```

> Lembre de atualizar o `.env` no servidor sempre que adicionar novas variáveis de ambiente.
