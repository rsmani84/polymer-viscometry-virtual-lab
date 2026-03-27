import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
)
from reportlab.lib import styles
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
import os
from datetime import datetime

# ------------------------------
# PAGE CONFIG
# ------------------------------
st.set_page_config(
    page_title="Virtual Lab - Polymer Viscometry",
    page_icon="🧪",
    layout="wide"
)

# ------------------------------
# MARK-HOUWINK DATABASE
# ------------------------------
mark_houwink = {
    "Polystyrene": {"K": 1.1e-4, "a": 0.73},
    "PMMA": {"K": 5.5e-4, "a": 0.76},
    "PVC": {"K": 6.3e-4, "a": 0.62},
    "Polyvinyl Alcohol (PVA)": {"K": 3.7e-4, "a": 0.65},
    "Polyethylene Oxide (PEO)": {"K": 6.4e-4, "a": 0.65},
}

# ------------------------------
# FEEDBACK FILE
# ------------------------------
feedback_file = "feedback_log.csv"

def initialize_feedback_file():
    if not os.path.exists(feedback_file):
        with open(feedback_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Register Number", "Rating", "Feedback", "Suggestion", "DateTime"])

def save_feedback(name, reg_no, rating, feedback_text, suggestion):
    with open(feedback_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            name,
            reg_no,
            rating,
            feedback_text,
            suggestion,
            datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        ])

initialize_feedback_file()

# ------------------------------
# HEADER
# ------------------------------
st.title("🧪 Virtual Lab: Molecular Weight Determination of Polymer using Viscometry")
st.markdown("---")

# ------------------------------
# SIDEBAR
# ------------------------------
st.sidebar.title("📚 Virtual Lab Sections")
section = st.sidebar.radio(
    "Go to:",
    ["Aim & Theory", "Experiment", "Quiz", "Feedback"]
)

# ------------------------------
# SECTION 1: AIM & THEORY
# ------------------------------
if section == "Aim & Theory":
    st.header("🎯 Aim")
    st.write("""
    To determine the intrinsic viscosity and molecular weight of a polymer
    using viscometric data and the Mark–Houwink equation.
    """)

    st.header("📖 Theory")
    st.write("""
    In polymer chemistry, viscosity measurements are used to estimate the
    molecular weight of polymers in solution.

    The following relationships are used:
    """)

    st.latex(r"\eta_r = \frac{t}{t_0}")
    st.write("**Relative viscosity (ηr):** Ratio of solution flow time to solvent flow time.")

    st.latex(r"\eta_{sp} = \eta_r - 1")
    st.write("**Specific viscosity (ηsp):** Increase in viscosity due to polymer.")

    st.latex(r"\frac{\eta_{sp}}{C}")
    st.write("**Reduced viscosity:** Specific viscosity normalized by concentration.")

    st.latex(r"[\eta] = K M^a")
    st.write("**Mark–Houwink equation:** Used to calculate molecular weight from intrinsic viscosity.")

    st.subheader("🔍 Interpretation of α (alpha)")
    st.write("""
    - **α ≈ 0.5** → Random coil polymer chain  
    - **α > 0.5** → Expanded polymer chain  
    - **α ≈ 1** → Rigid rod-like chain
    """)

    st.info("👉 Go to the **Experiment** section from the sidebar to perform the virtual lab.")

# ------------------------------
# SECTION 2: EXPERIMENT
# ------------------------------
elif section == "Experiment":
    st.header("🧪 Perform the Experiment")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👨‍🎓 Student Details")
        student_name = st.text_input("Enter Student Name")
        reg_no = st.text_input("Enter Register Number")
        department = st.text_input("Enter Department / Class", value="B.Tech / Chemistry")

    with col2:
        st.subheader("⚗ Experiment Details")
        polymer_name = st.selectbox("Select Polymer", list(mark_houwink.keys()))
        t0 = st.number_input("Enter Solvent Flow Time t₀ (s)", min_value=0.001, value=100.0, step=0.1)
        n = st.number_input("Enter Number of Readings", min_value=2, max_value=10, value=5, step=1)

    st.markdown("---")
    st.subheader("📝 Observation Table")

    # Blank observation table
    default_data = pd.DataFrame({
        "Concentration (g/dL)": [""] * int(n),
        "Flow Time (s)": [""] * int(n)
    })

    data = st.data_editor(
        default_data,
        num_rows="fixed",
        use_container_width=True,
        key="data_editor"
    )

    # ------------------------------
    # VALIDATION
    # ------------------------------
    valid = True
    error_messages = []

    if student_name.strip() == "":
        valid = False
        error_messages.append("Student name is required.")

    if reg_no.strip() == "":
        valid = False
        error_messages.append("Register number is required.")

    if data["Concentration (g/dL)"].astype(str).str.strip().eq("").any():
        valid = False
        error_messages.append("Please enter all concentration values.")

    if data["Flow Time (s)"].astype(str).str.strip().eq("").any():
        valid = False
        error_messages.append("Please enter all flow time values.")

    if valid:
        try:
            data["Concentration (g/dL)"] = pd.to_numeric(data["Concentration (g/dL)"])
            data["Flow Time (s)"] = pd.to_numeric(data["Flow Time (s)"])
        except:
            valid = False
            error_messages.append("Please enter only numeric values in the observation table.")

    if valid:
        if (data["Concentration (g/dL)"] <= 0).any():
            valid = False
            error_messages.append("All concentration values must be greater than zero.")

        if (data["Flow Time (s)"] <= 0).any():
            valid = False
            error_messages.append("All flow time values must be greater than zero.")

    # ------------------------------
    # RUN EXPERIMENT
    # ------------------------------
    if st.button("🚀 Run Experiment"):
        if not valid:
            for msg in error_messages:
                st.error(msg)
        else:
            concentration = data["Concentration (g/dL)"].to_numpy(dtype=float)
            flow_time = data["Flow Time (s)"].to_numpy(dtype=float)

            K = mark_houwink[polymer_name]["K"]
            a = mark_houwink[polymer_name]["a"]

            rel = flow_time / t0
            spec = rel - 1
            red = spec / concentration

            coeffs = np.polyfit(concentration, red, 1)
            intrinsic = coeffs[1]
            Mv = (intrinsic / K) ** (1 / a) if intrinsic > 0 else np.nan

            result_df = pd.DataFrame({
                "Concentration": np.round(concentration, 4),
                "Flow Time": np.round(flow_time, 4),
                "Relative Viscosity (ηr)": np.round(rel, 4),
                "Specific Viscosity (ηsp)": np.round(spec, 4),
                "Reduced Viscosity (ηsp/C)": np.round(red, 4),
            })

            st.success("✅ Experiment completed successfully!")

            st.subheader("📊 Calculated Observation Table")
            st.dataframe(result_df, use_container_width=True)

            # Graph
            st.subheader("📈 Graph: Reduced Viscosity vs Concentration")

            fig, ax = plt.subplots(figsize=(8, 5))
            ax.plot(concentration, red, 'o', label="Experimental Data")
            ax.plot(concentration, np.polyval(coeffs, concentration), '-', label="Best Fit")
            ax.set_xlabel("Concentration (g/dL)")
            ax.set_ylabel("Reduced Viscosity (ηsp/C)")
            ax.set_title(f"{polymer_name}")
            ax.grid(True)
            ax.legend()

            graph_file = "graph.png"
            fig.savefig(graph_file, bbox_inches="tight")
            st.pyplot(fig)
            plt.close(fig)

            # Results
            st.subheader("📌 Final Results")

            r1, r2, r3 = st.columns(3)
            r1.metric("Intrinsic Viscosity [η]", f"{intrinsic:.4f}")
            r2.metric("K Value", f"{K}")
            r3.metric("α Value", f"{a}")

            if np.isnan(Mv):
                st.warning("⚠ Molecular weight could not be calculated because intrinsic viscosity is not positive.")
            else:
                st.metric("Molecular Weight (Mv)", f"{Mv:.2f}")

            # Interpretation
            st.subheader("🧠 Interpretation")
            if intrinsic > 0:
                st.write(f"""
                - The **intrinsic viscosity** of **{polymer_name}** is **{intrinsic:.4f}**.
                - Based on the Mark–Houwink constants, the estimated **molecular weight** is **{Mv:.2f}**.
                - Since **α = {a}**, this polymer likely shows an **expanded/random coil behavior in solution**.
                """)
            else:
                st.write("""
                The intrinsic viscosity is not positive, so the molecular weight estimation may not be valid.
                Please verify your experimental readings.
                """)

            # PDF REPORT
            st.subheader("📄 Download Experiment Report")

            safe_name = student_name.replace(" ", "_") if student_name.strip() else "Student"
            pdf_file = f"{safe_name}_Viscometry_Report.pdf"

            doc = SimpleDocTemplate(pdf_file, pagesize=letter)
            style = styles.getSampleStyleSheet()

            center_style = ParagraphStyle(name='Center', alignment=TA_CENTER)
            justify_style = ParagraphStyle(
                name='Justify',
                alignment=TA_JUSTIFY,
                fontName='Helvetica-Bold',
                fontSize=10,
                leading=14
            )

            content = []

            content.append(Paragraph(
                "<b>SRM Institute of Science and Technology, Tiruchirappalli</b>",
                center_style
            ))
            content.append(Spacer(1, 10))
            content.append(Paragraph("<b>Faculty of Engineering and Technology</b>", center_style))
            content.append(Paragraph("<b>Department of Chemistry</b>", center_style))
            content.append(Spacer(1, 15))

            content.append(Paragraph(
                "<b>MOLECULAR WEIGHT DETERMINATION OF POLYMER USING VISCOMETRY</b>",
                style['Heading1']
            ))
            content.append(Spacer(1, 20))

            content.append(Paragraph(f"<b>Name:</b> {student_name}", style['Normal']))
            content.append(Paragraph(f"<b>Register Number:</b> {reg_no}", style['Normal']))
            content.append(Paragraph(f"<b>Department/Class:</b> {department}", style['Normal']))
            content.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d-%m-%Y %H:%M')}", style['Normal']))
            content.append(Spacer(1, 10))

            content.append(Paragraph("<b>Experiment Details</b>", style['Heading2']))
            content.append(Paragraph(f"Polymer: {polymer_name}", style['Normal']))
            content.append(Paragraph(f"Solvent flow time (t₀): {t0} s", style['Normal']))
            content.append(Spacer(1, 10))

            table_data = [["Conc", "Flow time", "Rel", "Spec", "Red"]]
            for i in range(len(concentration)):
                table_data.append([
                    f"{concentration[i]:.3f}",
                    f"{flow_time[i]:.3f}",
                    f"{rel[i]:.3f}",
                    f"{spec[i]:.3f}",
                    f"{red[i]:.3f}"
                ])

            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ]))
            content.append(table)
            content.append(Spacer(1, 15))

            content.append(Paragraph("<b>Theory & Formula</b>", style['Heading2']))
            content.append(Paragraph("<b>Relative viscosity (ηr = t / t₀):</b> Ratio of solution flow time to solvent flow time.", style['Normal']))
            content.append(Paragraph("<b>Specific viscosity (ηsp = ηr − 1):</b> Increase in viscosity due to polymer.", style['Normal']))
            content.append(Paragraph("<b>Reduced viscosity (ηsp / C):</b> Normalized viscosity with concentration.", style['Normal']))
            content.append(Paragraph("<b>Intrinsic viscosity [η]:</b> Obtained from graph intercept at zero concentration.", style['Normal']))
            content.append(Paragraph("<b>Mark–Houwink Equation:</b> [η] = K Mᵃ", style['Normal']))
            content.append(Spacer(1, 15))

            content.append(Paragraph("<b>Results</b>", style['Heading2']))
            content.append(Paragraph(f"Intrinsic viscosity = {intrinsic:.4f}", style['Normal']))
            content.append(Paragraph(f"K = {K}, α = {a}", style['Normal']))
            if not np.isnan(Mv):
                content.append(Paragraph(f"Molecular Weight (Mv) = {Mv:.2f}", style['Normal']))
            else:
                content.append(Paragraph("Molecular Weight (Mv) could not be calculated.", style['Normal']))

            content.append(Spacer(1, 15))

            content.append(Paragraph(
                "This experiment was performed using a Virtual Lab model, which eliminates the need for physical instruments "
                "and enables students from various disciplines to understand polymer characterization through computational methods. "
                "This approach enhances visualization, improves accuracy, and introduces students to modern data-driven scientific techniques.",
                justify_style
            ))

            content.append(Spacer(1, 15))

            content.append(Paragraph("<b>Graph</b>", style['Heading2']))
            if os.path.exists(graph_file):
                content.append(Image(graph_file, width=400, height=300))

            doc.build(content)

            with open(pdf_file, "rb") as f:
                st.download_button(
                    label="📥 Download PDF Report",
                    data=f,
                    file_name=pdf_file,
                    mime="application/pdf"
                )

# ------------------------------
# SECTION 3: QUIZ
# ------------------------------
elif section == "Quiz":
    st.header("🧠 Viva / Quiz Section")
    st.write("Answer the following questions to test your understanding of polymer viscometry.")

    score = 0
    feedback = []

    q1 = st.radio(
        "1. What is relative viscosity (ηr)?",
        ["t₀ / t", "t / t₀", "ηsp / C", "KMa"],
        key="q1"
    )

    q2 = st.radio(
        "2. What is obtained from the intercept of reduced viscosity vs concentration graph?",
        ["Flow time", "Specific viscosity", "Intrinsic viscosity", "Polymer density"],
        key="q2"
    )

    q3 = st.radio(
        "3. Which equation is used to estimate molecular weight?",
        ["Arrhenius equation", "Beer-Lambert law", "Mark–Houwink equation", "Nernst equation"],
        key="q3"
    )

    q4 = st.radio(
        "4. What does specific viscosity (ηsp) represent?",
        [
            "Ratio of flow times",
            "Increase in viscosity due to polymer",
            "Polymer concentration",
            "Intrinsic viscosity"
        ],
        key="q4"
    )

    q5 = st.radio(
        "5. Which quantity is plotted on the y-axis in this experiment?",
        [
            "Flow Time",
            "Concentration",
            "Reduced Viscosity (ηsp/C)",
            "Molecular Weight"
        ],
        key="q5"
    )

    q6 = st.radio(
        "6. Which quantity is plotted on the x-axis in this experiment?",
        [
            "Reduced Viscosity",
            "Concentration",
            "Relative Viscosity",
            "Molecular Weight"
        ],
        key="q6"
    )

    q7 = st.radio(
        "7. If polymer concentration increases, the viscosity generally:",
        [
            "Decreases",
            "Increases",
            "Remains zero",
            "Becomes negative"
        ],
        key="q7"
    )

    q8 = st.radio(
        "8. What does the constant α (alpha) in the Mark–Houwink equation indicate?",
        [
            "Color of polymer",
            "Polymer chain shape in solution",
            "Temperature of solvent",
            "Density of polymer"
        ],
        key="q8"
    )

    q9 = st.radio(
        "9. Why is extrapolation to zero concentration needed?",
        [
            "To find solvent density",
            "To calculate flow time",
            "To obtain intrinsic viscosity",
            "To remove the graph"
        ],
        key="q9"
    )

    q10 = st.radio(
        "10. Which of the following is a major advantage of this virtual lab?",
        [
            "Needs expensive instruments every time",
            "Cannot generate graphs",
            "Allows computational learning without wet-lab setup",
            "Removes all chemistry concepts"
        ],
        key="q10"
    )

    if st.button("Submit Quiz"):
        answers = {
            "q1": ("t / t₀", "Relative viscosity is defined as solution flow time divided by solvent flow time."),
            "q2": ("Intrinsic viscosity", "The intercept of the reduced viscosity vs concentration graph gives intrinsic viscosity."),
            "q3": ("Mark–Houwink equation", "The Mark–Houwink equation is used to estimate molecular weight from intrinsic viscosity."),
            "q4": ("Increase in viscosity due to polymer", "Specific viscosity shows how much the polymer increases the viscosity of the solution."),
            "q5": ("Reduced Viscosity (ηsp/C)", "The y-axis represents reduced viscosity in this experiment."),
            "q6": ("Concentration", "The x-axis represents polymer concentration."),
            "q7": ("Increases", "As polymer concentration increases, solution viscosity usually increases."),
            "q8": ("Polymer chain shape in solution", "The alpha value gives information about polymer conformation in solution."),
            "q9": ("To obtain intrinsic viscosity", "Extrapolation to zero concentration is needed to determine intrinsic viscosity."),
            "q10": ("Allows computational learning without wet-lab setup", "A major benefit of the virtual lab is computational learning without depending fully on physical instruments.")
        }

        user_answers = {
            "q1": q1,
            "q2": q2,
            "q3": q3,
            "q4": q4,
            "q5": q5,
            "q6": q6,
            "q7": q7,
            "q8": q8,
            "q9": q9,
            "q10": q10
        }

        for q, (correct, explanation) in answers.items():
            if user_answers[q] == correct:
                score += 1
                feedback.append(f"✅ {q.upper()}: Correct — {explanation}")
            else:
                feedback.append(f"❌ {q.upper()}: Incorrect. Correct Answer: **{correct}** — {explanation}")

        st.success(f"🎯 Your Score: {score}/10")

        st.subheader("📌 Performance Feedback")

        if score == 10:
            st.balloons()
            st.success("Excellent! You have a very strong understanding of polymer viscometry and molecular weight determination.")
        elif score >= 8:
            st.info("Very Good! You understood most concepts well. Only minor revision is needed.")
        elif score >= 6:
            st.warning("Good attempt. You understand the basics, but some concepts need revision.")
        elif score >= 4:
            st.warning("Fair attempt. Please review the theory and graph interpretation carefully.")
        else:
            st.error("You need more revision. Go back to the Aim & Theory section and try again.")

        st.subheader("📝 Question-wise Feedback")
        for item in feedback:
            st.write(item)

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
