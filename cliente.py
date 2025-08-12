# cliente.py (versão com chat inteligente e input de IP)
import socket  # Importa biblioteca para conexões de rede
import time    # Importa biblioteca para controle de tempo
import os      # Importa biblioteca para operações do sistema operacional

# As funções de arquivo não mudam
def enviar_arquivo(conn, caminho_arquivo):  # Função para enviar arquivo para o host
    try:  # Tenta executar o código
        if not os.path.exists(caminho_arquivo):  # Verifica se o arquivo existe
            print("Arquivo não encontrado.")  # Exibe mensagem de erro
            conn.send("ERRO_ARQUIVO".encode("utf-8"))  # Envia erro para o host
            return  # Sai da função
       
        nome_arquivo = os.path.basename(caminho_arquivo)  # Pega apenas o nome do arquivo
        conn.send(nome_arquivo.encode("utf-8"))  # Envia o nome do arquivo para o host
        time.sleep(0.1)  # Pausa para garantir que o nome seja enviado primeiro
        with open(caminho_arquivo, "rb") as f:  # Abre o arquivo em modo binário para leitura
            conn.send(f.read())  # Lê todo o arquivo e envia para o host
        print("Arquivo enviado.")  # Confirma que o arquivo foi enviado
    except Exception as e:  # Se der erro, captura a exceção
        print(f"Erro ao enviar arquivo: {e}")  # Exibe a mensagem de erro

def receber_arquivo(conn):  # Função para receber arquivo do host
    try:  # Tenta executar o código
        nome_arquivo = conn.recv(1024).decode("utf-8")  # Recebe o nome do arquivo (até 1024 bytes)
        if nome_arquivo == "ERRO_ARQUIVO":  # Verifica se houve erro no host
            print("O Host tentou enviar um arquivo que não existe.")  # Exibe mensagem de erro
            return  # Sai da função
        print(f"Recebendo '{nome_arquivo}'...")  # Informa que está recebendo o arquivo
        with open(nome_arquivo, "wb") as f:  # Cria/abre o arquivo em modo binário para escrita
            conteudo = conn.recv(4096 * 1024)  # Recebe o conteúdo do arquivo (até 4MB)
            f.write(conteudo)  # Escreve o conteúdo no arquivo
        print("Arquivo recebido com sucesso!")  # Confirma que recebeu o arquivo
    except Exception as e:  # Se der erro, captura a exceção
        print(f"Erro ao receber arquivo: {e}")  # Exibe a mensagem de erro

# ### MUDANÇA 1: INPUT DINÂMICO DO IP ###
# --- CONFIGURAÇÃO E CONEXÃO (com IP manual/fixo) ---
porta = 50000  # Porta que vai usar para conectar
cliente_IP = "127.0.0.1"  # IP do host (127.0.0.1 é o próprio computador)
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria um socket TCP
print(f"Tentando conectar ao Host em {cliente_IP}:{porta}...")  # Informa que está tentando conectar
cliente.connect((cliente_IP, porta))  # Conecta ao host no IP e porta especificados
print("Conectado ao Host!")  # Confirma que conectou com sucesso
print("OS COMANDOS SÃO /sair e /enviar 'nome.extensão'")  # Mostra os comandos disponíveis

# ### MUDANÇA 2: O LOOP PRINCIPAL FICOU MAIS INTELIGENTE ###
while True:  # Loop infinito para manter a conversa
    try:  # Tenta executar o código
        print("\n--- Seu Turno (Cliente) ---")  # Indica que é a vez do cliente
        msgcliente = input("Você: ")  # Pede para o cliente digitar uma mensagem
        if msgcliente.startswith('/enviar '):  # Se a mensagem começa com "/enviar "
            cliente.send("ENVIAR".encode("utf-8"))  # Avisa o host que vai enviar arquivo
            caminho_real = msgcliente.split(' ', 1)[1]  # Pega só o caminho do arquivo (remove "/enviar ")
            enviar_arquivo(cliente, caminho_real)  # Chama a função para enviar o arquivo
       
        elif msgcliente.lower() == '/sair':  # Se o cliente digitar "/sair"
            cliente.send("SAIR".encode("utf-8"))  # Avisa o host que vai sair
            print("Você encerrou o chat.")  # Confirma que está saindo
            break  # Sai do loop principal
       
        else:  # Se não for comando, é chat
            cliente.send("CHAT".encode("utf-8"))  # Avisa o host que é mensagem de chat
            cliente.send(msgcliente.encode("utf-8"))  # Envia a mensagem para o host

        # --- ETAPA 2: VEZ DO CLIENTE ESCUTAR ---
        print("\n--- Turno do Host ---")  # Indica que é a vez do host
        print("Aguardando ação do Host...")  # Informa que está esperando o host
        acao_host = cliente.recv(1024).decode("utf-8")  # Recebe a ação que o host quer fazer
        if acao_host == "CHAT":  # Se o host quer conversar
            msg = cliente.recv(1024).decode("utf-8")  # Recebe a mensagem do host
            print(f"Host: {msg}")  # Exibe a mensagem do host
        elif acao_host == "ENVIAR":  # Se o host quer enviar arquivo
            receber_arquivo(cliente)  # Chama a função para receber arquivo
        elif acao_host == "SAIR":  # Se o host quer sair
            print("O Host encerrou o chat.")  # Informa que o host saiu
            break  # Sai do loop principal
    except (ConnectionResetError, BrokenPipeError):  # Se a conexão for perdida
        print("\nConexão com o Host perdida.")  # Informa que perdeu a conexão
        break  # Sai do loop principal

cliente.close()  # Fecha a conexão com o host