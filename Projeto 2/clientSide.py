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
import random

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM4"                  # Windows(variacao de)


def main():
    try:
        clientCom = enlace('COM4')
        clientCom.enable()
        clientCom.fisica.flush()

        print('Comunicação Iniciada')
        initialTime = time.time()

        commandList = [b'\x00\xFF',b'\x00',b'\x0F',b'\xF0',b'\xFF\x00',b'\xFF']
        message = [commandList[random.randint(0,5)] for i in range(random.randint(10,30))]
        print('Mensagem a ser enviada:\n',message, '\n')
        
        txBuffer = message
        txBufferLen = len(txBuffer)

        print('Tamanho do Arquivo a ser enviado: {} bytes'.format(txBufferLen))
  
        print('Enviando início do protocolo...')
        txBufferHeader = txBufferLen.to_bytes(2, byteorder="big")
        print('txBufferHeader',txBufferHeader)
        clientCom.sendData(txBufferHeader)
        
        print('Aguardando Handshake...')
        rxBufferHeader, nRx = clientCom.getData(2)

        if txBufferHeader == rxBufferHeader:
            print('Comunicação estabelecida!')
            
            print('Enviando dados para o Server...')
            clientCom.sendData(np.asarray(txBuffer)) 

            print('Aguardando confirmação do envio...')
            rxBufferResponse, nRx = clientCom.getData(txBufferLen)
            
            if rxBufferResponse == txBuffer:
                print('Informação enviada é a mesma que a recebida')
            else:
                print('Informação Enviada divergente da recebida')
            
            
            print('Response recebida pelo server:\n{}\nTamanho da informação: {} bytes'.format(rxBufferResponse,nRx))

            finalTime = time.time()
            totalTime = finalTime - initialTime
            velocity = totalTime/txBufferLen           
        
            print("-------------------------")
            print("Comunicação encerrada")
            print(f'Tempo total da aplicação:\n{totalTime}s')
            print(f'Velocidade:\n{velocity} bytes/s')
            print("-------------------------")
        else:
            print('Comunicação mal estabelecida!')

        clientCom.disable()
        
    except Exception as erro:
        print("Ops! :-\\")
        print(erro)
        clientCom.disable()

    except KeyboardInterrupt:
        clientCom.disable()
        print('Client Finalizado na força!')
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
