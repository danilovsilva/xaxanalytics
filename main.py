from parser_main import CsGoDemoParser
import os
import requests


# Obter a lista de arquivos na pasta "demos/"
diretorio = "demos/"
arquivos = os.listdir(diretorio)

# Percorrer todos os arquivos
for arquivo in arquivos:
    # Construir o caminho completo do arquivo
    caminho_arquivo = os.path.join(diretorio, arquivo)

    # Executar o parser
    a = CsGoDemoParser(demo_file=caminho_arquivo)
    a.main()

    # Deletar o arquivo
    os.remove(caminho_arquivo)

# Caminho do arquivo JSON a ser enviado
# caminho_arquivo = "output/"
# arquivos = os.listdir(caminho_arquivo)

# for arquivo in arquivos:
#     # Abrir o arquivo JSON
#     with open(caminho_arquivo + arquivo, "rb") as json:
#         # Configurar o cabeçalho do request com o tipo de conteúdo
#         headers = {'Content-Type': 'application/json'}

#         # Enviar o POST request com o arquivo JSON
#         response = requests.post('https://xaxanalytics.fly.dev/api/matches', headers=headers, data=json)

#     # Verificar o status da resposta
#     if response.status_code == 200:
#         print("Arquivo JSON enviado com sucesso.")
#     else:
#         print("Erro ao enviar o arquivo JSON:", response.text)

