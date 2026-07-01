import streamlit as st
from dotenv import load_dotenv
from .retrival import get_rag_chain

load_dotenv()

st.set_page_config(page_title="Medical Chatbot")
st.title("Medical Chatbot")

@st.cache_resource
def load_chain():
    return get_rag_chain()

chain = load_chain()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am a medical assistant. Ask me a question based on the uploaded guidelines."}
    ]

# Render previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Box
if prompt := st.chat_input("Ask a medical question..."):
    
    # 1. Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate and show assistant response
    with st.chat_message("assistant"):
        with st.spinner("Searching medical guidelines..."):
            
            # Call the backend chain
            response = chain.invoke({"input": prompt})
            answer = response["answer"]
            
            st.markdown(answer)
            
            # Portfolio Feature: Show the exact PDF sources in a dropdown!
            with st.expander("View Source Documents"):
                for doc in response["context"]:
                    source_file = doc.metadata.get('source', 'Unknown File')
                    page_num = doc.metadata.get('page', 'Unknown Page')
                    st.write(f"- **{source_file}** (Page {page_num})")
                    
    # 3. Save assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": answer})