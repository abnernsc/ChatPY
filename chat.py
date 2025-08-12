from tkinter import *  # Importa todas as funções da interface gráfica
from tkinter import scrolledtext, messagebox, filedialog  # Importa componentes específicos
import socket  # Para comunicação de rede
import threading  # Para executar várias coisas ao mesmo tempo
import time  # Para pausas no código
import os  # Para trabalhar com arquivos

# Variáveis globais - acessíveis em todo o programa
janela_config = None  # Janela de configuração inicial
janela_chat = None  # Janela do chat
sock = None  # Socket principal
conn = None  # Conexão TCP específica
cliente_addr = None  # Endereço do cliente conectado
protocolo = None  # TCP ou UDP
modo = None  # host ou cliente
running = False  # Se o programa está rodando
meu_turno = False  # Se é minha vez de falar
modoselecionado = None  # Variável do botão de modo
protselect = None  # Variável do botão de protocolo
ip_escrever = None  # Campo de texto para IP
porta_escrever = None  # Campo de texto para porta
area_mensagens = None  # Área onde aparecem as mensagens
entrada_mensagem = None  # Campo para digitar mensagem
btn_enviar = None  # Botão de enviar
frame_turno = None  # Área do indicador de turno
label_turno = None  # Texto do indicador de turno
arquivo_para_enviar = None  # Arquivo selecionado para envio

def atualizar_interface():
    """Atualiza a interface baseado no modo selecionado"""
    if modoselecionado.get() == 'host':  # Se é host
        ip_escrever.config(state='disabled')  # Desabilita campo de IP
    elif modoselecionado.get() == 'cliente':  # Se é cliente
        ip_escrever.config(state='normal')  # Habilita campo de IP

def atualizar_status(texto):
    """Atualiza status na janela de configuração"""
    print(f"Status: {texto}")  # Mostra status no terminal

def conectar(ip, porta):
    """Realiza a conexão propriamente dita"""
    global sock, conn, cliente_addr, meu_turno  # Usa variáveis globais
    
    try:  # Tenta conectar
        # Define tipo de socket
        tipo_socket = socket.SOCK_STREAM if protocolo == 'TCP' else socket.SOCK_DGRAM
        
        if modo == 'host':  # Lógica do Host
            # Configuração automática para IPv4/IPv6
            info_addr = socket.getaddrinfo(None, porta, socket.AF_UNSPEC, tipo_socket, 0, socket.AI_PASSIVE)[0]
            sock = socket.socket(info_addr[0], info_addr[1])  # Cria socket
            # Se IPv6, aceita também IPv4
            if info_addr[0] == socket.AF_INET6: 
                sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            sock.bind(info_addr[4])  # Liga socket à porta
            
            atualizar_status("Aguardando conexão...")  # Avisa que está esperando
            
            if protocolo == 'TCP':  # Se TCP
                sock.listen()  # Escuta conexões
                conn, cliente_addr = sock.accept()  # Aceita cliente
                meu_turno = False  # Host escuta primeiro
            else:  # Se UDP
                dados, cliente_addr = sock.recvfrom(1024)  # Primeira mensagem
                meu_turno = False  # Host escuta primeiro
                
        else:  # Lógica do Cliente
            # Configuração para conectar no host
            info_addr = socket.getaddrinfo(ip, porta, socket.AF_UNSPEC, tipo_socket)[0]
            sock = socket.socket(info_addr[0], info_addr[1])  # Cria socket
            cliente_addr = info_addr[4]  # Guarda endereço
            
            if protocolo == 'TCP':  # Se TCP
                sock.connect(info_addr[4])  # Conecta no host
            else:  # Se UDP
                sock.sendto("OI_HOST".encode("utf-8"), info_addr[4])  # Primeira mensagem
            
            meu_turno = True  # Cliente fala primeiro
        
        # Se chegou até aqui, conexão funcionou
        janela_config.after(0, abrir_chat)  # Abre janela de chat
        
    except Exception as e:  # Se der erro
        messagebox.showerror("Erro de Conexão", f"Falha ao conectar: {e}")  # Mostra erro

def iniciar_conexao():
    """Inicia a conexão baseada nas configurações"""
    global modo, protocolo  # Usa variáveis globais
    
    modo = modoselecionado.get()  # Pega modo selecionado
    protocolo = protselect.get()  # Pega protocolo selecionado
    
    if modo == "cliente":  # Se é cliente
        ip = ip_escrever.get()  # Pega IP digitado
    elif modo == "host":  # Se é host
        ip = "0.0.0.0"  # IP genérico
    
    porta = int(porta_escrever.get() or "50000")  # Pega porta ou usa padrão
    
    # Inicia conexão em thread separada para não travar interface
    thread_conexao = threading.Thread(target=conectar, args=(ip, porta))
    thread_conexao.daemon = True  # Thread morre com o programa
    thread_conexao.start()  # Inicia thread

def criar_janela_config():
    """Cria a janela de configuração inicial"""
    global janela_config, modoselecionado, protselect, ip_escrever, porta_escrever  # Usa variáveis globais
    
    janela_config = Tk()  # Cria janela principal
    janela_config.title("Pychat P2P - Configuração")  # Título da janela
    janela_config.geometry("400x350")  # Tamanho da janela
    janela_config.resizable(False, False)  # Não pode redimensionar

    # Seção de modo
    MODO_TEXTO = Label(janela_config, text="1. ESCOLHA SEU MODO:", font=("Arial", 10, "bold"))
    MODO_TEXTO.grid(column=0, row=0, columnspan=3, sticky='w', padx=10, pady=(10,5))  # Posiciona na grade

    modoselecionado = StringVar()  # Variável para botões de opção
    modoselecionado.set("host")  # Valor padrão

    # Botões de opção para modo
    HOST = Radiobutton(janela_config, text="Host (Servidor)", variable=modoselecionado, 
                      value="host", command=atualizar_interface)
    HOST.grid(column=0, row=1, sticky='w', padx=20)  # Posiciona

    CLIENTE = Radiobutton(janela_config, text="Cliente", variable=modoselecionado, 
                         value="cliente", command=atualizar_interface)
    CLIENTE.grid(column=0, row=2, sticky='w', padx=20)  # Posiciona

    # Seção de endereço
    ENDERECO_TEXTO = Label(janela_config, text="2. DIGITE O ENDEREÇO:", font=("Arial", 10, "bold"))
    ENDERECO_TEXTO.grid(column=0, row=3, columnspan=3, sticky="w", padx=10, pady=(20,5))

    IP_HOST = Label(janela_config, text="IP DO HOST:")  # Rótulo
    IP_HOST.grid(column=0, row=4, sticky='w', padx=20, pady=(5,0))

    ip_escrever = Entry(janela_config, width=25)  # Campo de texto
    ip_escrever.grid(column=1, row=4, padx=10, sticky='ew')
    ip_escrever.insert(0, "127.0.0.1")  # IP padrão (localhost)

    PORTA = Label(janela_config, text="PORTA:")  # Rótulo
    PORTA.grid(column=0, row=5, sticky='w', padx=20, pady=(5,0))

    porta_escrever = Entry(janela_config, width=25)  # Campo de texto
    porta_escrever.grid(column=1, row=5, padx=10, sticky='ew')
    porta_escrever.insert(0, "50000")  # Porta padrão

    # Seção de protocolo
    PROTOCOLO_TEXTO = Label(janela_config, text="3. ESCOLHA SEU PROTOCOLO:", font=("Arial", 10, "bold"))
    PROTOCOLO_TEXTO.grid(column=0, row=6, columnspan=3, sticky='w', padx=10, pady=(20,5))

    protselect = StringVar()  # Variável para protocolo
    protselect.set("TCP")  # Valor padrão

    # Botões de opção para protocolo
    TCP = Radiobutton(janela_config, text="TCP", variable=protselect, value="TCP")
    TCP.grid(column=0, row=7, sticky='w', padx=20)

    UDP = Radiobutton(janela_config, text="UDP", variable=protselect, value="UDP")
    UDP.grid(column=0, row=8, sticky='w', padx=20)

    # Botão para iniciar
    INIC_CONEX = Button(janela_config, text="INICIAR CONEXÃO", 
                       command=iniciar_conexao, font=("Arial", 10, "bold"), padx=20, pady=5)
    INIC_CONEX.grid(column=1, row=9, padx=10, pady=20, sticky="e")

    atualizar_interface()  # Atualiza interface inicial
    janela_config.protocol("WM_DELETE_WINDOW", fechar_aplicacao)  # Ação ao fechar janela

def abrir_chat():
    """Abre a janela de chat"""
    janela_config.withdraw()  # Esconde a janela de configuração
    criar_janela_chat()  # Cria janela de chat

def atualizar_turno():
    """Atualiza o indicador de turno"""
    if meu_turno:  # Se é minha vez
        label_turno.config(text="SEU TURNO - Digite sua mensagem")  # Avisa que é minha vez
        entrada_mensagem.config(state='normal')  # Habilita digitação
        btn_enviar.config(state='normal')  # Habilita botão
    else:  # Se é vez do outro
        outro = "Cliente" if modo == "host" else "Host"  # Define quem é o outro
        label_turno.config(text=f"TURNO DO {outro.upper()} - Aguardando...")  # Avisa vez do outro
        entrada_mensagem.config(state='disabled')  # Desabilita digitação
        btn_enviar.config(state='disabled')  # Desabilita botão

def adicionar_mensagem(remetente, mensagem):
    """Adiciona mensagem à área de chat"""
    area_mensagens.config(state=NORMAL)  # Permite edição
    timestamp = time.strftime("%H:%M:%S")  # Pega horário atual
    
    if remetente == "SISTEMA":  # Se é mensagem do sistema
        area_mensagens.insert(END, f"[{timestamp}] {mensagem}\n")  # Adiciona sem remetente
    else:  # Se é mensagem de usuário
        area_mensagens.insert(END, f"[{timestamp}] {remetente}: {mensagem}\n")  # Adiciona com remetente
    
    area_mensagens.config(state=DISABLED)  # Bloqueia edição
    area_mensagens.see(END)  # Rola para o final

def enviar_mensagem(event=None):
    """Envia mensagem de texto"""
    global meu_turno  # Usa variável global
    
    if not meu_turno:  # Se não é minha vez
        return  # Não faz nada
        
    mensagem = entrada_mensagem.get().strip()  # Pega mensagem digitada
    if not mensagem:  # Se não digitou nada
        return  # Não faz nada
        
    try:  # Tenta enviar
        # Envia a mensagem
        if protocolo == 'TCP':  # Se TCP
            if modo == 'host':  # Se é host
                conn.send(mensagem.encode("utf-8"))  # Envia pela conexão
            else:  # Se é cliente
                sock.send(mensagem.encode("utf-8"))  # Envia pelo socket
        else:  # Se UDP
            sock.sendto(mensagem.encode("utf-8"), cliente_addr)  # Envia para endereço
        
        # Adiciona mensagem na tela
        adicionar_mensagem("Você", mensagem)  # Mostra na tela
        entrada_mensagem.delete(0, END)  # Limpa campo de texto
        
        # Processa comandos especiais
        if mensagem.lower() == '/sair':  # Se quer sair
            adicionar_mensagem("SISTEMA", "Encerrando chat...")  # Avisa
            fechar_chat()  # Fecha chat
            return  # Para função
        elif mensagem.lower() == '/enviar':  # Se quer enviar arquivo
            processar_comando_enviar()  # Processa comando
            return  # Para função
            
        # Troca o turno
        meu_turno = False  # Agora é vez do outro
        atualizar_turno()  # Atualiza interface
        
    except Exception as e:  # Se der erro
        messagebox.showerror("Erro", f"Erro ao enviar mensagem: {e}")  # Mostra erro

def processar_comando_enviar():
    """Processa o comando /enviar e inicia transferência"""
    global arquivo_para_enviar  # Usa variável global
    
    arquivo = filedialog.askopenfilename(title="Selecionar arquivo para enviar")  # Abre diálogo de arquivo
    if not arquivo:  # Se não selecionou nenhum
        adicionar_mensagem("SISTEMA", "Nenhum arquivo selecionado.")  # Avisa
        return  # Para função
        
    adicionar_mensagem("Você", "Enviando arquivo...")  # Avisa que está enviando
    arquivo_para_enviar = arquivo  # Guarda arquivo selecionado
    
    # Inicia transferência em thread separada
    thread_envio = threading.Thread(target=executar_envio_arquivo)
    thread_envio.daemon = True  # Thread morre com programa
    thread_envio.start()  # Inicia thread

def executar_envio_arquivo():
    """Executa o envio do arquivo usando as funções originais"""
    global meu_turno  # Usa variável global
    
    try:  # Tenta enviar
        if protocolo == 'TCP':  # Se TCP
            sock_para_envio = conn if modo == 'host' else sock  # Define socket correto
            enviar_arquivo_tcp(sock_para_envio, arquivo_para_enviar)  # Envia arquivo
        else:  # Se UDP
            enviar_arquivo_udp(sock, cliente_addr, arquivo_para_enviar)  # Envia arquivo
        
        # Avisa sucesso na interface
        janela_chat.after(0, lambda: adicionar_mensagem("SISTEMA", "Arquivo enviado!"))
    except Exception as e:  # Se der erro
        # Avisa erro na interface
        janela_chat.after(0, lambda: adicionar_mensagem("SISTEMA", f"Erro no envio: {e}"))
    finally:  # Sempre executa
        # Troca o turno
        meu_turno = False  # Vez do outro
        janela_chat.after(0, atualizar_turno)  # Atualiza interface

def loop_receber_mensagens():
    """Loop para receber mensagens (roda em thread separada)"""
    global meu_turno  # Usa variável global
    
    while running:  # Enquanto programa está rodando
        try:  # Tenta receber
            if meu_turno:  # Se é minha vez
                time.sleep(0.1)  # Espera um pouco
                continue  # Continua loop
            
            # Recebe mensagem
            if protocolo == 'TCP':  # Se TCP
                if modo == 'host':  # Se é host
                    msg = conn.recv(1024).decode("utf-8")  # Recebe pela conexão
                else:  # Se é cliente
                    msg = sock.recv(1024).decode("utf-8")  # Recebe pelo socket
            else:  # Se UDP
                dados, _ = sock.recvfrom(1024)  # Recebe dados
                msg = dados.decode("utf-8")  # Decodifica mensagem
            
            if not msg:  # Se não recebeu nada
                break  # Para loop
            
            # Processa a mensagem
            if msg.startswith('/enviar'):  # Se quer enviar arquivo
                janela_chat.after(0, lambda: adicionar_mensagem("Contato", "Enviando arquivo..."))  # Avisa
                receber_arquivo()  # Recebe arquivo
            elif msg.lower() == '/sair':  # Se quer sair
                janela_chat.after(0, lambda: adicionar_mensagem("SISTEMA", "Contato encerrou o chat."))  # Avisa
                break  # Para loop
            else:  # Mensagem normal
                outro = "Host" if modo == "cliente" else "Cliente"  # Define remetente
                janela_chat.after(0, lambda m=msg: adicionar_mensagem(outro, m))  # Mostra mensagem
            
            # Troca o turno
            meu_turno = True  # Agora é minha vez
            janela_chat.after(0, atualizar_turno)  # Atualiza interface
            
        except Exception as e:  # Se der erro
            if running:  # Se programa ainda está rodando
                janela_chat.after(0, lambda: adicionar_mensagem("SISTEMA", f"Erro na conexão: {e}"))  # Mostra erro
            break  # Para loop

def receber_arquivo():
    """Recebe arquivo em thread separada"""
    thread_receber = threading.Thread(target=executar_receber_arquivo)  # Cria thread
    thread_receber.daemon = True  # Thread morre com programa
    thread_receber.start()  # Inicia thread

def executar_receber_arquivo():
    """Executa o recebimento usando as funções originais"""
    try:  # Tenta receber
        if protocolo == 'TCP':  # Se TCP
            sock_para_receber = conn if modo == 'host' else sock  # Define socket correto
            receber_arquivo_tcp(sock_para_receber)  # Recebe arquivo
        else:  # Se UDP
            receber_arquivo_udp(sock, cliente_addr)  # Recebe arquivo
            
        # Avisa sucesso na interface
        janela_chat.after(0, lambda: adicionar_mensagem("SISTEMA", "Arquivo recebido!"))
    except Exception as e:  # Se der erro
        # Avisa erro na interface
        janela_chat.after(0, lambda: adicionar_mensagem("SISTEMA", f"Erro no recebimento: {e}"))

def enviar_arquivo_tcp(sock_envio, caminho):
    """Versão modificada da função original - sem input()"""
    try:  # Tenta enviar
        if not os.path.exists(caminho):  # Se arquivo não existe
            sock_envio.send("ERRO_ARQUIVO".encode("utf-8"))  # Avisa erro
            return  # Para função
        
        nome_arquivo = os.path.basename(caminho)  # Pega nome do arquivo
        sock_envio.send(nome_arquivo.encode("utf-8"))  # Envia nome
        time.sleep(0.1)  # Pausa
        
        with open(caminho, "rb") as f:  # Abre arquivo
            while True:  # Loop para ler
                bytes_lidos = f.read(4096)  # Lê 4KB
                if not bytes_lidos:  # Se acabou
                    break  # Para loop
                sock_envio.sendall(bytes_lidos)  # Envia pedaço
        
        time.sleep(0.1)  # Pausa
        sock_envio.send(b"<QSL>")  # Sinal de fim
    except Exception as e:  # Se der erro
        raise e  # Repassa erro

def receber_arquivo_tcp(sock_receber):
    """Versão modificada da função original"""
    try:  # Tenta receber
        nome_arquivo = sock_receber.recv(1024).decode("utf-8")  # Recebe nome
        if nome_arquivo == "ERRO_ARQUIVO":  # Se houve erro
            janela_chat.after(0, lambda: adicionar_mensagem("SISTEMA", "Arquivo não encontrado no remetente"))  # Avisa
            return  # Para função
        
        # Salva na pasta do executável atual
        caminho_destino = os.path.join(os.getcwd(), nome_arquivo)  # Define caminho
        
        with open(caminho_destino, "wb") as f:  # Cria arquivo
            while True:  # Loop para receber
                bytes_recebidos = sock_receber.recv(4096)  # Recebe 4KB
                if b"<QSL>" in bytes_recebidos:  # Se tem sinal de fim
                    f.write(bytes_recebidos.replace(b"<QSL>", b''))  # Remove sinal e salva
                    break  # Para loop
                f.write(bytes_recebidos)  # Salva pedaço
    except Exception as e:  # Se der erro
        raise e  # Repassa erro

def enviar_arquivo_udp(sock_udp, addr, caminho):
    """Versão modificada da função UDP original"""
    try:  # Tenta enviar
        if not os.path.exists(caminho):  # Se não existe
            sock_udp.sendto("ERRO_ARQUIVO".encode("utf-8"), addr)  # Avisa erro
            return  # Para função

        nome_arquivo = os.path.basename(caminho)  # Pega nome
        tamanho_arquivo = os.path.getsize(caminho)  # Pega tamanho
        
        sock_udp.sendto(f"{nome_arquivo}|{tamanho_arquivo}".encode("utf-8"), addr)  # Anuncia arquivo
        
        sock_udp.settimeout(5.0)  # Timeout de 5 segundos
        dados, _ = sock_udp.recvfrom(1024)  # Espera confirmação
        if dados != b"ACK_INICIO":  # Se não confirmou
            sock_udp.settimeout(None)  # Remove timeout
            return  # Para função
        
        num_pacote = 0  # Contador de pacotes
        sock_udp.settimeout(0.5)  # Timeout curto
        with open(caminho, "rb") as f:  # Abre arquivo
            while True:  # Loop para ler
                bytes_lidos = f.read(1400)  # Lê pedaço
                if not bytes_lidos:  # Se acabou
                    break  # Para loop
                
                while True:  # Loop de reenvio
                    pacote = f"{num_pacote}".encode('utf-8') + b'|' + bytes_lidos  # Monta pacote
                    sock_udp.sendto(pacote, addr)  # Envia pacote
                    try:  # Tenta receber confirmação
                        dados, _ = sock_udp.recvfrom(1024)  # Recebe resposta
                        if dados.decode('utf-8') == f"ACK|{num_pacote}":  # Se confirmou
                            break  # Próximo pacote
                    except socket.timeout:  # Se não respondeu
                        continue  # Tenta novamente
                num_pacote += 1  # Próximo pacote
        
        sock_udp.sendto(b"<FIN>", addr)  # Sinal de fim
    except Exception as e:  # Se der erro
        raise e  # Repassa erro
    finally:  # Sempre executa
        sock_udp.settimeout(None)  # Remove timeout

def receber_arquivo_udp(sock_udp, addr):
    """Versão modificada da função UDP original"""
    try:  # Tenta receber
        sock_udp.settimeout(120.0)  # Timeout longo
        dados, _ = sock_udp.recvfrom(1024)  # Recebe anúncio
        if dados.decode("utf-8") == "ERRO_ARQUIVO":  # Se é erro
            janela_chat.after(0, lambda: adicionar_mensagem("SISTEMA", "Arquivo não encontrado no remetente"))  # Avisa
            return  # Para função
        
        nome_arquivo, tamanho_total_str = dados.decode("utf-8").split('|')  # Separa nome e tamanho
        tamanho_total = int(tamanho_total_str)  # Converte tamanho
        
        # Salva na pasta do executável atual
        caminho_destino = os.path.join(os.getcwd(), nome_arquivo)  # Define caminho
        
        sock_udp.sendto(b"ACK_INICIO", addr)  # Confirma início
        
        bytes_recebidos = 0  # Contador de bytes
        pacote_esperado = 0  # Contador de pacotes
        with open(caminho_destino, "wb") as f:  # Cria arquivo
            while bytes_recebidos < tamanho_total:  # Enquanto não recebeu tudo
                dados, _ = sock_udp.recvfrom(1400 + 100)  # Recebe pacote
                if dados == b"<FIN>":  # Se é sinal de fim
                    break  # Para loop
                
                num_pacote_str, chunk = dados.split(b'|', 1)  # Separa número e dados
                num_pacote = int(num_pacote_str)  # Converte número
                
                if num_pacote == pacote_esperado:  # Se é o pacote certo
                    f.write(chunk)  # Salva dados
                    sock_udp.sendto(f"ACK|{num_pacote}".encode('utf-8'), addr)  # Confirma
                    bytes_recebidos += len(chunk)  # Atualiza contador
                    pacote_esperado += 1  # Próximo esperado
                else:  # Se pacote errado
                    ack_anterior = pacote_esperado - 1  # Último correto
                    sock_udp.sendto(f"ACK|{ack_anterior}".encode('utf-8'), addr)  # Confirma último correto
        
        # Limpa buffer
        while True:
            try:
                sock_udp.settimeout(0.2)  # Timeout curto
                dados, _ = sock_udp.recvfrom(1024)  # Tenta receber
                if dados == b"<FIN>":  # Se é fim
                    break  # Para
            except socket.timeout:  # Se não recebeu
                break  # Buffer limpo
    except Exception as e:  # Se der erro
        raise e  # Repassa erro
    finally:  # Sempre executa
        sock_udp.settimeout(None)  # Remove timeout

def criar_janela_chat():
    """Cria a janela de chat"""
    global janela_chat, area_mensagens, entrada_mensagem, btn_enviar, frame_turno, label_turno, running  # Usa variáveis globais
    
    janela_chat = Toplevel()  # Cria janela secundária
    janela_chat.title(f"Pychat P2P - {modo.upper()} ({protocolo})")  # Título com informações
    janela_chat.geometry("600x500")  # Tamanho da janela
    
    # Frame superior para informações
    frame_info = Frame(janela_chat, height=30)  # Cria área
    frame_info.pack(fill=X, padx=5, pady=5)  # Posiciona
    frame_info.pack_propagate(False)  # Mantém tamanho fixo
    
    # Texto com informações da conexão
    info_text = f"Modo: {modo.upper()} | Protocolo: {protocolo}"  # Texto base
    if cliente_addr:  # Se tem endereço do cliente
        info_text += f" | Conectado: {cliente_addr}"  # Adiciona endereço
    
    Label(frame_info, text=info_text, font=("Arial", 9)).pack(pady=5)  # Cria rótulo
    
    # Área de mensagens com scroll
    area_mensagens = scrolledtext.ScrolledText(janela_chat, state=DISABLED, 
                                              wrap=WORD, height=20)  # Cria área de texto
    area_mensagens.pack(fill=BOTH, expand=True, padx=5, pady=5)  # Posiciona
    
    # Frame inferior para entrada e botões
    frame_inferior = Frame(janela_chat)  # Cria área
    frame_inferior.pack(fill=X, padx=5, pady=5)  # Posiciona
    
    # Campo de entrada de mensagem
    entrada_mensagem = Entry(frame_inferior, font=("Arial", 10))  # Cria campo
    entrada_mensagem.pack(side=LEFT, fill=X, expand=True, padx=(0,5))  # Posiciona
    entrada_mensagem.bind("<Return>", enviar_mensagem)  # Liga Enter ao envio
    
    # Botão de enviar
    btn_enviar = Button(frame_inferior, text="Enviar", command=enviar_mensagem,
                       font=("Arial", 9, "bold"))  # Cria botão
    btn_enviar.pack(side=RIGHT, padx=2)  # Posiciona à direita
    
    # Frame para indicador de turno
    frame_turno = Frame(janela_chat, height=25)  # Cria área do turno
    frame_turno.pack(fill=X, padx=5, pady=(0,5))  # Posiciona
    
    label_turno = Label(frame_turno, font=("Arial", 9, "bold"))  # Cria rótulo do turno
    label_turno.pack(pady=2)  # Posiciona
    
    # Configurações iniciais
    running = True  # Marca que está rodando
    atualizar_turno()  # Atualiza indicador de turno
    
    # Inicia thread para receber mensagens
    thread_receber = threading.Thread(target=loop_receber_mensagens)  # Cria thread
    thread_receber.daemon = True  # Thread morre com programa
    thread_receber.start()  # Inicia thread
    
    janela_chat.protocol("WM_DELETE_WINDOW", fechar_chat)  # Ação ao fechar janela
    adicionar_mensagem("SISTEMA", "Conexão estabelecida! Use /sair para encerrar.")  # Mensagem inicial
    adicionar_mensagem("SISTEMA", "Comandos disponíveis: /enviar (para arquivos)")  # Mostra comandos

def fechar_chat():
    """Fecha a janela de chat"""
    global running  # Usa variável global
    
    running = False  # Para as threads
    
    try:  # Tenta fechar conexões
        if protocolo == 'TCP':  # Se TCP
            if conn:  # Se tem conexão
                conn.close()  # Fecha conexão
        if sock:  # Se tem socket
            sock.close()  # Fecha socket
    except:  # Se der erro
        pass  # Ignora erro
        
    janela_chat.destroy()  # Destroi janela
    janela_config.deiconify()  # Mostra a janela de configuração novamente

def fechar_aplicacao():
    """Fecha a aplicação completamente"""
    global running  # Usa variável global
    
    running = False  # Para as threads
    try:  # Tenta fechar conexões
        if sock:  # Se tem socket
            sock.close()  # Fecha socket
        if conn:  # Se tem conexão
            conn.close()  # Fecha conexão
    except:  # Se der erro
        pass  # Ignora erro
    janela_config.destroy()  # Destroi janela principal

def iniciar():
    """Inicia a aplicação"""
    criar_janela_config()  # Cria janela de configuração
    janela_config.mainloop()  # Inicia loop da interface

iniciar()  # Chama função para iniciar programa