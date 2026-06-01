import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

import numpy as np
import joblib
import time
from tensorflow.keras.models import load_model

# Import function bulb
from Smart_Bulb.send_data_to_bulb import send_to_bulb

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
# BUFFER LSTM
# =====================================================

SEQUENCE = 10

data_buffer = []

# =====================================================
# MAPPING OUTPUT AI
# =====================================================

# =====================================================
# PREDICT FUNCTION
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
        print(f"Menunggu sequence ({len(data_buffer)}/{SEQUENCE})")
        return None

    X_input = np.array(data_buffer)
    X_input = np.expand_dims(X_input, axis=0)
    prediction = model.predict(X_input, verbose=0)
    predicted_class = np.argmax(prediction)

    # Balikkan ke suhu asli
    keputusan_ac = predicted_class + 16

    return keputusan_ac

# =====================================================
# TEST MANUAL
# =====================================================

print("\n===================================")
print("TEST AI SMART AC MANUAL")
print("===================================\n")

last_keputusan = None

while True:

    try:

        # =========================================
        # INPUT MANUAL
        # =========================================

        suhu_manual = float(input("Masukkan suhu ruangan: "))
        orang_manual = int(input("Masukkan jumlah orang: "))

        # =========================================
        # PREDIKSI AI
        # =========================================

        hasil = predict_ac(
            suhu_manual,
            orang_manual
        )

        print("\n===================================")
        print(f"Suhu : {suhu_manual}°C")
        print(f"Jumlah Orang : {orang_manual}")

        # =========================================
        # HASIL AI
        # =========================================

        if hasil is not None:

            print(f"Keputusan AI : {hasil}")

            # =====================================
            # KIRIM KE BULB
            # =====================================

            if hasil != last_keputusan:

                print(f"\n[INFO] Mengirim command ke bulb...")

                send_to_bulb(hasil)

                last_keputusan = hasil

            else:

                print("[INFO] Keputusan sama")

        else:

            print("AI belum bisa prediksi")

        print("\n")

    except KeyboardInterrupt:

        print("\nProgram dihentikan")
        break

    except Exception as e:

        print(f"\nERROR: {e}")