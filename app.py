
import streamlit as st
import pandas as pd
from textblob import TextBlob
import uuid

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Complaint System",
    layout="wide",
    page_icon="🧠"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
body {
    background-color: #f4f6f9;
}
.main-title {
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(90deg, #6a11cb, #2575fc);
    -webkit-background-clip: text;
    color: transparent;
}
.subtitle {
    font-size: 18px;
    color: #555;
}
.card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    margin-bottom: 15px;
}
.badge-high {
    color: white;
    background-color: #e74c3c;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 14px;
}
.badge-medium {
    color: white;
    background-color: #f39c12;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 14px;
}
.badge-low {
    color: white;
    background-color: #2ecc71;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DATA ----------------
DATA_FILE = "complaints.csv"

def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except:
        return pd.DataFrame(columns=[
            "id","name","location","complaint",
            "category","priority","sentiment",
            "department","status"
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# ---------------- AI FUNCTIONS ----------------
def classify_category(text):
    t = text.lower()
    if any(w in t for w in ["water", "tap", "pipeline"]):
        return "Water"
    if any(w in t for w in ["road", "pothole"]):
        return "Roads"
    if any(w in t for w in ["garbage", "waste"]):
        return "Sanitation"
    if any(w in t for w in ["hospital", "medicine"]):
        return "Health"
    if any(w in t for w in ["school", "college"]):
        return "Education"
    if any(w in t for w in ["bribe", "corrupt"]):
        return "Corruption"
    return "Other"

def detect_priority(text):
    t = text.lower()
    if any(w in t for w in ["urgent", "danger", "no water", "disease"]):
        return "High"
    if any(w in t for w in ["problem", "delay", "not working"]):
        return "Medium"
    return "Low"

def sentiment(text):
    p = TextBlob(text).sentiment.polarity
    if p < -0.3:
        return "Angry 😡"
    elif p < 0:
        return "Frustrated 😤"
    return "Neutral 🙂"

def department(cat):
    return {
        "Water": "Water Supply Dept",
        "Roads": "Public Works Dept",
        "Sanitation": "Municipal Sanitation",
        "Health": "Health Dept",
        "Education": "Education Dept",
        "Corruption": "Anti-Corruption Bureau",
        "Other": "General Admin"
    }[cat]

# ---------------- HEADER ----------------
st.markdown("<div class='main-title'>AI Complaint Management System</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Smart governance through AI-powered complaint analysis</div>", unsafe_allow_html=True)
st.write("")

tab1, tab2 = st.tabs(["🧑 Citizen Portal", "🖥 Admin Dashboard"])

# ---------------- CITIZEN PORTAL ----------------
with tab1:
    st.subheader("📨 Submit a Complaint")

    name = st.text_input("Your Name (optional)")
    location = st.text_input("Location")
    complaint = st.text_area("Describe your issue")

    if st.button("🚀 Submit Complaint"):
        if location and complaint:
            cat = classify_category(complaint)
            pr = detect_priority(complaint)
            sent = sentiment(complaint)
            dept = department(cat)

            new = {
                "id": str(uuid.uuid4())[:8],
                "name": name if name else "Anonymous",
                "location": location,
                "complaint": complaint,
                "category": cat,
                "priority": pr,
                "sentiment": sent,
                "department": dept,
                "status": "Submitted"
            }

            df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
            save_data(df)

            st.success("Complaint submitted successfully 🎉")
            st.info(f"""
**Complaint ID:** {new['id']}  
**Category:** {cat}  
**Priority:** {pr}  
**Department:** {dept}
""")
        else:
            st.error("Please fill all required fields.")

# ---------------- ADMIN DASHBOARD ----------------
with tab2:
    st.subheader("📊 Admin Dashboard")

    if df.empty:
        st.info("No complaints yet.")
    else:
        for _, row in df.iterrows():
            badge = "badge-low"
            if row["priority"] == "High":
                badge = "badge-high"
            elif row["priority"] == "Medium":
                badge = "badge-medium"

            st.markdown(f"""
            <div class="card">
                <b>📍 {row['location']}</b><br>
                <i>{row['complaint']}</i><br><br>
                <span class="{badge}">{row['priority']} Priority</span><br><br>
                🏷 Category: {row['category']}  
                <br>🏢 Dept: {row['department']}  
                <br>📌 Status: {row['status']}  
                <br>💬 Sentiment: {row['sentiment']}
            </div>
            """, unsafe_allow_html=True)
