import os

import chromadb
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.logging_config import configure_logging
from app.config.settings import Settings

settings = Settings()


class VectorStore:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance

    def __init__(
        self,
        model_name=settings.EMBED_MODEL_NAME,
        persist_directory=settings.PERSIST_DIR,
    ):
        """Initialize the vector store with the specified embedding model."""
        if not hasattr(self, "initialized"):  # Ensure initialization happens only once
            self.logger = configure_logging()
            self.embedding_function = HuggingFaceEmbeddings(model_name=model_name)
            self.persist_directory = persist_directory
            self.db = None
            if os.path.exists(persist_directory):
                try:
                    self.db = Chroma(
                        persist_directory=persist_directory,
                        embedding_function=self.embedding_function,
                        client_settings=chromadb.config.Settings(
                            anonymized_telemetry=False, is_persistent=True
                        ),
                    )
                    self.logger.info(
                        "[__init__] Loaded existing vector store from disk"
                    )
                except Exception as e:
                    self.logger.error(
                        f"[__init__] Error loading existing vector store: {e}"
                    )
            self.initialized = True

    def is_initialized(self) -> bool:
        """Check if the vector store is initialized."""
        return self.db is not None

    def initialize_from_pdf(
        self,
        pdf_path,
        chunk_size=settings.CHUNKING_PARAM.get("size"),
        chunk_overlap=settings.CHUNKING_PARAM.get("overlap"),
    ):
        """Initialize vector DB with PDF content."""

        self.logger.debug(f"[initialize_from_pdf] Loading PDF: {pdf_path}")
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            self.logger.debug(
                f"[initialize_from_pdf] Loaded {len(documents)} pages from PDF"
            )

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                is_separator_regex=False,
            )
            docs = text_splitter.split_documents(documents)
            self.logger.debug(f"[initialize_from_pdf] Split into {len(docs)} chunks")

            self.db = Chroma.from_documents(
                documents=docs,
                embedding=self.embedding_function,
                persist_directory=self.persist_directory,
                client_settings=chromadb.config.Settings(
                    anonymized_telemetry=False, is_persistent=True
                ),
            )
            return True  # Return True on success
        except Exception as e:
            self.logger.error(
                f"[initialize_from_pdf] Error initializing vector store: {e}"
            )
            return False  # Return False on failure
