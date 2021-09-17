from enlace import *
import time

class Server:

    def __init__(self, fileName='received_image.png', serialName= 'COM3', baudRate= 115200):
       self.serverId = 12
       self.clientId = 14
       self.fileName = fileName
       self.serialName = serialName
       self.baudRate = baudRate
       self.eopEncoded = b'\x02\x05\x00\x07'
       self.rxBuffer = self.rxBufferLen = 0
       self.fileId = 0
       self.numberOfPackages = 0
       self.packages = []

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
        h8 = buffer[8]
        h9 = buffer[9]

        if h0 == 1:
            self.numberOfPackages = h3
            self.fileId = h5
            self.packageAnalyzed = h4
            self.currentPackage = h4
            self.currentPackageSize = h5
        elif h0 == 2:
            self.currentPackage = h4
            self.currentPackageSize = h5
        
        return [h0,h1,h2,h3,h4,h5,h6,h7,h8,h9]

    def changeHeaderByte(self,header,position, value):
        newValue = (value).to_bytes(1, byteorder='big')
        newHeader = header[:position]+newValue+header[position+1:]
        return newHeader


    def handshakePromise(self):
        print('Esperando Head Protocol...')
        rxBufferHeader, nRxHeaderLen = self.serverCom.getData(14)
        print('Tamanho do Head: {}.'.format(nRxHeaderLen))
        header = self.bufferDecoding(rxBufferHeader)
        
        if header[0]==1 and header[2]==self.serverId:
            print('Head Protocol recebido!')
            newHeader = self.changeHeaderByte(rxBufferHeader,0,2)

        print('Enviando Handshake...')
        self.serverCom.sendData(newHeader)


    def fileBufferIntegrity(self,package):
        header = self.bufferDecoding(package)
        if package[-4:]==self.eopEncoded and header[4]== self.packageAnalyzed+1:
            print('sequencial',header[4])
            self.packageAnalyzed=header[4]
            return True
        else:
            return False


    def receiveFileBuffer(self):
        while len(self.packages)<self.numberOfPackages:
            print(len(self.packages),self.numberOfPackages)
            self.serverCom.fisica.flush()
            rxBufferHeader, nRxHeaderLen = self.serverCom.getData(128)
            fileBufferIntegrity=self.fileBufferIntegrity(rxBufferHeader)

            responseBuffer = 0
            if fileBufferIntegrity:                
                responseBuffer=self.changeHeaderByte(rxBufferHeader,0,4)
                self.packages.append(rxBufferHeader)
            else:
                responseBuffer=self.changeHeaderByte(rxBufferHeader,0,6)
            print('RECEBIDO:',rxBufferHeader, len(self.packages))
            self.serverCom.sendData(responseBuffer)


    def startCommunication(self):
        self.handshakePromise()
        self.receiveFileBuffer()

    def fileDecoding(self):
        print('Iniciando decodificação do arquivo recebido...')

        def cleanPackage(package):
            packageSize=self.bufferDecoding(package)[5]
            packageBuffer=package[10:-4][:packageSize]
            return packageBuffer

        cleanedFileBuffer=[cleanPackage(i) for i in self.packages]
        buffer=bytes.join(b'',cleanedFileBuffer)
        received_file=open('files/received_image.png','wb')
        received_file.write(buffer)
        received_file.close()
        print('Arquivo received_image.png criado em "files".')


    def closeConnection(self):
        pass

    
    def startServer(self):
        try:
            self.serverCom = enlace(self.serialName,self.baudRate)
            self.serverCom.enable()
            self.serverCom.fisica.flush()

            print("""
            --------------------------------
            ------Comunicação Iniciada------
            --------- Porta: {} ----------
            -------- Baud Rate: {} ------
            --------------------------------
            """.format(self.serialName,self.baudRate))
            self.initialTime = time.time()

            print('Servidor aberto.')

            self.startCommunication()

            self.fileDecoding()

            self.closeConnection()
            
            self.serverCom.disable()

        except Exception as erro:
            print("Ops! Erro no Server! :-\\\n",erro)
            self.serverCom.disable()

        except KeyboardInterrupt:
            self.serverCom.disable()
            print('Server Finalizado na força!')


    def killProcess(self):
        print('Server Finalizado.')
        self.serverCom.disable()


def main():
    server = Server()
    server.startServer()

if __name__ == "__main__":
    main()