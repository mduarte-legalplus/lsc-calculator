import streamlit as st

# --- Page Configuration (Tab Title & Icon) ---
st.set_page_config(
    page_title="LSC Eligibility Portal",
    page_icon="⚖️",
    layout="centered"
)

# --- Custom Styling (CSS) for a Crisp Look ---
# This hides the default menu and adds a clean font style
st.markdown("""
    <style>
    /* Import a nice font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Style the header */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A; /* Navy Blue */
        text-align: center;
        margin-bottom: 10px;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #64748B;
        text-align: center;
        margin-bottom: 30px;
    }

    /* Card-like styling for result box */
    .result-card {
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Hide the default Streamlit footer */
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2025 LSC Data Constants ---
LIMITS = {
    "48 Contiguous States": {"base125": 19563, "inc125": 6875, "base200": 31300, "inc200": 11000},
    "Alaska": {"base125": 24438, "inc125": 8600, "base200": 39100, "inc200": 13760},
    "Hawaii": {"base125": 22488, "inc125": 7913, "base200": 35980, "inc200": 12660}
}

# --- App Layout ---

# 1. Modern Header
st.markdown('<div class="main-header">Legal Aid Eligibility Portal</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Financial Eligibility Screening Tool (2025 Guidelines)</div>', unsafe_allow_html=True)

st.divider()

# 2. Input Section (Using Columns for a Compact Grid)
st.subheader("📋 Household Information")

col1, col2 = st.columns(2)

with col1:
    location = st.selectbox("📍 Residence", options=LIMITS.keys())
    household_size = st.number_input("👥 Household Size", min_value=1, value=1, help="Count applicant + all financial dependents.")

with col2:
    income = st.number_input("💵 Total Annual Income", min_value=0, step=500, format="%d", help="Gross income from all sources before taxes.")
    assets = st.number_input("🏦 Countable Liquid Assets", min_value=0, step=100, format="%d", help="Cash/Savings. Exclude: Home, Car, Work Tools.")

# Domestic Violence Toggle (Full Width)
st.write("") # Spacer
is_dv_victim = st.toggle("🛡️ Applicant is a victim of domestic violence")
if is_dv_victim:
    st.info("Domestic Violence protocol applied: Asset limits waived. Ensure income entered is solely the applicant's.")

# --- Logic Engine ---

# 1. Get Data
data = LIMITS[location]

# 2. Calculate Thresholds
limit_125 = data["base125"] + ((household_size - 1) * data["inc125"])
limit_200 = data["base200"] + ((household_size - 1) * data["inc200"])
asset_limit = 5000 + ((household_size - 1) * 1000)

# 3. Determine Status
asset_pass = is_dv_victim or (assets <= asset_limit)
status_color = "gray"
status_text = "Ready to Calculate"
detail_text = ""

# --- Action Button ---
st.write("") # Spacer
if st.button("Check Eligibility", type="primary", use_container_width=True):
    
    st.subheader("📊 Determination Results")
    
    # Logic Checks
    if not asset_pass:
        status_text = "Likely Ineligible (Assets)"
        status_color = "#fee2e2" # Light Red
        text_color = "#991b1b" # Dark Red
        detail_text = f"Total assets (${assets:,}) exceed the household limit of **${asset_limit:,}**."
        
    elif income <= limit_125:
        status_text = "Eligible (Standard)"
        status_color = "#dcfce7" # Light Green
        text_color = "#166534" # Dark Green
        detail_text = f"Income is within the 125% Federal Poverty Guideline limit of **${limit_125:,}**."
        
    elif income <= limit_200:
        status_text = "Review Required (125% - 200%)"
        status_color = "#fef9c3" # Light Yellow
        text_color = "#854d0e" # Dark Yellow
        detail_text = f"Income exceeds standard limit (${limit_125:,}) but is under the 200% cap (${limit_200:,}). Eligibility depends on specific deductions (medical, employment, etc.)."
        
    else:
        status_text = "Ineligible (Income)"
        status_color = "#fee2e2" # Light Red
        text_color = "#991b1b" # Dark Red
        detail_text = f"Income (${income:,}) exceeds the absolute 200% ceiling of **${limit_200:,}**."

    # --- Modern Result Card ---
    st.markdown(f"""
