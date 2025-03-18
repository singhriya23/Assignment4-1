import streamlit as st
import requests

# FastAPI backend URL
BASE_URL = "http://127.0.0.1:8000"

st.title("📄 PDF to Markdown Converter, Summarizer & Q/A")

#upload file 
st.header("Upload a PDF")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    st.write("Uploading and processing...")
    
    # Ensure the filename is passed to the backend
    files = {
        "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
    }
    
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

# Select Q/A model
st.header("Ask a Question")
qa_model_options = ["gpt", "gemini"]
selected_qa_model = st.selectbox("Choose a Q/A Model", qa_model_options)

# Ask question
question = st.text_input("Enter your question")
if st.button("Get Answer"):
    if selected_file and question:
        qa_payload = {"question": question, "model": selected_qa_model}
        qa_response = requests.post(f"{BASE_URL}/ask_question/", json=qa_payload)

        if qa_response.status_code == 200:
            st.subheader("Answer")
            st.write(qa_response.json().get("answer"))
        else:
            st.error("Failed to process the question.")
    else:
        st.error("Please select a file and enter a question.")

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