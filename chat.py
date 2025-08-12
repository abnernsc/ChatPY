import socket  # Para comunicação de rede
import time    # Para pausas no código
import os      # Para trabalhar com arquivos

def enviar_arquivo_tcp(sock):
    """Envia um arquivo via TCP."""
    try:  # Tenta executar o código
        caminho = input("Digite o caminho do arquivo para enviar: ")  # Pede o arquivo ao usuário
        if not os.path.exists(caminho):  # Verifica se o arquivo existe
            print("Arquivo não encontrado.")  # Avisa se não existe
            sock.send("ERRO_ARQUIVO".encode("utf-8"))  # Avisa o outro lado
            return  # Para a função
        
        nome_arquivo = os.path.basename(caminho)  # Pega só o nome do arquivo
        sock.send(nome_arquivo.encode("utf-8"))  # Envia o nome
        time.sleep(0.1)  # Pequena pausa
        
        with open(caminho, "rb") as f:  # Abre o arquivo para ler
            while True:  # Loop para ler pedaços
                bytes_lidos = f.read(4096)  # Lê 4KB
                if not bytes_lidos:  # Se acabou o arquivo
                    break  # Para o loop
                sock.sendall(bytes_lidos)  # Envia o pedaço
        
        time.sleep(0.1)  # Pausa
        sock.send(b"<QSL>")  # Sinal de fim
        print("Arquivo TCP enviado.")  # Confirma envio
    except Exception as e:  # Se der erro
        print(f"Erro ao enviar arquivo TCP: {e}")  # Mostra o erro

def receber_arquivo_tcp(sock):
    """Recebe um arquivo via TCP."""
    try:  # Tenta executar
        nome_arquivo = sock.recv(1024).decode("utf-8")  # Recebe o nome do arquivo
        if nome_arquivo == "ERRO_ARQUIVO":  # Se houve erro
            print("O outro usuário informou que o arquivo não existe.")  # Avisa
            return  # Para a função
        
        print(f"Recebendo '{nome_arquivo}' via TCP...")  # Avisa que está recebendo
        with open(nome_arquivo, "wb") as f:  # Cria arquivo para salvar
            while True:  # Loop para receber pedaços
                bytes_recebidos = sock.recv(4096)  # Recebe 4KB
                if b"<QSL>" in bytes_recebidos:  # Se tem sinal de fim
                    f.write(bytes_recebidos.replace(b"<QSL>", b''))  # Remove sinal e salva
                    break  # Para o loop
                f.write(bytes_recebidos)  # Salva o pedaço
        print("Arquivo TCP recebido com sucesso!")  # Confirma recebimento
    except Exception as e:  # Se der erro
        print(f"Erro ao receber arquivo TCP: {e}")  # Mostra erro

def enviar_arquivo_udp(sock, addr):
    """Envia um arquivo via UDP com confirmação."""
    try:  # Tenta executar
        caminho = input("Digite o caminho do arquivo para enviar: ")  # Pede arquivo
        if not os.path.exists(caminho):  # Verifica se existe
            print("Arquivo não encontrado.")  # Avisa
            sock.sendto("ERRO_ARQUIVO".encode("utf-8"), addr)  # Avisa o outro lado
            return  # Para função

        nome_arquivo = os.path.basename(caminho)  # Pega nome
        tamanho_arquivo = os.path.getsize(caminho)  # Pega tamanho
        
        print("Anunciando arquivo...")  # Avisa início
        sock.sendto(f"{nome_arquivo}|{tamanho_arquivo}".encode("utf-8"), addr)  # Anuncia arquivo
        
        sock.settimeout(5.0)  # Timeout de 5 segundos
        dados, _ = sock.recvfrom(1024)  # Espera confirmação
        if dados != b"ACK_INICIO":  # Se não confirmou
            print("O outro lado não confirmou o início da transferência.")  # Avisa
            sock.settimeout(None)  # Remove timeout
            return  # Para função
        
        print("O outro lado confirmou. Iniciando envio...")  # Confirmou
        num_pacote = 0  # Contador de pacotes
        sock.settimeout(0.5)  # Timeout curto para cada pacote
        with open(caminho, "rb") as f:  # Abre arquivo
            while True:  # Loop para ler arquivo
                bytes_lidos = f.read(1400)  # Lê pedaço seguro para UDP
                if not bytes_lidos:  # Se acabou
                    break  # Para loop
                
                # Loop para reenviar até receber confirmação
                while True:
                    pacote = f"{num_pacote}".encode('utf-8') + b'|' + bytes_lidos  # Monta pacote
                    sock.sendto(pacote, addr)  # Envia pacote
                    try:  # Tenta receber confirmação
                        dados, _ = sock.recvfrom(1024)  # Recebe resposta
                        if dados.decode('utf-8') == f"ACK|{num_pacote}":  # Se confirmou este pacote
                            break  # Vai para próximo pacote
                    except socket.timeout:  # Se não respondeu
                        print(f"  Timeout! Reenviando pacote {num_pacote}...")  # Avisa reenvio
                num_pacote += 1  # Próximo pacote
        
        sock.sendto(b"<FIN>", addr)  # Sinal de fim
        print("Arquivo UDP enviado com sucesso!")  # Confirma
    except socket.timeout:  # Se deu timeout
        print("O outro lado não respondeu. Abortando.")  # Avisa timeout
    except Exception as e:  # Se der erro
        print(f"Erro ao enviar arquivo UDP: {e}")  # Mostra erro
    finally:  # Sempre executa
        sock.settimeout(None)  # Remove timeout

def receber_arquivo_udp(sock, addr):
    """Recebe um arquivo via UDP com confirmação."""
    try:  # Tenta executar
        sock.settimeout(120.0)  # Timeout longo
        # Recebe anúncio do arquivo
        dados, _ = sock.recvfrom(1024)  # Recebe dados
        # Verifica se é erro
        if dados.decode("utf-8") == "ERRO_ARQUIVO":
             print("O outro usuário informou que o arquivo não existe.")  # Avisa erro
             return  # Para função
        nome_arquivo, tamanho_total_str = dados.decode("utf-8").split('|')  # Separa nome e tamanho
        tamanho_total = int(tamanho_total_str)  # Converte tamanho para número
        print(f"Recebendo '{nome_arquivo}' via UDP ({tamanho_total} bytes)...")  # Avisa início
        # Confirma que está pronto
        sock.sendto(b"ACK_INICIO", addr)  # Confirma
        bytes_recebidos = 0  # Contador de bytes
        pacote_esperado = 0  # Contador de pacotes
        with open(nome_arquivo, "wb") as f:  # Cria arquivo
            while bytes_recebidos < tamanho_total:  # Enquanto não recebeu tudo
                dados, _ = sock.recvfrom(1400 + 100)  # Recebe pacote
                if dados == b"<FIN>":  # Se é sinal de fim
                    break  # Para
                
                num_pacote_str, chunk = dados.split(b'|', 1)  # Separa número e dados
                num_pacote = int(num_pacote_str)  # Converte número
                
                if num_pacote == pacote_esperado:  # Se é o pacote certo
                    f.write(chunk)  # Salva dados
                    sock.sendto(f"ACK|{num_pacote}".encode('utf-8'), addr)  # Confirma
                    bytes_recebidos += len(chunk)  # Atualiza contador
                    pacote_esperado += 1  # Próximo pacote esperado
                else:  # Se pacote errado
                    ack_anterior = pacote_esperado - 1  # Último correto
                    sock.sendto(f"ACK|{ack_anterior}".encode('utf-8'), addr)  # Confirma último correto
        
        # Limpa buffer de pacotes atrasados
        while True:
            try:
                sock.settimeout(0.2)  # Timeout curto
                dados, _ = sock.recvfrom(1024)  # Tenta receber
                if dados == b"<FIN>":  # Se é fim
                    break  # Para
            except socket.timeout:  # Se não recebeu nada
                break  # Buffer limpo
        print("Arquivo UDP recebido com sucesso!")  # Confirma
    except socket.timeout:  # Se deu timeout
        print("Timeout na transferência! O arquivo UDP pode estar incompleto.")  # Avisa problema
    except Exception as e:  # Se der erro
        print(f"Erro ao receber arquivo UDP: {e}")  # Mostra erro
    finally:  # Sempre executa
        sock.settimeout(None)  # Remove timeout

# PROGRAMA PRINCIPAL
while True:  # Loop do menu
    # Pergunta o que o usuário quer ser
    modo = input("Você quer ser (1) Host ou (2) Cliente? Digite 'sair' para fechar: ").lower()
    
    # LÓGICA DO HOST
    if modo == '1':  # Se escolheu Host
        porta = 50000  # Porta padrão
        cliente_addr = None  # Endereço do cliente
        # Pergunta protocolo
        escolha_protocolo = input("Escolha o protocolo (1 para TCP, 2 para UDP): ")
        # Define tipo de socket
        tipo_socket = socket.SOCK_STREAM if escolha_protocolo == '1' else socket.SOCK_DGRAM
        try:  # Tenta criar servidor
            # Configuração automática para IPv4/IPv6
            info_addr = socket.getaddrinfo(None, porta, socket.AF_UNSPEC, tipo_socket, 0, socket.AI_PASSIVE)[0]
            sock = socket.socket(info_addr[0], info_addr[1])  # Cria socket
            # Se IPv6, aceita também IPv4
            if info_addr[0] == socket.AF_INET6:
                sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            sock.bind(info_addr[4])  # Liga socket à porta
            print(f"Servidor escutando em modo Dual-Stack na porta {porta}")  # Confirma
        except Exception as e:  # Se der erro
            print(f"Falha ao iniciar o servidor: {e}")  # Mostra erro
            break  # Sai do programa
        
        # Configuração específica por protocolo
        if escolha_protocolo == '1':  # TCP
            sock.listen()  # Escuta conexões
            conn, cliente_addr = sock.accept()  # Aceita cliente
            print(f"Cliente conectado: {cliente_addr}")  # Confirma conexão
        else:  # UDP
            print(f"Aguardando primeira mensagem na porta {porta}...")  # Avisa espera
            dados, cliente_addr = sock.recvfrom(1024)  # Primeira mensagem
            print(f"Cliente estabelecido: {cliente_addr}")  # Confirma cliente
        
        print("Comandos: /sair e /enviar ")  # Mostra comandos
        
        # Loop principal do chat do Host
        try:
            while True:  # Chat infinito
                # Host sempre escuta primeiro
                print("\n--- Turno do Cliente --- \nAguardando ação do Cliente...")
                if escolha_protocolo == '1':  # TCP
                    msg_cliente = conn.recv(1024).decode("utf-8")  # Recebe mensagem
                else:  # UDP
                    dados, cliente_addr = sock.recvfrom(1024)  # Recebe mensagem
                    msg_cliente = dados.decode("utf-8")
                
                # Processa ação do cliente
                if msg_cliente.startswith('/enviar' or '/enviar '):  # Quer enviar arquivo
                    print("Cliente está enviando um arquivo...")
                    if escolha_protocolo == '1':  # TCP
                        receber_arquivo_tcp(conn)
                    else:  # UDP
                        receber_arquivo_udp(sock, cliente_addr)
                elif msg_cliente.lower() == '/sair':  # Quer sair
                    print("Cliente encerrou o chat.")
                    break
                else:  # Mensagem normal
                    print(f"Cliente: {msg_cliente}")
                
                # Vez do Host responder
                print("\n--- Seu Turno (Host) ---")
                msg_host = input("Você: ")  # Pede mensagem
                
                # Envia resposta
                if escolha_protocolo == '1':  # TCP
                    conn.send(msg_host.encode("utf-8"))
                else:  # UDP
                    sock.sendto(msg_host.encode("utf-8"), cliente_addr)

                # Processa ação do Host
                if msg_host.startswith('/enviar ' or '/enviar'):  # Quer enviar arquivo
                    if escolha_protocolo == '1':  # TCP
                        enviar_arquivo_tcp(conn)
                    else:  # UDP
                        enviar_arquivo_udp(sock, cliente_addr)
                elif msg_host.lower() == '/sair':  # Quer sair
                    print("Você encerrou o chat.")
                    break
        except (ConnectionResetError, BrokenPipeError, OSError):  # Erro de conexão
            print("\nConexão com o cliente perdida.")
        finally:  # Limpeza
            if escolha_protocolo == '1' and 'conn' in locals():  # Se TCP
                conn.close()  # Fecha conexão
            sock.close()  # Fecha socket
            print("Servidor Encerrado.")
        break  # Sai do menu
    
    # LÓGICA DO CLIENTE
    elif modo == '2':  # Se escolheu Cliente
        porta = 50000  # Porta padrão
        cliente_IP = input("Digite o IP do Host (padrão 127.0.0.1): ") or "127.0.0.1"  # IP do host
        ADDR = (cliente_IP, porta)  # Endereço completo
        escolha_protocolo = input("Escolha o protocolo (1 para TCP, 2 para UDP): ")  # Protocolo
        tipo_socket = socket.SOCK_STREAM if escolha_protocolo == '1' else socket.SOCK_DGRAM  # Tipo de socket
        try:  # Tenta conectar
            # Configuração automática
            info_addr = socket.getaddrinfo(cliente_IP, porta, socket.AF_UNSPEC, tipo_socket)[0]
            sock = socket.socket(info_addr[0], info_addr[1])  # Cria socket
            if escolha_protocolo == '1':  # TCP
                sock.connect(info_addr[4])  # Conecta
                print("Conectado ao Host!")
            else:  # UDP
                sock.sendto("OI_HOST".encode("utf-8"), info_addr[4])  # Primeira mensagem
                print("Contato UDP estabelecido!")
        except Exception as e:  # Se der erro
            print(f"Falha ao conectar: {e}")
            break
        
        print("Comandos: /sair e /enviar")  # Mostra comandos
        
        # Loop principal do chat do Cliente
        try:
            while True:  # Chat infinito
                # Cliente sempre fala primeiro
                print("\n--- Seu Turno (Cliente) ---")
                msg_para_enviar = input("Você: ")  # Pede mensagem
                
                # Envia mensagem
                if escolha_protocolo == '1':  # TCP
                    sock.send(msg_para_enviar.encode("utf-8"))
                else:  # UDP
                    sock.sendto(msg_para_enviar.encode("utf-8"), ADDR)
                
                # Processa própria ação
                if msg_para_enviar.startswith('/enviar ' or '/enviar'):  # Quer enviar arquivo
                    if escolha_protocolo == '1':  # TCP
                        enviar_arquivo_tcp(sock)
                    else:  # UDP
                        enviar_arquivo_udp(sock, ADDR)
                elif msg_para_enviar.lower() == '/sair':  # Quer sair
                    print("Você encerrou o chat.")
                    break
                
                # Vez do Host responder
                print("\n--- Turno do Host ---")
                print("Aguardando ação do Host...")
                if escolha_protocolo == '1':  # TCP
                    msg_recebida = sock.recv(1024).decode("utf-8")  # Recebe mensagem
                else:  # UDP
                    dados, _ = sock.recvfrom(1024)
                    msg_recebida = dados.decode("utf-8")
                
                # Processa ação do Host
                if msg_recebida.startswith('/enviar ' or '/enviar'):  # Host quer enviar arquivo
                    print("Host está enviando um arquivo...")
                    if escolha_protocolo == '1':  # TCP
                        receber_arquivo_tcp(sock)
                    else:  # UDP
                        receber_arquivo_udp(sock, ADDR)
                elif msg_recebida.lower() == '/sair':  # Host quer sair
                    print("O Host encerrou o chat.")
                    break
                else:  # Mensagem normal
                    print(f"Host: {msg_recebida}")
        except (ConnectionResetError, BrokenPipeError, OSError):  # Erro de conexão
            print("\nConexão com o Host perdida.")
        finally:  # Limpeza
            print("Cliente encerrado.")
            sock.close()  # Fecha socket
        break  # Sai do menu

    elif modo == 'sair':  # Se quer sair
        break  # Sai do programa
    else:  # Opção inválida
        print("Opção inválida. Tente novamente.")