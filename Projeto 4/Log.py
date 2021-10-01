from datetime import datetime

class Log:

    def __init__(self,side,caseType):
        self.side = side
        self.logFile = open('files/logs/{}{}.txt'.format(side,caseType), 'a')

    def logLine(self,typeSide,type,size,packageSent,totalPackages):
        """
        date: Instante do envio ou recebimento
        typeSide: envio/receb
        type: 3,4,5,...
        size: int
        packageSent: int (caso 3)
        totalPackages: int (caso 3)
        """
        date = datetime.now().strftime('%d/%m/%Y %H:%M:%S.%f')
        message = '{} / {} / {} / {}'.format(date,typeSide,type,size)
        message = message+' / {} / {}'.format(packageSent,totalPackages) if type == 3 else message
        self.logFile.write(message+'\n')

    def logClose(self):
        self.logFile.close()