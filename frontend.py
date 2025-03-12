import streamlit as st
import requests

# FastAPI backend URL
BASE_URL = "http://127.0.0.1:8000"

st.title("📄 PDF to Markdown Converter & Summarizer")

# Upload PDF
st.header("Upload a PDF")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    st.write("Uploading and processing...")
    files = {"file": uploaded_file.getvalue()}
    response = requests.post(f"{BASE_URL}/upload_pdf/", files=files)
    
    if response.status_code == 200:
        st.success("File processed successfully!")
        st.write("Markdown File URL:", response.json().get("gcs_url"))
    else:
        st.error("Failed to process file.")

# List files in GCS
st.header("Available Markdown Files")
list_response = requests.get(f"{BASE_URL}/list_files/")
if list_response.status_code == 200:
    files_list = list_response.json().get("files", [])
    selected_file = st.selectbox("Select a file", files_list)
else:
    st.error("Failed to fetch files from storage.")

# View file content
if st.button("View File Content"):
    if selected_file:
        file_response = requests.get(f"{BASE_URL}/get_file/{selected_file}")
        if file_response.status_code == 200:
            st.subheader("File Content")
            file_content = file_response.json().get("content")
            st.text_area("Markdown Content", file_content, height=300)
        else:
            st.error("Failed to fetch file content.")

# Select summarization model
st.header("Summarization")
model_options = ["gpt", "gemini"]
selected_model = st.selectbox("Choose a Summarization Model", model_options)

# Summarize file
if st.button("Summarize File"):
    if selected_file:
        file_response = requests.get(f"{BASE_URL}/get_file/{selected_file}")
        if file_response.status_code == 200:
            file_content = file_response.json().get("content")

            if file_content:
                summarize_payload = {"content": file_content, "model": selected_model}
                summarize_response = requests.post(f"{BASE_URL}/summarize_file/", json=summarize_payload)

                if summarize_response.status_code == 200:
                    st.subheader("Summarized Text")
                    st.text_area("Summary", summarize_response.json().get("summary"), height=200)
                else:
                    st.error("Failed to summarize file.")
            else:
                st.error("File content is empty.")
        else:
            st.error("Failed to fetch file content.")

# Download file
if st.button("Download File"):
    if selected_file:
        download_response = requests.get(f"{BASE_URL}/download_file/{selected_file}", stream=True)
        if download_response.status_code == 200:
            st.download_button(
                label="Click to Download",
                data=download_response.content,
                file_name=selected_file.split("/")[-1],
                mime="text/markdown"
            )
        else:
            st.error("Failed to download file.")
