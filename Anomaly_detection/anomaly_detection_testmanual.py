from datetime import datetime
import random
import time
import firebase_admin
from firebase_admin import credentials, db
import joblib
import pandas as pd

cred = credentials.Certificate("../serviceAccountKey.json")

firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": "https://aiot-project-5d7f9-default-rtdb.asia-southeast1.firebasedatabase.app/"
    },
)

# Referensi ke node 'security_logs' di Firebase
logs_ref = db.reference("security_logs")

print("Koneksi Firebase berhasil diinisialisasi!")

# =====================================================
# LOAD MODEL AI
# =====================================================

model = joblib.load("energy_anomaly_model.pkl")
print("Model AI berhasil dimuat!")

# =====================================================
# LOOP TESTING
# =====================================================

print("\n===================================")
print("AI ENERGY ANOMALY DETECTION")
print("===================================\n")

while True:
    try:
        jam = datetime.now().hour
        waktu_lengkap = datetime.now().strftime("%H:%M")

        # =================================================
        # DATA NORMAL
        # =================================================

        suhu_ruangan = round(random.uniform(24, 30), 1)
        jumlah_orang = random.randint(1, 6)
        voltage = round(random.uniform(215, 225), 1)
        current = round(random.uniform(1.5, 3.5), 2)
        power = round(voltage * current, 2)
        energy = round(power / 3600000, 6)
        status_skenario = "NORMAL"

        # =================================================
        # RANDOM ANOMALY (Hanya 2 Skenario Utama)
        # =================================================

        peluang = random.random()

        if peluang < 0.3:
            # Diubah hanya memilih antara lonjakan daya atau ac tanpa orang
            jenis_anomali = random.choice(["lonjakan_daya", "ac_nyala_tanpa_orang"])

            # =============================================
            # LONJAKAN DAYA
            # =============================================

            if jenis_anomali == "lonjakan_daya":
                current = round(random.uniform(7, 12), 2)
                power = round(voltage * current, 2)
                status_skenario = "ANOMALI - Terjadi Lonjakan Daya!"

            # =============================================
            # AC NYALA TANPA ORANG
            # =============================================

            elif jenis_anomali == "ac_nyala_tanpa_orang":
                jumlah_orang = 0
                current = round(random.uniform(3, 4), 2)
                power = round(voltage * current, 2)
                status_skenario = "ANOMALI - AC ON saat ruangan kosong!"

        # =================================================
        # INPUT DATA
        # =================================================

        input_data = pd.DataFrame(
            [
                {
                    "jam": jam,
                    "voltage": voltage,
                    "current": current,
                    "power": power,
                    "energy": energy,
                    "suhu_ruangan": suhu_ruangan,
                    "jumlah_orang": jumlah_orang,
                }
            ]
        )

        # =================================================
        # PREDIKSI AI
        # =================================================

        prediction = model.predict(input_data)[0]

        # =================================================
        # OUTPUT
        # =================================================

        print("\n===================================")

        print(f"Jam              : {jam}")
        print(f"Suhu             : {suhu_ruangan}°C")
        print(f"Jumlah Orang     : {jumlah_orang}")

        print(f"Voltage          : {voltage} V")
        print(f"Current          : {current} A")
        print(f"Power            : {power} Watt")
        print(f"Energy           : {energy} kWh")

        print(f"\nSkenario         : {status_skenario}")

        # =================================================
        # HASIL AI & FIREBASE UPDATE
        # =================================================

        if prediction == 0:
            print("\nStatus AI        : NORMAL")

        else:
            print("\nStatus AI        : ANOMALI")
            print("\n[WARNING] Penggunaan energi abnormal terdeteksi!")

            # Logika penentuan pesan Firebase disederhanakan menjadi 2 opsi saja
            if status_skenario == "ANOMALI - AC ON saat ruangan kosong!":
                tipe_log = "AC Alert"
                pesan_log = "AC terdeteksi menyala di ruangan kosong."
            else:
                # Default fallback jika AI mendeteksi lonjakan daya ekstrem
                tipe_log = "Anomali Daya"
                pesan_log = "Terdeteksi Lonjakan Daya!"

            # Struktur data yang dikirim ke Firebase
            log_data = {
                "jam": waktu_lengkap,
                "tipe": tipe_log,
                "pesan": pesan_log,
            }

            # Format: TAHUN-BULAN-HARI_JAM-MENIT-DETIK
            id_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            # Kirim ke Firebase Realtime Database
            logs_ref.child(id_timestamp).set(log_data)
            print(f"Log berhasil dikirim ke firebase!")

        time.sleep(30)

    except KeyboardInterrupt:
        print("\nProgram dihentikan")
        break

    except Exception as e:
        print(f"\nERROR: {e}")
        time.sleep(5)