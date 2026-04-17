import tkinter as tk
from tkinter import Frame, Label, Button
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import paho.mqtt.client as mqtt
import threading
import random
import time
import winsound
import queue

# ================= CONFIG =================
BROKER = "broker.hivemq.com"
TOPIC = "iot/gasolina/vehiculo1"
UMBRAL = 300

datos = []
cola = queue.Queue()
simulando = False
alertas = 0  # 🔥 CONTADOR

# ================= MQTT =================
client = mqtt.Client(protocol=mqtt.MQTTv311)

def on_connect(client, userdata, flags, rc):
    conexion_label.config(text="🟢 Conectado MQTT", fg="lightgreen")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    valor = float(msg.payload.decode())
    cola.put(valor)

client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, 1883, 60)

# ================= SENSOR =================
def sensor():
    global simulando
    while simulando:
        valor = random.randint(100, 500)
        client.publish(TOPIC, valor)
        time.sleep(2)

# ================= UI =================
root = tk.Tk()
root.title("🚗 Sistema IoT - Detección de Fugas")
root.geometry("1000x700")
root.config(bg="#0f172a")

# ===== HEADER =====
header = Frame(root, bg="#020617", height=60)
header.pack(fill="x")

titulo = Label(header, text="⛽ Sistema IoT de Detección de Fugas",
               font=("Arial", 20, "bold"),
               bg="#020617", fg="white")
titulo.pack(pady=10)

# ===== ESTADO =====
card = Frame(root, bg="#1e293b")
card.pack(pady=10, padx=20, fill="x")

estado_label = Label(card, text="⏸ Sistema detenido",
                     font=("Arial", 20, "bold"),
                     bg="#1e293b", fg="gray")
estado_label.pack(pady=10)

conexion_label = Label(card, text="🔌 Conectando...",
                       font=("Arial", 12),
                       bg="#1e293b", fg="yellow")
conexion_label.pack(pady=5)

# 🔥 CONTADOR VISUAL
contador_label = Label(card, text="🚨 Alertas: 0",
                       font=("Arial", 14, "bold"),
                       bg="#1e293b", fg="orange")
contador_label.pack(pady=5)

# ===== BOTONES =====
botones = Frame(root, bg="#0f172a")
botones.pack(pady=10)

def iniciar():
    global simulando
    if not simulando:
        simulando = True
        estado_label.config(text="🟢 Sistema en ejecución", fg="lightgreen")
        threading.Thread(target=sensor, daemon=True).start()

def detener():
    global simulando
    simulando = False
    estado_label.config(text="⏹ Sistema detenido", fg="gray")

def mostrar_detalles():
    ventana = tk.Toplevel(root)
    ventana.title("📘 Detalles del Sistema")
    ventana.geometry("500x500")
    ventana.config(bg="#0f172a")

    texto = """
🔍 SISTEMA IoT DE DETECCIÓN DE FUGAS

Este sistema simula sensores MQ-2 que detectan vapores de gasolina.

📡 FUNCIONAMIENTO:
- Genera datos entre 100 y 500
- Envía datos por MQTT
- Analiza en tiempo real
- Genera alerta si supera el límite

📊 RANGOS:

🟢 100 - 250 → NORMAL
🟡 251 - 300 → PRECAUCIÓN
🔴 301 - 500 → PELIGRO

🚨 ALERTA:
Se activa cuando el valor supera 300

🎯 OBJETIVO:
Prevenir accidentes, incendios y pérdidas de gasolina
"""

    Label(ventana, text=texto,
          justify="left",
          bg="#0f172a",
          fg="white",
          font=("Arial", 11)).pack(padx=20, pady=20)

Button(botones, text="▶ INICIAR", command=iniciar,
       bg="green", fg="white", width=15, height=2).grid(row=0, column=0, padx=10)

Button(botones, text="⏹ DETENER", command=detener,
       bg="red", fg="white", width=15, height=2).grid(row=0, column=1, padx=10)

Button(botones, text="📘 DETALLES", command=mostrar_detalles,
       bg="blue", fg="white", width=15, height=2).grid(row=0, column=2, padx=10)

# ===== VELOCÍMETRO =====
fig_vel, ax_vel = plt.subplots(figsize=(5,2))
fig_vel.patch.set_facecolor('#0f172a')

canvas_vel = FigureCanvasTkAgg(fig_vel, master=root)
canvas_vel.get_tk_widget().pack(pady=10)

def actualizar_velocimetro(valor):
    ax_vel.clear()

    ax_vel.barh(0, 250, color='green')
    ax_vel.barh(0, 50, left=250, color='yellow')
    ax_vel.barh(0, 200, left=300, color='red')

    ax_vel.plot([valor], [0], 'wo', markersize=12)

    ax_vel.set_xlim(0, 500)
    ax_vel.set_yticks([])
    ax_vel.set_title("Nivel de Fuga de Gasolina", color="white")
    ax_vel.set_facecolor("#0f172a")
    ax_vel.tick_params(colors='white')

    canvas_vel.draw()

# ===== GRÁFICA =====
fig, ax = plt.subplots()
fig.patch.set_facecolor('#0f172a')

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def actualizar_ui():
    global alertas

    while not cola.empty():
        valor = cola.get()
        datos.append(valor)

        if len(datos) > 25:
            datos.pop(0)

        actualizar_velocimetro(valor)

        ax.clear()
        ax.plot(datos, marker='o')
        ax.axhline(y=UMBRAL, linestyle='--')
        ax.set_ylim(0, 500)
        ax.set_title("Monitoreo de Gasolina", color="white")
        ax.set_facecolor("#0f172a")
        ax.tick_params(colors='white')

        canvas.draw()

        if valor > UMBRAL:
            alertas += 1  # 🔥 SUMA ALERTA
            contador_label.config(text=f"🚨 Alertas: {alertas}")

            estado_label.config(text="🚨 FUGA DETECTADA", fg="red")
            winsound.Beep(1200, 300)

        elif simulando:
            estado_label.config(text="🟢 Sistema en ejecución", fg="lightgreen")

    root.after(500, actualizar_ui)

# ================= THREADS =================
threading.Thread(target=client.loop_forever, daemon=True).start()

root.after(500, actualizar_ui)

root.mainloop()