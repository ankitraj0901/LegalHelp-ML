import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from xgboost import XGBRegressor
import os


df = pd.read_csv("dataset/tax_dataset.csv")


# Feature Engineering

df["gross_income"] = df["salary"] + df["other_income"] + df["lta"]

df["total_deductions"] = (
    df["invest_80C"]
    + df["invest_80D"]
    + df["home_loan_interest"]
    + df["standard_deduction"]
)

df["net_income_after_hra"] = df["gross_income"] - df["hra"]


# Features and Target

X = df[
    [
        "salary",
        "hra",
        "lta",
        "invest_80C",
        "invest_80D",
        "home_loan_interest",
        "rent_paid",
        "other_income",
        "gross_income",
        "total_deductions",
        "net_income_after_hra",
    ]
]

y = df["taxable_income"]


# Train-Test Split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)


# Model

model = XGBRegressor(
    n_estimators=1200,
    learning_rate=0.02,
    max_depth=10,
    subsample=0.9,
    colsample_bytree=0.9,
    reg_lambda=1.0,
    reg_alpha=0.5,
    objective="reg:squarederror",
    tree_method="hist",
    random_state=42
)


# Train the model

model.fit(X_train, y_train)


# Evaluating the model

pred = model.predict(X_test)
print("MAE:", mean_absolute_error(y_test, pred))
print("R²:", r2_score(y_test, pred))


# Save Model

os.makedirs("model", exist_ok=True)
model.save_model("model/xgb_tax_model.json")

print(" Model saved at model/xgb_tax_model.json")
