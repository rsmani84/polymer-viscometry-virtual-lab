import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
    ["Aim & Theory", "Experiment", "Quiz"]
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

    # Empty observation table
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

    # Check blank cells
    if data["Concentration (g/dL)"].astype(str).str.strip().eq("").any():
        valid = False
        error_messages.append("Please enter all concentration values.")

    if data["Flow Time (s)"].astype(str).str.strip().eq("").any():
        valid = False
        error_messages.append("Please enter all flow time values.")

    # Convert to numeric only if not blank
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
    # CALCULATE BUTTON
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

            # Calculations
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

            pdf_file = f"{student_name.replace(' ', '_')}_Viscometry_Report.pdf"

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

    score = 0

    q1 = st.radio(
        "1. What is relative viscosity (ηr)?",
        [
            "t₀ / t",
            "t / t₀",
            "ηsp / C",
            "KMa"
        ]
    )

    q2 = st.radio(
        "2. What is obtained from the intercept of reduced viscosity vs concentration graph?",
        [
            "Flow time",
            "Specific viscosity",
            "Intrinsic viscosity",
            "Polymer density"
        ]
    )

    q3 = st.radio(
        "3. Which equation is used to estimate molecular weight?",
        [
            "Arrhenius equation",
            "Beer-Lambert law",
            "Mark–Houwink equation",
            "Nernst equation"
        ]
    )

    if st.button("Submit Quiz"):
        if q1 == "t / t₀":
            score += 1
        if q2 == "Intrinsic viscosity":
            score += 1
        if q3 == "Mark–Houwink equation":
            score += 1

        st.success(f"✅ Your Score: {score}/3")

        if score == 3:
            st.balloons()
            st.write("Excellent! You understood the experiment very well.")
        elif score == 2:
            st.write("Good job! Review the theory once more for full clarity.")
        else:
            st.write("Please revise the theory section and try again.")
