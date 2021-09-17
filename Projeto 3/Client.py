from enlace import *
import time
from tqdm import tqdm
import os

class Client:

    def __init__(self, fileName='1.png', serialName= 'COM4', baudRate= 115200):
       self.serverId = 12
       self.clientId = 14
       self.fileName = fileName
       self.serialName = serialName
       self.baudRate = baudRate
       self.eopEncoded = b'\x02\x05\x00\x07'
       self.txBuffer = self.txBufferLen = 0
       self.packages = []
       self.numberOfPackages = 0

    
    def headerEnconding(self,typeOfMessage:int,numberOfPackage:int,packageSize:int=1):
        '''
        h0 – tipo de mensagem
        h1 – id do cliente
        h2 – id do servidor
        h3 – número total de pacotes do arquivo
        h4 – número do pacote sendo enviado
        h5 – se tipo for handshake:id do arquivo||se tipo for dados: tamanho do payload
        h6 – pacote solicitado para recomeço quando a erro no envio.
        h7 – último pacote recebido com sucesso.
        h8 – h9 – CRC
        '''
        h0 = (typeOfMessage).to_bytes(1,byteorder="big")
        h1 = (self.clientId).to_bytes(1,byteorder="big")
        h2 = (self.serverId).to_bytes(1,byteorder="big")
        h3 = (self.numberOfPackages).to_bytes(1,byteorder="big")
        h4 = (numberOfPackage).to_bytes(1,byteorder="big")
        h5 = (packageSize).to_bytes(1,byteorder="big")
        h6 = (0).to_bytes(1,byteorder="big")
        h7 = (0).to_bytes(1,byteorder="big")
        h8 = (0).to_bytes(1,byteorder="big")
        h9 = (0).to_bytes(1,byteorder="big")

        return h0+h1+h2+h3+h4+h5+h6+h7+h8+h9


    def bufferEncoding(self):
        numberOfPackages = self.txBufferLen//114
        self.numberOfPackages = numberOfPackages if self.txBufferLen%114==0 else numberOfPackages+1
        
        fileNameId=int(self.fileName.split('.')[0])
        header = self.headerEnconding(1,0,fileNameId)+self.eopEncoded
        self.packages.append(header)            
            
        filePackages = [self.txBuffer[i:i+114] for i in range(0,self.txBufferLen,114)]

        def packageEncoding(i:int):
            body = filePackages[i]
            header = self.headerEnconding(3,i+1,len(body))
            
            if len(body)!=114:
                body=body+ (0).to_bytes(114-len(body), byteorder="big")

            return header+body+self.eopEncoded

        filePackagesEncoded = [packageEncoding(i) for i in range(0,len(filePackages))]

        self.packages = self.packages+filePackagesEncoded

    def bufferDecoding(self, buffer):
        h0 = buffer[0]
        h1 = buffer[1]
        h2 = buffer[2]
        h3 = buffer[3]
        h4 = buffer[4]
        h5 = buffer[5]
        h6 = buffer[6]
        h7 = buffer[7]
        h8 = buffer[8]
        h9 = buffer[9]
        
        return [h0,h1,h2,h3,h4,h5,h6,h7,h8,h9]
    
    def changeHeaderByte(self,header,position, value):
        newValue = (value).to_bytes(1, byteorder='big')
        newHeader = header[:position]+newValue+header[position+1:]
        return newHeader

    def sendHandshake(self,i):
        sendingHeader= True
        while sendingHeader:
            self.clientCom.sendData(i)
            
            print('Aguardando Handshake...')
            rxBuffer, nRx = self.clientCom.getData(14,5)
            
            if not rxBuffer[0]:
                clientRetry = input("\n\nServidor inativo. Tentar novamente? s/n: ")
                if clientRetry == 's':
                    sendingHeader = True
                elif clientRetry == 'n':
                    sendingHeader = False
                    return False
            else:
                sendingHeader = False
                if rxBuffer[0] == 2 and rxBuffer[1:] == i[1:]:
                    print('Handshake concluído com sucesso! Server ID: {}'.format(rxBuffer[2]))
                    return True
                else:
                    print('Handshake mal sucedido...')
                    return False
    

    def sendPackage(self,package,index):
        # print('\nEnviando pacote: {}/{}'.format(index,len(self.packages)))
        self.clientCom.fisica.flush()
        packageNotSent=True
        while packageNotSent:
            self.clientCom.sendData(package)
            rxBuffer, nRx = self.clientCom.getData(len(package),5)

            if not rxBuffer[0]:
                packageTimeOut = self.changeHeaderByte(package,0,5)
                self.clientCom.sendData(packageTimeOut)
                clientRetry = input("Servidor inativo. Tentar novamente? s/n: ")
                if clientRetry == 's':
                    return False
                elif clientRetry == 'n':
                    self.killProcess()

            header = self.bufferDecoding(rxBuffer)
            if rxBuffer[1:] == package[1:] and header[0]==4:
                # print('RECEBIDO OK')
                packageNotSent=False
                return package       


    def startTransmission(self):
        currentPackage = lastPackage = []
        handshakeSuccessful = False
        pbar = tqdm(total=self.numberOfPackages,unit='packages',desc='Packages Enviados:')
        for i, package in enumerate(self.packages):
            currentPackage = package
            if package == self.packages[0]:  
                print('\nEnviando início do protocolo...')
                handshakeReponse = self.sendHandshake(package)
                if handshakeReponse:
                    lastPackage = package
                    handshakeSuccessful=True
                else:
                    self.killProcess()

            if handshakeSuccessful and package != self.packages[0]:
                response = self.sendPackage(package,i)
                lastPackage = response
                pbar.update(1)
        pbar.close()

    
    def closeConnection(self):
        print('\nAguardando confirmação de recebimento...')
        rxBuffer, nRx = self.clientCom.getData(len(self.packages[-1]))
        if rxBuffer==self.packages[-1]:
            print('Todos os pacotes foram recebidos com sucesso.')
        else:
            print('Erro ao enviar todos os arquivos...')
        self.killProcess()



    def startClient(self):
        try:
            self.clientCom = enlace(self.serialName,self.baudRate)
            self.clientCom.enable()
            self.clientCom.fisica.flush()

            print("""
            --------------------------------
            ------Comunicação Iniciada------
            --------- Porta: {} ----------
            ------ Baud Rate: {} ------
            --------------------------------
            """.format(self.serialName,self.baudRate))
            self.initialTime = time.time()

            file = open("files/sendFiles/{}".format(self.fileName),"rb")
            self.txBuffer=file.read()
            self.txBufferLen=len(self.txBuffer)
            file.close()

            print("""- Arquivo a ser enviado: {}. Tamanho: {} bytes.
            """.format(self.fileName,self.txBufferLen))

            print('Criando buffer para envio...')

            self.bufferEncoding()

            self.startTransmission()

            self.closeConnection()
            
            self.clientCom.disable()

        except Exception as erro:
            print("Ops! Erro no Client! :-\\\n",erro)
            self.clientCom.disable()

        except KeyboardInterrupt:
            self.clientCom.disable()
            print('Client Finalizado na força!')


    def killProcess(self):
        print('Client Finalizado.')
        self.clientCom.fisica.flush()
        self.clientCom.disable()


def main():
    files = os.listdir('files/sendFiles')
    for i,value in enumerate(files):
        print('{} - {}'.format(i,value))
    fileSelectedId = int(input('Escolha um arquivo: '))
    client = Client(files[fileSelectedId])
    client.startClient()

if __name__ == "__main__":
    main()