from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import Flask, request, jsonify
import pandas as pd
import xgboost as xgb

# For tax optimization imports
from tax_optimization import generate_tax_optimization
from new_regime_optimizer import optimize_new_regime



app = Flask(__name__)

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)


# Load Model
model = xgb.XGBRegressor()
model.load_model("model/xgb_tax_model.json")

def calculate_tax(taxable_income):
    # 1. Base Tax Calculation (without Cess and Rebate)
    tax = 0
    income_to_tax = max(0, taxable_income) # Ensure income is not negative

    # New Tax Regime Slabs (FY 2025-26 / AY 2026-27)
    # Slab 1: Up to 4,00,000 -> 0%
    if income_to_tax <= 400000:
        tax = 0
        

    # Slab 2: 4,00,001 to 8,00,000 -> 5%
    elif income_to_tax <= 800000:
        # Taxable amount in this slab: income_to_tax - 400000
        tax = (income_to_tax - 400000) * 0.05
        


    # Slab 3: 8,00,001 to 12,00,000 -> 10%
    elif income_to_tax <= 1200000:
        # Tax on 4L to 8L: 4,00,000 * 5%=20,000
        tax = 20000
        # Taxable amount in this slab: income_to_tax-800000
        tax += (income_to_tax - 800000) * 0.10
        


    # Slab 4: 12,00,001 to 16,00,000 -> 15%
    elif income_to_tax <= 1600000:
        # Tax on 4L to 12L: 20,000 + 40,000 = 60,000
        tax = 60000
        # Taxable amount in this slab: income_to_tax - 1200000
        tax += (income_to_tax - 1200000) * 0.15
        



    # Slab 5: 16,00,001 to 20,00,000 -> 20%
    elif income_to_tax <= 2000000:
        # Tax on 4L to 16L: 60,000 + 60,000 = 1,20,000
        tax = 120000
        # Taxable amount in this slab: income_to_tax - 1600000
        tax += (income_to_tax - 1600000) * 0.20
        

        

    # Slab 6: 20,00,001 to 24,00,000 -> 25%
    elif income_to_tax <= 2400000:
        # Tax on 4L to 20L: 1,20,000 + 80,000 = 2,00,000
        tax = 200000
        # Taxable amount in this slab: income_to_tax - 2000000
        tax += (income_to_tax - 2000000) * 0.25
        


    # Slab 7: Above 24,00,000 -> 30%
    else:
        # Tax on 4L to 24L: 2,00,000 + 1,00,000 = 3,00,000
        tax = 300000
        # Taxable amount above 24L: income_to_tax - 2400000
        tax += (income_to_tax - 2400000) * 0.30
        

    # 2. Rebate under Section 87A
    # Rebate up to Rs 60,000 for income up to Rs 12,00,000
    if income_to_tax <= 1200000:
        # Rebate is the lesser of the calculated tax or the maximum rebate (60,000)
        rebate = min(tax, 60000)
        tax = tax - rebate

    # Note: Surcharge is not included here for simplicity, as it only applies above ₹50 lakh.
    
    # 3. Health & Education Cess (4%)
    tax += tax * 0.04

    return round(tax, 2)


# Feature Engineering
def prepare_features(data):
    df = pd.DataFrame([data])

    df["gross_income"] = df["salary"] + df["other_income"] + df["lta"]

    df["total_deductions"] = (
        df["invest_80C"]
        + df["invest_80D"]
        + df["home_loan_interest"]
        + df["standard_deduction"]
    )

    df["net_income_after_hra"] = df["gross_income"] - df["hra"]

    return df[
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


# API
@app.route("/user/dashboard/tax-prediction", methods=["POST"])
def predict_tax():
    try:
        data = request.json

        required_fields = [
            "salary",
            "hra",
            "lta",
            "invest_80C",
            "invest_80D",
            "home_loan_interest",
            "rent_paid",
            "other_income",
            "standard_deduction",
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400

        # Prepare ML features
        X = prepare_features(data)

        # FIX 1: Convert NumPy → Python float
        taxable_income = float(model.predict(X)[0])
        taxable_income = max(0.0, round(taxable_income, 2))

        # FIX 2: Ensure tax is Python float
        final_tax = float(calculate_tax(taxable_income))

        return jsonify({
            "status": "success",
            "taxable_income": taxable_income,
            "final_tax_payable": final_tax,
            "tax_regime": "Old Regime",
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/cors-test", methods=["GET", "OPTIONS"])
def cors_test():
    return jsonify({"message": "CORS is working"})






# This code is for tax optimization
@app.route("/optimize-tax", methods=["POST"])
def optimize_tax():
    try:
        data = request.get_json()

        current_tax = data.get("current_tax")
        regime = data.get("regime")

        if current_tax is None or regime is None:
            return jsonify({
                "error": "current_tax and regime are required"
            }), 400

        if regime == "OLD":
            result = generate_tax_optimization(current_tax, data)
        elif regime == "NEW":
            result = optimize_new_regime(current_tax, data)
        else:
            return jsonify({
                "error": "Invalid regime. Use OLD or NEW."
            }), 400

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run App
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

# CORS(app)