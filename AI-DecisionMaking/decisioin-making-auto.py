# decision-making-auto.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import joblib
import time
from tensorflow.keras.models import load_model
import firebase_admin
from firebase_admin import credentials, db

# Import function bulb
from Smart_Bulb.send_data_to_bulb import send_to_bulb

# =====================================================
# INITIALIZE FIREBASE (Akses langsung ke Cloud)
# =====================================================
PATH_TO_JSON = "../serviceAccountKey.json"
DATABASE_URL = "https://aiot-project-5d7f9-default-rtdb.asia-southeast1.firebasedatabase.app/"

print("Menginisialisasi Firebase di Decision Making...")
try:
    cred = credentials.Certificate(PATH_TO_JSON)
    firebase_admin.initialize_app(cred, {
        'databaseURL': DATABASE_URL
    })
    print("Firebase Berhasil Terhubung!")
except Exception as e:
    print(f"Gagal koneksi Firebase: {e}")
    exit()

# Menuju ke node '/sensor' tempat kedua data berkumpul
firebase_ref = db.reference('/sensor')

# =====================================================
# LOAD MODEL AI & SCALER
# =====================================================
model = load_model("ai_model_lstm_smart_ac.h5")
print("Model AI berhasil dimuat!")

scaler = joblib.load("scaler_ac.save")
print("Scaler berhasil dimuat!")

# =====================================================
# BUFFER LSTM
# =====================================================
SEQUENCE = 10
data_buffer = []

# =====================================================
# PREDICT FUNCTION (Mengikuti Logika Versi Manual)
# =====================================================
def predict_ac(latest_suhu, jumlah_orang):
    global data_buffer
    from datetime import datetime

    # =====================================
    # AC OFF JIKA TIDAK ADA ORANG
    # =====================================
    if jumlah_orang == 0:
        return "OFF"

    jam = datetime.now().hour

    input_data = np.array([
        jam,
        latest_suhu,
        jumlah_orang
    ]).reshape(1, -1)
    input_scaled = scaler.transform(input_data)
    data_buffer.append(input_scaled[0])

    if len(data_buffer) > SEQUENCE:
        data_buffer.pop(0)

    if len(data_buffer) < SEQUENCE:
        print(f"Menunggu data sequence... ({len(data_buffer)}/{SEQUENCE})")
        return None

    X_input = np.array(data_buffer)
    X_input = np.expand_dims(X_input, axis=0)
    
    prediction = model.predict(X_input, verbose=0)
    
    # .item() mengubah tipe data np.int64 menjadi int standar Python
    predicted_class = np.argmax(prediction).item()

    # Balikkan ke suhu asli sesuai logika manual
    keputusan_ac = predicted_class + 16

    return keputusan_ac

# =====================================================
# LOOP REALTIME SYSTEM
# =====================================================
print("\n===================================")
print("SMART AC AI DECISION MAKING RUNNING (AUTO)")
print("===================================\n")

last_keputusan = None

while True:
    try:
        # Tarik seluruh snapshot data dari node '/sensor'
        sensor_snapshot = firebase_ref.get()

        if sensor_snapshot is None:
            print("[Sistem] Node database kosong/belum siap.")
            time.sleep(5)
            continue

        # Ekstrak masing-masing data dari snapshot database
        suhu_realtime = sensor_snapshot.get('suhu')
        orang_realtime = sensor_snapshot.get('jumlah_orang')

        # Validasi kelengkapan data sebelum masuk model
        if suhu_realtime is None or orang_realtime is None:
            print(f"[Sistem] Menunggu data lengkap... (Suhu: {suhu_realtime}, Orang: {orang_realtime})")
            time.sleep(5)
            continue

        # =============================================
        # PREDIKSI AI
        # =============================================
        hasil = predict_ac(float(suhu_realtime), int(orang_realtime))

        # =============================================
        # TAMPILKAN DATA & KONTROL SMART BULB
        # =============================================
        print("\n===================================")
        print(f"Suhu Ruangan : {suhu_realtime}°C")
        print(f"Jumlah Orang : {orang_realtime}")

        if hasil is not None:
            print(f"Keputusan AI : {hasil}")

            # =====================================
            # KIRIM COMMAND HANYA JIKA BERUBAH
            # =====================================
            if hasil != last_keputusan:
                print(f"\n[INFO] Mengirim command ke bulb : {hasil}")
                send_to_bulb(hasil)
                last_keputusan = hasil
            else:
                print("[INFO] Keputusan sama, command tidak dikirim")
        else:
            print("AI belum bisa prediksi (Menumpuk data sequence...)")

        # Delay interval pembacaan data otomatis (10 detik)
        time.sleep(10)

    except KeyboardInterrupt:
        print("\nProgram dihentikan")
        break
    except Exception as e:
        print(f"\nERROR: {e}")
        time.sleep(10)