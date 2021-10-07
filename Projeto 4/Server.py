from Log import Log
from enlace import *
import time
from tqdm import tqdm
from crccheck.crc import Crc16

class Server:

    def __init__(self, serialName= 'COM3',baudRate= 115200, caseType = 1):
       self.serverId = 12
       self.clientId = 0
       self.serialName = serialName
       self.baudRate = baudRate
       self.eopEncoded = b'\xFF\xAA\xFF\xAA'
       self.rxBuffer = self.rxBufferLen = 0
       self.fileId = 0
       self.numberOfPackages = 0
       self.packages = []
       self.caseType = caseType
       self.log = Log('Server',caseType)

    def bufferDecoding(self, buffer):
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
        h0 = buffer[0]
        h1 = buffer[1]
        h2 = buffer[2]
        h3 = buffer[3]
        h4 = buffer[4]
        h5 = buffer[5]
        h6 = buffer[6]
        h7 = buffer[7]
        crc = buffer[7:9]

        self.currentPackage = buffer

        if h0 == 1:
            self.numberOfPackages = h3
            self.fileId = h5
            self.clientId = h1
            self.packageAnalyzed = h4
            self.currentPackageId = h4
            self.currentPackageSize = h5
        elif h0 == 2:
            self.currentPackageId = h4
            self.currentPackageSize = h5
        
        return [h0,h1,h2,h3,h4,h5,h6,h7,crc]

    def changeHeaderByte(self,header,position, value):
        newValue = (value).to_bytes(1, byteorder='big')
        newHeader = header[:position]+newValue+header[position+1:]
        return newHeader


    def handshakePromise(self):
        print('Esperando Head Protocol...')
        rxBuffer, nRxHeaderLen = self.serverCom.getData(14)
        self.log.logLine('receb',rxBuffer[0],len(rxBuffer),rxBuffer[4],rxBuffer[3])

        print('Tamanho do Head: {} bytes.'.format(nRxHeaderLen))
        header = self.bufferDecoding(rxBuffer)
        
        if header[0]==1 and header[2]==self.serverId:
            print('Head Protocol recebido! Client ID: {}.'
            .format(self.clientId))
            newHeader = self.changeHeaderByte(rxBuffer,0,2)
            newHeader = self.changeHeaderByte(newHeader,7,self.packageAnalyzed)
            print('Enviando Handshake...\n')
            self.serverCom.sendData(newHeader)
            self.log.logLine('envio',newHeader[0],len(newHeader),newHeader[4],newHeader[3])

        else:
            print('ERRO: Handshake enviado para Server ID {}'.format(header[2]))
            self.closeConnection()


    def crcCalc(self, data):
        crcResult = Crc16.calc(data)
        crcEncoded = crcResult.to_bytes(2, "big")
        return crcEncoded


    def fileBufferIntegrity(self,package):
        header = self.bufferDecoding(package)
        
        crcClient = package[8:10]
        crcServer = self.crcCalc(package[10:-4])   

        rules = [
            header[0] == 3,
            package[-4:] == self.eopEncoded,
            header[4] == self.packageAnalyzed+1,
            crcClient == crcServer
        ]

        if all(rules):
            self.packageAnalyzed=header[4]
            return [True,header]
        else:
            return [False,header]


    def receiveFileBuffer(self):
        pbar = tqdm(total=self.numberOfPackages,unit='bytes',unit_scale=128,
        desc='Bytes Recebidos')
        
        while len(self.packages)<self.numberOfPackages:
            self.serverCom.fisica.flush()
            rxBuffer, _ = self.serverCom.getData(128,20)

            if not rxBuffer[0]:
                print('ERRO: Client Inativo.(Timeout)')
                response=self.changeHeaderByte(self.currentPackage,0,5)
                response=response[:10]+self.eopEncoded
                self.serverCom.sendData(response)
                self.log.logLine('envio',response[0],len(response),response[4],response[3],response[8:10])

                self.closeConnection()
            else:
                self.log.logLine('receb',rxBuffer[0],len(rxBuffer),rxBuffer[4],rxBuffer[3],rxBuffer[8:10])

            fileIntegrity=self.fileBufferIntegrity(rxBuffer)


            if fileIntegrity[1][0]==5:
                    print('\nERRO: Client Desligado.')
                    self.closeConnection()

            response = 0
            if fileIntegrity[0]:               
                response=self.changeHeaderByte(rxBuffer,0,4)
                response=self.changeHeaderByte(response,7,self.packageAnalyzed)
                self.packages.append(rxBuffer)
                pbar.update(1)
            else:
                response=self.changeHeaderByte(rxBuffer,0,6)
                response=self.changeHeaderByte(response,6,self.packageAnalyzed+1)

            response=response[:10]+self.eopEncoded

            self.serverCom.sendData(response)
            self.log.logLine('envio',response[0],len(response),response[4],response[3],response[8:10])

        pbar.close()


    def startCommunication(self):
        self.handshakePromise()
        self.receiveFileBuffer()

    def fileDecoding(self):
        print('\nIniciando decodificação do arquivo recebido...')

        def cleanPackage(package):
            packageSize=self.bufferDecoding(package)[5]
            packageBuffer=package[10:-4][:packageSize]
            return packageBuffer

        cleanedFileBuffer=[cleanPackage(i) for i in self.packages]
        buffer=bytes.join(b'',cleanedFileBuffer)
        received_file=open('files/receivedFiles/{}.png'.format(self.fileId),'wb')
        received_file.write(buffer)
        received_file.close()
        print('Arquivo {}.png (Size: {} bytes) criado em "files".'
        .format(self.fileId,len(buffer)))


    def closeConnection(self):
        print('\nFechando conexão com o cliente...')
        time.sleep(0.05)
        if len(self.packages)==self.numberOfPackages:
            response = self.packages[-1]
            response=self.changeHeaderByte(response,0,4)    
            self.serverCom.sendData(response)
            self.log.logLine('envio',response[0],len(response),response[4],response[3],response[8:10])

        print('Conexão fechada com client de ID: {}.'.format(self.clientId))
        self.log.logClose()
        self.rxBuffer = self.rxBufferLen = 0
        self.fileId = 0
        self.numberOfPackages = 0
        self.packages = []
        self.packageAnalyzed = 0
        self.currentPackage = 0
        self.currentPackageId = 0
        self.currentPackageSize = 0
        self.killProcess()


    def startServer(self):
        try:
            while True:
                self.serverCom = enlace(self.serialName,self.baudRate)
                self.serverCom.enable()
                self.serverCom.fisica.flush()

                print("""
                --------------------------------
                ------Comunicação Iniciada------
                --------- Porta: {} ----------
                ------ Baud Rate: {} ------
                --------------------------------
                """.format(self.serialName,self.baudRate))
                self.initialTime = time.time()

                print('Servidor aberto.')

                self.startCommunication()

                self.fileDecoding()

                self.closeConnection()
            
        except Exception as erro:
            print("Ops! Erro no Server! :-\\\n",erro)
            self.serverCom.disable()

        except KeyboardInterrupt:
            self.serverCom.disable()
            print('Server Finalizado na força!')


    def killProcess(self):
        print('Server Finalizado.')
        self.serverCom.fisica.flush()
        self.serverCom.disable()


def main():
    serialName = input('Escolha a porta(Enter: COM3): (COM3, COM4,...): ')
    if not serialName:
        serialName='COM3'
    server = Server(serialName,caseType=5)
    server.startServer()

if __name__ == "__main__":
    main()