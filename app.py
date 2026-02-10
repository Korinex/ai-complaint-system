import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
from textblob import TextBlob
import plotly.express as px
import folium
from streamlit_folium import st_folium

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AI Grievance Redressal",
    page_icon="🧠",
    layout="wide"
)

DATA_FILE = "grievances.csv"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------- SKY BLUE UI ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#dbeafe,#e0f2fe,#f0f9ff);
    font-family: 'Segoe UI', sans-serif;
}
h1,h2,h3 {color:#0c4a6e;font-weight:800;}
.stButton>button{
    background:linear-gradient(135deg,#38bdf8,#0284c7);
    color:white;font-weight:700;
    border-radius:999px;padding:0.6rem 1.8rem;
}
[data-testid="stTable"],[data-testid="stDataFrame"]{
    background:white;border-radius:14px;
}
footer{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------- INIT DATA ----------------
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=[
        "id","name","city","location","type","description",
        "department","sentiment","priority","status","created_at","image"
    ])
    df_init.to_csv(DATA_FILE, index=False)

def load_data():
    df = pd.read_csv(DATA_FILE)
    if "image" not in df.columns:
        df["image"] = ""
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# ---------------- CITY DROPDOWN ----------------
city_list = [
    "Nagpur","Wardha","Jabalpur","Bhopal","Patna","Jamshedpur",
    "Solapur","Pune","Mumbai","Nashik","Aurangabad",
    "Indore","Gwalior","Ranchi","Gaya","Ahmedabad","Surat",
    "Bangalore","Mysore","Kolkata","Hyderabad","Delhi"
]

# ---------------- AI FUNCTIONS ----------------
def analyze_sentiment(text):
    p = TextBlob(text).sentiment.polarity
    if p < -0.3:
        return "Negative 😠"
    elif p < 0.1:
        return "Neutral 😐"
    return "Positive 😊"

def detect_priority(text):
    t = text.lower()
    if any(w in t for w in ["urgent","danger","accident","death","fire"]):
        return "High 🔥"
    if any(w in t for w in ["delay","problem","not working"]):
        return "Medium ⚠️"
    return "Low 🟢"

def route_department(gtype):
    return {
        "Public Safety": "🚓 Police",
        "Sanitation": "🧹 Municipal",
        "Infrastructure": "🏗 PWD",
        "Healthcare": "🏥 Health Dept",
        "Utilities": "⚡ Electricity Board",
        "Education": "🎓 Education Dept",
        "Administrative Delay": "📂 General Admin",
        "Other": "📂 General Admin"
    }.get(gtype, "📂 General Admin")

# ---------------- LOGIN ----------------
st.markdown("<h1 style='text-align:center;'>🧠 AI-Powered Grievance Redressal System</h1>", unsafe_allow_html=True)

role = st.selectbox("🔐 Login As", ["Citizen","Admin"])
password = st.text_input("🔑 Password", type="password")

if role == "Admin" and password != "admin":
    st.error("Invalid Admin Password ❌")
    st.stop()

if role == "Citizen" and password == "":
    st.error("Password Required ❌")
    st.stop()

st.success(f"Logged in as {role} ✅")

# ==================================================
# ================= CITIZEN ========================
# ==================================================
if role == "Citizen":

    st.header("📨 Submit a Grievance")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("👤 Name")
        city = st.selectbox("🏙 City", city_list)

    with col2:
        location = st.selectbox("📍 Location",["Urban","Rural","Semi-Urban"])
        gtype = st.selectbox("⚠️ Type",[
            "Public Safety","Sanitation","Infrastructure",
            "Healthcare","Utilities","Education",
            "Administrative Delay","Other"
        ])

    description = st.text_area("📝 Description")

    uploaded_file = st.file_uploader("📷 Upload Photo (Optional)", type=["png","jpg","jpeg"])

    if st.button("🚀 Submit Complaint"):

        sid = str(uuid.uuid4())[:8]
        sentiment = analyze_sentiment(description)
        priority = detect_priority(description)
        department = route_department(gtype)

        image_path = ""
        if uploaded_file is not None:
            image_filename = f"{sid}_{uploaded_file.name}"
            image_path = os.path.join(UPLOAD_DIR, image_filename)
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

        new_data = {
            "id":sid,
            "name":name if name else "Anonymous",
            "city":city,
            "location":location,
            "type":gtype,
            "description":description,
            "department":department,
            "sentiment":sentiment,
            "priority":priority,
            "status":"Submitted ⏳",
            "created_at":datetime.now().strftime("%Y-%m-%d %H:%M"),
            "image":image_path
        }

        df = pd.concat([df,pd.DataFrame([new_data])],ignore_index=True)
        save_data(df)

        st.success("Complaint Submitted Successfully 🎉")

        c1,c2,c3 = st.columns(3)
        c1.metric("Sentiment",sentiment)
        c2.metric("Priority",priority)
        c3.metric("Department",department)

    st.divider()

    st.subheader("📍 Your Complaint Timeline")

    user_df = df[df["name"] == name] if name else df.tail(5)

    if not user_df.empty:
        timeline = user_df[["id","type","status","created_at"]]
        st.dataframe(timeline,use_container_width=True)
    else:
        st.info("No complaints yet.")

# ==================================================
# ================= ADMIN ==========================
# ==================================================
else:

    st.header("🖥 Admin Dashboard")

    col1,col2,col3 = st.columns(3)
    col1.metric("📨 Total",len(df))
    col2.metric("⏳ Pending",len(df[df["status"].str.contains("Submitted")]))
    col3.metric("✅ Resolved",len(df[df["status"].str.contains("Resolved")]))

    st.divider()

    st.subheader("📋 Complaint Details")

    if df.empty:
        st.info("No complaints available.")
    else:
        selected_id = st.selectbox("Select Complaint ID",df["id"].tolist())
        selected = df[df["id"]==selected_id].iloc[0]

        details_df = pd.DataFrame({
            "Field":[
                "👤 Name","🏙 City","📍 Location","📂 Type",
                "🏢 Department","🔥 Priority","😊 Sentiment",
                "📅 Created","📌 Status"
            ],
            "Value":[
                selected["name"],
                selected["city"],
                selected["location"],
                selected["type"],
                selected["department"],
                selected["priority"],
                selected["sentiment"],
                selected["created_at"],
                selected["status"]
            ]
        })

        st.table(details_df)

        # Show Image safely
        if "image" in selected and isinstance(selected["image"], str) and selected["image"] != "":
            if os.path.exists(selected["image"]):
                st.image(selected["image"], caption="Uploaded Evidence 📷")

        status_options = ["Submitted ⏳","In Progress 🔧","Resolved ✅"]

        current_status = selected["status"]
        if current_status not in status_options:
            current_status = "Submitted ⏳"

        new_status = st.selectbox(
            "Update Status",
            status_options,
            index=status_options.index(current_status)
        )

        if st.button("💾 Update Status"):
            df.loc[df["id"]==selected_id,"status"] = new_status
            save_data(df)
            st.success("Status Updated Successfully ✅")

    st.divider()

    st.subheader("📊 Department Performance")

    chart = df.groupby("department").size().reset_index(name="count")

    fig = px.bar(
        chart,
        x="department",
        y="count",
        color="department",
        text="count",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig.update_layout(showlegend=False)
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig,use_container_width=True)

    st.divider()

    st.subheader("🗺 Complaint Map")

    city_coords = {
        "Nagpur":[21.1458,79.0882],
        "Wardha":[20.7453,78.6022],
        "Jabalpur":[23.1815,79.9864],
        "Bhopal":[23.2599,77.4126],
        "Patna":[25.5941,85.1376],
        "Jamshedpur":[22.8046,86.2029],
        "Solapur":[17.6599,75.9064],
        "Pune":[18.5204,73.8567],
        "Mumbai":[19.0760,72.8777],
        "Nashik":[19.9975,73.7898],
        "Aurangabad":[19.8762,75.3433],
        "Indore":[22.7196,75.8577],
        "Gwalior":[26.2183,78.1828],
        "Ranchi":[23.3441,85.3096],
        "Gaya":[24.7914,85.0002],
        "Ahmedabad":[23.0225,72.5714],
        "Surat":[21.1702,72.8311],
        "Bangalore":[12.9716,77.5946],
        "Mysore":[12.2958,76.6394],
        "Kolkata":[22.5726,88.3639],
        "Hyderabad":[17.3850,78.4867],
        "Delhi":[28.6139,77.2090]
    }

    m = folium.Map(location=[22.5,80],zoom_start=5)

    city_counts = df["city"].value_counts().to_dict()

    for city,count in city_counts.items():
        if city in city_coords:
            folium.CircleMarker(
                location=city_coords[city],
                radius=6+count,
                popup=f"{city}: {count} complaints",
                color="red",
                fill=True,
                fill_opacity=0.7
            ).add_to(m)

    st_folium(m,width=1000,height=500)

st.caption("💡 Built with Streamlit, NLP & AI for Smart Governance 🚀")
