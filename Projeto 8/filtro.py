#!/usr/bin/env python3

# sudo pip install PeakUtils

import numpy as np
import sounddevice as sd
import soundfile   as sf
import matplotlib.pyplot as plt

from scipy.fftpack import fft
from scipy import signal
from scipy import signal as sg

def generateSin(freq, amplitude, time, fs):
        n = time*fs
        x = np.linspace(0.0, time, n)
        s = amplitude*np.sin(freq*x*2*np.pi)
        return (x, s)

def calcFFT(signal, fs):
        # https://docs.scipy.org/doc/scipy/reference/tutorial/fftpack.html
        N  = len(signal)
        T  = 1/fs
        xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
        yf = fft(signal)
        return(xf, yf[0:N//2])

def filtro(y, samplerate, cutoff_hz):
  # https://scipy.github.io/old-wiki/pages/Cookbook/FIRFilter.html
    nyq_rate = samplerate/2
    width = 5.0/nyq_rate
    ripple_db = 60.0 #dB
    N , beta = sg.kaiserord(ripple_db, width)
    taps = sg.firwin(N, cutoff_hz/nyq_rate, window=('kaiser', beta))
    yFiltrado = sg.lfilter(taps, 1.0, y)
    return yFiltrado

def LPF(signal, cutoff_hz, fs):
        #####################
        # Filtro
        #####################
        # https://scipy.github.io/old-wiki/pages/Cookbook/FIRFilter.html
        nyq_rate = fs/2
        width = 5.0/nyq_rate
        ripple_db = 60.0 #dB
        N , beta = sg.kaiserord(ripple_db, width)
        taps = sg.firwin(N, cutoff_hz/nyq_rate, window=('kaiser', beta))
        return( sg.lfilter(taps, 1.0, signal))

def main():
    fs = 44100
    sd.default.samplerate = fs
    sd.default.channels = 1

    audio, samplerate = sf.read('projeto8.wav')
    print(f'Sample Rate: {samplerate}Hz')

    yAudio = audio
    samplesAudio = len(yAudio)

    print('Áudio Original em execução...')
    sd.play(audio)
    sd.wait()

    #####################
    # Normaliza audio
    #####################
    print('Normalizando Áudio...')
    audioMax = np.max(np.abs(yAudio))
    yAudioNormalizado = yAudio/audioMax

    plt.figure("Gráfico 1: Sinal de áudio original normalizado – domínio do tempo")
    plt.plot(yAudioNormalizado)
    plt.grid()
    plt.title('Áudio Normalizado vs Tempo (s)')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Amplitude')
    
    #####################
    # Filtro
    #####################
    print('Áudio sendo Filtrado...')
    #####################
    # Aplica filtro no sinal
    #####################
    yfiltrado = LPF(audio, 4000, fs)
    print('Áudio Filtrado em execução...')
    sd.play(yfiltrado)
    sd.wait()

    plt.figure("Gráfico 2: Sinal de áudio filtrado – domínio do tempo")
    plt.plot(yfiltrado)
    plt.grid()
    plt.title('Áudio Filtrado vs Tempo (s)')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Amplitude')
    #####################
    # FFT Sinal filtrado
    #####################
    X, Y = calcFFT(yfiltrado, samplerate)
    plt.figure("Gráfico 3: Sinal de áudio filtrado – domínio da frequência")
    plt.plot(X, np.abs(Y))
    plt.grid()
    plt.title('Sinal de áudio filtrado – domínio da frequência')

    #####################
    # Gera portadora
    #####################
    freqPortadora = 14000
    xPortadora, yPortadora = generateSin(freqPortadora, 1, int(samplesAudio/samplerate), samplerate)
    # plt.figure("Portadora")
    # plt.title('Portadora')
    # plt.plot(xPortadora[0:500], yPortadora[0:500])
    # plt.grid()

    #####################
    # Gera sinal AM
    # AM-SC
    #####################
    yAM = yfiltrado * yPortadora
    # plt.figure("AM")
    # plt.title('AM')
    # plt.plot(yAM[0:500])
    # plt.grid()

    plt.figure("Gráfico 4: Sinal de áudio modulado – domínio do tempo")
    plt.plot(yAM)
    plt.grid()
    plt.title('Áudio Filtrado vs Tempo (s)')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Amplitude')

    sf.write('projeto8_modulado.wav', yAM, fs) 
    sd.wait()

    # Fourier mensagem
    XAM, YAM = calcFFT(yAM, samplerate)
    plt.figure("Gráfico 5: sinal de áudio modulado – domínio da frequência")
    plt.plot(XAM, np.abs(YAM))
    plt.grid()
    plt.title('Sinal de áudio modulado – domínio da frequência')

    #####################
    # Demodula sinal AM
    # AM-SC
    # via product detection e low pass filter
    # https://en.wikipedia.org/wiki/Product_detector
    #####################
    audioAM, audioAMFS = sf.read('projeto8_modulado.wav')
    yAMFile = audioAM

    xPortadoraDemod, yPortadoraDemod = generateSin(freqPortadora, 1, int(len(yAMFile)/samplerate), samplerate)

    yDemod = yAMFile * yPortadoraDemod
    
    yDemodFiltrado = LPF(yDemod, 4000, fs)

    XAMDemod, YAMDemod = calcFFT(yDemod, samplerate)
    XAMDemodFiltrado, YAMDemodFiltrado = calcFFT(yDemodFiltrado, samplerate)
    plt.figure("Gráfico 6: Sinal de áudio demodulado")
    plt.plot(XAMDemod, np.abs(YAMDemod))
    plt.grid()
    plt.title('Sinal de áudio demodulado')

    plt.figure("Gráfico 7: Sinal de áudio demodulado e filtrado")
    plt.plot(XAMDemodFiltrado, np.abs(YAMDemodFiltrado))
    plt.grid()
    plt.title('Sinal de áudio demodulado e filtrado')


    #####################
    # Reproduz audio
    #####################
    print('Reproduzindo Áudio Demodulado...')
    sd.play(yDemod, samplerate)
    sd.wait()

    #####################
    # Reproduz audio
    #####################
    print('Reproduzindo Áudio Demodulado e Filtrado...')
    sd.play(yDemodFiltrado, samplerate)
    sd.wait()


    ## Exibe gráficos
    plt.show()
    sd.wait()

    


if __name__ == "__main__":
    main()
