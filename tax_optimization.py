# tax_optimization.py

def generate_tax_optimization(current_tax, data):
    suggestions = []
    estimated_saving = 0

    age = data.get("age", 30)
    invest_80c = data.get("invest_80C", 0)
    invest_80d = data.get("invest_80D", 0)
    home_loan = data.get("home_loan_interest", 0)
    hra_claimed = data.get("hra_claimed", False)

    # --- Section 80C ---
    if invest_80c < 150000:
        gap = 150000 - invest_80c
        saving = int(gap * 0.20)
        estimated_saving += saving

        suggestions.append({
            "section": "80C",
            "message": f"You can invest up to ₹{gap} more under Section 80C.",
            "estimated_tax_saving": saving
        })

    # --- Section 80D ---
    limit = 25000 if age < 60 else 50000
    if invest_80d < limit:
        saving = int((limit - invest_80d) * 0.20)
        estimated_saving += saving

        suggestions.append({
            "section": "80D",
            "message": "Health insurance premium qualifies for deduction under Section 80D.",
            "estimated_tax_saving": saving
        })

    # --- Home Loan ---
    if home_loan == 0:
        suggestions.append({
            "section": "24B",
            "message": "Home loan interest up to ₹2,00,000 is deductible under Section 24.",
            "estimated_tax_saving": "Depends on loan"
        })

    # --- HRA ---
    if not hra_claimed:
        suggestions.append({
            "section": "HRA",
            "message": "You may be eligible for HRA exemption if you pay rent.",
            "estimated_tax_saving": "Depends on rent & salary"
        })

    optimized_tax = max(current_tax - estimated_saving, 0)

    return {
        "current_tax": current_tax,
        "optimized_tax_estimate": optimized_tax,
        "estimated_tax_saving": estimated_saving,
        "suggestions": suggestions
    }
