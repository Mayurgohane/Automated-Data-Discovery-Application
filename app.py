import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import skew, kurtosis
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
    st.session_state.data_types = pd.DataFrame({"Data Type": st.session_state.df.dtypes.astype(str), "Unique Values": st.session_state.df.nunique()})
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

    # Pairplot for Numerical Columns
    st.write("## Pairplot for Numerical Variables")
    numerical_df = st.session_state.df.select_dtypes(include=['float64', 'int64'])
    if not numerical_df.empty:
        fig = sns.pairplot(numerical_df)
        plt.savefig("pairplot.png")
        st.pyplot(fig)

    # Skewness and Kurtosis
    st.write("## Skewness and Kurtosis")
    skew_kurt_df = pd.DataFrame({
        "Skewness": numerical_df.apply(lambda x: skew(x.dropna())),
        "Kurtosis": numerical_df.apply(lambda x: kurtosis(x.dropna()))
    })
    st.write(skew_kurt_df)

    # Distribution of Target Variable
    target_column = st.selectbox("Select a target column (if applicable) for distribution analysis", st.session_state.df.columns)
    if target_column:
        st.write(f"## Distribution of Target Variable: {target_column}")
        fig, ax = plt.subplots()
        sns.histplot(st.session_state.df[target_column], kde=True, ax=ax)
        st.pyplot(fig)

    # Box Plot of All Numerical Columns
    st.write("## Box Plot of All Numerical Columns")
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.boxplot(data=numerical_df, orient="h")
    plt.savefig("boxplot_all_numerical.png")
    st.pyplot(fig)

    # Count Plot for Categorical Variables
    st.write("## Count Plot for Categorical Variables")
    categorical_columns = st.session_state.df.select_dtypes(include=['object', 'category']).columns
    for col in categorical_columns:
        st.write(f"### Count Plot for {col}")
        fig, ax = plt.subplots()
        sns.countplot(y=st.session_state.df[col], order=st.session_state.df[col].value_counts().index, ax=ax)
        st.pyplot(fig)

    # Correlation Heatmap
    st.session_state.numerical_df = numerical_df  # Store numerical_df in session state
    if st.session_state.numerical_df.shape[1] > 1:
        st.write("## Correlation Heatmap")
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(st.session_state.numerical_df.corr(), annot=True, cmap="coolwarm", ax=ax)
        plt.savefig("correlation_heatmap.png")
        st.pyplot(fig)
    else:
        st.write("Not enough numerical columns for a correlation heatmap.")

# PDF Generation Function (no changes needed for new features in PDF)
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
    if "numerical_df" in st.session_state and st.session_state.numerical_df.shape[1] > 1:
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
