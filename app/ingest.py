import os
from time import time
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_ollama import OllamaEmbeddings
from pinecone import Pinecone, ServerlessSpec
from typing import List
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

def load_pdf(pdf_path):
    loader = DirectoryLoader(
        pdf_path,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )
    documents = loader.load()
    return documents

def doc_filter(data: List[Document]) -> List[Document]:
    """
        Given a list of Document objects, return a new list of Document objects containing only 'source' in metadata and the original page_content.

    """

    filter_docs: List[Document] = []
    for doc in data:
        src = doc.metadata.get("source")
        filter_docs.append(
            Document(
                page_content=doc.page_content,
                metadata={"source": src}
            )
        )
    
    return filter_docs

def ingest_docs(data):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    text_chunk = text_splitter.split_documents(data)

    embeddings = OllamaEmbeddings(
        model="mxbai-embed-large:latest"
    )

    pc = Pinecone(
        api_key=os.getenv("PINECONE_API_KEY")
    )

    index_name = "medical-chatbot"

    print("Ingesting the text chunks to Pinecone...")

    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=1024,
            metric='cosine',
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)
        
    print("Index created successfully!")
    
    docsearch = PineconeVectorStore.from_documents(
        documents=text_chunk,
        embedding=embeddings,
        index_name=index_name
    )
    
    print(f"Successfully ingested {len(text_chunk)} chunks")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_directory = os.path.join(project_root, "data")
    
    print(f"DEBUG: Searching for PDFs exactly here -> {data_directory}")

    docs = load_pdf(data_directory)
    print(f"DEBUG: Found {len(docs)} PDF pages.")

    print("Filtering metadata...")
    filtered_doc = doc_filter(docs)

    print("Starting ingestion...")
    ingest_docs(filtered_doc)