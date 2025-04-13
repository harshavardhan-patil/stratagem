import streamlit as st
from src.utils.dynamic_ppt_generator import generate_dynamic_pptx_from_chat
st.set_page_config(layout='wide', initial_sidebar_state='expanded', page_title="StrataGem")

import os
import streamlit as st
import base64
from src.utils.roadmap_creation import generate_roadmap

# Function to set background image
def set_jpg_as_page_bg(bg):
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url(data:image/jpg;base64,{base64.b64encode(open(bg, "rb").read()).decode()});
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

# Function to remove background image and set beige background color
def set_beige_bg():
    st.markdown(
         """
         <style>
         .stApp {
             background-image: none;
             background-color: #f5f0e5; /* Light beige color similar to banner3.png */
         }
         </style>
         """,
         unsafe_allow_html=True
     )
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

# Initialize session states
if 'welcome_complete' not in st.session_state:
    st.session_state.welcome_complete = False
if 'case_studies_fetched' not in st.session_state:
    st.session_state.case_studies_fetched = False
    st.session_state.context_prompt = ""

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

# Function to handle starting the app
def start_app():
    st.session_state.welcome_complete = True
    set_beige_bg()  # Set beige background when moving to main app

# Welcome Screen
if not st.session_state.welcome_complete:
    # Set background image for welcome screen
    set_jpg_as_page_bg('static/banner3.png')
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown(
            """
            <div style="background-color: #222; padding: 30px; border-radius: 10px; margin-bottom: 20px; text-align: center;">
                <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                    <span style="color: #FFB627; font-size: 40px; margin-right: 10px;">&#9733;</span>
                    <h1 style="color: white; margin: 0;">StrataGem</h1>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <h1 style="text-align: center; font-size: 2.5rem; margin-bottom: 30px;">
            Your friendly neighborhood Business Advisor :)
            </h1>
            """, 
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <p style="text-align: center; font-size: 1.2rem; margin-bottom: 40px; color: #555;">
            StrataGem analyzes your business data, generates comprehensive strategy plans, 
            and builds tailored presentations for different stakeholders using the power of AI 
            </p>
            """, 
            unsafe_allow_html=True
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("Let's get started!", use_container_width=True, type="primary"):
                start_app()
                st.rerun()

# Main Application
else:
    # Set beige background when in main app
    set_beige_bg()
    st.title("StrataGem")

    # File uploader
    uploaded_files = st.file_uploader("Attach anything that will help me understand your business 😄", accept_multiple_files=True)
    attached_text = ""  # Store all uploaded content here

    if uploaded_files:
        for file in uploaded_files:
            extracted = extract_text(file)
            attached_text += f"\n\n--- File: {file.name} ---\n{extracted}"
        
        # Only fetch case studies if we have new content and haven't fetched them yet
        if attached_text and not st.session_state.case_studies_fetched:
            with st.spinner('Tapping into the infinite wisdom of universe...'):
                st.session_state.context_prompt = str(get_rich_case_studies(attached_text)).replace("{", "{{").replace("}", "}}")
                st.session_state.case_studies_fetched = True
                st.success("Case studies retrieved successfully!")

    llm = get_llm()

    # Use the stored context prompt from session state
    context_prompt = st.session_state.context_prompt

    # Prompt Template (inject file content here)
    system_prompt = f"""
    You are a world-class Strategic Business Advisor helping businesses across industries design effective business strategies to support growth, innovation, and long-term success.

    Carefully analyze the content provided by the user (if it is provided) to understand their current business model, challenges, or goals.

    You should explicitly refer to the reference case studies provided by the system to craft thoughtful, tailored, and actionable responses to the user's questions.
    It is very important to provide reference http URLs from the Relevant Case Studies in your response

    Analyze the following key factors for your reponse:-
    1. 	Business Context Industry specifics (e.g., tech, FMCG, healthcare) -Market structure (monopoly, oligopoly, fragmented, etc.), Regulatory environment (local/global, highly regulated or not), Stage of business lifecycle (startup, growth, maturity, decline)
    2. 	Strategic Intent Vision/Mission alignment - Growth objectives (scale, profit, market leadership, innovation), Geographic goals (domestic focus vs global expansion), Long-term vs. short-term priorities
    3. 	Key Capability Inputs Core competencies (e.g., R&D, brand strength, distribution) - Technology maturity, Talent & leadership, Operational infrastructure
    4. 	Customer Dimensions Target segment behavior - Customer jobs to be done, Channel preferences (D2C, retail, B2B), Value perception and willingness to pay
    5. 	Competitive Forces Rivalry intensity - Barriers to entry, Threat of substitutes, Supplier/buyer power (Porter's Five Forces), Innovation speed in the industry
    6. 	Strategic Options Spectrum Growth levers (market penetration, product dev, M&A, diversification) - Business models (B2B/B2C, SaaS, subscription, platform), Differentiation methods (price, innovation, service, brand), Focus areas (niche vs mass market)
    7. 	Risk & Resilience Metrics Financial risk tolerance, Operational risk (supply chain fragility), Market volatility exposure, Crisis adaptability (e.g., COVID learnings)
    8. 	Measurement and Governance Key Performance Indicators (KPIs) -Feedback loops, Decision accountability, Scalability of strategy

    Based upon this analysis, what are the gaps in the existing business and develop detailed 3 month, 6 month and 1 year plan y first asking user what they want to know.

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
        elif msg.type == 'ai' and msg.content.startswith('IMAGE_REFS:'):
            # This is our special image reference message
            image_paths = msg.content.replace('IMAGE_REFS:', '').split(',')
            for img_path in image_paths:
                if os.path.exists(img_path):
                    st.chat_message('ai').image(img_path)
        else:
            st.chat_message(msg.type).write(msg.content)

    ppt_trigger_keywords = ["ppt", "powerpoint", "create ppt", "generate ppt", "presentation"]
    roadmap_trigger_keywords = ["ppt", "powerpoint", "create ppt", "generate ppt", "roadmap"]
    # If user inputs a new prompt, generate and draw a new response
    if user_input := st.chat_input("How can I help?"):
        st.chat_message("human").write(user_input)
        if any(keyword in user_input.lower() for keyword in ppt_trigger_keywords):
            st.chat_message('ai').write("Sure, let me whip that right up!")
            try:
                chat_history = "\n".join([f"{msg.type.upper()}: {msg.content}" for msg in msgs.messages])
                pptx_path = generate_dynamic_pptx_from_chat(chat_history, llm)

                with open(pptx_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Presentation (.pptx)",
                        data=f,
                        file_name="Strategic_Plan_Generated.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
            except Exception as e:
                st.error(f"⚠️ Failed to generate presentation: {e}")
        elif any(keyword in user_input.lower() for keyword in roadmap_trigger_keywords):
            st.chat_message('ai').write("Sure, let me whip that right up!")
            try:
                chat_history = "\n".join([f"{msg.type.upper()}: {msg.content}" for msg in msgs.messages])
                if generate_roadmap(chat_history):
                    # Create a special message to store image references
                    image_paths = []
                    for i in range(4):
                        if os.path.exists(f"img{i}.jpg"):
                            image_paths.append(f"img{i}.jpg")
                            st.image(f"img{i}.jpg")
                    
                    # Only add to history if we found images
                    if image_paths:
                        # Store image references in the chat history as a special format
                        image_references = "IMAGE_REFS:" + ",".join(image_paths)
                        msgs.add_ai_message(image_references)
                        
            except Exception as e:
                st.error(f"⚠️ Failed to generate img: {e}")
        else:
            # New messages are saved to history automatically by Langchain during run
            config = {"configurable": {"session_id": "any"}}
            st.chat_message('ai').write_stream(chain_with_history.stream({"question": user_input}, config))



