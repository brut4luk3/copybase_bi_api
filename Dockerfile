# Usa uma imagem base oficial de Python
FROM python:3.10-slim

# Defina o diretório de trabalho
WORKDIR /app

# Copia os arquivos necessários para o contêiner
COPY requirements.txt .
COPY . /app/api

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta que sua API utiliza
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["python", "/app/api/app.py"]
