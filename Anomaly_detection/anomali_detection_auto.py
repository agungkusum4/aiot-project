from datetime import datetime
import time
import firebase_admin
from firebase_admin import credentials, db
import joblib
import pandas as pd

# =====================================================
# INITIALIZE FIREBASE
# =====================================================
cred = credentials.Certificate("../serviceAccountKey.json")

firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": "https://aiot-project-5d7f9-default-rtdb.asia-southeast1.firebasedatabase.app/"
    },
)

# Referensi node database flat path /sensor
sensor_ref = db.reference("sensor")
logs_ref = db.reference("security_logs")

print("Koneksi Firebase berhasil diinisialisasi!")

# =====================================================
# LOAD MODEL AI
# =====================================================
model = joblib.load("energy_anomaly_model.pkl")
print("Model AI berhasil dimuat!")
print("\n[INFO] Layanan Aktif. Menunggu update data riil dari hardware...")


# =====================================================
# FUNGSI DETEKSI AI (DIJALANKAN OTOMATIS)
# =====================================================
def proses_deteksi_anomali(event):
    """Fungsi ini otomatis tereksekusi setiap kali ada perubahan data di path 'sensor'."""
    if event.data is None:
        return

    try:
        # Ambil snapshot data terbaru dari node 'sensor'
        data_sensor = sensor_ref.get()

        # 1. Ekstraksi Data Lingkungan & Kamera
        suhu_ruangan = float(data_sensor.get("suhu", 0))
        jumlah_orang = int(data_sensor.get("jumlah_orang", 0))

        # 2. PERBAIKAN UTAMA: Ambil langsung dari induk /sensor menggunakan key bahasa Indonesia
        voltage = float(data_sensor.get("tegangan", 0))
        current = float(data_sensor.get("arus", 0))
        power = float(data_sensor.get("daya", 0))
        energy = float(data_sensor.get("energi", 0))

        # Parsing waktu terkini untuk input Model AI
        jam = datetime.now().hour
        waktu_lengkap = datetime.now().strftime("%H:%M")

        # Abaikan deteksi JIKA sensor benar-benar mati total (0V dan 0A)
        # Tapi jika tegangan PLN normal (~220V), abaikan kondisi ini agar tetep jalan
        if voltage == 0 and current == 0:
            return

        # =================================================
        # INPUT DATA UNTUK MODEL AI
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

        # AI Melakukan Prediksi Berdasarkan Data Riil Lapangan
        prediction = model.predict(input_data)[0]

        # =================================================
        # OUTPUT MONITORING DI TERMINAL VS CODE
        # =================================================
        print("\n===================================")
        print(f"data diterima : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"suhu          : {suhu_ruangan} °C")
        print(f"orang         : {jumlah_orang} Orang")
        print(f"Daya          : {power} Watt")
        print(f"Listrik       : {current} A")
        print(f"Tegangan      : {voltage} V")
        
        if prediction == 0:
            print("Status sistem : NORMAL")
        else:
            print("Status sistem : ANOMALI ⚠️")

            # Penentuan label log berdasarkan kondisi riil data sensor lapangan
            if jumlah_orang == 0 and power > 300:
                tipe_log = "AC Alert"
                pesan_log = "AC terdeteksi menyala di ruangan kosong."
                warna_log = "merah"
            else:
                tipe_log = "Anomali Daya"
                pesan_log = "Terdeteksi Lonjakan Daya!"
                warna_log = "kuning"

            # Format data untuk dikirim ke Firebase
            log_data = {
                "jam": waktu_lengkap,
                "tipe": tipe_log,
                "pesan": pesan_log,
                "warna": warna_log,
            }

            # Nama path berupa waktu mendeteksi (Format: TAHUN-BULAN-HARI_JAM-MENIT-DETIK)
            id_timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

            # Push ke Node security_logs
            logs_ref.child(id_timestamp).set(log_data)
            print(f"[FIREBASE] Log [{tipe_log}] berhasil diperbarui!")

    except Exception as e:
        print(f"\nGagal memproses data: {e}")


# =====================================================
# JALANKAN LISTENER STREAMING
# =====================================================
sensor_ref.listen(proses_deteksi_anomali)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nLayanan deteksi AI dihentikan secara aman.")