# matrix.py - The Core Logic for your Customs Oracle SaaS

# High-volume China-to-Ghana import categories seeded with 2026 ECOWAS CET bands
TARIFF_MATRIX = {
    "Electronics & Gadgets": {"hs_prefix": "8517.13", "duty": 0.10, "desc": "Smartphones, laptops, and consumer electronic units."},
    "Textiles & Clothing": {"hs_prefix": "6109.10", "duty": 0.20, "desc": "Baled garments, finished apparel, and bulk fabrics."},
    "Lithium Batteries & Solar": {"hs_prefix": "8504.40", "duty": 0.10, "desc": "Renewable energy storage, inverters, and PV components."},
    "Industrial Machinery": {"hs_prefix": "8479.89", "duty": 0.05, "desc": "Manufacturing plants, production tools, and heavy spares."}
}

def calculate_landed_cost(category_key, fob_usd, freight_usd, exchange_rate):
    """
    Computes Ghana Port customs obligations following the 2026 VAT Act 1151.
    VAT, NHIL, and GETFund are re-coupled and calculated on the exact same base.
    """
    if category_key not in TARIFF_MATRIX:
        return None
        
    # 1. Base Valuation
    cif_usd = fob_usd + freight_usd
    cif_ghs = cif_usd * exchange_rate
    
    # 2. Duty Layer
    duty_rate = TARIFF_MATRIX[category_key]["duty"]
    import_duty_ghs = cif_ghs * duty_rate
    
    # 3. The 2026 Unified Base (CIF + Import Duty)
    # Under Act 1151, Levies and VAT are calculated concurrently on this exact line item
    unified_tax_base = cif_ghs + import_duty_ghs
    
    nhil_ghs = unified_tax_base * 0.025      # 2.5% National Health Insurance
    getfund_ghs = unified_tax_base * 0.025   # 2.5% Ghana Education Trust Fund
    vat_ghs = unified_tax_base * 0.15        # 15% Standard VAT
    
    # 4. Standard Operational Port Fees
    exim_levy_ghs = cif_ghs * 0.01          # 1% EXIM Levy
    au_levy_ghs = cif_ghs * 0.002           # 0.2% African Union Levy
    exam_fee_ghs = cif_ghs * 0.01           # 1% Physical Examination Levy
    
    total_statutory_levies = nhil_ghs + getfund_ghs + exim_levy_ghs + au_levy_ghs + exam_fee_ghs
    total_taxes_ghs = import_duty_ghs + total_statutory_levies + vat_ghs
    final_landed_cost_ghs = cif_ghs + total_taxes_ghs
    
    return {
        "hs_code": TARIFF_MATRIX[category_key]["hs_prefix"],
        "cif_ghs": round(cif_ghs, 2),
        "import_duty_ghs": round(import_duty_ghs, 2),
        "nhil_ghs": round(nhil_ghs, 2),
        "getfund_ghs": round(getfund_ghs, 2),
        "vat_ghs": round(vat_ghs, 2),
        "other_levies_ghs": round(exim_levy_ghs + au_levy_ghs + exam_fee_ghs, 2),
        "total_taxes_ghs": round(total_taxes_ghs, 2),
        "final_total_ghs": round(final_landed_cost_ghs, 2)
    }

    cif_usd = declared_value_usd + freight_usd
    cif_ghs = cif_usd * customs_exchange_rate
    
    import_duty = cif_ghs * item_data['duty_rate']
    
    # Granular GRA Levies (Total 6.2%)
    nhil = cif_ghs * 0.025
    getfund = cif_ghs * 0.025
    exim = cif_ghs * 0.010
    au_levy = cif_ghs * 0.002
    total_levies = nhil + getfund + exim + au_levy
    
    # Multi-staged VAT Calculation
    vat_base = cif_ghs + import_duty
    vat_amount = vat_base * item_data['vat_rate']
    
    total_taxes = import_duty + total_levies + vat_amount
    grand_total = cif_ghs + total_taxes

    return {
        "hs_code": item_data['hs_code'],
        "description": item_data['description'],
        "exchange_rate": customs_exchange_rate,
        "cif_usd": round(cif_usd, 2),
        "cif_ghs": round(cif_ghs, 2),
        "import_duty_ghs": round(import_duty, 2),
        "levy_breakdown": {
            "NHIL (2.5%)": round(nhil, 2),
            "GETFund (2.5%)": round(getfund, 2),
            "EXIM (1.0%)": round(exim, 2),
            "AU Levy (0.2%)": round(au_levy, 2),
            "total": round(total_levies, 2)
        },
        "vat_base_ghs": round(vat_base, 2),
        "vat_ghs": round(vat_amount, 2),
        "total_taxes_ghs": round(total_taxes, 2),
        "grand_total_ghs": round(grand_total, 2)
    }
