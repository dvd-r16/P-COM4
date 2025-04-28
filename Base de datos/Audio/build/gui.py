# Integrado y adaptado: se toma la grafica de audio funcional del primer código y se aplica correctamente sobre la GUI del segundo

import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage
import wave
from datetime import datetime
import os

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

window = Tk()
window.geometry("1536x864")
window.configure(bg="#FFFFFF")

canvas = Canvas(
    window,
    bg="#FFFFFF",
    height=864,
    width=1536,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas.place(x=0, y=0)
canvas.create_rectangle(
    12.0,
    0.0,
    1548.0,
    864.0,
    fill="#FFFFFF",
    outline="")
actualizar_hora_id = None
img_button2 = PhotoImage(file=relative_to_assets("button_2.png"))
img_button2_1 = PhotoImage(file=relative_to_assets("button_2.1.png"))
img_button3 = PhotoImage(file=relative_to_assets("button_3.png"))
img_button3_1 = PhotoImage(file=relative_to_assets("button_3.1.png"))
img_button4 = PhotoImage(file=relative_to_assets("button_4.png"))
img_button4_1 = PhotoImage(file=relative_to_assets("button_4.1.png"))
img_button5 = PhotoImage(file=relative_to_assets("button_5.png"))
img_button5_1 = PhotoImage(file=relative_to_assets("button_5.1.png"))

boton_activo = None
carpeta_destino = None
grabando = False
temporizador_texto_id = None

stream = None
actualizar_audio_id = None

try:
    dispositivos = sd.query_devices()
    indice_microfono = next(i for i, d in enumerate(dispositivos) if d['max_input_channels'] > 0)
except Exception as e:
    print(f"Error al detectar el micrófono: {e}")
    indice_microfono = None

if indice_microfono is not None:
    FS = 44100
    CHUNK = 1024
    BUFFER_SIZE = CHUNK * 100
    AMPLIFICACION_VISUAL = 5

   

    fig, ax = plt.subplots(figsize=(2.5, 6.0), dpi=100, facecolor='black')
    buffer_audio = np.zeros(BUFFER_SIZE)
    line, = ax.plot(buffer_audio, np.arange(BUFFER_SIZE), color='red')
    ax.set_facecolor('black')
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(0, BUFFER_SIZE)
    ax.invert_yaxis()
    ax.axis('off')

    canvas_graf = FigureCanvasTkAgg(fig, master=canvas)
    canvas_graf_widget = canvas_graf.get_tk_widget()
    canvas_graf_widget.place(x=110, y=270, width=400, height=520)

    from datetime import datetime

def actualizar_hora():
    global actualizar_hora_id
    now = datetime.now()
    hora_actual = now.strftime("%H:%M")
    canvas.itemconfig(texto_hora_id, text=hora_actual)
    actualizar_hora_id = window.after(1000, actualizar_hora)  # 👈 Guarda el after_id


    stream = sd.InputStream(device=indice_microfono, channels=1, samplerate=FS, blocksize=CHUNK)
    stream.start()

    def actualizar_grafico_audio():
        global actualizar_audio_id
        try:
            audio, _ = stream.read(CHUNK)
            audio = np.squeeze(audio) * AMPLIFICACION_VISUAL
            global buffer_audio
            buffer_audio = np.roll(buffer_audio, -CHUNK)
            buffer_audio[-CHUNK:] = audio
            line.set_xdata(buffer_audio)
            line.set_ydata(np.arange(BUFFER_SIZE))
            canvas_graf.draw_idle()
            actualizar_audio_id = window.after(50, actualizar_grafico_audio)
        except Exception as e:
            print(f"Error en actualizar_grafico_audio: {e}")

    actualizar_grafico_audio()

def cerrar_ventana():
    global stream, actualizar_audio_id, actualizar_hora_id
    try:
        if stream:
            stream.stop()
            stream.close()
        if actualizar_audio_id:
            window.after_cancel(actualizar_audio_id)
        if actualizar_hora_id:
            window.after_cancel(actualizar_hora_id)
    except Exception as e:
        print(f"Error cerrando recursos: {e}")
    window.quit()


def seleccionar_carpeta(boton_id):
    global boton_activo, carpeta_destino
    botones = {'3': button_3, '4': button_4, '5': button_5}
    rutas = {'3': OUTPUT_PATH.parent / "ORP", '4': OUTPUT_PATH.parent / "IRP", '5': OUTPUT_PATH.parent / "REP"}
    normales = {'3': img_button3, '4': img_button4, '5': img_button5}
    activas = {'3': img_button3_1, '4': img_button4_1, '5': img_button5_1}
    if boton_activo == boton_id:
        botones[boton_id].config(image=normales[boton_id])
        boton_activo = carpeta_destino = None
    else:
        for k in botones: botones[k].config(image=normales[k])
        botones[boton_id].config(image=activas[boton_id])
        boton_activo, carpeta_destino = boton_id, rutas[boton_id]
    button_2.config(image=img_button2_1 if boton_activo else img_button2)

def grabar_audio():
    global carpeta_destino, grabando, temporizador_texto_id
    if not carpeta_destino or grabando: return
    grabando = True
    duracion = 5
    fs = 44100
    texto_temporizador = ["5s", "4s", "3s", "2s", "1s", "0s"]
    segundos = [0]

    def actualizar_temporizador():
        if segundos[0] <= 5:
            canvas.itemconfig(temporizador_texto_id, text=texto_temporizador[segundos[0]])
            segundos[0] += 1
            window.after(1000, actualizar_temporizador)
        else:
            guardar_audio()
            canvas.itemconfig(temporizador_texto_id, text="5s")
            global grabando
            grabando = False

    def guardar_audio():
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        ruta_archivo = os.path.join(carpeta_destino, f"{timestamp}.wav")
        audio_data = sd.rec(int(duracion * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        with wave.open(ruta_archivo, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(audio_data.tobytes())

    canvas.itemconfig(temporizador_texto_id, text="5s")
    window.after(1000, actualizar_temporizador)



image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    152.0,
    143.0,
    image=image_image_1
)

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=cerrar_ventana,
    relief="flat"
)
button_1.place(
    x=1278.0,
    y=70.0,
    width=149.0,
    height=149.0
)

image_image_2 = PhotoImage(
    file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(
    398.0,
    144.0,
    image=image_image_2
)

texto_hora_id = canvas.create_text(
    300.0,
    100.0,
    anchor="nw",
    text="HH:MM",
    fill="#FFFFFF",
    font=("Inter Bold", 72 * -1)
)

image_image_3 = PhotoImage(
    file=relative_to_assets("image_3.png"))
image_3 = canvas.create_image(
    314.0,
    538.0,
    image=image_image_3
)

button_2 = Button(
    image=img_button2,
    borderwidth=0,
    highlightthickness=0,
    command=grabar_audio,
    relief="flat"
)
button_2.place(x=601.0, y=438.0, width=309.0, height=309.0)


button_3 = Button(
    image=img_button3,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: seleccionar_carpeta('3'),
    relief="flat"
)
button_3.place(x=960.0, y=308.0, width=458.0, height=157.0)


button_4 = Button(
    image=img_button4,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: seleccionar_carpeta('4'),
    relief="flat"
)
button_4.place(x=960.0, y=483.0, width=458.0, height=157.0)


image_image_4 = PhotoImage(
    file=relative_to_assets("image_4.png"))
image_4 = canvas.create_image(
    756.0,
    354.0,
    image=image_image_4
)

temporizador_texto_id = canvas.create_text(
    628.0,
    310.0,
    anchor="nw",
    text="-",
    fill="#000000",
    font=("Inter Bold", 72 * -1)
)

canvas.create_text(
    602.0,
    237.0,
    anchor="nw",
    text="Tiempo:",
    fill="#000000",
    font=("Inter Bold", 50 * -1)
)

canvas.create_text(
    960.0,
    237.0,
    anchor="nw",
    text="Tipo de daño:",
    fill="#000000",
    font=("Inter Bold", 50 * -1)
)

canvas.create_text(
    619.0,
    101.0,
    anchor="nw",
    text="GRABAR AUDIO",
    fill="#060606",
    font=("Inter Bold", 72 * -1)
)


button_5 = Button(
    image=img_button5,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: seleccionar_carpeta('5'),
    relief="flat"
)
button_5.place(x=960.0, y=658.0, width=458.0, height=157.0)


window.resizable(False, False)
actualizar_hora()
window.mainloop()
