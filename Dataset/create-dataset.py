import pandas as pd
import numpy as np

np.random.seed(42)

# =====================================================
# CONFIG
# =====================================================

JUMLAH_HARI = 30

data = []

# =====================================================
# GENERATE DATA
# =====================================================

for hari in range(JUMLAH_HARI):

    suhu = np.random.uniform(28.0, 30.0)

    for jam in range(24):

        # =============================================
        # POLA JUMLAH ORANG BERDASARKAN JAM
        # =============================================

        if 0 <= jam <= 6:
            jumlah_orang = np.random.randint(0, 1)

        elif 7 <= jam <= 9:
            jumlah_orang = np.random.randint(1, 4)

        elif 10 <= jam <= 16:
            jumlah_orang = np.random.randint(3, 9)

        elif 17 <= jam <= 20:
            jumlah_orang = np.random.randint(1, 5)

        else:
            jumlah_orang = np.random.randint(0, 2)

        # =============================================
        # SIMULASI SUHU RUANGAN
        # =============================================

        kenaikan_orang = jumlah_orang * 0.25

        perubahan_acak = np.random.uniform(-0.4, 0.4)

        suhu = suhu + kenaikan_orang * 0.1 + perubahan_acak

        suhu = np.clip(suhu, 24, 33)

        suhu = round(suhu, 1)

        # =============================================
        # LOGIKA SMART AC
        # =============================================

        if jumlah_orang == 0:

            suhu_ac = 30

        else:

            # SUHU 24-25
            if suhu <= 25:
                suhu_ac = 28

            # SUHU 25-26
            elif suhu <= 26:
                suhu_ac = 27

            # SUHU 26-27
            elif suhu <= 27:
                suhu_ac = 26

            # SUHU 27-28
            elif suhu <= 28:
                suhu_ac = 25

            # SUHU 28-29
            elif suhu <= 29:
                suhu_ac = 24

            # SUHU 29-30
            elif suhu <= 30:
                suhu_ac = 23

            # SUHU 30-31
            elif suhu <= 31:
                suhu_ac = 22

            # SUHU >31
            else:
                suhu_ac = 20

            # =========================================
            # PENYESUAIAN BERDASARKAN JUMLAH ORANG
            # =========================================

            if jumlah_orang >= 6:
                suhu_ac -= 2

            elif jumlah_orang >= 4:
                suhu_ac -= 1

            suhu_ac = int(np.clip(suhu_ac, 16, 30))

        # =============================================
        # SIMPAN DATA
        # =============================================

        data.append([
            jam,
            suhu,
            jumlah_orang,
            suhu_ac
        ])

# =====================================================
# DATAFRAME
# =====================================================

dataset = pd.DataFrame(
    data,
    columns=[
        "jam",
        "suhu_ruangan",
        "jumlah_orang",
        "suhu_ac"
    ]
)

# =====================================================
# SAVE CSV
# =====================================================

dataset.to_csv(
    "dataset_smart_ac_realistic.csv",
    index=False
)

print(dataset.head(50))

print("\nDataset berhasil dibuat!")
print(dataset["suhu_ac"].value_counts().sort_index())