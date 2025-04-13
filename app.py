import os
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
import pdfplumber
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from src.data.rag import get_rich_case_studies
from langchain_google_genai import ChatGoogleGenerativeAI

# Model Settings
model_provider = os.getenv("MODEL_PROVIDER", "ollama")  # 'ollama' or 'openai'
llm_model = os.getenv("LLM_MODEL", "Gemma3")  # Default for ollama

def get_llm():
    """Initialize LLM model based on environment settings."""
    llm = None

    if model_provider.lower() == "openai":
        llm = ChatOpenAI(
            model_name=os.getenv("LLM_MODEL", "gpt-4"),
            temperature=0.1
        )
    elif model_provider.lower() == "google":
        llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-001",
        temperature=0,
        max_tokens=None,
        timeout=5,
        max_retries=2,
        # other params...
    )
    else:  # Default to ollama
        llm = ChatOllama(
            model=llm_model,
            temperature=0.1
        )

    return llm

# File Text Extractor Functions
def extract_text(file):
    if file.type == "application/pdf":
        return extract_pdf_text(file)
    elif file.type == "text/plain":
        return file.read().decode("utf-8")
    else:
        return f"❌ Unsupported file type: {file.type}"

def extract_pdf_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# Streamlit UI Setup
st.set_page_config(page_title="Strategy Synthesis AI", layout="wide")
st.title("Strategy Synthesis AI")

# File uploader
uploaded_files = st.file_uploader("📎 Attach relevant files", accept_multiple_files=True)
attached_text = ""  # Store all uploaded content here

if uploaded_files:
    st.markdown("**Attached Files:**")
    for file in uploaded_files:
        st.markdown(f"📄 `{file.name}`")
        extracted = extract_text(file)
        attached_text += f"\n\n--- File: {file.name} ---\n{extracted}"

llm = get_llm()

if attached_text:
    st.chat_message('assistant').write("*Searching for relevant case studies...*")
    context_prompt = str(get_rich_case_studies(attached_text)).replace("{", "{{").replace("}", "}}")
# Prompt Template (inject file content here)
system_prompt = f"""
You are a world-class Strategic Business Advisor helping businesses across industries design effective business strategies to support growth, innovation, and long-term success.

Carefully analyze the content provided by the user (if it is provided) to understand their current business model, challenges, or goals.

You should explicitly refer to the reference case studies provided by the system to craft thoughtful, tailored, and actionable responses to the user's questions.
It is very important to provide reference http URLs from the Relevant Case Studies in your response

Do not make up information or assumptions. If the user content is insufficient to fully answer a question, clearly say so and suggest what additional information would help.

Be clear, insightful, and professional — your goal is to act as a trusted strategic advisor.

--- Attached User Content ---
{attached_text}

--- Relevant Case Studies ---
{context_prompt}

"""

# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

chain = prompt | llm
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: msgs,
    input_messages_key="question",
    history_messages_key="history",
)


# Render current messages from StreamlitChatMessageHistory
for msg in msgs.messages:
    if msg.type == 'AIMessageChunk':
        st.chat_message('ai').write(msg.content)
    else:
        st.chat_message(msg.type).write(msg.content)

# If user inputs a new prompt, generate and draw a new response
if user_input := st.chat_input("How can I help?"):
    st.chat_message("human").write(user_input)

    # New messages are saved to history automatically by Langchain during run
    config = {"configurable": {"session_id": "any"}}
    st.chat_message('ai').write_stream(chain_with_history.stream({"question": user_input}, config))
        