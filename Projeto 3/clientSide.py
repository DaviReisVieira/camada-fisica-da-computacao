####################################################
#Camada Física da Computação
#Davi Reis Vieira de Souza
#27/08/2021
#Client Side
####################################################

from enlace import *
import time
import random

#   python -m serial.tools.list_ports
serialName = "COM4"

def main():
    try:
        clientCom = enlace(serialName,57600)
        clientCom.enable()
        clientCom.fisica.flush()

        print('Comunicação Iniciada...')
        initialTime = time.time()

        commandList = [b'\x00\xFF',b'\x00',b'\x0F',b'\xF0',b'\xFF\x00',b'\xFF']

        commands = [(commandList[random.randint(0,5)]) for i in range(random.randint(10,30))]
        message = [(i+b'\xee') for i in commands]
        txBuffer = (b''.join(message))
        txBufferLen = len(txBuffer)

        print('Comandos a serem enviados:\n{}\nTotal de Comandos: {}\n'.format(commands,len(commands)))
        print('Mensagem a ser enviada:\n{}.\nTamanho da mensagem ENVIADA: {} bytes.\n'.format(txBuffer,txBufferLen))
  
        print('Enviando início do protocolo...')
        txBufferHeader = txBufferLen.to_bytes(2, byteorder="big")
        clientCom.sendData(txBufferHeader)
        
        print('Aguardando Handshake...')
        rxBufferHeader, nRx = clientCom.getData(2)

        if txBufferHeader == rxBufferHeader:
            print('Comunicação estabelecida!')
            
            print('Enviando dados para o Server...')
            clientCom.sendData((txBuffer)) 

            print('Aguardando confirmação do envio...\n')
            rxBufferResponse, nRx = clientCom.getData(txBufferLen)

            if rxBufferResponse == txBuffer:
                print('Informação Enviada é IGUAL a recebida!')
            else:
                print('Informação Enviada DIVERGENTE da recebida.')

            
            print('\nResponse recebida pelo server:\n{}\nTamanho da informação RECEBIDA: {} bytes.\n'.format(rxBufferResponse,nRx))

            numberOfCommands = len(commands).to_bytes(2, byteorder="big")
            numberOfCommandsResponse, nRx = clientCom.getData(2)
            lenNumberOfCommandsResponse = int.from_bytes(numberOfCommandsResponse, "big")
            
            print('\nNúmero de Comandos Enviados: {} comandos.\nNúmero de Comandos Recebidos: {} comandos.\n'.format(len(commands),lenNumberOfCommandsResponse))
            
            if numberOfCommands == numberOfCommandsResponse:
                print('Número de comandos Enviados é IGUAL a recebida!')
            else:
                print('Número de comandos Enviados é DIVERGENTE da recebida.')

            finalTime = time.time()
            totalTime = finalTime - initialTime
            velocity = totalTime/txBufferLen           
        
            print("-------------------------------")
            print("Comunicação encerrada")
            print(f'Tempo total da aplicação:\n{totalTime}s')
            print(f'Velocidade:\n{velocity} bytes/s')
            print("-------------------------------")
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
        

if __name__ == "__main__":
    main()