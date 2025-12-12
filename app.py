import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="LSC Eligibility Portal",
    page_icon="⚖️",
    layout="centered"
)

# --- Custom Styling (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .success-box { padding: 20px; background-color: #d1e7dd; color: #0f5132; border-radius: 8px; border: 1px solid #badbcc; margin-top: 10px; }
    .warning-box { padding: 20px; background-color: #fff3cd; color: #664d03; border-radius: 8px; border: 1px solid #ffecb5; margin-top: 10px; }
    .error-box { padding: 20px; background-color: #f8d7da; color: #842029; border-radius: 8px; border: 1px solid #f5c2c7; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2025 LSC Official Data (Exact Tables from Federal Register) ---
# Source: 45 CFR Part 1611 Appendix A (Jan 2025)
# We use a lookup table for sizes 1-8 to account for rounding variances.
OFFICIAL_DATA = {
    "48 Contiguous States & DC": {
        "125%": [0, 19563, 26438, 33313, 40188, 47063, 53938, 60813, 67688], # Index 0 is dummy, Index 1 is size 1
        "200%": [0, 31300, 42300, 53300, 64300, 75300, 86300, 97300, 108300],
        "inc125": 6875, # Add-on for size 9+
        "inc200": 11000 # Add-on for size 9+
    },
    "Alaska": {
        "125%": [0, 24438, 33038, 41638, 50238, 58838, 67438, 76038, 84638],
        "200%": [0, 39100, 52860, 66620, 80380, 94140, 107900, 121660, 135420],
        "inc125": 8600,
        "inc200": 13760
    },
    "Hawaii": {
        "125%": [0, 22488, 30400, 38313, 46225, 54138, 62050, 69963, 77875],
        "200%": [0, 35980, 48640, 61300, 73960, 86620, 99280, 111940, 124600],
        "inc125": 7913,
        "inc200": 12660
    }
}

# --- Helper Function to Get Limit ---
def get_limit(location, size, limit_type):
    data = OFFICIAL_DATA[location]
    # For households 1-8, use the exact table value
    if size <= 8:
        return data[limit_type][size]
    # For households 9+, use the size 8 value + increments
    else:
        base = data[limit_type][8]
        increment = data["inc125"] if limit_type == "125%" else data["inc200"]
        extra_people = size - 8
        return base + (extra_people * increment)

# --- App Header ---
st.title("⚖️ LSC Financial Eligibility (2025)")
st.markdown("Use this tool to estimate client eligibility based on **125%** and **200%** Federal Poverty Guidelines.")
st.info("Attorney Work Product: For estimation only. Verify all documents.")

# --- Inputs ---
col1, col2 = st.columns(2)

with col1:
    location = st.selectbox("Location", options=OFFICIAL_DATA.keys())
    household_size = st.number_input("Household Size", min_value=1, value=1, step=1)

with col2:
    income = st.number_input("Total Annual Income ($)", min_value=0, step=100)
    assets = st.number_input("Countable Liquid Assets ($)", min_value=0, step=100, help="Exclude home, car, and trade tools.")

is_dv_victim = st.checkbox("Applicant is a victim of domestic violence")

if is_dv_victim:
    st.caption("🔴 **DV Rule Applied:** Asset ceiling waived. Ensure income entered is solely the applicant's.")

# --- Logic Engine ---
if st.button("Calculate Eligibility", type="primary"):
    
    # 1. Get Exact Thresholds from Lookup Table
    threshold_125 = get_limit(location, household_size, "125%")
    threshold_200 = get_limit(location, household_size, "200%")
    
    # 2. Calculate Asset Limit
    # Asset limits (Part 1611) typically use $5k base + $1k/person logic, which is consistent.
    asset_limit = 5000 + ((household_size - 1) * 1000)
    
    # 3. Check Assets (Pass if DV victim OR assets under limit)
    asset_pass = is_dv_victim or (assets <= asset_limit)
    
    st.divider()
    
    # --- Results Display ---
    if not asset_pass:
        st.markdown(f"""
        <div class="error-box">
            <strong>🚫 Likely Ineligible (Excess Assets)</strong><br>
            Assets of <strong>${assets:,}</strong> exceed the limit of <strong>${asset_limit:,}</strong> for a household of {household_size}.
        </div>
        """, unsafe_allow_html=True)
        
    else:
        # Asset test passed, check income
        if income <= threshold_125:
            st.markdown(f"""
            <div class="success-box">
                <strong>✅ Eligible (Standard)</strong><br>
                Income ($ {income:,}) is below 125% FPG ($ {threshold_125:,}).
            </div>
            """, unsafe_allow_html=True)
            
        elif income <= threshold_200:
            st.markdown(f"""
            <div class="warning-box">
                <strong>⚠️ Potentially Eligible (Exceptions Required)</strong><br>
                Income ($ {income:,}) is between 125% ($ {threshold_125:,}) and 200% ($ {threshold_200:,}).
                <br><br>
                <em>Check applicable exceptions: Medical expenses, fixed debts, or employment expenses.</em>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.markdown(f"""
            <div class="error-box">
                <strong>🚫 Likely Ineligible (Excess Income)</strong><br>
                Income ($ {income:,}) exceeds the 200% absolute ceiling ($ {threshold_200:,}).
            </div>
            """, unsafe_allow_html=True)
