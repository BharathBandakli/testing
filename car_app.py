import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
from PIL import Image
import os

# ---------------------------------------
# Page Configuration
# ---------------------------------------
st.set_page_config(
    page_title="Car Price Prediction",
    page_icon="🚗",
    layout="wide"
)

# ---------------------------------------
# Custom CSS
# ---------------------------------------
st.markdown("""
<style>
.main {
    padding: 1rem;
}

h1 {
    color: #e74c3c;
    text-align: center;
}

.stButton>button {
    width:100%;
    background:#e74c3c;
    color:white;
    border-radius:10px;
    height:45px;
}

.stMetric{
    background:#f8f9fa;
    padding:10px;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------
# Load Model
# ---------------------------------------
@st.cache_resource
def load_model():
    try:
        return joblib.load("car_prediction_model.pkl")
    except:
        return None

model = load_model()

# ---------------------------------------
# Header
# ---------------------------------------
st.title("🚗 Car Price Prediction System")
st.markdown("### Get Instant Valuation for Your Used Car")

if model is None:
    st.error("car_prediction_model.pkl not found.")
    st.stop()
    # ==========================================
# Sidebar Inputs
# ==========================================

st.sidebar.title("🚗 Car Details")

st.sidebar.subheader("Basic Information")

# -------------------------
# Select Car
# -------------------------
car_name = st.sidebar.selectbox(
    "Select Car",
    [
        "Swift",
        "Baleno",
        "Kwid",
        "BMW",
        "i20"
    ]
)

# -------------------------
# Car Images
# -------------------------
car_images = {
    "Swift": "swift.jpg",
    "Baleno": "baleno.jpg",
    "Kwid": "kwid.jpg",
    "BMW": "bmw.jpg",
    "i20": "i20.jpg"
}

image_path = os.path.join("static", car_images[car_name])

if os.path.exists(image_path):
    st.sidebar.image(image_path, caption=car_name, use_container_width=True)
else:
    st.sidebar.warning("Car image not found")

# -------------------------
# Manufacturing Year
# -------------------------
year = st.sidebar.slider(
    "Manufacturing Year",
    2000,
    2024,
    2018
)

# -------------------------
# Showroom Price
# -------------------------
present_price = st.sidebar.number_input(
    "Current Ex-Showroom Price (Lakhs)",
    min_value=0.0,
    max_value=50.0,
    value=5.0,
    step=0.1
)

# -------------------------
# Kilometers Driven
# -------------------------
kms_driven = st.sidebar.number_input(
    "Kilometers Driven",
    min_value=0,
    max_value=500000,
    value=50000,
    
    step=1000
)

# ==========================================
# Car Specifications
# ==========================================

st.sidebar.subheader("Car Specifications")

fuel_type = st.sidebar.selectbox(
    "Fuel Type",
    [
        "Petrol",
        "Diesel",
        "CNG"
    ]
)

seller_type = st.sidebar.selectbox(
    "Seller Type",
    [
        "Dealer",
        "Individual"
    ]
)

transmission = st.sidebar.selectbox(
    "Transmission",
    [
        "Manual",
        "Automatic"
    ]
)

owner = st.sidebar.selectbox(
    "Previous Owners",
    [
        0,
        1,
        2,
        3
    ]
)

# ==========================================
# Car Age
# ==========================================

current_year = 2024
car_age = current_year - year

# ==========================================
# Predict Button
# ==========================================

st.sidebar.markdown("---")

predict_btn = st.sidebar.button(
    "🚗 Get Price Estimate",
    use_container_width=True
)
# ==========================================
# Prediction
# ==========================================

if predict_btn:

    # Encode categorical values
    fuel_encoded = {
        "Petrol": 0,
        "Diesel": 1,
        "CNG": 2
    }[fuel_type]

    seller_encoded = {
        "Dealer": 0,
        "Individual": 1
    }[seller_type]

    transmission_encoded = {
        "Manual": 0,
        "Automatic": 1
    }[transmission]

    # Create dataframe for prediction
    input_data = pd.DataFrame({
        "Year": [year],
        "Present_Price": [present_price],
        "Kms_Driven": [kms_driven],
        "Fuel_Type": [fuel_encoded],
        "Seller_Type": [seller_encoded],
        "Transmission": [transmission_encoded],
        "Owner": [owner]
    })

    # Predict Price
    predicted_price = model.predict(input_data)[0]

    # Avoid negative values
    if predicted_price < 0:
        predicted_price = 0

    # Depreciation
    depreciation = present_price - predicted_price

    if present_price > 0:
        depreciation_percent = (depreciation / present_price) * 100
    else:
        depreciation_percent = 0

    # ==========================================
    # Results Header
    # ==========================================

    st.markdown("---")
    st.header("🚗 Price Estimation Results")

    st.subheader(f"Selected Car : {car_name}")

    # Show Selected Car Image
    if os.path.exists(image_path):
        st.image(image_path, width=450)

    st.success("Prediction Generated Successfully ✅")

    # ==========================================
    # Price Cards
    # ==========================================

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Estimated Selling Price",
            f"₹ {predicted_price:.2f} Lakhs"
        )

    with col2:
        st.metric(
            "Current Showroom Price",
            f"₹ {present_price:.2f} Lakhs"
        )

    with col3:
        st.metric(
            "Depreciation",
            f"₹ {depreciation:.2f} Lakhs",
            delta=f"-{depreciation_percent:.1f}%"
        )

    st.markdown("---")
        # ==========================================
    # Price Analysis
    # ==========================================

    st.subheader("📊 Price Analysis")

    col1, col2 = st.columns([2, 1])

    with col1:

        lower_estimate = predicted_price * 0.90
        upper_estimate = predicted_price * 1.10

        st.success(f"""
### 💰 Expected Market Price

**₹ {lower_estimate:.2f} Lakhs  -  ₹ {upper_estimate:.2f} Lakhs**

This is the expected market selling price of your car.
""")

        st.markdown("### 🚗 Price Factors")

        factors = []

        if car_age <= 2:
            factors.append("✅ Very New Car (High Resale Value)")
        elif car_age <= 5:
            factors.append("✅ Good Resale Value")
        elif car_age <= 10:
            factors.append("⚠ Average Resale Value")
        else:
            factors.append("❌ Older Car (Higher Depreciation)")

        if kms_driven < 30000:
            factors.append("✅ Low Mileage")
        elif kms_driven < 80000:
            factors.append("⚠ Average Mileage")
        else:
            factors.append("❌ High Mileage")

        if transmission == "Automatic":
            factors.append("✅ Automatic Transmission")

        if fuel_type == "Diesel":
            factors.append("✅ Diesel Vehicle")
        elif fuel_type == "Petrol":
            factors.append("✅ Petrol Vehicle")
        else:
            factors.append("✅ CNG Vehicle")

        if seller_type == "Dealer":
            factors.append("✅ Dealer Selling")
        else:
            factors.append("✅ Individual Seller")

        for factor in factors:
            st.write(factor)

    with col2:

        max_price = max(present_price * 1.2, 1)

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=predicted_price,
            title={"text": "Estimated Price"},
            number={"prefix": "₹ ", "suffix": " Lakh"},
            gauge={
                "axis": {"range": [0, max_price]},
                "bar": {"color": "darkgreen"},
                "steps": [
                    {"range": [0, max_price * 0.30], "color": "#ffcccc"},
                    {"range": [max_price * 0.30, max_price * 0.70], "color": "#fff4b3"},
                    {"range": [max_price * 0.70, max_price], "color": "#ccffcc"}
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "value": present_price
                }
            }
        ))

        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
        # ==========================================
    # Car Details Summary
    # ==========================================

    st.subheader("🚗 Car Details")

    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:
        st.write(f"**Car Name:** {car_name}")
        st.write(f"**Manufacturing Year:** {year}")
        st.write(f"**Car Age:** {car_age} Years")
        st.write(f"**Fuel Type:** {fuel_type}")
        st.write(f"**Kilometers Driven:** {kms_driven:,} km")

    with detail_col2:
        st.write(f"**Transmission:** {transmission}")
        st.write(f"**Seller Type:** {seller_type}")
        st.write(f"**Previous Owners:** {owner}")
        st.write(f"**Current Showroom Price:** ₹{present_price:.2f} Lakhs")
        st.write(f"**Estimated Selling Price:** ₹{predicted_price:.2f} Lakhs")

    st.markdown("---")

    # ==========================================
    # Selling Tips
    # ==========================================

    st.subheader("💡 Tips to Get Better Selling Price")

    tips = [
        "✔ Wash and clean your car before selling.",
        "✔ Keep all service records ready.",
        "✔ Repair minor dents and scratches.",
        "✔ Replace worn-out tyres if required.",
        "✔ Take high-quality photos of the car.",
        "✔ Sell with all original documents.",
        "✔ Compare prices with similar cars online."
    ]

    for tip in tips:
        st.write(tip)

# ==========================================
# Home Page (Before Prediction)
# ==========================================

else:
    st.markdown("---")

    st.info("👈 Fill in the car details from the sidebar and click **Get Price Estimate**.")

    st.subheader("🚗 Available Cars")

c1, c2, c3, c4, c5 = st.columns(5)

cars = [
    ("Swift", "swift.jpg"),
    ("Baleno", "beleno.jpg"),   
    ("Renault ", "kwid.jpg"),
    ("BMW", "bmw.jpg"),
    ("Hyundai ", "i20.jpg")
]

columns = [c1, c2, c3, c4, c5]

IMAGE_WIDTH = 180
IMAGE_HEIGHT = 120

for col, (name, img) in zip(columns, cars):
    with col:
        img_path = os.path.join("static", img)

        if os.path.exists(img_path):
            image = Image.open(img_path)
            image = image.resize((IMAGE_WIDTH, IMAGE_HEIGHT))
            st.image(image)

        st.markdown(
            f"<h5 style='text-align:center;'>{name}</h5>",
            unsafe_allow_html=True
        )

# <-- Loop ends here

st.markdown("---")

st.subheader("📈 Model Information")

info1, info2, info3 = st.columns(3)

info1.metric("Algorithm", "Machine Learning Regression")
info2.metric("Accuracy", "85%")

info3.metric("Cars", "5 Models")