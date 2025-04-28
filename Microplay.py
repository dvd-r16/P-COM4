import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# IDs de micrófonos (ajusta según tu sistema)
MIC_ID_1 = 1
MIC_ID_2 = 3
CHUNK = 1024
RATE = 44100

p = pyaudio.PyAudio()

stream1 = p.open(format=pyaudio.paInt16,
                 channels=1,
                 rate=RATE,
                 input=True,
                 input_device_index=MIC_ID_1,
                 frames_per_buffer=CHUNK)

stream2 = p.open(format=pyaudio.paInt16,
                 channels=1,
                 rate=RATE,
                 input=True,
                 input_device_index=MIC_ID_2,
                 frames_per_buffer=CHUNK)

# Crear figura con 4 subplots (2 por micrófono)
fig, axs = plt.subplots(2, 2, figsize=(10, 6))

# Tiempo
x = np.arange(0, CHUNK)
line1, = axs[0, 0].plot(x, np.random.rand(CHUNK), lw=2)
line2, = axs[1, 0].plot(x, np.random.rand(CHUNK), lw=2)

# Frecuencia (FFT)
xf = np.fft.rfftfreq(CHUNK, 1.0 / RATE)
fft_line1, = axs[0, 1].plot(xf, np.zeros_like(xf), lw=2)
fft_line2, = axs[1, 1].plot(xf, np.zeros_like(xf), lw=2)

# Configurar límites y títulos
axs[0, 0].set_ylim(-30000, 30000)
axs[1, 0].set_ylim(-30000, 30000)
axs[0, 1].set_ylim(0, 5000)
axs[1, 1].set_ylim(0, 5000)

axs[0, 0].set_title("Micrófono 1 - Tiempo")
axs[0, 1].set_title("Micrófono 1 - Frecuencia")
axs[1, 0].set_title("Micrófono 2 - Tiempo")
axs[1, 1].set_title("Micrófono 2 - Frecuencia")

# Animación
def update(frame):
    # Leer datos
    data1 = np.frombuffer(stream1.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
    data2 = np.frombuffer(stream2.read(CHUNK, exception_on_overflow=False), dtype=np.int16)

    # Tiempo
    line1.set_ydata(data1)
    line2.set_ydata(data2)

    # FFT
    fft_data1 = np.abs(np.fft.rfft(data1)) / CHUNK
    fft_data2 = np.abs(np.fft.rfft(data2)) / CHUNK
    fft_line1.set_ydata(fft_data1)
    fft_line2.set_ydata(fft_data2)

    return line1, line2, fft_line1, fft_line2

ani = animation.FuncAnimation(fig, update, interval=50, blit=True)
plt.tight_layout()
plt.show()
