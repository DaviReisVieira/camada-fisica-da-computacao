

#importe as bibliotecas
import numpy as np
import sys
import sounddevice as sd
import matplotlib.pyplot as plt
import math
from suaBibSignal import signalMeu


def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)

#converte intensidade em Db, caso queiram ...
def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)

def frequenciesRelation(key):
    frequenciesList = {"1":[697, 1209], "2":[697,1336], "3":[697, 1477], "4":[770, 1209], "5":[770, 1336], "6":[770, 1477], "7":[852, 1209], "8":[852,1336], "9":[852, 1477],
    "A": [697, 1633], "B":[770, 1633], "C":[852, 1633], "D":[941,1633], "X":[941, 1209], "0": [941, 1336], "#":[941,1477]}
    # 1209 Hz 1336 Hz 1477 Hz 1633 Hz
    # 697 Hz	1	2	3	A
    # 770 Hz	4	5	6	B
    # 852 Hz	7	8	9	C
    # 941 Hz	*	0	#	D
    freq1 = frequenciesList[key][0]
    freq2 = frequenciesList[key][1]

    return freq1, freq2

def main():
    print("Inicializando encoder...")
    
    #declare um objeto da classe da sua biblioteca de apoio (cedida)
    signal = signalMeu()
    #declare uma variavel com a frequencia de amostragem, sendo 44100
    Fs = 44100
    amplitude = 1
    T = 2
    t = np.linspace(-T/2, T/2, T*Fs)

    teclaSelecionada = input('Digite uma tecla do teclado numérico DTMF (0 a 9, A, B, C, D ou #): ')
    freq1, freq2 = frequenciesRelation(teclaSelecionada)
    
    #voce importou a bilioteca sounddevice como, por exemplo, sd. entao
    # os seguintes parametros devem ser setados:
    sd.default.samplerate = Fs
    sd.default.channels = 1
    
    
    # duration = #tempo em segundos que ira emitir o sinal acustico
    print("Gerando Tons base")
    
    
    #gere duas senoides para cada frequencia da tabela DTMF ! Canal x e canal y 
    _, sin1 = signal.generateSin(freq1,amplitude,T,Fs)
    _, sin2 = signal.generateSin(freq2,amplitude,T,Fs)
    #use para isso sua biblioteca (cedida)
    #obtenha o vetor tempo tb.
    #deixe tudo como array
    sin = sin1+sin2

    #printe a mensagem para o usuario teclar um numero de 0 a 9. 
    #nao aceite outro valor de entrada.
    print("Gerando Tom referente ao símbolo : {}".format(teclaSelecionada))
    
    
    #construa o sunal a ser reproduzido. nao se esqueca de que é a soma das senoides
    
    #printe o grafico no tempo do sinal a ser reproduzido
    # reproduz o som
    sd.play(sin, Fs)
    # Exibe gráficos
    plt.figure()
    plt.plot(t[:400], sin1[:400], 'b--', alpha=0.5, label= (f'{freq1}Hz'))
    plt.plot(t[:400], sin2[:400], 'r--', alpha=0.5, label=(f'{freq2}Hz'))
    plt.plot(t[:400], sin[:400], 'k', alpha=1, label=(f'Soma de {freq1}Hz e {freq2}Hz'))
    plt.legend()
    plt.title(f'Frequências DTMF para {teclaSelecionada}')
    plt.grid(True)
    plt.autoscale(enable=True, axis='both', tight=True)
    plt.show()

    signal.plotFFT(sin, Fs)
    plt.show()
    # aguarda fim do audio
    sd.wait()

if __name__ == "__main__":
    main()
