import socket  # Biblioteca para comunicação em rede
import time    # Biblioteca para funções de tempo (sleep)
import os      # Biblioteca para operações do sistema operacional

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

# ### MUDANÇA PRINCIPAL AQUI ###
# --- CONFIGURAÇÃO E CONEXÃO com LÓGICA UNIFICADA para IPv4/IPv6 ---
porta = 50000  # Porta de comunicação
cliente_addr = None  # Variável para guardar endereço do cliente

# Pergunta ao usuário qual protocolo usar
escolha_protocolo = input("Escolha o protocolo (1 para TCP, 2 para UDP): ")

# Define o tipo de socket baseado na escolha do usuário
if escolha_protocolo == '1':
    tipo_socket = socket.SOCK_STREAM  # TCP - conexão confiável
    print("Iniciando servidor em modo TCP...")
else:
    tipo_socket = socket.SOCK_DGRAM  # UDP - sem conexão
    print("Iniciando servidor em modo UDP...")

# Lógica robusta e unificada para criar um socket que aceita tanto IPv4 quanto IPv6
try:
    # Usamos getaddrinfo para que o Python escolha a melhor configuração
    # None = escuta em todos os IPs disponíveis da máquina
    # AF_UNSPEC = permite tanto IPv4 quanto IPv6
    # AI_PASSIVE = configuração para servidor (escutar conexões)
    info_addr = socket.getaddrinfo(None, porta, socket.AF_UNSPEC, tipo_socket, 0, socket.AI_PASSIVE)[0]
    
    # Cria o socket usando as informações obtidas pelo getaddrinfo
    sock = socket.socket(info_addr[0], info_addr[1])
    
    # Se o socket for IPv6, desativa o modo "apenas IPv6"
    # Isso permite que o servidor também aceite conexões IPv4
    if info_addr[0] == socket.AF_INET6:
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        
    # Associa o socket ao endereço e porta
    sock.bind(info_addr[4])
    print(f"Servidor escutando em modo Dual-Stack (IPv4/IPv6) na porta {porta}")

except Exception as e:  # Se algo der errado na criação do servidor
    print(f"Falha ao iniciar o servidor: {e}")
    exit()  # Encerra o programa

# O resto da lógica de conexão (específica para cada protocolo)
if escolha_protocolo == '1':  # TCP
    sock.listen()  # Coloca o socket para escutar conexões
    # Aceita a primeira conexão que chegar
    conn, cliente_addr = sock.accept()
    print(f"Cliente conectado pelo endereço: {cliente_addr}")
else:  # UDP
    print(f"Aguardando primeira mensagem na porta {porta}...")
    # Em UDP, a primeira mensagem recebida estabelece o "cliente"
    dados, cliente_addr = sock.recvfrom(1024)
    print(f"Cliente estabelecido pelo endereço: {cliente_addr}")

# Exibe instruções para o usuário
print("OS COMANDOS SÃO /sair e /enviar 'nome.extensão' (apenas TCP)")

# --- LOOP PRINCIPAL (sem alterações) ---
while True:  # Loop infinito do chat
    try:
        print("\n--- Turno do Cliente ---")  # Indica turno do cliente
        
        # Recebe a ação do cliente
        if escolha_protocolo == '1':  # TCP
            acao_cliente = conn.recv(1024).decode("utf-8")
        else:  # UDP
            # Recebe dados e endereço do cliente
            dados, cliente_addr = sock.recvfrom(1024)
            acao_cliente = dados.decode("utf-8")

        # Verifica qual ação o cliente quer fazer
        if acao_cliente == "CHAT":  # Se é uma mensagem de chat
            if escolha_protocolo == '1':  # TCP
                msg = conn.recv(1024).decode("utf-8")  # Recebe mensagem
            else:  # UDP
                dados, cliente_addr = sock.recvfrom(1024)  # Recebe mensagem
                msg = dados.decode("utf-8")
            print(f"Cliente: {msg}")  # Exibe mensagem do cliente
            
        elif acao_cliente == "ENVIAR":  # Se quer enviar arquivo
            if escolha_protocolo == '1':  # Só funciona em TCP
                receber_arquivo(conn)  # Chama função para receber
            else:  # Em UDP ignora
                print("Cliente tentou enviar arquivo em modo UDP. Ação ignorada.")
                
        elif acao_cliente.lower() == "sair":  # Se cliente quer sair
            print("Cliente encerrou o chat.")
            break  # Sai do loop principal
        
        print("\n--- Seu Turno (Host) ---")  # Indica turno do host
        hostmsg = input("Você: ")  # Recebe mensagem do usuário host

        # Verifica se host quer enviar arquivo
        if hostmsg.startswith('/enviar ') and escolha_protocolo == '1':
            conn.send("ENVIAR".encode("utf-8"))  # Avisa que vai enviar
            enviar_arquivo(conn)  # Chama função de envio
            
        # Se tentou enviar arquivo em UDP
        elif hostmsg.startswith('/enviar ') and escolha_protocolo == '2':
            print("ERRO: Envio de arquivos só é permitido em TCP.")
            # Envia mensagem vazia para manter o protocolo
            sock.sendto("CHAT".encode("utf-8"), cliente_addr)
            sock.sendto("".encode("utf-8"), cliente_addr)
            
        # Se host quer sair
        elif hostmsg.lower() == '/sair':
            if escolha_protocolo == '1':  # TCP
                conn.send("SAIR".encode("utf-8"))  # Avisa o cliente
            else:  # UDP
                sock.sendto("SAIR".encode("utf-8"), cliente_addr)
            print("Você encerrou o chat.")
            break  # Sai do loop
            
        else:  # Se não for comando, é chat
            if escolha_protocolo == '1':  # TCP
                conn.send("CHAT".encode("utf-8"))  # Avisa que é chat
                conn.send(hostmsg.encode("utf-8"))  # Envia mensagem
            else:  # UDP
                sock.sendto("CHAT".encode("utf-8"), cliente_addr)  # Avisa que é chat
                sock.sendto(hostmsg.encode("utf-8"), cliente_addr)  # Envia mensagem
                
    except (ConnectionResetError, BrokenPipeError, OSError):  # Captura erros de conexão
        print("\nConexão com o cliente perdida.")
        break  # Sai do loop

# Fecha as conexões
if escolha_protocolo == '1': conn.close()  # Fecha conexão TCP se existir
sock.close()  # Fecha o socket principal