import sounddevice as sd
import soundfile as sf
import time

Fs = 44100
T = 5
sd.default.samplerate = Fs #taxa de amostragem
sd.default.channels = 1  #voce pode ter que alterar isso dependendo da sua placa
numAmostras = T*Fs 
print('Iniciando gravação em 2 segundos...')
time.sleep(2)
print('GRAVANDO!')
audio = sd.rec(int(numAmostras), Fs, channels=1)
sd.wait()
print('GRAVADO! Reproduzindo...')
sd.play(audio, Fs)
sd.wait()
    
filename='projeto8.wav'
print(f'Salvando o arquivo de som em: {filename}')
sf.write(filename, audio, Fs) 
sd.wait()