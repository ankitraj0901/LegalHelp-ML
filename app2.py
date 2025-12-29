from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib

# ==========================================
# FLASK SETUP
# ==========================================
app = Flask(__name__)
CORS(app)

# ==========================================
# LOAD MODEL & ENCODER
# ==========================================
model = joblib.load("model/rf_model.pkl")
label_encoder = joblib.load("model/label_encoder.pkl")

# MUST match training order
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

ALLOWED_CLASSIFICATIONS = list(label_encoder.classes_)

# ==========================================
# ENDPOINTS
# ==========================================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ML API running"})


@app.route("/classifications", methods=["GET"])
def classifications():
    return jsonify({
        "allowed_classifications": ALLOWED_CLASSIFICATIONS
    })


@app.route("/features", methods=["GET"])
def features():
    return jsonify({
        "required_features": FEATURES
    })


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # Normalize classification input
        classification = str(data.get("classification")).lower().strip()

        if classification not in ALLOWED_CLASSIFICATIONS:
            return jsonify({
                "error": "Invalid classification value",
                "allowed_classifications": ALLOWED_CLASSIFICATIONS
            }), 400

        # Build input DataFrame
        input_df = pd.DataFrame([data])

        input_df['classification'] = classification
        input_df['classification'] = label_encoder.transform(
            input_df['classification']
        )

        input_df = input_df[FEATURES]

        prediction = model.predict(input_df)[0]

        return jsonify({
            "predicted_1y_return": round(float(prediction), 2),
            "unit": "%"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ==========================================
# RUN SERVER
# ==========================================
if __name__ == "__main__":
    app.run(debug=True)
