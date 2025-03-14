# Assignment4-1
Overview
This is an extension to the first assignment wherein we use Large Language Models to Summarize the previously parsed document. Also, we have the feature to ask questions about the document. This is done by using RAG methodology.

Contribution
Kaushik - Deepseek, Claude Models (Summarization and QA), Diagrams.
Arvind - GPT-4o-mini, Gemini, Groq Models(Summarization and QA), Codelabs, Sample POCS for frontend and backend
Riya - Frontend, Backend and Deployment.

Codelabs - https://docs.google.com/document/d/1MiDw0Wc_P5yULQMNc03unchqYNCEI25uHvXQqc18LRQ/edit?tab=t.0#heading=h.31ankfht5pc0

Architecture
![WhatsApp Image 2025-03-14 at 10 29 16 AM](https://github.com/user-attachments/assets/ba486e58-4c1d-4f50-874e-b2daed6b6b2a)

First, the user uploads PDF and it is then parsed and converted to markdown.
It is then stored in google buckets.
We then create an API Endpoint pointing to summarization engine, which lets you choose different models.
Finally, the endpoint is deployed on the cloud using docker.



Folders.
POC - Contains some samples of Gemini and Gpt Models and some frontend,backend POCs
Backend - Contains the Backend and deployment files.
Frontend.py - the final frontend code.


