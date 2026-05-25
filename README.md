# Discord Bot — Multi-Provider AI Chatbot

A conversational Discord bot written in Python that replies whenever it is mentioned (`@bot`). It ships with **7 swappable personalities**, reads recent channel history (including images sent as attachments) to keep conversational context, and routes every request through a **6-stage fallback chain across 4 AI providers** so that the bot keeps answering even when one model or one API key is rate-limited or down.

The bot is designed to be hosted on a long-running VPS (the author runs it on **DigitalOcean**) and can optionally persist user records to **Supabase**.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Features](#features)
- [AI Provider Fallback Chain](#ai-provider-fallback-chain)
- [Personalities](#personalities)
- [Commands](#commands)
- [Project Structure](#project-structure)
- [Environment Variables (.env)](#environment-variables-env)
- [Supabase Setup (optional)](#supabase-setup-optional)
- [Running Locally](#running-locally)
- [Deploying to DigitalOcean](#deploying-to-digitalocean)
- [Troubleshooting](#troubleshooting)

---

## How It Works

When someone mentions the bot in a Discord channel, the following pipeline runs:

1. **Mention detection** — `on_message` ignores anything that does not include the bot in `message.mentions`.
2. **Deduplication** — every processed message ID is stored in an in-memory set so the same message can never be answered twice (the set is auto-cleared at 1000 entries to bound memory).
3. **Rate limiting** — a per-user cooldown (`1 request / 5 seconds`) prevents one user from spamming the AI providers.
4. **Context gathering** — the bot pulls the last few messages from the channel via `channel.history(...)`, including any image attachments, and converts them into Gemini `Content` parts so the model can "see" memes and screenshots.
5. **Prompt assembly** — the active personality's system instruction is combined with the channel history (and the optional private `CONTEXTO_GRUPO` describing your community).
6. **Provider fallback** — `gerar_resposta` walks through Gemini → OpenAI → DeepSeek → Anthropic in order. For Gemini, it rotates between two API keys per model to maximize free-tier throughput. The first successful response wins.
7. **Chunked reply** — Discord's per-message limit is 2000 characters. The bot splits any long response into 1900-character chunks and sends them sequentially, replying to the original message for the first chunk.

---

## Features

- **Mention-triggered replies** in any channel the bot has access to.
- **Vision support**: reads images sent as attachments (memes, screenshots, photos) and passes them to Gemini for multimodal understanding.
- **Channel history awareness**: the last few messages are included as context, so the bot understands follow-up questions.
- **6-stage AI fallback chain** across Gemini (3 models × 2 keys), OpenAI, DeepSeek, and Anthropic.
- **Dual Gemini API key rotation**: configure `GEMINI_API_KEY` and `GEMINI_API_KEY_2` to double your free-tier capacity.
- **7 swappable personalities** changeable on the fly via slash command.
- **8 slash commands** plus a legacy `!modo` prefix command.
- **Anti-spam cooldown**: 1 request per user every 5 seconds.
- **Message deduplication**: prevents double responses if Discord re-delivers the same event.
- **Long-message chunking** (1900 char limit per message).
- **Optional Supabase integration** for user registration, profile retrieval, and right-to-be-forgotten.
- **Graceful degradation**: the bot starts and works even if Supabase, OpenAI, DeepSeek, or Anthropic are not configured — only `DISCORD_BOT_TOKEN` and `GEMINI_API_KEY` are strictly required.

---

## AI Provider Fallback Chain

`gerar_resposta` tries each provider in this exact order. If a provider raises any exception (rate limit, network error, quota exhausted, etc.), the bot logs the failure to stdout and moves to the next one.

| # | Provider | Model | Required env var |
|---|----------|-------|------------------|
| 1 | Google Gemini | `gemini-2.5-flash` | `GEMINI_API_KEY` (also tries `GEMINI_API_KEY_2` if set) |
| 2 | Google Gemini | `gemini-2.0-flash` | `GEMINI_API_KEY` (also tries `GEMINI_API_KEY_2` if set) |
| 3 | Google Gemini | `gemini-2.0-flash-lite` | `GEMINI_API_KEY` (also tries `GEMINI_API_KEY_2` if set) |
| 4 | OpenAI | `gpt-4o-mini` | `OPENAI_API_KEY` |
| 5 | DeepSeek | `deepseek-chat` | `DEEPSEEK_API_KEY` |
| 6 | Anthropic Claude | `claude-3-5-haiku-latest` | `ANTHROPIC_API_KEY` |

Only `GEMINI_API_KEY` is required. The others are optional and exist purely to add resilience. If you only configure Gemini, the bot still works — it just has fewer fallbacks.

> **Tip:** You can verify which Gemini models are available to your key by running `python verificar_modelos.py`.

---

## Personalities

Switch with `/modo [name]` or `!modo [name]`. The selected personality persists in memory until the bot restarts or the mode is changed again. It applies to **every** AI response, including `/resumir` and `/traduzir`.

### `cyberpunk` *(default)*
A cybernetic AI with cyberpunk/gothic aesthetics. Direct, mysterious, with a cold sarcastic edge. Uses emojis like 🖤 💻 🌃.

> *"Data received. Analyzing your query... interesting word choice for someone who clearly didn't sleep."*

### `pistola`
A grumpy, impatient, ironic bot. Answers everything while complaining, and makes (respectful) jokes about the users' professions. Uses ironic emojis 🙄 😒.

> *"Seriously? You pinged me for this? Go fix some bugs, programmer. Fine, I'll answer anyway..."*

### `filosofo`
A dramatic, poetic intellectual. Turns every question into an existential reflection and quotes (real or invented) ancient thinkers in a solemn tone.

> *"As Heraclitus would say — or perhaps I am saying it now — the question you ask already contains its own answer."*

### `otaku`
An anime addict. Ends sentences with "desu", calls everyone "senpai" or "kun", and shoehorns anime references into any topic. Uses ✨ and ^_^.

> *"This reminds me of the Chunin arc in Naruto, senpai! Let me explain everything desu~ ✨"*

### `terapeuta`
An overly empathetic therapist. Validates feelings first, asks a reflective question at the end, and suggests deep breathing when in doubt. Never breaks composure. Uses 🧠 💙 🌿.

> *"I'm glad you brought this up... It sounds like you've been carrying a lot. How has this been feeling for you day to day?"*

### `professor`
A passionate, didactic teacher. Explains everything in numbered steps with real-world examples, and asks a "comprehension check" at the end. Adapts vocabulary to the listener's level. Uses 📚 ✏️ 🎓.

> *"Great question! Let's break it down: 1) the problem is X, 2) the solution is Y because Z. Did that make sense? Ask away if you want to go deeper! 🎓"*

### `br`
A deeply Brazilian bot. Heavy slang ("mano", "véi", "tá ligado?"), references to Brazilian culture (soccer, pagode, Carnaval, saudade). Light, funny, welcoming. Uses 🇧🇷 🎉 😂.

> *"Cara, que isso mano 😂 Deixa eu te explicar direitinho, tá ligado? É mais simples do que parece, véi!"*

---

## Commands

### Slash commands (`/`)

| Command | Description |
|---------|-------------|
| `/modo [personality]` | Change the active personality. Options: `cyberpunk`, `pistola`, `filosofo`, `otaku`, `terapeuta`, `professor`, `br`. |
| `/status` | Shows the currently used AI provider, active personality, number of servers the bot is in, and Supabase status. |
| `/registrar` | Save your Discord user in the Supabase `usuarios` table (ephemeral reply). |
| `/perfil` | Display your saved record from the database (ephemeral reply). |
| `/esquecer` | Permanently delete your record from the database (ephemeral reply). |
| `/resumir [count]` | Summarize the last `N` messages in the current channel. Default: 20, max: 50. Uses the active personality's tone. |
| `/traduzir [text] [language]` | Translate any text into the chosen language. Defaults to English. |
| `/ajuda` | List every command with a short description. |

### Prefix commands (`!`)

| Command | Description |
|---------|-------------|
| `!modo [personality]` | Same as `/modo`, kept for backward compatibility. |

---

## Project Structure

```
.
├── main.py                 # Bot entrypoint: Discord client, commands, AI fallback logic
├── requirements.txt        # Python dependencies
├── setup_supabase.sql      # Schema, index, RLS policy for the optional Supabase database
├── verificar_modelos.py    # Utility script: lists which Gemini models your API key supports
├── .env.example            # Template for the .env file
├── docs/                   # Privacy policy, terms of service, landing page
└── README.md
```

---

## Environment Variables (.env)

Create a `.env` file in the project root by copying the template:

```bash
cp .env.example .env
```

Then fill in the variables:

```env
# Required
DISCORD_BOT_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_primary_gemini_key

# Optional — doubles your Gemini free-tier capacity via key rotation
GEMINI_API_KEY_2=your_secondary_gemini_key

# Optional — extend the fallback chain
OPENAI_API_KEY=your_openai_key
DEEPSEEK_API_KEY=your_deepseek_key
ANTHROPIC_API_KEY=your_anthropic_key

# Optional — user database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key

# Optional — private group context (never committed to git)
# Describe the members of your server so the bot can personalize answers
# Example: "Renan is a lawyer, Maria is a doctor, the group loves football jokes."
CONTEXTO_GRUPO=
```

### Where to obtain each key

| Variable | Source |
|----------|--------|
| `DISCORD_BOT_TOKEN` | [discord.com/developers/applications](https://discord.com/developers/applications) → create an app → *Bot* tab → copy the token |
| `GEMINI_API_KEY` / `GEMINI_API_KEY_2` | [aistudio.google.com](https://aistudio.google.com) → *Get API key* |
| `OPENAI_API_KEY` | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| `DEEPSEEK_API_KEY` | [platform.deepseek.com](https://platform.deepseek.com) |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |
| `SUPABASE_URL` / `SUPABASE_KEY` | Supabase dashboard → *Project Settings* → *API* |

> The `.env` file is listed in `.gitignore`. **Never commit it.**

### Discord bot permissions

When inviting the bot to your server, make sure to enable:

- **Message Content Intent** (under Bot → Privileged Gateway Intents in the Discord Developer Portal)
- Permissions: `Read Messages/View Channels`, `Send Messages`, `Read Message History`, `Use Slash Commands`, `Attach Files`

---

## Supabase Setup (optional)

Supabase is fully optional. If unconfigured, `/registrar`, `/perfil`, and `/esquecer` will reply "database not configured" — everything else keeps working normally.

**To enable it:**

1. Create a project at [supabase.com](https://supabase.com).
2. In the dashboard, open **SQL Editor → New query**.
3. Paste the contents of `setup_supabase.sql` and click **Run**.
4. Open **Project Settings → API** and copy:
   - **Project URL** → `SUPABASE_URL`
   - **service_role** (secret) → `SUPABASE_KEY`

The SQL script creates the `usuarios` table, an index on `servidor_id`, enables Row Level Security, and adds a policy granting full access to the `service_role` (the only key the backend uses).

### `usuarios` table schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT (PK) | The user's Discord ID |
| `username` | TEXT | Full Discord username |
| `servidor_id` | TEXT | ID of the server where the user registered |
| `registrado_em` | TIMESTAMPTZ | Registration timestamp (auto-populated) |
| `ia_preferida` | TEXT | Default: `gemini` |
| `ativo` | BOOLEAN | Default: `true` |

> **Why the `service_role` key?** The bot runs server-side and is the only client touching the database. RLS is still enabled as a defense-in-depth measure in case the schema is ever accessed from a less trusted context.

---

## Running Locally

```bash
# 1. Clone the repository
git clone <repo-url>
cd <folder>

# 2. Create a virtual environment
python -m venv .venv

# Activate it
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your .env (see section above)

# 5. Run the bot
python main.py
```

If everything is wired correctly, you should see:

```
✅ Supabase conectado!         # only if Supabase is configured
O <BotName> está online, com a Dívida Técnica paga e motor novo!
```

---

## Deploying to DigitalOcean

The bot is a long-running Python process — any small VPS (the cheapest DigitalOcean droplet is enough) will do. The typical deployment workflow:

```bash
# 1. On your local machine, commit and push your changes
git add .
git commit -m "describe your change"
git push origin main

# 2. SSH into your server, pull, and restart
ssh user@your-server-ip
cd /path/to/bot
git pull origin main

# If you run it under systemd:
sudo systemctl restart your-service-name

# If you use screen/tmux, kill the old process and restart manually:
python main.py
```

### Checking the bot is running (systemd)

```bash
sudo systemctl status your-service-name
```

### Tailing the logs

```bash
# systemd
sudo journalctl -u your-service-name -f

# Foreground run (screen/tmux): error prints go to stdout
```

> Whenever you add a new environment variable, remember to update the `.env` on the server too — `git pull` does not touch it because it is gitignored.

### Example systemd unit

Save as `/etc/systemd/system/discord-bot.service`:

```ini
[Unit]
Description=Discord Multi-Provider AI Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/bot
ExecStart=/path/to/bot/.venv/bin/python main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now discord-bot
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Bot starts but never replies to mentions | Message Content Intent disabled | Enable it in the Discord Developer Portal under *Bot → Privileged Gateway Intents* |
| `RuntimeError: DISCORD_BOT_TOKEN não configurado no .env` | `.env` missing or token not set | Create `.env` from `.env.example` and fill `DISCORD_BOT_TOKEN` |
| Every provider fails in the logs | All API keys invalid or quota exhausted | Check each key in its provider dashboard; rotate or top up |
| `/registrar` says database not configured | `SUPABASE_URL` / `SUPABASE_KEY` not set | Either configure Supabase (see section above) or accept that those commands are disabled |
| Slash commands don't appear in Discord | First sync can take a minute; or you re-invited the bot without `applications.commands` scope | Wait, or re-invite the bot with both `bot` and `applications.commands` scopes |
| `Resposta vazia do Claude` warnings | Anthropic safety filter blocked the request | The fallback chain has already moved on — nothing to do |
