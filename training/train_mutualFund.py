import pandas as pd
import numpy as np
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score

# ==========================================
# CREATE MODEL DIRECTORY
# ==========================================
os.makedirs("model", exist_ok=True)

# ==========================================
# LOAD DATA
# ==========================================
df = pd.read_csv("dataset/Mutual-Funds2.csv")

# ==========================================
# CLEAN NUMERIC COLUMNS
# ==========================================
numeric_cols = [
    'Return (%)1 yr', 'Alpha', 'Standard Deviation', 'Sharpe',
    'ExpenseRatio (%)', 'AUM(in Rs. cr)', 'NAV ', 'Beta',
    'Large Cap(%)', 'Mid Cap(%)', 'Small Cap(%)',
    'category_average_return_1year'
]

def clean_numeric(val):
    if pd.isna(val) or str(val).strip() == '-':
        return np.nan
    val = str(val).replace('%', '').replace(',', '').strip()
    try:
        return float(val)
    except:
        return np.nan

for col in numeric_cols:
    df[col] = df[col].apply(clean_numeric)

# ==========================================
# NORMALIZE CLASSIFICATION TEXT
# ==========================================
df['classification'] = (
    df['classification']
    .astype(str)
    .str.lower()
    .str.strip()
)

# ==========================================
# DROP ROWS WITH MISSING TARGET
# ==========================================
df = df.dropna(subset=['Return (%)1 yr']).copy()

# ==========================================
# FEATURE SELECTION
# ==========================================
FEATURES = [
    'Alpha',
    'Standard Deviation',
    'Sharpe',
    'ExpenseRatio (%)',
    'AUM(in Rs. cr)',
    'Beta',
    'category_average_return_1year',
    'classification'
]

TARGET = 'Return (%)1 yr'

X = df[FEATURES].copy()
y = df[TARGET]

# ==========================================
# ENCODE CLASSIFICATION
# ==========================================
label_encoder = LabelEncoder()
X['classification'] = label_encoder.fit_transform(X['classification'])

# ==========================================
# HANDLE MISSING VALUES
# ==========================================
X = X.fillna(X.median())

# ==========================================
# TRAIN MODEL
# ==========================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=10,
    random_state=42
)

model.fit(X_train, y_train)

# ==========================================
# EVALUATION
# ==========================================
y_pred = model.predict(X_test)
print("MAE:", mean_absolute_error(y_test, y_pred))
print("R2 :", r2_score(y_test, y_pred))

# ==========================================
# SAVE MODEL & ENCODER
# ==========================================
joblib.dump(model, "model/rf_model.pkl")
joblib.dump(label_encoder, "model/label_encoder.pkl")

print("✅ Model & Encoder saved")
print("Allowed classifications:")
print(list(label_encoder.classes_))
