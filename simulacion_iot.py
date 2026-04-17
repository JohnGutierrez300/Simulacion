import random
import time
import threading
import paho.mqtt.client as mqtt

# Configuración
BROKER = "broker.hivemq.com"
TOPIC = "sensor/gasolina"
UMBRAL_GAS = 300

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("✅ Conectado al broker MQTT")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    valor = float(msg.payload.decode())
    print(f"📥 Dato recibido: {valor}")

    if valor > UMBRAL_GAS:
        print("🚨 ALERTA: Posible fuga de gasolina 🚨")

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883, 60)

def simular_sensor():
    print("📡 Sensor iniciado...")
    while True:
        valor = random.randint(100, 500)
        print(f"📤 Enviando dato: {valor}")
        client.publish(TOPIC, valor)
        time.sleep(5)

# Hilo
thread = threading.Thread(target=simular_sensor)
thread.daemon = True
thread.start()

print("🚀 Simulación iniciada...")

client.loop_forever()