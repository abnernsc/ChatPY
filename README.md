# Pychat P2P: Aplicação de Chat com Transferência de Arquivos

## Sumário

Pychat P2P é uma aplicação de chat ponto-a-ponto (peer-to-peer) desenvolvida em Python, focada no estudo e na implementação prática da programação de sockets. O projeto estabelece uma comunicação direta entre dois usuários — um atuando como Host e outro como Cliente — sem a necessidade de um servidor central. A aplicação se destaca por sua interface gráfica construída com Tkinter, pelo sistema de comunicação no estilo "walkie-talkie" (half-duplex) e pela capacidade de transferir arquivos de forma robusta, permitindo ao usuário escolher entre os protocolos TCP e UDP.

---

## 🚀 Funcionalidades Principais

* **Comunicação Ponto-a-Ponto:** Conexão direta entre cliente e host.
* **Interface Gráfica Completa:** GUI desenvolvida com a biblioteca **Tkinter**, com janelas separadas para configuração e para o chat, além de pop-ups de notificação (`messagebox`).
* **Sistema de Turnos (Walkie-Talkie):** Modelo de comunicação half-duplex que organiza o diálogo, com um indicador visual claro de quem possui o turno para falar.
* **Seleção de Protocolo:** Suporte para conexões via **TCP** (garantindo confiabilidade) e **UDP** (priorizando velocidade).
* **Transferência de Arquivos:** Funcionalidade de envio de arquivos em ambos os protocolos, iniciada pelo comando `/enviar` e com seleção de arquivo através de uma janela de diálogo (`filedialog`).
* **Chat com Timestamps:** Todas as mensagens no chat são registradas com o horário (HH:MM:SS) em que foram enviadas ou recebidas.
* **Suporte a Dual-Stack (IPv4/IPv6):** Capacidade de operar em diferentes versões do Protocolo de Internet.
* **Execução Multi-Threaded:** Utilização de `threading` para assegurar que a interface gráfica permaneça 100% responsiva durante as operações de rede.
* **Comandos Internos:** Suporte para comandos como `/enviar` (iniciar transferência de arquivo) e `/sair` (encerrar a sessão de chat de forma limpa).

---

## 🛠️ Pilha Tecnológica

* **Python 3:** Linguagem de programação principal.
* **Bibliotecas Nativas do Python:**
    * **Tkinter:** Para a construção da interface gráfica (GUI), incluindo os widgets `scrolledtext`, `messagebox` e `filedialog`.
    * **Sockets:** Para a programação de rede de baixo nível (TCP/UDP).
    * **Threading:** Para a execução de operações concorrentes (rede e GUI).
    * **OS:** Para manipulação de caminhos de arquivos (`os.path`).
    * **Time:** Para a geração de timestamps nas mensagens.

---

## ⚙️ Instalação e Uso

### Pré-requisitos

* Python 3 instalado e configurado no PATH do sistema.

### Execução

1.  **Clone o repositório para a sua máquina local:**
    ```bash
    git clone https://github.com/abnernsc/ChatPY.git
    ```

2.  **Navegue para o diretório do projeto:**
    ```bash
    cd ChatPY
    ```

3.  **Execute o script principal da aplicação:**
    ```bash
    python chat.py
    ```

4.  **Iniciando uma sessão de chat:**
    * **Máquina Host:** Na janela de configuração, selecione "Host", configure a porta (o padrão é 50000) e o protocolo (TCP/UDP), e clique em "INICIAR CONEXÃO".
    * **Máquina Cliente:** Na janela de configuração, selecione "Cliente", insira o endereço IP do Host, a porta correspondente e o mesmo protocolo, e clique em "INICIAR CONEXÃO".
    * *Para testes locais, utilize o endereço `127.0.0.1` no Cliente.*

5.  **Comandos:**
    * `/enviar`: Abre uma janela para selecionar um arquivo e iniciar a transferência para o outro usuário.
    * `/sair`: Encerra a sessão de chat atual e retorna para a tela de configuração.

---

## 📖 Evolução do Projeto (Histórico de Commits)

O desenvolvimento deste projeto foi estruturado em etapas incrementais. O histórico abaixo detalha a evolução da aplicação desde a sua concepção básica até a versão final com interface gráfica.

### v1.0: Comunicação Textual via TCP/IPv4 `(Commit 1)`
O ponto de partida do projeto. Nesta fase, a funcionalidade mais básica de um chat foi implementada.

* **Implementado:** Troca de mensagens de texto entre cliente e host sobre uma conexão TCP, garantindo entrega e ordem.

### v1.1: Transferência de Arquivos via TCP `(Commit 2)`
Expansão da capacidade do protocolo TCP para permitir o envio de arquivos.

* **Implementado:** Um protocolo para negociar e transmitir dados binários sobre a mesma conexão TCP.

### v1.2: Adição de Comunicação Textual via UDP `(Commit 3)`
Introdução do protocolo UDP como alternativa, adicionando flexibilidade.

* **Implementado:** Lógica para chat de texto sobre UDP/IPv4.

### v2.0: Suporte a IPv6 (Dual-Stack) `(Commit 4)`
Modernização da camada de rede para compatibilidade com endereçamento IPv6.

* **Implementado:** Uso de `socket.getaddrinfo` para que o Host aceite conexões IPv4 e IPv6 simultaneamente.

### v2.1: Transferência de Arquivos Confiável via UDP `(Commit 5)`
Implementação de uma camada de controle para simular a confiabilidade do TCP sobre o UDP.

* **Implementado:** Protocolo de transferência para UDP com handshake (`ACK`), pacotes numerados e lógica de retransmissão.

### v3.0: Refatoração e Unificação do Código-Fonte `(Commit 6)`
Melhoria na arquitetura para organização e reutilização de código.

* **Implementado:** Unificação dos scripts de host e cliente em um único arquivo com menu inicial para seleção de modo.

### v4.0: Implementação da Interface Gráfica (GUI) `(Commit 7)`
A evolução final do projeto, substituindo o terminal por uma interface gráfica completa e amigável.

* **Implementado:** Interface gráfica com Tkinter, janelas separadas para configuração e chat, e uso de `threading` para garantir a responsividade da GUI.

---


## 👥 Desenvolvedores

**Abner Vitor Silva Nascimento**
**Ana Leticia Alves de Lima**
**Maria Valentina de Oliveira Menezes**
**Pedro Lucas Araujo Fernandes**


* **Email:** `abner.vnascimento@gmail.com`
* **GitHub:** `https://github.com/abnernsc`
