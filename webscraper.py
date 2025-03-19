import os
import requests
import asyncio
from dotenv import load_dotenv
from google.cloud import storage  # Google Cloud Storage SDK
from playwright.async_api import async_playwright

# Load Google Cloud credentials from .env file
load_dotenv()

# NVIDIA Financial Reports Page
URL = "https://investor.nvidia.com/financial-info/financial-reports/default.aspx"

# Updated Google Cloud Storage Details
GCS_BUCKET_NAME = "pdfstorage_1"  # New GCS bucket
GCS_FOLDER_NAME = "pdf_files"     # New folder inside the bucket

# Initialize Google Cloud Storage Client
storage_client = storage.Client()

async def get_pdf_links():
    """Extracts 10-Q and 10-K PDF links from NVIDIA's financial page using Playwright."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Debug mode enabled
        page = await browser.new_page()

        print("🚀 Loading webpage...")
        await page.goto(URL, timeout=90000)
        await page.wait_for_load_state("networkidle")  # Ensure page loads completely

        print("🔍 Extracting all links on page...")
        all_links = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll("a")).map(a => ({
                text: a.innerText,
                href: a.href
            }));
        }''')

        # Filter only 10-Q and 10-K PDFs
        pdf_links = [link["href"] for link in all_links if ".pdf" in link["href"] and ("10-Q" in link["text"] or "10-K" in link["text"])]

        await browser.close()

    return pdf_links

async def download_and_upload_pdfs(pdf_links):
    """Downloads PDFs and uploads them to Google Cloud Storage (GCS)."""
    bucket = storage_client.bucket(GCS_BUCKET_NAME)

    for pdf_url in pdf_links:
        pdf_name = pdf_url.split("/")[-1]

        print(f"📥 Downloading {pdf_name}...")
        response = requests.get(pdf_url, stream=True)
        if response.status_code == 200:
            # Upload to GCS
            blob = bucket.blob(f"{GCS_FOLDER_NAME}/{pdf_name}")
            blob.upload_from_string(response.content, content_type="application/pdf")
            
            print(f"✅ Uploaded {pdf_name} to GCS: gs://{GCS_BUCKET_NAME}/{GCS_FOLDER_NAME}/{pdf_name}")
        else:
            print(f"❌ Failed to download {pdf_url}")

async def main():
    pdf_links = await get_pdf_links()
    if pdf_links:
        print(f"✅ Found {len(pdf_links)} PDF links. Uploading to GCS...")
        await download_and_upload_pdfs(pdf_links)
    else:
        print("❌ No PDFs found.")

# Run the scraper
asyncio.run(main())
