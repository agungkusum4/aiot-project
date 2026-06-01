import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# =====================================================
# LOAD DATASET
# =====================================================

df = pd.read_csv("dataset_energy_anomaly.csv")

print("\nDataset berhasil dimuat!")

print(df.head())

# =====================================================
# UBAH LABEL
# NORMAL = 0
# ANOMALI = 1
# =====================================================

df["status"] = df["status"].map({
    "NORMAL": 0,
    "ANOMALI": 1
})

# =====================================================
# FEATURE & LABEL
# =====================================================

X = df[
    [
        "jam",
        "voltage",
        "current",
        "power",
        "energy",
        "suhu_ruangan",
        "jumlah_orang"
    ]
]

y = df["status"]

# =====================================================
# SPLIT DATA
# =====================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# =====================================================
# MODEL AI
# =====================================================

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# =====================================================
# TRAINING
# =====================================================

print("\nTraining model AI...")

model.fit(X_train, y_train)

print("Training selesai!")

# =====================================================
# TESTING
# =====================================================

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n===================================")
print("HASIL EVALUASI MODEL")
print("===================================")

print(f"\nAccuracy : {accuracy * 100:.2f}%")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# =====================================================
# SAVE MODEL
# =====================================================

joblib.dump(
    model,
    "energy_anomaly_model.pkl"
)

print("\nModel berhasil disimpan!")