
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
    background-color: #f2f4f7;
    color: #1f2933;
}

h1, h2, h3, h4 {
    color: #0f172a;
}

.header {
    background-color: #0b5ed7;
    padding: 25px;
    border-radius: 12px;
    color: white;
    margin-bottom: 20px;
}

.header-title {
    font-size: 34px;
    font-weight: 700;
}

.header-subtitle {
    font-size: 16px;
    opacity: 0.9;
}

.card {
    background-color: #ffffff;
    padding: 18px;
    border-radius: 12px;
    border-left: 6px solid #0b5ed7;
    box-shadow: 0 3px 8px rgba(0,0,0,0.05);
    margin-bottom: 15px;
    color: #1f2933;
}

.card b {
    color: #0f172a;
}

.badge-high {
    background-color: #dc2626;
    color: white;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
}

.badge-medium {
    background-color: #f59e0b;
    color: white;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
}

.badge-low {
    background-color: #16a34a;
    color: white;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
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
st.markdown("""
<div class="header">
    <div class="header-title">AI-Powered Grievance Redressal System</div>
    <div class="header-subtitle">
        Intelligent complaint classification, prioritization, and routing
    </div>
</div>
""", unsafe_allow_html=True)
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
    col1, col2, col3 = st.columns(3)

    with col1:
        priority_filter = st.selectbox(
            "Filter by Priority",
            ["All", "High", "Medium", "Low"]
        )

    with col2:
        category_filter = st.selectbox(
            "Filter by Category",
            ["All"] + sorted(df["category"].unique().tolist())
        )

    with col3:
        department_filter = st.selectbox(
            "Filter by Department",
            ["All"] + sorted(df["department"].unique().tolist())
        )


    if df.empty:
        st.info("No complaints yet.")
    else:
                filtered_df = df.copy()

                if priority_filter != "All":
                     filtered_df = filtered_df[filtered_df["priority"] == priority_filter]

                if category_filter != "All":
                    filtered_df = filtered_df[filtered_df["category"] == category_filter]

                if department_filter != "All":
                    filtered_df = filtered_df[filtered_df["department"] == department_filter]

                if filtered_df.empty:
                    st.info("No complaints match the selected filters.")
                else:
                    for _, row in filtered_df.iterrows():

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
