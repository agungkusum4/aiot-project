import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials, db
import time
import json  # Ditambahkan untuk membaca format JSON dari ESP32

# ================= VARIABLE LOKAL =================
latest_suhu = 0.0
latest_humidity = 0.0  # Variabel baru untuk menyimpan kelembapan terkini

# ================= 1. KONFIGURASI FIREBASE =================
PATH_TO_JSON = "../serviceAccountKey.json"
DATABASE_URL = "https://aiot-project-5d7f9-default-rtdb.asia-southeast1.firebasedatabase.app/"

print("Menginisialisasi Firebase...")
try:
    cred = credentials.Certificate(PATH_TO_JSON)
    firebase_admin.initialize_app(cred, {
        'databaseURL': DATABASE_URL
    })
    print("Firebase Berhasil Terhubung!")
except Exception as e:
    print(f"Gagal koneksi Firebase: {e}")
    exit()

firebase_ref = db.reference('/sensor')

# ================= 2. KONFIGURASI MQTT =================
# Pastikan MQTT_BROKER ini sama dengan yang diisi di ESP32 (Lokal IP atau HiveMQ)
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC_SENSOR = "ruangan/sensor/data"  # Disamakan dengan topik baru di ESP32

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Terhubung ke MQTT Broker!")
        client.subscribe(MQTT_TOPIC_SENSOR)
        print(f"Mendengarkan topik: {MQTT_TOPIC_SENSOR}")
    else:
        print(f"Gagal konek ke MQTT, return code: {rc}")

def on_message(client, userdata, msg):
    global latest_suhu, latest_humidity
    try:
        # Dekode payload JSON dari ESP32
        payload_string = msg.payload.decode("utf-8")
        data_masuk = json.loads(payload_string)
        
        # Ekstrak data berdasarkan key JSON
        latest_suhu = float(data_masuk['suhu'])
        latest_humidity = float(data_masuk['kelembapan'])
        
        print(f"\n[MQTT] Data Masuk -> Suhu: {latest_suhu} °C | Kelembapan: {latest_humidity} %")
        
    except Exception as e:
        print(f"Error membaca atau memparsing pesan MQTT: {e}")

# Menambahkan argumen CallbackAPIVersion.VERSION1 agar paho-mqtt versi baru tidak komplain
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

print("Menghubungkan ke MQTT Broker...")
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
except Exception as e:
    print(f"Gagal terhubung ke Broker: {e}")
    exit()

client.loop_start()

# ================= 3. LOOP UTAMA (KIRIM KE FIREBASE) =================
print("Sistem Testing Siap. Menunggu data dari ESP32...")
try:
    while True:
        # Cek apakah data sudah terisi (tidak kosong)
        if latest_suhu != 0.0 and latest_humidity != 0.0:
            print(f"[Loop Utama] Data siap dikirim: Suhu={latest_suhu}°C, Kelembapan={latest_humidity}%")
            print("[Firebase] Mengirim ke Realtime Database...")
            
            # Kirim kedua data sekaligus ke Firebase Realtime Database
            firebase_ref.update({
                'suhu': latest_suhu,
                'kelembapan': latest_humidity
            })
            print("[Firebase] Update Berhasil!\n")
        else:
            print("[Sistem] Menunggu kiriman data lengkap pertama dari ESP32...")
            
        time.sleep(10)

except KeyboardInterrupt:
    print("\nSistem dihentikan.")
    client.loop_stop()