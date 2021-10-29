#!/usr/bin/env python3
"""Show a text-mode spectrogram using live microphone data."""

#Importe todas as bibliotecas
import numpy as np
import sounddevice as sd
import time
import matplotlib.pyplot as plt
import peakutils
from suaBibSignal import signalMeu


#funcao para transformas intensidade acustica em dB
def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)


def main():
 
    #declare um objeto da classe da sua biblioteca de apoio (cedida) 
    signal = signalMeu()   
    #declare uma variavel com a frequencia de amostragem, sendo 44100
    
    #voce importou a bilioteca sounddevice como, por exemplo, sd. entao
    # os seguintes parametros devem ser setados:
    Fs = 44100
    T = 2
    sd.default.samplerate = Fs#taxa de amostragem
    sd.default.channels = 2  #voce pode ter que alterar isso dependendo da sua placa
    duration = 2 #tempo em segundos que ira aquisitar o sinal acustico captado pelo mic


    numAmostras = Fs * duration
    # faca um printo na tela dizendo que a captacao comecará em n segundos. e entao 
    #use um time.sleep para a espera
    print('Gravando áudio em 2 segundos...')
    time.sleep(2)
   
   #faca um print informando que a gravacao foi inicializada
   
   #declare uma variavel "duracao" com a duracao em segundos da gravacao. poucos segundos ... 
   #calcule o numero de amostras "numAmostras" que serao feitas (numero de aquisicoes)
    print('Iniciando gravação...')
    audio = sd.rec(int(numAmostras), Fs, channels=1)
    sd.wait()
    print("...     FIM")
    print('Reproduzindo áudio...')
    sd.playrec(audio)
    time.sleep(2)
    
    #analise sua variavel "audio". pode ser um vetor com 1 ou 2 colunas, lista ...
    #grave uma variavel com apenas a parte que interessa (dados)
    

    # use a funcao linspace e crie o vetor tempo. Um instante correspondente a cada amostra!
    t = np.linspace(-T/2,T/2,T*Fs)

    # plot do gravico  áudio vs tempo!
   
    yAudio = audio[:,0]
    ## Calcula e exibe o Fourier do sinal audio. como saida tem-se a amplitude e as frequencias
    xf, yf = signal.calcFFT(yAudio, Fs)
    plt.figure("F(y)")
    plt.plot(xf,yf)
    plt.grid()
    plt.title('Fourier audio')

    X, Y = signal.calcFFT(yAudio, Fs)

    picoFrequenias = []
    index = peakutils.indexes(np.abs(Y), thres=0.4, min_dist=20)
    print("index de picos {}" .format(index))
    for freq in X[index]:
        print("Frequências de pico: {}" .format(freq))
        picoFrequenias.append(freq)

    #esta funcao analisa o fourier e encontra os picos
    #voce deve aprender a usa-la. ha como ajustar a sensibilidade, ou seja, o que é um pico?
    #voce deve tambem evitar que dois picos proximos sejam identificados, pois pequenas variacoes na
    #frequencia do sinal podem gerar mais de um pico, e na verdade tempos apenas 1.
   
    frequencyList = [[697, 770, 852, 941], [1209, 1336, 1477, 1633]]
    
    digits = [
        ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]]


    margem = 25
    
    if len(picoFrequenias) < 2:
        print('Por favor, refaça a gravação.')
    else:
        for freq in picoFrequenias:
            for index, value in enumerate(frequencyList[0]):
                if (value-margem) < freq < (value+margem):
                    columnIndex = index

            for index, value in enumerate(frequencyList[1]):
                if (value-margem) < freq < (value+margem):
                    rowIndex = index

        finalDigit = digits[columnIndex][rowIndex]    



    print("Tecla Escolhida: ", finalDigit)
    
    #printe os picos encontrados! 
    
    #encontre na tabela duas frequencias proximas às frequencias de pico encontradas e descubra qual foi a tecla
    #print a tecla.
    
  
    ## Exibe gráficos
    plt.show()

if __name__ == "__main__":
    main()
