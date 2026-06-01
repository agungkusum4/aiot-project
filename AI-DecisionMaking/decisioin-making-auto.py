import numpy as np
import joblib
import time
from Smart_Bulb.send_data_to_bulb import send_to_bulb
from tensorflow.keras.models import load_model

# =====================================================
# IMPORT DATA REALTIME
# =====================================================

# Import dari folder
import Suhu.suhu_gateway as suhu_gateway
import People_Counting.main as people_counter

# =====================================================
# LOAD MODEL AI
# =====================================================

model = load_model("ai_model_lstm_smart_ac.h5")

print("Model AI berhasil dimuat!")

# =====================================================
# LOAD SCALER
# =====================================================

scaler = joblib.load("scaler_ac.save")

print("Scaler berhasil dimuat!")

# =====================================================
# BUFFER DATA SEQUENCE UNTUK LSTM
# =====================================================

SEQUENCE = 10

data_buffer = []

# =====================================================
# SIMPAN KEPUTUSAN TERAKHIR
# =====================================================

last_keputusan = None

# =====================================================
# MAPPING HASIL PREDIKSI
# =====================================================

reverse_mapping = {
    0: "OFF",
    1: "22",
    2: "24",
    3: "26"
}

# =====================================================
# FUNGSI PREDIKSI AI
# =====================================================

def predict_ac(latest_suhu, jumlah_orang):

    global data_buffer

    # =================================================
    # AMBIL JAM REALTIME
    # =================================================

    from datetime import datetime

    jam = datetime.now().hour

    # =================================================
    # BENTUK INPUT DATA
    # =================================================

    input_data = np.array([
        jam,
        latest_suhu,
        jumlah_orang
    ]).reshape(1, -1)

    # =================================================
    # NORMALISASI
    # =================================================

    input_scaled = scaler.transform(input_data)

    # =================================================
    # MASUKKAN KE BUFFER
    # =================================================

    data_buffer.append(input_scaled[0])

    # Simpan hanya 10 data terakhir
    if len(data_buffer) > SEQUENCE:
        data_buffer.pop(0)

    # =================================================
    # TUNGGU BUFFER PENUH
    # =================================================

    if len(data_buffer) < SEQUENCE:

        print(f"Menunggu data sequence... ({len(data_buffer)}/{SEQUENCE})")

        return None

    # =================================================
    # BENTUK INPUT LSTM
    # =================================================

    X_input = np.array(data_buffer)

    X_input = np.expand_dims(X_input, axis=0)

    # =================================================
    # PREDIKSI MODEL AI
    # =================================================

    prediction = model.predict(X_input, verbose=0)

    predicted_class = np.argmax(prediction)

    keputusan_ac = reverse_mapping[predicted_class]

    return keputusan_ac

# =====================================================
# LOOP REALTIME SYSTEM
# =====================================================

print("\n===================================")
print("SMART AC AI DECISION MAKING")
print("===================================\n")

while True:

    try:
        if suhu_realtime is None or orang_realtime is None:
            print("Data sensor belum tersedia")
            time.sleep(5)
            continue
        # =============================================
        # AMBIL DATA REALTIME
        # =============================================

        suhu_realtime = suhu_gateway.latest_suhu
        orang_realtime = people_counter.jumlah_orang

        if suhu_realtime is None or orang_realtime is None:
            print("Data sensor belum tersedia")
            time.sleep(5)
            continue

        # =============================================
        # PREDIKSI AI
        # =============================================

        hasil = predict_ac(
            suhu_realtime,
            orang_realtime
        )

        # =============================================
        # TAMPILKAN DATA
        # =============================================

        print("\n===================================")
        print(f"Suhu Ruangan : {suhu_realtime}°C")
        print(f"Jumlah Orang : {orang_realtime}")

        # =============================================
        # HASIL KEPUTUSAN AI
        # =============================================

        if hasil is not None:

            print(f"Keputusan AI : {hasil}")

            # =========================================
            # KIRIM COMMAND HANYA JIKA BERUBAH
            # =========================================

            if hasil != last_keputusan:

                print(f"\n[INFO] Mengirim command AC : {hasil}")
                send_to_bulb(hasil)
                last_keputusan = hasil
            else:
                print("[INFO] Keputusan sama, command tidak dikirim")

        else:
            print("AI belum bisa prediksi")

        # =============================================
        # DELAY 10 DETIK
        # =============================================

        time.sleep(10)

    except KeyboardInterrupt:

        print("\nProgram dihentikan")
        break

    except Exception as e:

        print(f"\nERROR: {e}")

        time.sleep(10)