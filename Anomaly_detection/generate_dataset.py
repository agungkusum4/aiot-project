import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# =====================================================
# JUMLAH DATA
# =====================================================

JUMLAH_DATA = 3000

# =====================================================
# LIST PENYIMPANAN DATA
# =====================================================

dataset = []

# =====================================================
# WAKTU AWAL
# =====================================================

start_time = datetime(2026, 5, 1, 0, 0, 0)

# =====================================================
# GENERATE DATA
# =====================================================

for i in range(JUMLAH_DATA):

    # ================================================
    # TIMESTAMP
    # ================================================

    timestamp = start_time + timedelta(seconds=i * 10)

    jam = timestamp.hour

    # ================================================
    # JUMLAH ORANG
    # ================================================

    if 7 <= jam <= 17:

        jumlah_orang = random.randint(1, 10)

    else:

        jumlah_orang = random.randint(0, 3)

    # ================================================
    # SUHU RUANGAN
    # ================================================

    suhu_ruangan = round(
        random.uniform(24, 32),
        1
    )

    # ================================================
    # KEPUTUSAN SUHU AC
    # ================================================

    if jumlah_orang == 0:

        suhu_ac = "OFF"

    elif suhu_ruangan >= 30:

        suhu_ac = 22

    elif suhu_ruangan >= 27:

        suhu_ac = 24

    else:

        suhu_ac = 26

    # ================================================
    # POWER NORMAL
    # ================================================

    if suhu_ac == "OFF":

        power = random.uniform(5, 20)

    elif suhu_ac == 22:

        power = random.uniform(700, 950)

    elif suhu_ac == 24:

        power = random.uniform(500, 700)

    else:

        power = random.uniform(300, 500)

    # ================================================
    # VOLTAGE & CURRENT
    # ================================================

    voltage = round(
        random.uniform(215, 225),
        1
    )

    current = round(
        power / voltage,
        2
    )

    # ================================================
    # ENERGY
    # simulasi akumulasi energi
    # ================================================

    energy = round(
        (power / 1000) * (10 / 3600),
        4
    )

    # ================================================
    # STATUS NORMAL
    # ================================================

    status = "NORMAL"

    # ================================================
    # SISIPKAN ANOMALI
    # 5% data anomaly
    # ================================================

    if random.random() < 0.05:

        status = "ANOMALI"

        anomaly_type = random.choice([
            "LONJAKAN_DAYA",
            "DAYA_TINGGI_MALAM",
            "DAYA_TIDAK_WAJAR",
            "VOLTAGE_DROP"
        ])

        # ============================================
        # LONJAKAN DAYA
        # ============================================

        if anomaly_type == "LONJAKAN_DAYA":

            power = random.uniform(1200, 2000)
            current = round(power / voltage, 2)

        # ============================================
        # DAYA TINGGI MALAM
        # ============================================

        elif anomaly_type == "DAYA_TINGGI_MALAM":

            if jam >= 0 and jam <= 5:

                power = random.uniform(1000, 1800)
                current = round(power / voltage, 2)

        # ============================================
        # DAYA TIDAK WAJAR
        # ============================================

        elif anomaly_type == "DAYA_TIDAK_WAJAR":

            jumlah_orang = 0
            power = random.uniform(800, 1500)
            current = round(power / voltage, 2)

        # ============================================
        # VOLTAGE DROP
        # ============================================

        elif anomaly_type == "VOLTAGE_DROP":

            voltage = random.uniform(150, 180)
            current = round(power / voltage, 2)

    # ================================================
    # SIMPAN DATA
    # ================================================

    dataset.append([
        timestamp,
        jam,
        voltage,
        current,
        round(power, 2),
        energy,
        suhu_ruangan,
        jumlah_orang,
        suhu_ac,
        status
    ])

# =====================================================
# BUAT DATAFRAME
# =====================================================

columns = [
    "timestamp",
    "jam",
    "voltage",
    "current",
    "power",
    "energy",
    "suhu_ruangan",
    "jumlah_orang",
    "suhu_ac",
    "status"
]

df = pd.DataFrame(dataset, columns=columns)

# =====================================================
# SIMPAN CSV
# =====================================================

df.to_csv(
    "dataset_energy_anomaly.csv",
    index=False
)

# =====================================================
# INFO
# =====================================================

print("\nDataset berhasil dibuat!")
print(df.head())

print("\nJumlah Data:")
print(len(df))

print("\nJumlah Status:")
print(df["status"].value_counts())