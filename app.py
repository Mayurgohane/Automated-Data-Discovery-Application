import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import os

# Set up Streamlit page
st.title("Enhanced Automated Data Discovery Application")
st.write("Upload a CSV or Excel file to start exploring your data.")

# File upload
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

# Add a Submit button to start the analysis
if uploaded_file and st.button("Submit"):
    # Read the uploaded file and store it in session state
    if uploaded_file.name.endswith(".csv"):
        st.session_state.df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xlsx"):
        st.session_state.df = pd.read_excel(uploaded_file)

    # Store other calculated data in session state
    st.session_state.data_types = pd.DataFrame({"Data Type": st.session_state.df.dtypes, "Unique Values": st.session_state.df.nunique()})
    st.session_state.missing_values = st.session_state.df.isnull().sum()

    # Display data preview
    st.write("## Data Preview")
    st.dataframe(st.session_state.df.head())

    # Data Types and Unique Counts
    st.write("## Data Types and Unique Counts")
    st.write(st.session_state.data_types)

    # Basic Statistics
    st.write("## Basic Statistics")
    st.write(st.session_state.df.describe())

    # Missing Values
    st.write("## Missing Values")
    st.write(st.session_state.missing_values[st.session_state.missing_values > 0])

    # Visual representation of missing data
    if st.session_state.missing_values.sum() > 0:
        st.write("### Missing Values Heatmap")
        fig, ax = plt.subplots()
        sns.heatmap(st.session_state.df.isnull(), cbar=False, cmap="viridis")
        plt.savefig("missing_values_heatmap.png")
        st.pyplot(fig)

    # Outlier Detection with Box Plot
    st.write("## Outlier Detection (Box Plot)")
    numerical_columns = st.session_state.df.select_dtypes(include=['float64', 'int64']).columns
    selected_boxplot_column = st.selectbox("Select a column for box plot", numerical_columns)
    if selected_boxplot_column:
        st.write(f"### Box Plot for {selected_boxplot_column}")
        fig, ax = plt.subplots()
        sns.boxplot(x=st.session_state.df[selected_boxplot_column], ax=ax)
        plt.savefig("boxplot.png")
        st.pyplot(fig)

    # Histograms for Numerical Data
    st.write("## Histograms for Numerical Data")
    selected_hist_column = st.selectbox("Select a column for histogram", numerical_columns)
    if selected_hist_column:
        st.write(f"### Histogram for {selected_hist_column}")
        fig, ax = plt.subplots()
        sns.histplot(st.session_state.df[selected_hist_column], kde=True, ax=ax)
        plt.savefig("histogram.png")
        st.pyplot(fig)

    # Categorical Column Analysis
    st.write("## Categorical Column Analysis")
    categorical_columns = st.session_state.df.select_dtypes(include=['object', 'category']).columns
    selected_cat_column = st.selectbox("Select a categorical column for analysis", categorical_columns)
    if selected_cat_column:
        st.write(f"### Count Plot for {selected_cat_column}")
        fig, ax = plt.subplots()
        sns.countplot(y=st.session_state.df[selected_cat_column], order=st.session_state.df[selected_cat_column].value_counts().index, ax=ax)
        plt.savefig("countplot.png")
        st.pyplot(fig)

    # Correlation Heatmap
    numerical_df = st.session_state.df.select_dtypes(include=['float64', 'int64'])  # Filter only numerical columns
    if not numerical_df.empty and numerical_df.shape[1] > 1:  # Check if there are at least two numerical columns
        st.write("## Correlation Heatmap")
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(numerical_df.corr(), annot=True, cmap="coolwarm", ax=ax)
        plt.savefig("correlation_heatmap.png")
        st.pyplot(fig)
    else:
        st.write("Not enough numerical columns for a correlation heatmap.")

# PDF Generation Function
def generate_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Enhanced Data Discovery Report")

    # Data Types and Unique Counts
    c.setFont("Helvetica", 12)
    c.drawString(30, 720, "Data Types and Unique Counts:")
    data_types_text = st.session_state.data_types.to_string()
    text_object = c.beginText(30, 700)
    text_object.setFont("Helvetica", 10)
    for line in data_types_text.splitlines():
        text_object.textLine(line)
    c.drawText(text_object)

    # Basic Statistics
    c.drawString(30, 580, "Basic Statistics:")
    stats_text = st.session_state.df.describe().to_string()
    text_object = c.beginText(30, 560)
    text_object.setFont("Helvetica", 10)
    for line in stats_text.splitlines():
        text_object.textLine(line)
    c.drawText(text_object)

    # Missing Values
    if st.session_state.missing_values.sum() > 0:
        c.drawString(30, 440, "Missing Values:")
        missing_text = st.session_state.missing_values[st.session_state.missing_values > 0].to_string()
        text_object = c.beginText(30, 420)
        text_object.setFont("Helvetica", 10)
        for line in missing_text.splitlines():
            text_object.textLine(line)
        c.drawText(text_object)
        c.drawImage("missing_values_heatmap.png", 100, 250, width=400, height=150)

    # Correlation Heatmap
    if not numerical_df.empty and numerical_df.shape[1] > 1:
        c.drawString(30, 120, "Correlation Heatmap:")
        c.drawImage("correlation_heatmap.png", 100, 20, width=400, height=100)

    c.save()
    buffer.seek(0)
    return buffer

# Download PDF button
if "df" in st.session_state and st.button("Download Enhanced EDA Report as PDF"):
    pdf = generate_pdf()
    st.download_button(
        label="Download EDA Report",
        data=pdf.getvalue(),
        file_name="Enhanced_EDA_Report.pdf",
        mime="application/pdf"
    )

else:
    st.info("Please upload a file and click Submit to begin the analysis.")
