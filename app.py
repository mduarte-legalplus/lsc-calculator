import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="LSC Part 1611 Eligibility",
    page_icon="⚖️",
    layout="wide"
)

# --- CSS Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .success-box { padding: 20px; background-color: #d1e7dd; color: #0f5132; border-radius: 8px; border: 1px solid #badbcc; margin-bottom: 10px; }
    .warning-box { padding: 20px; background-color: #fff3cd; color: #664d03; border-radius: 8px; border: 1px solid #ffecb5; margin-bottom: 10px; }
    .error-box { padding: 20px; background-color: #f8d7da; color: #842029; border-radius: 8px; border: 1px solid #f5c2c7; margin-bottom: 10px; }
    .info-text { font-size: 0.9em; color: #555; font-style: italic; }
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
st.title("⚖️ LSC Part 1611 Eligibility Determination")
st.markdown("Assess financial eligibility based on **45 CFR Part 1611** (Final Rule) and **2025 Federal Poverty Guidelines**.")

# --- Tabs for Individual vs Group ---
tab1, tab2 = st.tabs(["👤 Individual Applicant", "👥 Group/Corporation"])

# ==========================================
# TAB 1: INDIVIDUAL APPLICANT
# ==========================================
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Household & Location")
        location = st.selectbox("Location", options=OFFICIAL_DATA.keys())
        household_size = st.number_input("Household Size", min_value=1, value=1)
        
        st.subheader("2. Special Status")
        is_dv = st.checkbox("Applicant is a victim of domestic violence")
        if is_dv:
            st.info("ℹ️ **Part 1611.3(e):** Consider ONLY applicant's income/assets. Exclude assets jointly held with abuser.")

    with col2:
        st.subheader("3. Financials")
        # Income Definition 1611.2(i)
        income = st.number_input("Total Annual Cash Receipts ($)", min_value=0, step=100, 
            help="Include wages (before taxes), benefits, support. Exclude: Tax refunds, gifts, food/rent in lieu of wages, $2k Native American trust income.")
        
        # Asset Definition 1611.2(d) & 1611.3(d)(1)
        assets = st.number_input("Countable Liquid Assets ($)", min_value=0, step=100, 
            help="Exclude: Principal residence, vehicles used for transportation, assets used to produce income (tools/farm), and assets exempt from bankruptcy.")

    st.divider()

    if st.button("Determine Individual Eligibility", type="primary"):
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
            Assets (${assets:,}) exceed the ceiling of ${asset_limit:,}. <br>
            <em>Part 1611.3(d): Waiver available only for unusual circumstances by Executive Director.</em></div>""", unsafe_allow_html=True)

        # Scenario B: Income <= 125% (Standard Eligibility)
        elif income <= limit_125:
            st.markdown(f"""<div class="success-box"><strong>✅ Financially Eligible</strong><br>
            Income (${income:,}) is at or below 125% FPG (${limit_125:,}).<br>
            <em>Part 1611.4(b)</em></div>""", unsafe_allow_html=True)

        # Scenario C: Income > 200% (Generally Ineligible)
        elif income > limit_200:
            st.markdown(f"""<div class="error-box"><strong>🚫 Likely Ineligible (Income > 200%)</strong><br>
            Income (${income:,}) exceeds the absolute ceiling of 200% FPG (${limit_200:,}).</div>""", unsafe_allow_html=True)
            
            st.markdown("#### **Authorized Exceptions for Income > 200%** (Part 1611.5(a)(1)-(2))")
            ex_nursing = st.checkbox("Income is primarily committed to medical or nursing home expenses?")
            ex_maintain_benefits = st.checkbox("Applicant is seeking to MAINTAIN governmental benefits for low-income families?")
            
            if ex_nursing or ex_maintain_benefits:
                st.markdown(f"""<div class="success-box"><strong>✅ Eligible via Exception</strong><br>
                Applicant qualifies under Part 1611.5(a)(1) or (2). Documentation required.</div>""", unsafe_allow_html=True)

        # Scenario D: Income between 125% and 200% (The "Authorized Exceptions" Zone)
        else:
            st.markdown(f"""<div class="warning-box"><strong>⚠️ Review Required (Income 125% - 200%)</strong><br>
            Income (${income:,}) is above 125% (${limit_125:,}) but below 200% (${limit_200:,}).<br>
            Applicant is eligible <strong>ONLY IF</strong> one of the factors below applies.</div>""", unsafe_allow_html=True)
            
            st.markdown("#### **Select Applicable Factors (Part 1611.5(a)(3)-(4)):**")
            
            # List specific factors from regulation
            f1 = st.checkbox("Seeking to obtain low-income governmental benefits")
            f2 = st.checkbox("Seeking to obtain/maintain disability benefits")
            f3 = st.checkbox("Unreimbursed medical expenses / insurance premiums")
            f4 = st.checkbox("Fixed debts and obligations (e.g., mortgage, rent, past taxes)")
            f5 = st.checkbox("Employment/Job Training expenses (child care, transport, equipment)")
            f6 = st.checkbox("Expenses associated with age or disability")
            f7 = st.checkbox("Current Taxes (State, Federal, Local)")
            
            if any([f1, f2, f3, f4, f5, f6, f7]):
                 st.markdown(f"""<div class="success-box"><strong>✅ Financially Eligible (Authorized Exception)</strong><br>
                 Applicant qualifies under Part 1611.5. Record the specific factors selected in the client file.</div>""", unsafe_allow_html=True)
            else:
                 st.markdown("Please select a factor above to verify eligibility.")

# ==========================================
# TAB 2: GROUP / CORPORATION
# ==========================================
with tab2:
    st.subheader("Eligibility of Groups (Part 1611.6)")
    st.markdown("A recipient may provide legal assistance to a group, corporation, or association if it lacks funds to retain private counsel **AND** meets one of the criteria below.")
    
    lack_funds = st.checkbox("1. The group lacks (and has no means to obtain) funds to retain private counsel.")
    
    st.markdown("---")
    st.markdown("**2. Determine Category:**")
    
    # Category 1: Composition
    cat_composed = st.checkbox("Category A: The group is primarily composed of eligible individuals.")
    if cat_composed:
        st.info("Must verify that a majority of members (or the governing body) are financially eligible individuals.")
        
    # Category 2: Activity
    cat_activity = st.checkbox("Category B: Principal activity is delivering services to eligible persons.")
    if cat_activity:
        st.info("Must verify the legal assistance sought relates to this activity.")

    if st.button("Determine Group Eligibility"):
        if not lack_funds:
            st.markdown(f"""<div class="error-box"><strong>🚫 Ineligible</strong><br>
            Group must lack funds to retain private counsel (Part 1611.6(a)).</div>""", unsafe_allow_html=True)
        elif cat_composed or cat_activity:
            st.markdown(f"""<div class="success-box"><strong>✅ Eligible Group</strong><br>
            Group meets the criteria of Part 1611.6(a)(1) or (2). <br>Collect documentation demonstrating eligibility (Part 1611.6(b)).</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="warning-box"><strong>⚠️ Incomplete</strong><br>
            Group must either be composed of eligible individuals OR serve eligible individuals.</div>""", unsafe_allow_html=True)
