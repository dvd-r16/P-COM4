import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Configuraciones
DURACION = 0.05  # duración de cada muestra en segundos
FS = 44100  # frecuencia de muestreo
FRAMES = int(DURACION * FS)
AMPLIFICACION_VISUAL = 5  # Aumenta la sensibilidad visual
BUFFER_SIZE = FRAMES * 100  # Número total de muestras a mostrar en el barrido

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))

# Gráfica de barrido de forma de onda
buffer_audio = np.zeros(BUFFER_SIZE)
linea_audio, = ax1.plot(buffer_audio, lw=1)
ax1.set_ylim(-1, 1)
ax1.set_xlim(0, BUFFER_SIZE)
ax1.set_title("Barrido de forma de onda del micrófono")
ax1.set_xlabel("Muestras acumuladas")
ax1.set_ylabel("Amplitud")

# Gráfica de volumen
barra_volumen = ax2.bar([0], [0], width=0.6, color='green')
texto_volumen = ax2.text(0, 0.5, "Vol: 0.00", ha='center', va='bottom', fontsize=12, color='black')
ax2.set_ylim(0, 1)
ax2.set_xlim(-1, 1)
ax2.set_title("Nivel de volumen")
ax2.set_ylabel("Volumen RMS")
ax2.set_xticks([])

def actualizar(frame):
    global buffer_audio
    try:
        audio = sd.rec(FRAMES, samplerate=FS, channels=1, dtype='float32')
        sd.wait()
        audio = audio.flatten() * AMPLIFICACION_VISUAL

        # Desplaza el buffer y agrega nuevas muestras al final
        buffer_audio = np.roll(buffer_audio, -FRAMES)
        buffer_audio[-FRAMES:] = audio

        linea_audio.set_ydata(buffer_audio)

        # Calcula y muestra el volumen RMS
        rms = np.sqrt(np.mean(audio**2))
        barra_volumen[0].set_height(rms)
        texto_volumen.set_text(f"Vol: {rms:.2f}")
        texto_volumen.set_position((0, rms))

    except Exception as e:
        print("Error capturando audio:", e)

    return linea_audio, barra_volumen, texto_volumen

ani = FuncAnimation(fig, actualizar, interval=int(DURACION*1000), blit=False)
plt.tight_layout()
plt.show()