import os
from contextlib import asynccontextmanager
from tempfile import NamedTemporaryFile

import uvicorn
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from app.api.models import AnswerResponse, QuestionRequest
from app.config.logging_config import configure_logging
from app.config.settings import Settings
from app.core.graph.master_graph import generate_response
from app.core.vector_db import VectorStore  # Import the VectorStore class

logger = configure_logging()  # Configure logging
settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize heavy objects (e.g., VectorStore) when the app starts
    app.state.vector_store = VectorStore()
    logger.info("Initialized VectorStore.")
    yield
    # Clean up resources when the app shuts down
    logger.info("Shutting down VectorStore.")
    del app.state.vector_store


app = FastAPI(lifespan=lifespan)


def get_vector_store(request: Request):
    return request.app.state.vector_store


@app.get("/health")
def health_check():
    logger.info("Health check endpoint accessed.")
    return {"status": "ok"}


@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    vector_store: VectorStore = Depends(get_vector_store),
):
    logger.info(f"Received file upload request: {file.filename}")

    # Check if the uploaded file is a PDF
    if file.content_type != "application/pdf":
        error_msg = (
            f"Invalid file type for '{file.filename}'. Expected 'application/pdf'."
        )
        logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)

    # Save the uploaded file temporarily
    try:
        logger.info(f"Saving temporary file for '{file.filename}'...")
        with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_file_path = temp_file.name
            logger.debug(f"Temporary file saved at: {temp_file_path}")

        # Initialize VectorStore and index the PDF
        logger.info(f"Indexing PDF file: {file.filename}")
        success = vector_store.initialize_from_pdf(temp_file_path)

        # Clean up the temporary file
        logger.debug(f"Cleaning up temporary file: {temp_file_path}")
        os.unlink(temp_file_path)

        if success:
            logger.info(f"PDF file '{file.filename}' indexed successfully.")
            return JSONResponse(
                status_code=200,
                content={"message": f"PDF file '{file.filename}' indexed successfully"},
            )
        else:
            error_msg = f"Failed to index the PDF file: {file.filename}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)

    except Exception as e:
        # Clean up the temporary file in case of an error
        if "temp_file_path" in locals() and os.path.exists(temp_file_path):
            logger.debug(f"Cleaning up temporary file due to error: {temp_file_path}")
            os.unlink(temp_file_path)
        error_msg = (
            f"An error occurred while processing the file '{file.filename}': {str(e)}"
        )
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/ask", response_model=AnswerResponse)
async def ask_questions(
    body: QuestionRequest, vector_store: VectorStore = Depends(get_vector_store)
):
    questions = body.questions
    try:
        logger.info(f"Received question answering request with questions: {questions}")

        # Check if the vector store is initialized
        if not vector_store.is_initialized():
            error_msg = "No PDF has been indexed. Please upload and index a PDF first."
            logger.warning(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)

        logger.info("Generating responses for the questions...")

        result = await generate_response(questions)
        logger.info(f"Successfully generated responses for questions: {questions}")
        return JSONResponse(status_code=200, content=result)

    except ValueError as e:
        error_msg = f"ValueError occurred while processing questions: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error_msg = f"An unexpected error occurred while processing questions: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def start_server():
    logger.info(
        f"Starting FastAPI server on {settings.FASTAPI_HOST}:{settings.FASTAPI_PORT}"
    )
    uvicorn.run(
        "app.main:app",  # Path to the FastAPI app (module:app)
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
        reload=True,  # Enable auto-reload
    )


if __name__ == "__main__":
    start_server()
