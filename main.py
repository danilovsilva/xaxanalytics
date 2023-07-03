import sys
from parser_main import CsGoDemoParser
from downloader import DownloadFTP
import os
import requests
import time


def run(diretorio, output_path):
    print("[DVS] - Starting download from FTP")
    downloader = DownloadFTP()
    print("[DVS] - diretorio: "+diretorio)
    print("[DVS] - output_path: "+output_path)
    downloader.download_demos(diretorio)

    arquivos = os.listdir(diretorio)
    print("[DVS] - arquivos: "+str(arquivos))

    # Percorrer todos os arquivos
    for arquivo in arquivos:
        # Construir o caminho completo do arquivo
        caminho_arquivo = os.path.join(diretorio, arquivo)

        # Executar o parser
        print("Starting parse of file "+str(caminho_arquivo))
        a = CsGoDemoParser(demo_file=caminho_arquivo, output=output_path)
        a.main()
        print("Finished parser of file "+str(caminho_arquivo))

    # Caminho do arquivo JSON a ser enviado
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    arquivos = os.listdir(output_path)

    for arquivo in arquivos:
        # Abrir o arquivo JSON
        if arquivo.endswith('.json') and 'payload' in arquivo:
            print("Sending file "+str(arquivo))
            with open(output_path + arquivo, "rb") as json:
                # Configurar o cabeçalho do request com o tipo de conteúdo
                headers = {'Content-Type': 'application/json'}

                # Enviar o POST request com o arquivo JSON
                response = requests.post(
                    'https://xaxanalytics.fly.dev/api/matches', headers=headers, data=json)

            # Verificar o status da resposta
            if response.status_code == 200:
                print(str(arquivo)+" sent sucesfully.")
                # os.remove(caminho_arquivo + arquivo)
            else:
                print("Erro sending JSON file:", response.text)


if __name__ == "__main__":
    # diretorio = "demos/"
    # output_path = "output/"
    diretorio = "/tmp/demos/"
    output_path = "/tmp/output/"
    run(diretorio, output_path)


def handler(event, context):
    start_date = time.time()
    diretorio = "/tmp/demos/"
    output_path = "/tmp/output/"

    run(diretorio, output_path)
    end_date = time.time()
    total_time = end_date - start_date
    return 'Hello from AWS Lambda using Python' + sys.version + '! ' + str(total_time)
