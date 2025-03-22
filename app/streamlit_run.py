import json

import requests
import streamlit as st

from app.config.settings import Settings

setttings = Settings()


# FastAPI backend URL
FASTAPI_URL = f"http://{setttings.FASTAPI_HOST}:{setttings.FASTAPI_PORT}"  # Update this if your FastAPI server is hosted elsewhere

# Streamlit App Title
st.title("PDF Question Answering System")

# Sidebar for PDF Upload
st.sidebar.header("Upload PDF")
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Send the file to the FastAPI backend
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
    response = requests.post(
        f"{FASTAPI_URL}/upload-pdf",
        files=files,
    )

    if response.status_code == 200:
        st.sidebar.success("PDF uploaded and indexed successfully!")
    else:
        st.sidebar.error(
            f"Failed to upload PDF: {response.json().get('detail', 'Unknown error')}"
        )

# Main section for asking questions
st.header("Ask Questions")
questions = st.text_area(
    "Enter your questions (one per line)",
    height=150,
    help="Type one question per line.",
)

if st.button("Get Answers"):
    if not questions:
        st.warning("Please enter at least one question.")
    else:
        # Split questions into a list
        question_list = [q.strip() for q in questions.split("\n") if q.strip()]

        # Send questions to FastAPI backend
        response = requests.post(
            f"{FASTAPI_URL}/ask",
            json={"questions": question_list},
        )

        if response.status_code == 200:
            answers = response.json()
            st.subheader("Answers")

            for elem in answers:
                st.write(f"**Q:** {elem.get('question', '')}")
                st.write(f"**A:** {elem.get('answer', '')}")
                st.write("---")

            # Option to download answers as JSON
            st.download_button(
                label="Download Answers as JSON",
                data=json.dumps(answers, indent=4),
                file_name="answers.json",
                mime="application/json",
            )
        else:
            st.error(
                f"Failed to get answers: {response.json().get('detail', 'Unknown error')}"
            )
