import pandas as pd
import numpy as np

# =========================================================
# SMART AC DATASET GENERATOR V2
# REALISTIC TIME-SERIES FOR LSTM
# =========================================================

np.random.seed(42)

JUMLAH_BARIS = 3000

# =========================================================
# LIST PENAMPUNG DATA
# =========================================================

suhu_ruangan = []
jumlah_orang = []
suhu_ac = []
jam_data = []

# =========================================================
# KONDISI AWAL
# =========================================================

current_temp = 27.0
current_people = 0
current_ac = 0

# =========================================================
# GENERATE DATA
# =========================================================

for i in range(JUMLAH_BARIS):

    # =====================================================
    # SIMULASI WAKTU
    # =====================================================

    jam = i % 24
    jam_data.append(jam)

    # =====================================================
    # SIMULASI OCCUPANCY BERDASARKAN JAM
    # =====================================================

    # Malam / dini hari
    if 0 <= jam <= 5:

        target_people = np.random.choice(
            [0, 0, 0, 1],
            p=[0.50, 0.25, 0.15, 0.10]
        )

    # Pagi
    elif 6 <= jam <= 9:

        target_people = np.random.randint(1, 4)

    # Jam kerja / siang
    elif 10 <= jam <= 16:

        target_people = np.random.randint(2, 7)

    # Sore
    elif 17 <= jam <= 20:

        target_people = np.random.randint(1, 5)

    # Malam
    else:

        target_people = np.random.choice(
            [0, 1, 2],
            p=[0.60, 0.30, 0.10]
        )

    # =====================================================
    # PERUBAHAN ORANG BERTAHAP
    # =====================================================

    if target_people > current_people:
        current_people += 1

    elif target_people < current_people:
        current_people -= 1

    current_people = np.clip(current_people, 0, 6)

    # =====================================================
    # LOGIKA SMART AC
    # =====================================================

    if current_people == 0:

        current_ac = 0

    else:

        # SUHU DINGIN
        if current_temp <= 25.5:

            if current_people <= 2:
                current_ac = 26
            else:
                current_ac = 24

        # SUHU NORMAL
        elif 25.5 < current_temp <= 28.0:

            if current_people <= 2:
                current_ac = 24
            else:
                current_ac = 22

        # SUHU PANAS
        else:

            current_ac = 22

    # =====================================================
    # SIMULASI PENGARUH AC KE SUHU
    # =====================================================

    # Suhu lingkungan luar
    suhu_luar = np.random.uniform(29, 34)

    # Pengaruh orang terhadap panas
    heat_people = current_people * 0.08

    # Pendinginan AC
    cooling_effect = 0

    if current_ac == 22:
        cooling_effect = -0.30

    elif current_ac == 24:
        cooling_effect = -0.20

    elif current_ac == 26:
        cooling_effect = -0.10

    elif current_ac == 0:
        cooling_effect = 0.15

    # Pengaruh lingkungan
    environmental_effect = (suhu_luar - current_temp) * 0.02

    # Noise/random kecil
    noise = np.random.normal(0, 0.05)

    # =====================================================
    # HITUNG SUHU BARU
    # =====================================================

    current_temp = (
        current_temp
        + heat_people
        + cooling_effect
        + environmental_effect
        + noise
    )

    # Batasi suhu ruangan realistis indoor
    current_temp = np.clip(current_temp, 23.0, 32.0)

    # =====================================================
    # SIMPAN DATA
    # =====================================================

    suhu_ruangan.append(round(current_temp, 1))
    jumlah_orang.append(current_people)
    suhu_ac.append(current_ac)

# =========================================================
# BUAT DATAFRAME
# =========================================================

dataset_ac = pd.DataFrame({
    'jam': jam_data,
    'suhu_ruangan': suhu_ruangan,
    'jumlah_orang': jumlah_orang,
    'suhu_ac': suhu_ac
})

# =========================================================
# SIMPAN CSV
# =========================================================

nama_file = "dataset_smart_ac_realistic.csv"

dataset_ac.to_csv(nama_file, index=False)

# =========================================================
# INFO DATASET
# =========================================================

print(f"\nDataset berhasil dibuat: {nama_file}")
print(f"Jumlah data: {JUMLAH_BARIS}")

print("\nContoh data:")
print(dataset_ac.head(20))

print("\nDistribusi Label:")
print(dataset_ac['suhu_ac'].value_counts())

print("\nStatistik Dataset:")
print(dataset_ac.describe())