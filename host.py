import socket  # Biblioteca para comunicação em rede
import time    # Biblioteca para funções de tempo (sleep)
import os      # Biblioteca para operações do sistema operacional

# --- FUNÇÕES DE ARQUIVO (SÓ FUNCIONAM EM TCP) ---
def enviar_arquivo(conn):  # Função para enviar arquivo através da conexão
    try:
        # Pede ao usuário o caminho do arquivo
        caminho = input("Digite o caminho do arquivo para enviar: ")
        
        # Verifica se o arquivo existe no sistema
        if not os.path.exists(caminho):
            print("Arquivo não encontrado.")  # Exibe mensagem de erro
            conn.send("ERRO_ARQUIVO".encode("utf-8"))  # Envia erro para o cliente
            return  # Sai da função
        
        # Pega apenas o nome do arquivo (sem o caminho completo)
        nome_arquivo = os.path.basename(caminho)
        conn.send(nome_arquivo.encode("utf-8"))  # Envia o nome do arquivo
        time.sleep(0.1)  # Pequena pausa para garantir que a mensagem chegue

        # Abre o arquivo em modo binário para leitura
        with open(caminho, "rb") as f:
            while True:  # Loop infinito para ler o arquivo
                bytes_lidos = f.read(4096)  # Lê 4KB do arquivo
                if not bytes_lidos: break  # Se não há mais dados, sai do loop
                conn.sendall(bytes_lidos)  # Envia os bytes lidos
        
        time.sleep(0.1)  # Pausa antes de enviar sinal de fim
        conn.send(b"<EOF>")  # Envia sinal indicando fim do arquivo
        print("Arquivo e sinal de fim enviados.")  # Confirma envio

    except Exception as e:  # Captura qualquer erro
        print(f"Erro ao enviar arquivo: {e}")  # Exibe o erro

def receber_arquivo(conn):  # Função para receber arquivo do cliente
    try:
        # Recebe o nome do arquivo
        nome_arquivo = conn.recv(1024).decode("utf-8")
        
        # Verifica se houve erro no cliente
        if nome_arquivo == "ERRO_ARQUIVO":
            print("O Cliente tentou enviar um arquivo que não existe.")
            return  # Sai da função
        
        print(f"Recebendo '{nome_arquivo}'...")  # Informa que está recebendo
        
        # Abre arquivo para escrita em modo binário
        with open(nome_arquivo, "wb") as f:
            while True:  # Loop para receber dados
                bytes_recebidos = conn.recv(4096)  # Recebe até 4KB
                
                # Verifica se chegou o sinal de fim
                if b"<EOF>" in bytes_recebidos:
                    # Remove o sinal de fim e escreve o resto
                    f.write(bytes_recebidos.replace(b"<EOF>", b''))
                    break  # Sai do loop
                
                f.write(bytes_recebidos)  # Escreve dados no arquivo
        
        print("Arquivo recebido com sucesso!")  # Confirma recebimento

    except Exception as e:  # Captura erros
        print(f"Erro ao receber arquivo: {e}")

# --- CONFIGURAÇÃO E CONEXÃO (Agora com escolha de protocolo) ---
server_IP = "0.0.0.0"  # IP do servidor (aceita conexões de qualquer IP)
porta = 50000  # Porta de comunicação
ADDR = (server_IP, porta)  # Tupla com endereço completo
cliente_addr = None  # Variável para guardar endereço do cliente UDP

# Pergunta ao usuário qual protocolo usar
escolha_protocolo = input("Escolha o protocolo (1 para TCP, 2 para UDP): ")

if escolha_protocolo == '1':  # Se escolheu TCP
    # Cria socket TCP (SOCK_STREAM = TCP)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(ADDR)  # Associa o socket ao endereço
    sock.listen()  # Coloca o socket para escutar conexões
    print("Aguardando conexão do cliente TCP...")
    
    # Aceita a conexão do cliente
    cliente, cliente_addr = sock.accept()
    print(f"Cliente conectado pelo endereço: {cliente_addr}")
    
else:  # Se escolheu UDP
    # Cria socket UDP (SOCK_DGRAM = UDP)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(ADDR)  # Associa o socket ao endereço
    print("Aguardando primeira mensagem do cliente UDP...")
    
    # Em UDP, recebe a primeira mensagem para "conectar"
    dados, cliente_addr = sock.recvfrom(1024)
    print(f"Cliente estabelecido pelo endereço: {cliente_addr}")

# Exibe instruções para o usuário
print("OS COMANDOS SÃO /sair e /enviar 'nome.extensão' (apenas TCP)")

# --- LOOP PRINCIPAL MODIFICADO PARA ACEITAR UDP ---
while True:  # Loop infinito do chat
    try:
        print("\n--- Turno do Cliente ---")  # Indica turno do cliente
        
        # Recebe a ação do cliente
        if escolha_protocolo == '1':  # TCP
            acao_cliente = cliente.recv(1024).decode("utf-8")
        else:  # UDP
            # Recebe dados e endereço do cliente
            dados, cliente_addr = sock.recvfrom(1024)
            acao_cliente = dados.decode("utf-8")

        # Verifica qual ação o cliente quer fazer
        if acao_cliente == "CHAT":  # Se é uma mensagem de chat
            if escolha_protocolo == '1':  # TCP
                msg = cliente.recv(1024).decode("utf-8")  # Recebe mensagem
            else:  # UDP
                dados, cliente_addr = sock.recvfrom(1024)  # Recebe mensagem
                msg = dados.decode("utf-8")
            print(f"Cliente: {msg}")  # Exibe mensagem do cliente

        elif acao_cliente == "ENVIAR":  # Se quer enviar arquivo
            if escolha_protocolo == '1':  # Só funciona em TCP
                receber_arquivo(cliente)  # Chama função para receber
            else:  # Em UDP ignora
                print("Cliente tentou enviar arquivo em modo UDP. Ação ignorada.")
        
        elif acao_cliente.lower() == "sair":  # Se cliente quer sair
            print("Cliente encerrou o chat.")
            break  # Sai do loop principal
        
        print("\n--- Seu Turno (Host) ---")  # Indica turno do host
        hostmsg = input("Você: ")  # Recebe mensagem do usuário host

        # Verifica se host quer enviar arquivo
        if hostmsg.startswith('/enviar ') and escolha_protocolo == '1':
            cliente.send("ENVIAR".encode("utf-8"))  # Avisa que vai enviar
            enviar_arquivo(cliente)  # Chama função de envio
        
        # Se tentou enviar arquivo em UDP
        elif hostmsg.startswith('/enviar ') and escolha_protocolo == '2':
            print("ERRO: Envio de arquivos só é permitido em TCP.")
            # Envia mensagem vazia para manter o protocolo
            sock.sendto("CHAT".encode("utf-8"), cliente_addr)
            sock.sendto("".encode("utf-8"), cliente_addr)
        
        # Se host quer sair
        elif hostmsg.lower() == '/sair':
            if escolha_protocolo == '1':  # TCP
                cliente.send("SAIR".encode("utf-8"))  # Avisa o cliente
            else:  # UDP
                sock.sendto("SAIR".encode("utf-8"), cliente_addr)
            print("Você encerrou o chat.")
            break  # Sai do loop
        
        else:  # Se não é comando, é mensagem normal
            if escolha_protocolo == '1':  # TCP
                cliente.send("CHAT".encode("utf-8"))  # Avisa que é chat
                cliente.send(hostmsg.encode("utf-8"))  # Envia mensagem
            else:  # UDP
                sock.sendto("CHAT".encode("utf-8"), cliente_addr)  # Avisa que é chat
                sock.sendto(hostmsg.encode("utf-8"), cliente_addr)  # Envia mensagem

    except (ConnectionResetError, BrokenPipeError, OSError):  # Captura erros de conexão
        print("\nConexão com o cliente perdida.")
        break  # Sai do loop

# Fecha as conexões
if escolha_protocolo == '1': cliente.close()  # Fecha conexão TCP se existir
sock.close()  # Fecha o socket principal