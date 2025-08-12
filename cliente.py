import socket  # Biblioteca para comunicação em rede
import time    # Biblioteca para funções de tempo (sleep)
import os      # Biblioteca para operações do sistema operacional

# --- FUNÇÕES DE ARQUIVO TCP  ---
def enviar_arquivo_tcp(sock):  # Função para enviar arquivo via TCP
    try:
        # Pede ao usuário o caminho do arquivo
        caminho = input("Digite o caminho do arquivo para enviar: ")
        # Verifica se existe, se não: informa erro, envia sinal de erro e retorna
        if not os.path.exists(caminho): print("Arquivo não encontrado."); sock.send("ERRO_ARQUIVO".encode("utf-8")); return
        # Pega o nome do arquivo, envia para o host, dá uma pausa
        nome_arquivo = os.path.basename(caminho); sock.send(nome_arquivo.encode("utf-8")); time.sleep(0.1)
        # Abre arquivo em modo binário e envia em chunks de 4KB
        with open(caminho, "rb") as f:
            while True:
                bytes_lidos = f.read(4096)  # Lê 4KB do arquivo
                if not bytes_lidos: break   # Se acabou o arquivo, sai do loop
                sock.sendall(bytes_lidos)   # Envia os bytes (TCP garante entrega)
        # Pausa e envia sinal de fim
        time.sleep(0.1); sock.send(b"<EOF>"); print("Arquivo TCP enviado.")
    except Exception as e:
        print(f"Erro ao enviar arquivo TCP: {e}")

def receber_arquivo_tcp(sock):  # Função para receber arquivo via TCP
    try:
        # Recebe o nome do arquivo
        nome_arquivo = sock.recv(1024).decode("utf-8")
        # Se houve erro no host, informa e retorna
        if nome_arquivo == "ERRO_ARQUIVO": print("O Host informou que o arquivo não existe."); return
        print(f"Recebendo '{nome_arquivo}' via TCP...")
        # Abre arquivo para escrita e recebe dados
        with open(nome_arquivo, "wb") as f:
            while True:
                bytes_recebidos = sock.recv(4096)  # Recebe até 4KB
                # Se encontrou sinal de fim, remove ele, escreve o resto e sai
                if b"<EOF>" in bytes_recebidos:
                    f.write(bytes_recebidos.replace(b"<EOF>", b'')); break
                f.write(bytes_recebidos)  # Escreve dados no arquivo
        print("Arquivo TCP recebido com sucesso!")
    except Exception as e:
        print(f"Erro ao receber arquivo TCP: {e}")

# --- FUNÇÕES PARA UDP CONFIÁVEL ---
def enviar_arquivo_udp(sock, addr):  # Função para enviar arquivo via UDP confiável
    try:
        # Pede caminho e verifica se arquivo existe
        caminho = input("Digite o caminho do arquivo para enviar: ")
        if not os.path.exists(caminho): print("Arquivo não encontrado."); return
        
        # Pega nome e tamanho do arquivo
        nome_arquivo = os.path.basename(caminho)
        tamanho_arquivo = os.path.getsize(caminho)
        
        # Anuncia o arquivo para o host (nome|tamanho)
        print("Anunciando arquivo para o Host...")
        sock.sendto(f"{nome_arquivo}|{tamanho_arquivo}".encode("utf-8"), addr)
        
        # Define timeout para esperar confirmação do host
        sock.settimeout(5.0)
        dados, _ = sock.recvfrom(1024)
        # Se host não confirmar, aborta
        if dados != b"ACK_INICIO":
            print("Host não confirmou o início da transferência."); sock.settimeout(None); return
            
        print("Host confirmou. Iniciando envio...")
        num_pacote = 0  # Contador de pacotes
        sock.settimeout(0.5)  # Timeout menor para reenvios
        
        # Lê arquivo e envia em pacotes numerados
        with open(caminho, "rb") as f:
            while True:
                bytes_lidos = f.read(1400)  # Lê 1400 bytes (tamanho seguro para UDP)
                if not bytes_lidos: break   # Se acabou o arquivo, sai
                
                # Loop de reenvio até receber ACK do pacote atual
                while True:
                    # Cria pacote: número|dados
                    pacote = f"{num_pacote}".encode('utf-8') + b'|' + bytes_lidos
                    sock.sendto(pacote, addr)  # Envia pacote
                    try:
                        # Espera confirmação (ACK) do host
                        dados, _ = sock.recvfrom(1024)
                        if dados.decode('utf-8') == f"ACK|{num_pacote}":
                            break  # ACK correto, próximo pacote
                    except socket.timeout:
                        # Se não receber ACK, reenvia
                        print(f"  Timeout! Reenviando pacote {num_pacote}...")
                num_pacote += 1  # Incrementa contador de pacotes
                
        # Envia sinal de fim
        sock.sendto(b"<FIN>", addr)
        print("Arquivo UDP enviado com sucesso!")
    except socket.timeout:
        print("Host não respondeu. Abortando.")
    except Exception as e:
        print(f"Erro ao enviar arquivo UDP: {e}")
    finally:
        sock.settimeout(None)  # Remove timeout

def receber_arquivo_udp(sock, addr):  # Função para receber arquivo via UDP confiável
    try:
        # Define timeout longo para receber anúncio
        sock.settimeout(120.0)  # 2 minutos para esperar o anúncio
        
        # Recebe anúncio do arquivo (nome|tamanho)
        dados, _ = sock.recvfrom(1024)
        nome_arquivo, tamanho_total_str = dados.decode("utf-8").split('|')
        tamanho_total = int(tamanho_total_str)
        print(f"Recebendo '{nome_arquivo}' via UDP ({tamanho_total} bytes)...")
        
        # Confirma que está pronto para receber
        sock.sendto(b"ACK_INICIO", addr)
        
        # Variáveis de controle
        bytes_recebidos = 0      # Contador de bytes já recebidos
        pacote_esperado = 0      # Número do próximo pacote esperado
        
        # Abre arquivo para escrita
        with open(nome_arquivo, "wb") as f:
            # Continua até receber todos os bytes
            while bytes_recebidos < tamanho_total:
                # Recebe pacote (com margem extra para cabeçalho)
                dados, _ = sock.recvfrom(1400 + 100)
                
                # Se receber sinal de fim antes da hora, sai
                if dados == b"<FIN>": break
                
                # Separa número do pacote dos dados
                num_pacote_str, chunk = dados.split(b'|', 1)
                num_pacote = int(num_pacote_str)
                
                # Se é o pacote esperado
                if num_pacote == pacote_esperado:
                    f.write(chunk)  # Escreve dados no arquivo
                    # Envia confirmação (ACK) para este pacote
                    sock.sendto(f"ACK|{num_pacote}".encode('utf-8'), addr)
                    bytes_recebidos += len(chunk)  # Atualiza contador
                    pacote_esperado += 1           # Próximo pacote esperado
                else:
                    # Pacote fora de ordem - reenvia ACK do último pacote correto
                    ack_anterior = pacote_esperado - 1
                    sock.sendto(f"ACK|{ack_anterior}".encode('utf-8'), addr)

        
        while True:
            try:
                sock.settimeout(0.2)  # Espera apenas 0.2 segundos
                dados, _ = sock.recvfrom(1024)
                # Se encontrar o sinal de fim, ótimo - sai do loop
                if dados == b"<FIN>":
                    break
            except socket.timeout:
                # Se não receber mais nada em 0.2s, buffer está limpo
                break
        print("Arquivo UDP recebido com sucesso!")
    except socket.timeout:
        print("Timeout na transferência! O arquivo UDP pode estar incompleto.")
    except Exception as e:
        print(f"Erro ao receber arquivo UDP: {e}")
    finally:
        sock.settimeout(None)  # Garante que o timeout seja desativado


# --- CÓDIGO PRINCIPAL---
porta = 50000  # Porta de comunicação
# Pede IP do host ou usa padrão
cliente_IP = input("Digite o IP do Host (padrão 127.0.0.1): ") or "127.0.0.1"
ADDR = (cliente_IP, porta)  # Endereço completo do host
# Pergunta protocolo e define tipo de socket
escolha_protocolo = input("Escolha o protocolo (1 para TCP, 2 para UDP): ")
tipo_socket = socket.SOCK_STREAM if escolha_protocolo == '1' else socket.SOCK_DGRAM

try:
    # Usa getaddrinfo para detectar IPv4/IPv6 automaticamente
    info_addr = socket.getaddrinfo(cliente_IP, porta, socket.AF_UNSPEC, tipo_socket)[0]
    sock = socket.socket(info_addr[0], info_addr[1])  # Cria socket correto
    
    if escolha_protocolo == '1':  # TCP
        sock.connect(info_addr[4]); print("Conectado ao Host!")  # Conecta ao host
    else:  # UDP
        # Em UDP, primeira mensagem estabelece "contato"
        sock.sendto("OI_HOST".encode("utf-8"), info_addr[4]); print("Contato UDP estabelecido!")
except Exception as e:
    print(f"Falha ao conectar: {e}"); exit()  # Sai se der erro

print("Comandos: /sair e /enviar 'nome.extensão'")  # Instruções

try:
    while True:  # Loop principal do chat
        print("\n--- Seu Turno (Cliente) ---")
        msg_para_enviar = input("Você: ")  # Recebe mensagem do usuário
        
        # Envia mensagem para o host
        if escolha_protocolo == '1': sock.send(msg_para_enviar.encode("utf-8"))      # TCP
        else: sock.sendto(msg_para_enviar.encode("utf-8"), ADDR)                    # UDP
        
        # Processa ação do cliente
        if msg_para_enviar.startswith('/enviar '):  # Cliente quer enviar arquivo
            if escolha_protocolo == '1': enviar_arquivo_tcp(sock)     # TCP
            else: enviar_arquivo_udp(sock, ADDR)                      # UDP confiável
        elif msg_para_enviar.lower() == '/sair':  # Cliente quer sair
            print("Você encerrou o chat."); break
        
        # Turno do host
        print("\n--- Turno do Host ---")
        print("Aguardando ação do Host...")
        
        # Recebe mensagem do host
        if escolha_protocolo == '1':  # TCP
            msg_recebida = sock.recv(1024).decode("utf-8")
        else:  # UDP
            dados, _ = sock.recvfrom(1024); msg_recebida = dados.decode("utf-8")

        # Processa ação do host
        if msg_recebida.startswith('/enviar '):  # Host quer enviar arquivo
            print("Host está enviando um arquivo...")
            if escolha_protocolo == '1': receber_arquivo_tcp(sock)    # TCP
            else: receber_arquivo_udp(sock, ADDR)                     # UDP confiável
        elif msg_recebida.lower() == '/sair':  # Host quer sair
            print("O Host encerrou o chat."); break
        else:  # Mensagem normal de chat
            print(f"Host: {msg_recebida}")
            
except (ConnectionResetError, BrokenPipeError, OSError):  # Erros de conexão
    print("\nConexão com o Host perdida.");
finally:  # Limpeza final
    print("Cliente encerrado.")
    sock.close()  # Fecha socket