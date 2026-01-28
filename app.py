import streamlit as st
import pandas as pd
from textblob import TextBlob
import uuid
from datetime import datetime

# ---------- CONFIG ----------
st.set_page_config(page_title="AI Complaint Management System", layout="wide")

DATA_FILE = "complaints.csv"

# ---------- LOAD DATA ----------
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

# ---------- NLP FUNCTIONS ----------
def classify_category(text):
    text = text.lower()
    if any(word in text for word in ["water", "pipeline", "tap"]):
        return "Water"
    elif any(word in text for word in ["road", "pothole", "street"]):
        return "Roads"
    elif any(word in text for word in ["garbage", "waste", "dirty"]):
        return "Sanitation"
    elif any(word in text for word in ["hospital", "doctor", "medicine"]):
        return "Health"
    elif any(word in text for word in ["school", "college", "teacher"]):
        return "Education"
    elif any(word in text for word in ["bribe", "corrupt"]):
        return "Corruption"
    else:
        return "Other"

def detect_priority(text):
    text = text.lower()
    if any(word in text for word in ["urgent", "danger", "accident", "no water", "disease"]):
        return "High"
    elif any(word in text for word in ["not working", "delay", "problem"]):
        return "Medium"
    else:
        return "Low"

def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity < -0.3:
        return "Angry"
    elif polarity < 0:
        return "Frustrated"
    else:
        return "Neutral"

def route_department(category):
    mapping = {
        "Water": "Water Supply Department",
        "Roads": "Public Works Department",
        "Sanitation": "Municipal Sanitation",
        "Health": "Health Department",
        "Education": "Education Department",
        "Corruption": "Anti-Corruption Bureau",
        "Other": "General Administration"
    }
    return mapping.get(category, "General Administration")

# ---------- UI ----------
st.title("🧠 AI-Powered Complaint Management System")

tab1, tab2 = st.tabs(["🧑 Citizen Portal", "🖥️ Admin Dashboard"])

# ---------- CITIZEN PORTAL ----------
with tab1:
    st.header("Submit a Complaint")

    name = st.text_input("Name (optional)")
    location = st.text_input("Location")
    complaint_text = st.text_area("Describe your complaint")

    if st.button("Submit Complaint"):
        if location and complaint_text:
            category = classify_category(complaint_text)
            priority = detect_priority(complaint_text)
            sentiment = analyze_sentiment(complaint_text)
            department = route_department(category)

            new_entry = {
                "id": str(uuid.uuid4())[:8],
                "name": name if name else "Anonymous",
                "location": location,
                "complaint": complaint_text,
                "category": category,
                "priority": priority,
                "sentiment": sentiment,
                "department": department,
                "status": "Submitted"
            }

            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(df)

            st.success("✅ Complaint Submitted Successfully!")
            st.markdown(f"""
            **Complaint ID:** `{new_entry['id']}`  
            **Category:** {category}  
            **Priority:** {priority}  
            **Sentiment:** {sentiment}  
            **Assigned To:** {department}
            """)
        else:
            st.error("Please fill in all required fields.")

# ---------- ADMIN DASHBOARD ----------
with tab2:
    st.header("Admin Dashboard")

    if df.empty:
        st.info("No complaints yet.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            dept_filter = st.selectbox("Filter by Department", ["All"] + sorted(df["department"].unique().tolist()))
        with col2:
            priority_filter = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])

        filtered_df = df.copy()

        if dept_filter != "All":
            filtered_df = filtered_df[filtered_df["department"] == dept_filter]

        if priority_filter != "All":
            filtered_df = filtered_df[filtered_df["priority"] == priority_filter]

        st.dataframe(filtered_df, use_container_width=True)

        st.subheader("Update Complaint Status")
        selected_id = st.selectbox("Select Complaint ID", df["id"].tolist())
        new_status = st.selectbox("New Status", ["Submitted", "In Progress", "Resolved"])

        if st.button("Update Status"):
            df.loc[df["id"] == selected_id, "status"] = new_status
            save_data(df)
            st.success("Status updated successfully!")
