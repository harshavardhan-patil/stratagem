import os
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage

import fitz  # PyMuPDF
from docx import Document

# ------------- File Text Extractor Functions -------------
def extract_text(file):
    if file.type == "application/pdf":
        return extract_pdf_text(file)
    elif file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_docx_text(file)
    else:
        return f"❌ Unsupported file type: {file.type}"

def extract_pdf_text(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_docx_text(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

# ------------- Streamlit UI Setup -------------
st.set_page_config(page_title="Bitcamp AI Chatbot", layout="wide")
st.title("🤖 Bitcamp AI Strategy Assistant")

# File uploader
uploaded_files = st.file_uploader("📎 Attach relevant files", accept_multiple_files=True)
attached_text = ""  # Store all uploaded content here

if uploaded_files:
    st.markdown("**Attached Files:**")
    for file in uploaded_files:
        st.markdown(f"📄 `{file.name}`")
        extracted = extract_text(file)
        attached_text += f"\n\n--- File: {file.name} ---\n{extracted}"

# ------------- Session-Based Chat Memory -------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Wrapper to expose .messages for LangChain
class MessageStore:
    def __init__(self, messages):
        self._messages = messages
    @property
    def messages(self):
        return self._messages

# ------------- LLM Setup -------------
llm = ChatOllama(model="llama3")  # Use `ollama pull llama3` beforehand

# Prompt Template (inject file content here)
system_prompt = f"""
You are a strategic AI assistant helping businesses across industries design effective business strategy tools to support growth, innovation, and long-term success.

Carefully analyze the content provided by the user to understand their current business model, challenges, or goals. Use this information to offer thoughtful, tailored, and actionable responses to the user's questions.

Do not make up information or assumptions. If the file content is insufficient to fully answer a question, clearly say so and suggest what additional information would help.

Be clear, insightful, and professional — your goal is to act as a trusted strategic advisor.

--- Attached File Content ---
{attached_text}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

chain = prompt | llm
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: MessageStore(st.session_state.chat_history),
    input_messages_key="question",
    history_messages_key="history",
)

# ------------- Display Chat History -------------
for msg in st.session_state.chat_history:
    st.chat_message("ai" if isinstance(msg, AIMessage) else "human").write(msg.content)

# ------------- User Input + LLM Response -------------
user_input = st.chat_input("Ask something about your AI strategy...")
if user_input:
    # Add user message
    user_msg = HumanMessage(content=user_input)
    st.session_state.chat_history.append(user_msg)
    st.chat_message("human").write(user_input)

    # Run through LLM
    config = {"configurable": {"session_id": "bitcamp"}}
    response = chain_with_history.invoke({"question": user_input}, config)

    # Add assistant message
    ai_msg = AIMessage(content=response.content)
    st.session_state.chat_history.append(ai_msg)
    st.chat_message("ai").write(response.content)