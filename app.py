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
    /* Import a nice font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .success-box { 
        padding: 20px; 
        background-color: #d1e7dd; 
        color: #0f5132; 
        border-radius: 8px; 
        border: 1px solid #badbcc;
        margin-top: 10px;
    }
    .warning-box { 
        padding: 20px; 
        background-color: #fff3cd; 
        color: #664d03; 
        border-radius: 8px; 
        border: 1px solid #ffecb5;
        margin-top: 10px;
    }
    .error-box { 
        padding: 20px; 
        background-color: #f8d7da; 
        color: #842029; 
        border-radius: 8px; 
        border: 1px solid #f5c2c7;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2025 LSC Data Constants ---
LIMITS = {
    "48 Contiguous States & DC": {
        "base125": 19563, "inc125": 6875, 
        "base200": 31300, "inc200": 11000
    },
    "Alaska": {
        "base125": 24438, "inc125": 8600, 
        "base200": 39100, "inc200": 13760
    },
    "Hawaii": {
        "base125": 22488, "inc125": 7913, 
        "base200": 35980, "inc200": 12660
    }
}

# --- App Header ---
st.title("⚖️ LSC Financial Eligibility (2025)")
st.markdown("Use this tool to estimate client eligibility based on **125%** and **200%** Federal Poverty Guidelines.")
st.info("Attorney Work Product: For estimation only. Verify all documents.")

# --- Inputs ---
col1, col2 = st.columns(2)

with col1:
    location = st.selectbox("Location", options=LIMITS.keys())
    household_size = st.number_input("Household Size", min_value=1, value=1, step=1)

with col2:
    income = st.number_input("Total Annual Income ($)", min_value=0, step=100)
    assets = st.number_input("Countable Liquid Assets ($)", min_value=0, step=100, help="Exclude home, car, and trade tools.")

is_dv_victim = st.checkbox("Applicant is a victim of domestic violence")

if is_dv_victim:
    st.caption("🔴 **DV Rule Applied:** Asset ceiling waived. Ensure income entered is solely the applicant's.")

# --- Logic Engine ---
if st.button("Calculate Eligibility", type="primary"):
    
    # 1. Get Data for Location
    data = LIMITS[location]
    
    # 2. Calculate Thresholds
    threshold_125 = data["base125"] + ((household_size - 1) * data["inc125"])
    threshold_200 = data["base200"] + ((household_size - 1) * data["inc200"])
    
    # 3. Calculate Asset Limit
    asset_limit = 5000 + ((household_size - 1) * 1000)
    
    # 4. Check Assets (Pass if DV victim OR assets under limit)
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
