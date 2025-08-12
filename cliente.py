import socket  # Biblioteca para comunicação em rede
import time    # Biblioteca para funções de tempo (sleep)
import os      # Biblioteca para operações do sistema operacional

def enviar_arquivo(conn):  # Função para enviar arquivo para o host
    try:
        # Pede ao usuário o caminho do arquivo
        caminho = input("Digite o caminho do arquivo para enviar: ")
        
        # Verifica se o arquivo existe no sistema
        if not os.path.exists(caminho):
            print("Arquivo não encontrado.")  # Exibe mensagem de erro
            conn.send("ERRO_ARQUIVO".encode("utf-8"))  # Envia erro para o host
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

def receber_arquivo(conn):  # Função para receber arquivo do host
    try:
        # Recebe o nome do arquivo
        nome_arquivo = conn.recv(1024).decode("utf-8")
        
        # Verifica se houve erro no host
        if nome_arquivo == "ERRO_ARQUIVO":
            print("O Host tentou enviar um arquivo que não existe.")
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

# ### MUDANÇA PRINCIPAL AQUI ###
# --- CONFIGURAÇÃO E CONEXÃO com IPv4/IPv6 ---
porta = 50000  # Porta de comunicação (mesma do host)

# Pede IP do host com exemplos de IPv4 e IPv6
cliente_IP = input("Digite o IP do Host (Ex: 127.0.0.1 ou ::1): ") or "127.0.0.1"

# Pergunta ao usuário qual protocolo usar
escolha_protocolo = input("Escolha o protocolo (1 para TCP, 2 para UDP): ")

# Define o tipo de socket baseado na escolha do usuário
if escolha_protocolo == '1':
    tipo_socket = socket.SOCK_STREAM  # TCP - conexão confiável
    print(f"Tentando conectar ao Host TCP em {cliente_IP}:{porta}...")
else:
    tipo_socket = socket.SOCK_DGRAM  # UDP - sem conexão
    print(f"Estabelecendo contato UDP com {cliente_IP}:{porta}...")

# Lógica robusta para se conectar a um endereço IPv4 ou IPv6
try:
    # Usamos getaddrinfo para que o Python descubra automaticamente
    # se o IP fornecido é IPv4 ou IPv6 e configure corretamente o socket
    # AF_UNSPEC = permite tanto IPv4 quanto IPv6
    info_addr = socket.getaddrinfo(cliente_IP, porta, socket.AF_UNSPEC, tipo_socket)[0]
    
    # Cria o socket usando as informações corretas (IPv4 ou IPv6)
    sock = socket.socket(info_addr[0], info_addr[1])
    
    # Se for TCP, conecta ao host. Se for UDP, já está "pronto" para enviar.
    if escolha_protocolo == '1':  # TCP precisa estabelecer conexão
        sock.connect(info_addr[4])  # Conecta usando o endereço correto
        print("Conectado ao Host!")
    else:  # UDP não precisa conectar, só enviar
        # Em UDP, a primeira mensagem já estabelece o contato com o host
        sock.sendto("OI_HOST".encode("utf-8"), info_addr[4])
        print("Contato UDP estabelecido!")

except Exception as e:  # Se algo der errado na conexão
    print(f"Falha ao conectar: {e}")
    exit()  # Encerra o programa

# Exibe instruções para o usuário
print("OS COMANDOS SÃO /sair e /enviar 'nome.extensão' (apenas TCP)")

# --- LOOP PRINCIPAL ---
while True:  # Loop infinito do chat
    try:
        print("\n--- Seu Turno (Cliente) ---")  # Indica turno do cliente
        msgcliente = input("Você: ")  # Recebe mensagem do usuário cliente

        # Verifica se cliente quer enviar arquivo
        if msgcliente.startswith('/enviar ') and escolha_protocolo == '1':
            sock.send("ENVIAR".encode("utf-8"))  # Avisa que vai enviar
            enviar_arquivo(sock)  # Chama função de envio
            
        # Se tentou enviar arquivo em UDP
        elif msgcliente.startswith('/enviar ') and escolha_protocolo == '2':
            print("ERRO: Envio de arquivos só é permitido em TCP, peste ruim!")
            # Envia mensagem vazia para manter o protocolo
            sock.sendto("CHAT".encode("utf-8"), (cliente_IP, porta))
            sock.sendto("".encode("utf-8"), (cliente_IP, porta))
            
        # Se cliente quer sair
        elif msgcliente.lower() == '/sair':
            if escolha_protocolo == '1':  # TCP
                sock.send("SAIR".encode("utf-8"))  # Avisa o host
            else:  # UDP
                sock.sendto("SAIR".encode("utf-8"), (cliente_IP, porta))
            print("Você encerrou o chat.")
            break  # Sai do loop
            
        else:  # Se não é comando, é mensagem normal
            if escolha_protocolo == '1':  # TCP
                sock.send("CHAT".encode("utf-8"))  # Avisa que é chat
                sock.send(msgcliente.encode("utf-8"))  # Envia mensagem
            else:  # UDP
                sock.sendto("CHAT".encode("utf-8"), (cliente_IP, porta))  # Avisa que é chat
                sock.sendto(msgcliente.encode("utf-8"), (cliente_IP, porta))  # Envia mensagem

        print("\n--- Turno do Host ---")  # Indica turno do host
        print("Aguardando ação do Host...")  # Informa que está esperando
        
        # Recebe ação do host
        if escolha_protocolo == '1':  # TCP
            acao_host = sock.recv(1024).decode("utf-8")
        else:  # UDP
            dados, _ = sock.recvfrom(1024)  # Recebe dados (ignora endereço com _)
            acao_host = dados.decode("utf-8")
            
        # Verifica qual ação o host quer fazer
        if acao_host == "CHAT":  # Se é uma mensagem de chat
            if escolha_protocolo == '1':  # TCP
                msg = sock.recv(1024).decode("utf-8")  # Recebe mensagem
            else:  # UDP
                dados, _ = sock.recvfrom(1024)  # Recebe mensagem
                msg = dados.decode("utf-8")
            print(f"Host: {msg}")  # Exibe mensagem do host
            
        elif acao_host == "ENVIAR":  # Se host quer enviar arquivo
            if escolha_protocolo == '1':  # Só funciona em TCP
                receber_arquivo(sock)  # Chama função para receber
            else:  # Em UDP ignora
                print("Host tentou enviar arquivo em modo UDP. Ação ignorada.")
                
        elif acao_host.lower() == "sair":  # Se host quer sair
            print("O Host encerrou o chat.")
            break  # Sai do loop principal
            
    except (ConnectionResetError, BrokenPipeError, OSError):  # Captura erros de conexão
        print("\nConexão com o Host perdida.")
        break  # Sai do loop

# Fecha o socket
sock.close()  # Fecha a conexão