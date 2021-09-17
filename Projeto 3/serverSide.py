####################################################
#Camada Física da Computação
#Davi Reis Vieira de Souza
#27/08/2021
#Server Side
####################################################

from enlace import *
import time

#   python -m serial.tools.list_ports
serialName = "COM3"

def getCommands(messageString):
    commands = messageString.split(b'\xee')
    del commands[-1]
    return commands

def main():
    try:
        serverCom = enlace(serialName,115200)

        serverCom.enable()
        serverCom.fisica.flush()

        print('Servidor aberto.')
        
        print('Esperando Head Protocol...')
        rxBufferHeader, nRxHeaderLen = serverCom.getData(14)
        print(rxBufferHeader)
        rxBufferResponse = int.from_bytes(rxBufferHeader, "big")
        print('Tamanho do dado: {}.'.format(nRxHeaderLen))
        print('Head Protocol recebido!')
        initialTime = time.time()

        print('Enviando Handshake..')
        serverCom.sendData(rxBufferHeader) 
        print('Handshake realizado!')

        print('Esperando Dados do Client...')
        rxBuffer, nRx = serverCom.getData(rxBufferResponse)
        
        rxLen = len(rxBuffer)
        print("Dado recebido: {}\n" .format(rxBuffer))
        print("Foram recebidos {} bytes." .format(nRx))

        commands = getCommands(rxBuffer)
        print('\nComandos recebidos: {}.\nTotal de comandos: {} Comandos.\n'.format(commands,len(commands)))

        serverCom.sendData(rxBuffer)

        time.sleep(0.05)
        txBufferLen = len(commands).to_bytes(2, byteorder="big")
        serverCom.sendData(txBufferLen)


        finalTime = time.time()
        totalTime = finalTime - initialTime
        velocity = totalTime/rxLen           
    
        print("-------------------------------")
        print("Comunicação encerrada")
        print(f'Tempo total da aplicação:\n{totalTime}s')
        print(f'Velocidade:\n{velocity} bytes/s')
        print("-------------------------------")
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
