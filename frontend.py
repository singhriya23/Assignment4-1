import streamlit as st
import requests

# FastAPI Backend URL
FASTAPI_URL = "http://127.0.0.1:8000"

st.title("📄 PDF Processing & Q/A Service")

# Sidebar navigation
option = st.sidebar.radio("Choose an action:", ["📂 List PDFs in GCS", "📤 Upload & Parse PDF", "📜 Parse GCS PDF"])

# ✅ List PDFs in GCS
if option == "📂 List PDFs in GCS":
    st.subheader("🗂 List PDF Files from GCS")

    if st.button("🔄 Refresh List"):
        response = requests.get(f"{FASTAPI_URL}/list_pdf_files")
        
        if response.status_code == 200:
            files = response.json().get("files", [])
            if files:
                st.write("### Available PDFs in GCS:")
                for file in files:
                    st.write(f"📄 {file}")
            else:
                st.warning("No PDFs found in GCS.")
        else:
            st.error("❌ Failed to fetch PDF list.")

# ✅ Upload & Parse a PDF
if option == "📤 Upload & Parse PDF":
    st.subheader("📤 Upload a PDF File for Parsing")

    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    # Select the parsing method
    parse_method = st.selectbox(
        "Select Parsing Method",
        ["pymupdf", "mistral", "docling"],
        index=0
    )

    if uploaded_file is not None:
        file_name = uploaded_file.name  # Retain the original file name

        if st.button("🚀 Upload & Parse"):
            # Prepare the file upload
            files = {
                "file": (file_name, uploaded_file.getvalue(), "application/pdf")
            }
            
            # Include the parse method as a query parameter
            response = requests.post(
                f"{FASTAPI_URL}/upload_and_parse_pdf/?parse_method={parse_method}",
                files=files
            )

            if response.status_code == 200:
                markdown_content = response.json().get("markdown_content", "")
                st.success(f"✅ File **{file_name}** parsed successfully using **{parse_method}**!")
                st.subheader("📜 Extracted Markdown Content:")
                st.markdown(markdown_content)
            else:
                st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")

# ✅ Parse a Selected PDF from GCS
elif option == "📜 Parse GCS PDF":
    st.subheader("📜 Select a PDF from GCS for Parsing")

    # Fetch the list of files from the FastAPI endpoint
    response = requests.get(f"{FASTAPI_URL}/list_pdf_files")
    
    if response.status_code == 200:
        files = response.json().get("files", [])
        
        if files:
            # Let the user select a file from the list
            selected_file = st.selectbox("Choose a PDF file:", files)

            # Select the parsing method
            parse_method = st.selectbox(
                "Select Parsing Method",
                ["pymupdf", "mistral", "docling"],
                index=0
            )

            if selected_file and st.button("🚀 Parse Selected PDF"):
                # Request to parse the selected file from GCS with the selected parse method
                response = requests.get(
                    f"{FASTAPI_URL}/parse_gcs_pdf",
                    params={"file_name": selected_file, "parse_method": parse_method}
                )

                if response.status_code == 200:
                    # If parsing is successful, display the extracted markdown content
                    markdown_content = response.json().get("markdown_content", "")
                    st.success(f"✅ File **{selected_file}** parsed successfully using **{parse_method}**!")
                    st.subheader("📜 Extracted Markdown Content:")
                    st.markdown(markdown_content)
                else:
                    # Show error if something went wrong with parsing
                    st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
        else:
            st.warning("❌ No PDF files available for parsing.")
    else:
        # Show an error if the list of PDFs cannot be fetched
        st.error("❌ Failed to fetch PDF list.")