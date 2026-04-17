// ================= CONFIG =================
const BROKER = "wss://test.mosquitto.org:8081/mqtt";
const TOPIC = "sensor/gasolina";
const UMBRAL_GAS = 300;

let simulando = true;

// ================= MQTT =================
const client = mqtt.connect(BROKER);

// 🔊 desbloquear audio en navegador
document.addEventListener("click", () => {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    ctx.resume();
});

// ================= CONEXIÓN =================
client.on("connect", () => {
    console.log("✅ Conectado al broker MQTT");
    client.subscribe(TOPIC);
});

// ================= RECEPCIÓN =================
client.on("message", (topic, message) => {
    let valor = parseFloat(message.toString());

    if (isNaN(valor)) return;

    console.log("📥 Dato recibido:", valor);

    if (valor > UMBRAL_GAS) {
        console.log("🚨 ALERTA: Posible fuga de gasolina 🚨");
        alert("🚨 FUGA DETECTADA: " + valor);
        beep();
    }
});

// ================= SIMULADOR (CORREGIDO) =================
setInterval(() => {

    if (!simulando) return;

    let valor = Math.floor(Math.random() * 400) + 100;

    console.log("📤 Enviando dato:", valor);

    client.publish(TOPIC, valor.toString());

    // ⚠️ esto evita errores si existe función en HTML
    if (typeof procesar === "function") {
        procesar(valor);
    }

}, 2000);

console.log("🚀 Simulación iniciada...");

// ================= BEEP =================
function beep() {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();

        const osc = ctx.createOscillator();
        osc.type = "square";
        osc.frequency.value = 1200;

        osc.connect(ctx.destination);
        osc.start();

        setTimeout(() => {
            osc.stop();
        }, 200);

    } catch (e) {
        console.log("Audio error:", e);
    }
}

// ================= QR CLOSE =================
function cerrarQR() {
    const modal = document.getElementById("qrModal");
    if (modal) {
        modal.style.display = "none";
    }
}