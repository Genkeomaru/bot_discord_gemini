# Use uma imagem oficial do Python como imagem pai
FROM python:3.12-slim

# Defina o diretório de trabalho no container
WORKDIR /app

# Copie os arquivos de dependências e instale-os
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie o conteúdo do diretório atual para o container em /app
COPY . .

# Comando para rodar o bot
CMD ["python", "main.py"]
