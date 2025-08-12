import socket

server_IP = "0.0.0.0"
porta = 8080
ADDR =(server_IP, porta)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Cria o socket TCP/IP (IPv4)
server.bind(ADDR) # Vincula o socket ao endereço e porta definidos

server.listen() # Modo de escuta
print("Aguardando conexão do cliente...")

cliente, end = server.accept() # Server vai aceitar as conexões do cliente
print(f"Cliente conectado pelo endereço: {end}")
valid = False 

while not valid:
    msg = cliente.recv(1024).decode("utf-8") # Mensagem recebida do cliente, ele vai decodificar no formato utf-8
    if msg == "sair":
        print("O chat foi encerrado")
        valid = True
        break
    else: 
        print(f"Cliente: {msg}")
    hostmsg = input("Você: ")
    if hostmsg == "sair":
        print("O chat foi encerrado")
        valid = True    
    cliente.send(str(hostmsg).encode("utf-8")) # A mensagem que o host está enviando

cliente.close()
server.close()