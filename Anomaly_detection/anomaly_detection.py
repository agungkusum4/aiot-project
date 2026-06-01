import time
import random
import joblib
import pandas as pd

# =====================================================
# LOAD MODEL AI
# =====================================================

model = joblib.load(
    "energy_anomaly_model.pkl"
)

print("Model AI berhasil dimuat!")

# =====================================================
# LOOP TESTING
# =====================================================

print("\n===================================")
print("AI ENERGY ANOMALY DETECTION")
print("===================================\n")

while True:

    try:

        # =================================================
        # JAM
        # =================================================

        from datetime import datetime

        jam = datetime.now().hour

        # =================================================
        # DATA NORMAL
        # =================================================

        suhu_ruangan = round(
            random.uniform(24, 30),
            1
        )

        jumlah_orang = random.randint(1, 6)

        voltage = round(
            random.uniform(215, 225),
            1
        )

        current = round(
            random.uniform(1.5, 3.5),
            2
        )

        power = round(
            voltage * current,
            2
        )

        energy = round(
            power / 3600000,
            6
        )

        status_skenario = "NORMAL"

        # =================================================
        # RANDOM ANOMALY
        # =================================================

        peluang = random.random()

        if peluang < 0.3:

            jenis_anomali = random.choice([
                "lonjakan_daya",
                "ac_nyala_tanpa_orang",
                "daya_turun"
            ])

            # =============================================
            # LONJAKAN DAYA
            # =============================================

            if jenis_anomali == "lonjakan_daya":

                current = round(
                    random.uniform(7, 12),
                    2
                )

                power = round(
                    voltage * current,
                    2
                )

                status_skenario = "ANOMALI - LONJAKAN DAYA"

            # =============================================
            # AC NYALA TANPA ORANG
            # =============================================

            elif jenis_anomali == "ac_nyala_tanpa_orang":

                jumlah_orang = 0

                current = round(
                    random.uniform(3, 4),
                    2
                )

                power = round(
                    voltage * current,
                    2
                )

                status_skenario = "ANOMALI - AC NYALA TANPA ORANG"

            # =============================================
            # DAYA TURUN
            # =============================================

            elif jenis_anomali == "daya_turun":

                current = round(
                    random.uniform(0, 0.2),
                    2
                )

                power = round(
                    voltage * current,
                    2
                )

                status_skenario = "ANOMALI - DAYA TURUN"

        # =================================================
        # INPUT DATA
        # =================================================

        input_data = pd.DataFrame([{
            "jam": jam,
            "voltage": voltage,
            "current": current,
            "power": power,
            "energy": energy,
            "suhu_ruangan": suhu_ruangan,
            "jumlah_orang": jumlah_orang
        }])

        # =================================================
        # PREDIKSI AI
        # =================================================

        prediction = model.predict(
            input_data
        )[0]

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
        # HASIL AI
        # =================================================

        if prediction == 0:

            print("\nStatus AI        : NORMAL")

        else:

            print("\nStatus AI        : ANOMALI")

            print("\n[WARNING]")
            print("Penggunaan energi abnormal terdeteksi!")

        time.sleep(5)

    except KeyboardInterrupt:

        print("\nProgram dihentikan")
        break

    except Exception as e:

        print(f"\nERROR: {e}")

        time.sleep(5)