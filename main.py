from parser_main import CsGoDemoParser
from downloader import DownloadFTP
import os
import requests


# get the files list in the right folder depending on the environment
if os.getenv('env') == "PRD":
    diretorio = "/app/demos/"
else:
    diretorio = "demos/"

downloader = DownloadFTP()
downloader.download_demos(diretorio)

arquivos = os.listdir(diretorio)

# Percorrer todos os arquivos
for arquivo in arquivos:
    # Construir o caminho completo do arquivo
    caminho_arquivo = os.path.join(diretorio, arquivo)

    # Executar o parser
    print("Iniciando parser do arquivo "+str(caminho_arquivo))
    a = CsGoDemoParser(demo_file=caminho_arquivo)
    a.main()
    print("Finalizado parser do arquivo "+str(caminho_arquivo))

    # Deletar o arquivo
    # os.remove(caminho_arquivo)

# Caminho do arquivo JSON a ser enviado
caminho_arquivo = "output/"
arquivos = os.listdir(caminho_arquivo)

for arquivo in arquivos:
    # Abrir o arquivo JSON
    print("Iniciando envio do arquivo "+str(arquivo))
    with open(caminho_arquivo + arquivo, "rb") as json:
        # Configurar o cabeçalho do request com o tipo de conteúdo
        headers = {'Content-Type': 'application/json'}

        # Enviar o POST request com o arquivo JSON
        response = requests.post(
            'https://xaxanalytics.fly.dev/api/matches', headers=headers, data=json)

    # Verificar o status da resposta
    if response.status_code == 200:
        print(str(arquivo)+" enviado com sucesso.")
        # os.remove(caminho_arquivo + arquivo)
    else:
        print("Erro ao enviar o arquivo JSON:", response.text)
