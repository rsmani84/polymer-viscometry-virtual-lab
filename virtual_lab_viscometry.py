# (ONLY SHOWING CHANGED PARTS TO KEEP IT CLEAR)

# ------------------------------
# SIDEBAR
# ------------------------------
st.sidebar.title("📚 Virtual Lab Sections")
section = st.sidebar.radio(
    "Go to:",
    ["Aim & Theory", "Experiment", "Quiz", "Feedback"]   # ✅ ADDED Feedback
)

# ------------------------------
# SECTION 4: FEEDBACK
# ------------------------------
elif section == "Feedback":
    st.header("⭐ Student Feedback on Virtual Lab")

    st.write("Please share your feedback about this Virtual Lab experience.")

    st.markdown("---")

    fb_name = st.text_input("Enter Your Name", key="fb_name")
    fb_reg = st.text_input("Enter Register Number", key="fb_reg")

    rating = st.slider("Rate this Virtual Lab (1 = Poor, 5 = Excellent)", 1, 5, 4)

    # Star display
    st.write("### ⭐ Your Rating")
    st.write("⭐" * rating)

    feedback_text = st.text_area("What did you like about this Virtual Lab?")
    suggestion = st.text_area("Any suggestion for improvement?")

    if st.button("Submit Feedback"):
        if fb_name.strip() == "" or fb_reg.strip() == "":
            st.error("Please enter your Name and Register Number.")
        else:
            save_feedback(fb_name, fb_reg, rating, feedback_text, suggestion)
            st.success("✅ Thank you! Your feedback has been submitted successfully.")
            st.balloons()

            st.info(f"Your Rating: {'⭐' * rating}")

    st.markdown("---")

    st.subheader("📌 Why your feedback matters")
    st.write("""
    Your feedback helps improve this Virtual Lab by:
    - improving student learning experience
    - making the experiment more user-friendly
    - enhancing teaching innovation
    """)
