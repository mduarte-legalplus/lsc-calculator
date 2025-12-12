import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="LSC Eligibility Calculator",
    page_icon="⚖️",
    layout="centered"
)

# --- CSS Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .success-box { padding: 20px; background-color: #d1e7dd; color: #0f5132; border-radius: 8px; border: 1px solid #badbcc; margin-bottom: 10px; }
    .warning-box { padding: 20px; background-color: #fff3cd; color: #664d03; border-radius: 8px; border: 1px solid #ffecb5; margin-bottom: 10px; }
    .error-box { padding: 20px; background-color: #f8d7da; color: #842029; border-radius: 8px; border: 1px solid #f5c2c7; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2025 LSC Official Data (Lookup Tables) ---
OFFICIAL_DATA = {
    "48 Contiguous States & DC": {
        "125%": [0, 19563, 26438, 33313, 40188, 47063, 53938, 60813, 67688],
        "200%": [0, 31300, 42300, 53300, 64300, 75300, 86300, 97300, 108300],
        "inc125": 6875, "inc200": 11000
    },
    "Alaska": {
        "125%": [0, 24438, 33038, 41638, 50238, 58838, 67438, 76038, 84638],
        "200%": [0, 39100, 52860, 66620, 80380, 94140, 107900, 121660, 135420],
        "inc125": 8600, "inc200": 13760
    },
    "Hawaii": {
        "125%": [0, 22488, 30400, 38313, 46225, 54138, 62050, 69963, 77875],
        "200%": [0, 35980, 48640, 61300, 73960, 86620, 99280, 111940, 124600],
        "inc125": 7913, "inc200": 12660
    }
}

def get_limit(location, size, limit_type):
    data = OFFICIAL_DATA[location]
    if size <= 8:
        return data[limit_type][size]
    else:
        base = data[limit_type][8]
        increment = data["inc125"] if limit_type == "125%" else data["inc200"]
        return base + ((size - 8) * increment)

# --- App Header ---
st.title("⚖️ LSC Financial Eligibility (2025)")
st.markdown("Assess financial eligibility based on **45 CFR Part 1611** and **2025 Federal Poverty Guidelines**.")

# --- Inputs ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Household & Location")
    location = st.selectbox("Location", options=OFFICIAL_DATA.keys())
    household_size = st.number_input("Household Size", min_value=1, value=1)
    
    st.subheader("Special Status")
    is_dv = st.checkbox("Applicant is a victim of domestic violence")
    if is_dv:
        st.caption("ℹ️ **DV Rule:** Consider ONLY applicant's income/assets. Exclude joint assets.")

with col2:
    st.subheader("Financials")
    # Simplified Labels with Legal Help Text
    income = st.number_input("Annual Income ($)", min_value=0, step=100, 
        help="Total cash receipts before taxes. Include wages, benefits, support. Exclude tax refunds, gifts, food/rent in lieu of wages.")
    
    assets = st.number_input("Liquid Assets ($)", min_value=0, step=100, 
        help="Cash or resources readily convertible to cash. Exclude principal residence, work vehicles, and income-producing assets (e.g., tools).")

st.divider()

if st.button("Determine Eligibility", type="primary"):
    # Thresholds
    limit_125 = get_limit(location, household_size, "125%")
    limit_200 = get_limit(location, household_size, "200%")
    asset_limit = 5000 + ((household_size - 1) * 1000)

    # Asset Test
    asset_pass = True
    if not is_dv and assets > asset_limit:
        asset_pass = False

    # --- LOGIC ENGINE ---
    
    # Scenario A: Failed Asset Test
    if not asset_pass:
        st.markdown(f"""<div class="error-box"><strong>🚫 Ineligible (Excess Assets)</strong><br>
        Assets (${assets:,}) exceed the limit of ${asset_limit:,}. <br>
        <em>Waiver available only for unusual circumstances by Executive Director.</em></div>""", unsafe_allow_html=True)

    # Scenario B: Income <= 125% (Standard Eligibility)
    elif income <= limit_125:
        st.markdown(f"""<div class="success-box"><strong>✅ Financially Eligible</strong><br>
        Income (${income:,}) is at or below 125% FPG (${limit_125:,}).</div>""", unsafe_allow_html=True)

    # Scenario C: Income > 200% (Generally Ineligible)
    elif income > limit_200:
        st.markdown(f"""<div class="error-box"><strong>🚫 Likely Ineligible (Income > 200%)</strong><br>
        Income (${income:,}) exceeds the absolute ceiling of 200% FPG (${limit_200:,}).</div>""", unsafe_allow_html=True)
        
        st.markdown("#### **Exceptions for Income > 200%**")
        ex_nursing = st.checkbox("Income is committed to nursing home/medical expenses?")
        ex_maintain_benefits = st.checkbox("Seeking to maintain governmental benefits?")
        
        if ex_nursing or ex_maintain_benefits:
            st.markdown(f"""<div class="success-box"><strong>✅ Eligible via Exception</strong><br>
            Applicant qualifies under Part 1611.5(a) exceptions.</div>""", unsafe_allow_html=True)

    # Scenario D: Income between 125% and 200% (The "Authorized Exceptions" Zone)
    else:
        st.markdown(f"""<div class="warning-box"><strong>⚠️ Review Required (Income 125% - 200%)</strong><br>
        Income is above standard eligibility but below the absolute ceiling.<br>
        Applicant is eligible <strong>ONLY IF</strong> one of the factors below applies.</div>""", unsafe_allow_html=True)
        
        st.markdown("#### **Select Applicable Factors:**")
        
        f1 = st.checkbox("Seeking to obtain governmental benefits")
        f3 = st.checkbox("Unreimbursed medical expenses / insurance premiums")
        f4 = st.checkbox("Fixed debts (e.g., mortgage, rent, past taxes)")
        f5 = st.checkbox("Employment/training expenses (child care, transport)")
        f6 = st.checkbox("Expenses associated with age or disability")
        f7 = st.checkbox("Current Taxes (State, Federal, Local)")
        
        if any([f1, f3, f4, f5, f6, f7]):
                st.markdown(f"""<div class="success-box"><strong>✅ Eligible (Authorized Exception)</strong><br>
                Applicant qualifies based on the selected factors. Document these in the file.</div>""", unsafe_allow_html=True)
        else:
                st.markdown("Please select a factor above to verify eligibility.")
