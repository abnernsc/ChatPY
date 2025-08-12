# host.py (versão com chat inteligente)
import socket  # Importa biblioteca para conexões de rede
import time    # Importa biblioteca para controle de tempo
import os      # Importa biblioteca para operações do sistema operacional

# --- FUNÇÕES DE ARQUIVO (não mudam, estão perfeitas) ---
def enviar_arquivo(conn):  # Função para enviar arquivos para o cliente
    try:  # Tenta executar o código, se der erro vai para except
        caminho = input("Digite o caminho do arquivo para enviar: ")  # Pede o caminho do arquivo
        if not os.path.exists(caminho):  # Verifica se o arquivo existe
            print("Arquivo não encontrado.")  # Exibe mensagem de erro
            conn.send("ERRO_ARQUIVO".encode("utf-8"))  # Envia mensagem de erro para o cliente
            return  # Sai da função
        nome_arquivo = os.path.basename(caminho)  # Pega apenas o nome do arquivo (sem o caminho)
        conn.send(nome_arquivo.encode("utf-8"))  # Envia o nome do arquivo para o cliente
        time.sleep(0.1)  # Pausa por 0,1 segundo para garantir que o nome seja enviado primeiro
        with open(caminho, "rb") as f:  # Abre o arquivo em modo binário para leitura
            conn.send(f.read())  # Lê todo o arquivo e envia para o cliente
        print("Arquivo enviado.")  # Confirma que o arquivo foi enviado
    except Exception as e:  # Se der algum erro, captura a exceção
        print(f"Erro ao enviar arquivo: {e}")  # Exibe a mensagem de erro

def receber_arquivo(conn):  # Função para receber arquivos do cliente
    try:  # Tenta executar o código
        nome_arquivo = conn.recv(1024).decode("utf-8")  # Recebe o nome do arquivo (até 1024 bytes)
        if nome_arquivo == "ERRO_ARQUIVO":  # Verifica se houve erro no cliente
            print("O Cliente tentou enviar um arquivo que não existe.")  # Exibe mensagem de erro
            return  # Sai da função
        print(f"Recebendo '{nome_arquivo}'...")  # Informa que está recebendo o arquivo
        with open(nome_arquivo, "wb") as f:  # Cria/abre o arquivo em modo binário para escrita
            conteudo = conn.recv(4096 * 1024)  # Recebe o conteúdo do arquivo (até 4MB)
            f.write(conteudo)  # Escreve o conteúdo no arquivo
        print("Arquivo recebido com sucesso!")  # Confirma que recebeu o arquivo
    except Exception as e:  # Se der erro, captura a exceção
        print(f"Erro ao receber arquivo: {e}")  # Exibe a mensagem de erro

# --- CONFIGURAÇÃO E CONEXÃO (não muda) ---
server_IP = "0.0.0.0"  # IP do servidor (0.0.0.0 aceita conexões de qualquer lugar)
porta = 50000  # Porta que o servidor vai usar
ADDR = (server_IP, porta)  # Tupla com IP e porta
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria um socket TCP
server.bind(ADDR)  # Vincula o socket ao endereço e porta
server.listen()  # Coloca o servidor em modo de escuta
print("Aguardando conexão do cliente...")  # Informa que está esperando conexão
cliente, end = server.accept()  # Aceita a conexão do cliente
print(f"Cliente conectado pelo endereço: {end}")  # Mostra o endereço do cliente conectado
print("OS COMANDOS SÃO /sair e /enviar 'nome.extensão'")  # Mostra os comandos disponíveis

# ### MUDANÇA 2: O LOOP PRINCIPAL FICOU MAIS INTELIGENTE ###
while True:  # Loop infinito para manter a conversa
    try:  # Tenta executar o código
        print("\n--- Turno do Cliente ---")  # Indica que é a vez do cliente
        acao_cliente = cliente.recv(1024).decode("utf-8")  # Recebe a ação que o cliente quer fazer
        if acao_cliente == "CHAT":  # Se o cliente quer conversar
            msg = cliente.recv(1024).decode("utf-8")  # Recebe a mensagem do cliente
            print(f"Cliente: {msg}")  # Exibe a mensagem do cliente
        elif acao_cliente == "ENVIAR":  # Se o cliente quer enviar arquivo
            receber_arquivo(cliente)  # Chama a função para receber arquivo
        elif acao_cliente == "SAIR":  # Se o cliente quer sair
            print("Cliente encerrou o chat.")  # Informa que o cliente saiu
            break  # Sai do loop principal
       
        # --- Agora é a vez do Host ---
        print("\n--- Seu Turno (Host) ---")  # Indica que é a vez do host
        hostmsg = input("Você: ")  # Pede para o host digitar uma mensagem
        if hostmsg.startswith('/enviar '):  # Se a mensagem começa com "/enviar "
            cliente.send("ENVIAR".encode("utf-8"))  # Avisa o cliente que vai enviar arquivo
            # Remove o comando '/enviar ' da string para pegar só o caminho
            caminho_real = hostmsg.split(' ', 1)[1]  # Pega só o caminho do arquivo (remove "/enviar ")
            # Vamos recriar a função 'enviar_arquivo' aqui de forma simplificada
            if os.path.exists(caminho_real):  # Verifica se o arquivo existe
                nome_arquivo = os.path.basename(caminho_real)  # Pega apenas o nome do arquivo
                cliente.send(nome_arquivo.encode("utf-8"))  # Envia o nome do arquivo
                time.sleep(0.1)  # Pausa para garantir que o nome seja enviado primeiro
                with open(caminho_real, "rb") as f:  # Abre o arquivo em modo binário
                    cliente.send(f.read())  # Lê e envia todo o conteúdo do arquivo
                print("Arquivo enviado.")  # Confirma que enviou o arquivo
            else:  # Se o arquivo não existe
                print("Arquivo não encontrado.")  # Exibe mensagem de erro
                cliente.send("ERRO_ARQUIVO".encode("utf-8"))  # Envia erro para o cliente
        elif hostmsg.lower() == '/sair':  # Se o host digitar "/sair"
            cliente.send("SAIR".encode("utf-8"))  # Avisa o cliente que vai sair
            print("Você encerrou o chat.")  # Confirma que está saindo
            break  # Sai do loop principal
       
        else:  # Se não for comando, é chat
            cliente.send("CHAT".encode("utf-8"))  # Avisa o cliente que é mensagem de chat
            cliente.send(hostmsg.encode("utf-8"))  # Envia a mensagem para o cliente
    except (ConnectionResetError, BrokenPipeError):  # Se a conexão for perdida
        print("\nConexão com o cliente perdida.")  # Informa que perdeu a conexão
        break  # Sai do loop principal

cliente.close()  # Fecha a conexão com o cliente
server.close()   # Fecha o servidor