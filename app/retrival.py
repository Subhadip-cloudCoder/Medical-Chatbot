import os
from langchain_pinecone import PineconeVectorStore
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from pinecone import Pinecone

from .utils import system_prompt

def get_rag_chain():

    embeddings = OllamaEmbeddings(
        model='mxbai-embed-large:latest'
    )

    llm = ChatOllama(
        model='llama3:8b'
    )

    index_name = "medical-chatbot"
    vectorstore = PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings
    )

    retriever = vectorstore.as_retriever(
        search_type='similarity',
        search_kwargs={"k": 3}
    )

    system_prompt_ = system_prompt()
    prompt = ChatPromptTemplate.from_messages(
    [
        ("system",  system_prompt_),
        ("human", "{input}")
    ]
    )

    qa = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, qa)

    return rag_chain