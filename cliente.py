import socket


cliente_IP = "127.0.0.1" 
porta = 8080

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Cria o socket TCP/IP (IPv4)
cliente.connect((cliente_IP, porta))  # Conecta ao ip e porta
print("Conectado ao Host!")

valid = False
print("Digita 'sair' para encerrar o chat")
while not valid:
    msgcliente = input("Você: ")
    cliente.send(str(msgcliente).encode("utf-8")) # A mensagem que o cliente está enviando
    if msgcliente == "sair":
        print("O chat foi encerrado")
        valid = True
        break
    msg = cliente.recv(1024).decode("utf-8") # A mensagem que o host enviou está sendo decodificada
    if msg=="sair":
        print("O chat foi encerrado")
        valid = True
    else: 
        print(f"Host: {msg}")
cliente.close()