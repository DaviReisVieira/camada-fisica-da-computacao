#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
import numpy as np
import time

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM3"                  # Windows(variacao de)


def main():
    try:
        serverCom = enlace('COM3')

        serverCom.enable()
        serverCom.fisica.flush()

        print('Servidor aberto.')
        print('Esperando Head Protocol...')
        rxBufferHeader, nRxHeader = serverCom.getData(2)
        rxBufferResponse = int.from_bytes(rxBufferHeader, "big")
        print('Response',rxBufferResponse,nRxHeader)
        print('Head Protocol recebido!')
        initialTime = time.time()

        print('Enviando Handshake..')
        serverCom.sendData(rxBufferHeader) 
        print('Handshake realizado!')

        print('Esperando Dados do Client...')
        rxBuffer, nRx = serverCom.getData(rxBufferResponse)
        print('Dados do Client recebidos!')

        serverCom.sendData(np.asarray(rxBuffer))
        
        rxLen = len(rxBuffer)
        print("Dado recebido {}\n" .format(rxBuffer))
        print("Foram recebidos {} bytes" .format(nRx))


        finalTime = time.time()
        totalTime = finalTime - initialTime
        velocity = totalTime/rxLen           
    
        print("-------------------------")
        print("Comunicação encerrada")
        print(f'Tempo total da aplicação:\n{totalTime}s')
        print(f'Velocidade:\n{velocity} bytes/s')
        print("-------------------------")
        serverCom.disable()
        
    except Exception as erro:
        print("Ops! :-\\")
        print(erro)
        serverCom.disable()
    
    except KeyboardInterrupt:
        serverCom.disable()
        print('Server Finalizado na força!')
        
        

if __name__ == "__main__":
    main()
