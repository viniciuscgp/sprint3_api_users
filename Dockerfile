# Use uma imagem base oficial do Python
FROM python:3.8-slim

# Defina o diretório de trabalho no container
WORKDIR /app

# Copie os arquivos do projeto para o diretório de trabalho
COPY . /app

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Exponha a porta que sua aplicação vai rodar
EXPOSE 5002

# Comando para executar a aplicação
CMD ["python", "app.py"]
