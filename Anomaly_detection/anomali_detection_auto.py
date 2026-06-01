from datetime import datetime
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

# Referensi node database sesuai struktur Anda
sensor_ref = db.reference("sensor")
logs_ref = db.reference("security_logs")

print("Koneksi Firebase berhasil diinisialisasi!")

# =====================================================
# LOAD MODEL AI
# =====================================================
model = joblib.load("energy_anomaly_model.pkl")
print("Model AI berhasil dimuat!")
print("\n[INFO] Layanan Aktif. Menunggu update data dari hardware...")


# =====================================================
# FUNGSI DETEKSI AI (DIJALANKAN OTOMATIS)
# =====================================================
def proses_deteksi_anomali(event):
    """Fungsi ini otomatis tereksekusi setiap kali ada perubahan data di path 'sensor'."""
    # Mencegah error jika data kosong saat pertama kali script dijalankan
    if event.data is None:
        return

    try:
        # Ambil snapshot data terbaru dari node 'sensor'
        data_sensor = sensor_ref.get()

        # Ekstraksi data utama
        suhu_ruangan = float(data_sensor.get("suhu", 0))
        jumlah_orang = int(data_sensor.get("jumlah_orang", 0))

        # Ekstraksi data dari sub-node 'pzem'
        data_pzem = data_sensor.get("pzem", {})
        voltage = float(data_pzem.get("voltage", 0))
        current = float(data_pzem.get("current", 0))
        power = float(data_pzem.get("power", 0))
        energy = float(data_pzem.get("energy", 0))

        # Parsing waktu terkini
        jam = datetime.now().hour
        waktu_lengkap = datetime.now().strftime("%H:%M")

        # Abaikan deteksi jika hardware sedang offline / mengirim data 0 mutlak
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

        # AI Melakukan Prediksi
        prediction = model.predict(input_data)[0]

        # =================================================
        # OUTPUT MONITORING DI TERMINAL
        # =================================================
        print("\n===================================")
        print(f"Data Diterima    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Suhu / Orang     : {suhu_ruangan}°C / {jumlah_orang} Orang")
        print(f"Daya Listrik     : {power} Watt ({current} A)")

        if prediction == 0:
            print("Status AI        : NORMAL")
        else:
            print("Status AI        : ANOMALI ⚠️")

            # Penentuan label log berdasarkan kondisi riil data sensor lapangan
            if jumlah_orang == 0 and power > 300:
                tipe_log = "AC Alert"
                pesan_log = "AC terdeteksi menyala di ruangan kosong."
                warna_log = "merah"
            else:
                # Default jika konsumsi daya melonjak melebihi batas wajar umum
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
# Perintah ini yang membuat Python selalu stand-by mengawasi Firebase
sensor_ref.listen(proses_deteksi_anomali)

# Menjaga thread utama script tetap hidup di background terminal
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nLayanan deteksi AI dihentikan secara aman.")