import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import openpyxl
import os
import time

# Excel File Setup
EXCEL_FILE = "skill_pledges.xlsx"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_data():
    try:
        df = pd.read_excel(EXCEL_FILE)
        records = df.to_dict(orient="records")
        
        # Ensure that 'reviews' and 'updates' are lists
        for record in records:
            if isinstance(record.get("reviews"), str):  # If stored as a string, convert it back to a list
                import ast
                record["reviews"] = ast.literal_eval(record["reviews"])  # Safely convert string to list
            if isinstance(record.get("updates"), str):
                record["updates"] = ast.literal_eval(record["updates"])

        return records
    except FileNotFoundError:
        return []

def save_data(data):
    for pledge in data:
        if "updates" not in pledge:
            pledge["updates"] = []  # Ensure every pledge has an 'updates' field
    
    df = pd.DataFrame(data)
    df["reviews"] = df["reviews"].apply(lambda x: str(x))  # Convert list to string for safe saving
    df["updates"] = df["updates"].apply(lambda x: str(x))
    df.to_excel(EXCEL_FILE, index=False)
  
st.session_state.pledges = load_data()

# Title with animation effect
st.title("🎯 Skill Pledge Platform")
st.subheader("Support learners by pledging small amounts to help them grow!")

# Sidebar with transitions
st.sidebar.title("Sign Up")
st.sidebar.markdown("---")
page = st.sidebar.radio("Go to", ["Investor Dashboard", "Student Support", "Student Reviews", "Student Updates"], help="Select a page")

if page == "Investor Dashboard":
    st.header("💰 Investor Sign Up")
    investor_name = st.text_input("Your Name")
    investor_email = st.text_input("Your Email")
    
    st.header("📢 Browse & Support Students")
    for pledge in st.session_state.pledges:
        with st.expander(f"📌 {pledge['name']} - {pledge['skill']}"):
            st.markdown(f"**Funding Needed:** ${pledge['amount']}")
            st.markdown(f"**Supporters Get:** {pledge['reward']}")
            
            min_amount = int(pledge['amount'].replace("$", "").strip())
            amount_supported = st.number_input(f"Pledge Amount for {pledge['name']}", min_value=min_amount, step=1, key=pledge['name'])
            
            if st.button(f"💵 Support {pledge['name']}", key=f"support_{pledge['name']}"):
                with st.spinner("Processing..."):
                    time.sleep(1.5)
                st.success(f"✅ Thank you {investor_name} for supporting {pledge['name']} with ${amount_supported}!")
            
            # Investor Review Section
            st.subheader(f"💬 Leave a Review for {pledge['name']}")
            rating = st.slider(f"Rating for {pledge['name']}", 1, 5, 3)
            review_text = st.text_area(f"Write your review for {pledge['name']}")
            if st.button(f"📝 Submit Review for {pledge['name']}"):
                pledge['reviews'].append({"rating": rating, "review": review_text})
                save_data(st.session_state.pledges)
                st.success(f"✅ Review submitted for {pledge['name']}!")
            st.markdown("---")

elif page == "Student Support":
    st.header("🙌 Apply for Skill Pledge")
    student_name = st.text_input("Your Name")
    skill = st.text_input("Skill You Want to Learn")
    amount_needed = st.text_input("Funding Required ($)")
    reward = st.text_area("What Do Supporters Get in Return?")
    
    if st.button("🚀 Submit Pledge"):
        with st.spinner("Submitting..."):
            time.sleep(1.5)
        new_pledge = {"name": student_name, "skill": skill, "amount": amount_needed, "reward": reward, "reviews": [], "updates": []}
        st.session_state.pledges.append(new_pledge)
        save_data(st.session_state.pledges)
        st.success("✅ Pledge submitted successfully!")

elif page == "Student Reviews":
    st.header("📊 Student Reviews")
    st.subheader("See how students are performing based on investor feedback.")
    
    if st.session_state.pledges:
        for pledge in st.session_state.pledges:
            reviews = pledge.get("reviews", [])
            if reviews:
                ratings = [r["rating"] for r in reviews]
                rating_counts = {rating: ratings.count(rating) for rating in range(1, 6)}
                
                st.subheader(f"{pledge['name']} - {pledge['skill']}")
                
                fig, ax = plt.subplots()
                bars = ax.bar(rating_counts.keys(), rating_counts.values(), 
                              color=['red' if r < 3 else 'green' for r in rating_counts.keys()])
                
                ax.set_xlabel("Ratings")
                ax.set_ylabel("Number of Ratings")
                ax.set_xticks(range(1, 6))
                ax.set_ylim(0, max(rating_counts.values(), default=1))
                
                st.pyplot(fig)
                
                for review in reviews:
                    st.write(f"⭐ {review['rating']}/5 - {review['review']}")
                st.markdown("---")

elif page == "Student Updates":
    st.header("📢 Post Your Learning Updates")
    student_name = st.text_input("Enter Your Name")
    update_text = st.text_area("Write your update")
    uploaded_image = st.file_uploader("📷 Upload an image (optional)", type=["png", "jpg", "jpeg"])
    uploaded_video = st.file_uploader("🎥 Upload a video (optional)", type=["mp4", "mov", "avi"])
    uploaded_file = st.file_uploader("📎 Attach a file (optional)", type=["pdf", "docx", "txt"])
    
    if st.button("🚀 Submit Update"):
        with st.spinner("Uploading..."):
            time.sleep(1.5)
        for pledge in st.session_state.pledges:
            if pledge['name'] == student_name:
                update_entry = {"text": update_text, "image": None, "video": None, "file": None}
                pledge['updates'].append(update_entry)
                save_data(st.session_state.pledges)
                st.success("✅ Update posted successfully!")
                break
        else:
            st.error("⚠️ No matching pledge found. Make sure you are registered.")
