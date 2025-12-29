# new_regime_optimizer.py

def optimize_new_regime(current_tax, data):
    """
    Rule-based tax optimization for NEW tax regime.
    No deductions like 80C/80D/HRA allowed here.
    """

    suggestions = []

    salary = data.get("salary", 0)
    has_employer_nps = data.get("has_employer_nps", False)

    # --- Standard Deduction ---
    suggestions.append({
        "title": "Standard Deduction",
        "message": "Ensure the ₹50,000 standard deduction is applied under the New Tax Regime.",
        "impact": "Reduces taxable income directly"
    })

    # --- Employer NPS (80CCD(2)) ---
    if not has_employer_nps:
        suggestions.append({
            "title": "Employer NPS Contribution",
            "message": (
                "Employer contribution to NPS under Section 80CCD(2) "
                "is allowed even in the New Tax Regime and can reduce taxable income."
            ),
            "impact": "Can significantly reduce tax if employer offers NPS"
        })

    # --- Salary Structure Optimization ---
    if salary > 0:
        suggestions.append({
            "title": "Salary Structure Optimization",
            "message": (
                "Consider restructuring salary to include non-taxable components "
                "like employer reimbursements or benefits."
            ),
            "impact": "Tax saving depends on employer policy"
        })

    # --- Regime Comparison ---
    suggestions.append({
        "title": "Regime Comparison",
        "message": (
            "If you plan to invest in tax-saving instruments, "
            "compare Old vs New Regime to check which is more beneficial."
        ),
        "impact": "May reduce tax in future years"
    })

    return {
        "current_tax": current_tax,
        "optimized_tax_estimate": current_tax,  # no direct reduction
        "estimated_tax_saving": "Depends on employer benefits and salary structure",
        "suggestions": suggestions
    }
