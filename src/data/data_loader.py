import os
import json
import logging
import re
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import argparse
from tqdm import tqdm
from typing import List, Dict, Any, Tuple
import numpy as np
from transformers import pipeline
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from src.config import RAW_DATA_DIR
from src.data.db import connect_to_db
from src.data.constants import CATEGORIES

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Model Settings
model_provider = os.getenv("MODEL_PROVIDER", "ollama")  # 'ollama' or 'openai'
embedding_model = os.getenv("EMBEDDING_MODEL", "mxbai-embed-large")  # Default for ollama

# Define constants for chunk size
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def setup_classifiers(device="cuda"):
    """Initialize the zero-shot classification model for metadata extraction."""
    logger.info(f"Loading zero-shot classification model on {device}...")
    classifier = pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
        device=device
    )
    
    # Initialize embedding model based on environment settings
    logger.info(f"Setting up embedding model...")
    embeddings = None
    
    # too broke for OpenAI rn :)
    # if model_provider.lower() == "openai":
    #     from langchain_openai import OpenAIEmbeddings
        
    #     embeddings = OpenAIEmbeddings(
    #         model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
    #     )
    # else:  # Default to ollama
    from langchain_ollama import OllamaEmbeddings
    
    embeddings = OllamaEmbeddings(
        model=embedding_model
    )
    
    return classifier, embeddings

def get_embedding_model():
    """Initialize embedding model based on environment settings."""
    logger.info(f"Setting up embedding model...")
    embeddings = None
    
    if model_provider.lower() == "openai":
        from langchain_openai import OpenAIEmbeddings
        
        embeddings = OpenAIEmbeddings(
            model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
        )
    else:  # Default to ollama
        from langchain_ollama import OllamaEmbeddings
        
        embeddings = OllamaEmbeddings(
            model=embedding_model
        )
    
    return embeddings

def parse_case_study(file_path: str) -> Dict[str, str]:
    """Extract title, source and content from a case study text file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Extract title and source if they exist
    title_match = re.search(r'Title:\s*(.*?)(?=\n|$)', content)
    source_match = re.search(r'Source:\s*(.*?)(?=\n|$)', content)
    
    title = title_match.group(1).strip() if title_match else os.path.basename(file_path)
    source = source_match.group(1).strip() if source_match else ""
    
    # Remove title and source lines from content if they exist
    if title_match:
        content = content.replace(title_match.group(0), "", 1)
    if source_match:
        content = content.replace(source_match.group(0), "", 1)
    
    content = content.strip()
    
    return {
        "title": title,
        "source": source,
        "content": content,
        "source_file": os.path.basename(file_path)
    }

def preprocess_text(text: str) -> str:
    """Clean and preprocess text for classification."""
    # Remove special characters and extra whitespace
    text = re.sub(r'[^\w\s\.\,\:\;\-\(\)]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_summary(content: str, max_length: int = 1024) -> str:
    """Extract a summary from case study content."""
    # Use the first few sentences (up to max_length characters)
    sentences = re.split(r'(?<=[.!?])\s+', content)
    summary = ""
    
    for sentence in sentences:
        if len(summary) + len(sentence) <= max_length:
            summary += sentence + " "
        else:
            break
    
    return summary.strip()

def extract_metadata_with_zero_shot(classifier, content: str, title: str) -> Dict[str, Any]:
    """Use zero-shot classification to extract metadata from case study content."""
    metadata = {}
    
    # Prepare text by combining title and first part of content
    summary = extract_summary(content)
    combined_text = f"{title}. {summary}"
    processed_text = preprocess_text(combined_text)
    
    # Generate summary
    metadata["summary"] = summary[:250] + "..." if len(summary) > 250 else summary
    
    # Classify each category
    for category, options in CATEGORIES.items():
        if category in ['key_challenges', 'core_strategies']:
            # For multi-label categories, we'll get top 3
            results = classifier(processed_text, options, multi_label=True)
            top_indices = np.argsort(results['scores'])[-3:][::-1]
            # Only include options with a score above 0.3
            top_items = [results['labels'][i] for i in top_indices if results['scores'][i] > 0.3]
            metadata[category] = top_items
        else:
            # For single-label categories
            results = classifier(processed_text, options, multi_label=False)
            metadata[category] = results['labels'][0]
    
    return metadata

def chunk_text(content: str, text_splitter: RecursiveCharacterTextSplitter) -> List[Document]:
    """Split case study content into chunks for embedding."""
    return text_splitter.create_documents([content])

def compute_embeddings(chunks: List[Document], embeddings) -> List[np.ndarray]:
    """Compute embeddings for text chunks."""
    texts = [chunk.page_content for chunk in chunks]
    return embeddings.embed_documents(texts)

def insert_case_study(conn, case_study: Dict[str, Any]) -> int:
    """Insert case study into database and return the ID."""
    cursor = conn.cursor()
    
    query = """
    INSERT INTO case_studies (
        title, 
        source_url,
        summary,
        industry, 
        company_size, 
        business_model, 
        growth_stage, 
        key_challenges, 
        core_strategies, 
        source_file, 
        content, 
        raw_metadata
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """
    
    try:
        cursor.execute(query, (
            case_study["title"],
            case_study["source"],
            case_study["metadata"].get("summary", ""),
            case_study["metadata"].get("industry", "Unknown"),
            case_study["metadata"].get("company_size", "Unknown"),
            case_study["metadata"].get("business_model", "Unknown"),
            case_study["metadata"].get("growth_stage", "Unknown"),
            case_study["metadata"].get("key_challenges", []),
            case_study["metadata"].get("core_strategies", []),
            case_study["source_file"],
            case_study["content"],
            json.dumps(case_study["metadata"])
        ))
        
        case_study_id = cursor.fetchone()[0]
        conn.commit()
        return case_study_id
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting case study: {e}")
        raise
    finally:
        cursor.close()

def insert_chunks(conn, case_study_id: int, chunks: List[Document], embeddings_list: List[np.ndarray]):
    """Insert chunks and their embeddings into database."""
    cursor = conn.cursor()
    
    # Prepare data for batch insert
    chunk_data = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_list)):
        chunk_data.append((
            case_study_id,
            i,
            chunk.page_content,
            embedding
        ))
    
    query = """
    INSERT INTO case_study_chunks (case_study_id, chunk_number, content, embedding)
    VALUES %s
    """
    
    try:
        execute_values(cursor, query, chunk_data)
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting chunks: {e}")
        raise
    finally:
        cursor.close()

def process_case_studies(directory_path: str):
    """Process all text files in the directory and populate the database."""
    conn = connect_to_db()
    classifier, embedding_model = setup_classifiers()
    
    # Create text splitter for chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    
    # Get all text files in the directory
    file_paths = [os.path.join(directory_path, f) for f in os.listdir(directory_path) 
                  if f.endswith('.txt') and os.path.isfile(os.path.join(directory_path, f))]
    
    logger.info(f"Found {len(file_paths)} text files to process")
    
    for file_path in tqdm(file_paths, desc="Processing case studies"):
        try:
            # Parse case study from file
            case_study = parse_case_study(file_path)
            
            # Extract metadata using zero-shot classification
            metadata = extract_metadata_with_zero_shot(classifier, case_study["content"], case_study["title"])
            case_study["metadata"] = metadata
            
            # Insert case study into database
            case_study_id = insert_case_study(conn, case_study)
            
            # Chunk text and compute embeddings
            chunks = chunk_text(case_study["content"], text_splitter)
            chunk_embeddings = compute_embeddings(chunks, embedding_model)
            
            # Insert chunks and embeddings into database
            insert_chunks(conn, case_study_id, chunks, chunk_embeddings)

            # Insert category embeddings
            populate_category_embeddings(conn, case_study)
            
            logger.info(f"Successfully processed case study: {case_study['title']}")
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
    
    conn.close()

def format_categories_for_embedding(case_study: Dict[str, Any]) -> Dict[str, List[str]]:
    """Format case study categories into a consistent structure for embedding."""
    categories = {
        "industry": [case_study.get("industry")] if case_study.get("industry") else [],
        "company_size": [case_study.get("company_size")] if case_study.get("company_size") else [],
        "business_model": [case_study.get("business_model")] if case_study.get("business_model") else [],
        "growth_stage": [case_study.get("growth_stage")] if case_study.get("growth_stage") else [],
        "key_challenges": case_study.get("key_challenges", []),
        "core_strategies": case_study.get("core_strategies", [])
    }
    
    # Remove None or empty values
    for key, values in categories.items():
        categories[key] = [v for v in values if v]
    
    return categories

def categories_to_text(categories: Dict[str, List[str]]) -> str:
    """Convert categories dictionary to a text string for embedding."""
    text_parts = []
    
    for category, values in categories.items():
        if values:
            formatted_category = category.replace("_", " ")
            values_str = ", ".join(values)
            text_parts.append(f"{formatted_category}: {values_str}")
    
    return ". ".join(text_parts)

def populate_category_embeddings(conn, case_study):
    """Generate and store embeddings for all case studies' categories."""
    # Initialize embedding model
    embedding_model = get_embedding_model()
    
    cursor = conn.cursor()
    
    try:
        # Format categories
        categories = format_categories_for_embedding(case_study)
        
        # Convert to text for embedding
        categories_text = categories_to_text(categories)
        
        # Generate embedding
        embedding = embedding_model.embed_query(categories_text)
        
        # Insert or update in database
        query = """
        INSERT INTO case_study_category_embeddings 
            (case_study_id, categories_json, categories_embedding)
        VALUES 
            (%s, %s, %s)
        ON CONFLICT (case_study_id) 
        DO UPDATE SET 
            categories_json = EXCLUDED.categories_json,
            categories_embedding = EXCLUDED.categories_embedding,
            created_at = CURRENT_TIMESTAMP
        """
        
        cursor.execute(query, (
            case_study["id"],
            json.dumps(categories),
            embedding
        ))
    
    except Exception as e:
        logger.error(f"Error processing case study {case_study['id']}: {e}")




# import os
# import json
# import logging
# import re
# import psycopg2
# from psycopg2.extras import execute_values
# from dotenv import load_dotenv
# import argparse
# from tqdm import tqdm
# from typing import List, Dict, Any, Tuple
# import numpy as np
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.schema.document import Document
# from src.config import RAW_DATA_DIR
# from src.data.db import connect_to_db

# # Initialize logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# load_dotenv()

# # Model Settings
# model_provider = os.getenv("MODEL_PROVIDER", "ollama")  # 'ollama' or 'openai'
# llm_model = os.getenv("LLM_MODEL", "Gemma3")  # Default for ollama
# embedding_model = os.getenv("EMBEDDING_MODEL", "mxbai-embed-large")  # Default for ollama

# # Define constants for chunk size
# CHUNK_SIZE = 1000
# CHUNK_OVERLAP = 200


# def setup_models():
#     """Initialize LLM and embedding models based on environment settings."""
#     llm = None
#     embeddings = None

#     if model_provider.lower() == "openai":
#         from langchain_openai import ChatOpenAI
#         from langchain_openai import OpenAIEmbeddings
        
#         llm = ChatOpenAI(
#             model_name=os.getenv("LLM_MODEL", "gpt-4"),
#             temperature=0.1
#         )
#         embeddings = OpenAIEmbeddings(
#             model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
#         )
#     else:  # Default to ollama
#         from langchain_ollama import ChatOllama
#         from langchain_ollama import OllamaEmbeddings
        
#         #ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
#         llm = ChatOllama(
#             model=llm_model,
#             #base_url=ollama_base_url,
#             temperature=0.1
#         )
#         embeddings = OllamaEmbeddings(
#             model=embedding_model,
#             #base_url=ollama_base_url
#         )
    
#     return llm, embeddings

# def parse_case_study(file_path: str) -> Dict[str, str]:
#     """Extract title, source and content from a case study text file."""
#     with open(file_path, 'r', encoding='utf-8') as file:
#         content = file.read()
    
#     # Extract title and source if they exist
#     title_match = re.search(r'Title:\s*(.*?)(?=\n|$)', content)
#     source_match = re.search(r'Source:\s*(.*?)(?=\n|$)', content)
    
#     title = title_match.group(1).strip() if title_match else os.path.basename(file_path)
#     source = source_match.group(1).strip() if source_match else ""
    
#     # Remove title and source lines from content if they exist
#     if title_match:
#         content = content.replace(title_match.group(0), "", 1)
#     if source_match:
#         content = content.replace(source_match.group(0), "", 1)
    
#     content = content.strip()
    
#     return {
#         "title": title,
#         "source": source,
#         "content": content,
#         "source_file": os.path.basename(file_path)
#     }

# def extract_metadata(llm, content: str, title: str) -> Dict[str, Any]:
#     """Use LLM to extract metadata from case study content."""
    
#     # Create a prompt for the LLM
#     prompt = f"""
#     Based on the following business case study, extract and categorize the information according to these specific categories:
    
#     1. Summary: A 2-3 sentence summary of the case study
#     2. Industry: The specific industry the business operates in
#     3. Company Size: One of [Startup, Small Business, Medium Business, Large Business, Enterprise, Micro-Enterprise, Unicorn]
#     4. Business Model: One of [B2B, B2C, B2B2C, C2C, B2G, D2C, Marketplace/Platform, Freemium, Subscription, SaaS, PaaS, IaaS, Hardware/Product, Service-Based, Franchise, Manufacturing, Retail, Wholesale]
#     5. Growth Stage: One of [Pre-Seed/Idea Stage, Seed/Startup, Early Growth, Scaling, Maturity, Expansion, Diversification, Consolidation, Turnaround/Restructuring, Declining, Exit Preparation]
#     6. Key Challenges: List up to 3 main challenges from [Funding/Capital Access, Cash Flow Management, Market Entry, Customer Acquisition, Customer Retention, Product Development, Scaling Operations, Talent Acquisition/Retention, Competition, Regulatory Compliance, Technology Adoption, Digital Transformation, Supply Chain Optimization, Cost Reduction, Internationalization, Brand Development, Innovation Management, Organizational Restructuring, Merger/Acquisition Integration, Succession Planning, Crisis Management]
#     7. Core Strategies: List up to 3 main strategies from [Cost Leadership, Value-Based Pricing, Differentiation, Market Focus/Niche, Diversification, Integration, First Mover Advantage, Fast Follower, Growth Through Acquisition, Organic Growth, Network Effects, Ecosystem Building, Disruptive Innovation, Blue Ocean Strategy, Strategic Alliances/Partnerships, Licensing/Franchising, Market Penetration, Customer Experience, Technological Leadership, Sustainable/Green Strategy, Digital Transformation, Platform Strategy, Lean Operations, Agile Methodology]
    
#     Case study title: {title}
#     Case study excerpt:
#     {content}
    
#     Respond ONLY with a JSON object containing these fields. If information for a field isn't clearly available, use your best guess based on the available content. For array fields, provide actual arrays.
#     """
    
#     try:
#         response = llm.invoke(prompt)
#         response_text = response.content if hasattr(response, 'content') else str(response)
        
#         # Extract JSON object from response
#         json_match = re.search(r'```json(.*?)```', response_text, re.DOTALL)
#         if json_match:
#             json_str = json_match.group(1).strip()
#         else:
#             # Try to extract JSON without code blocks
#             json_str = response_text.strip()
            
#             # Remove any text before the first '{' and after the last '}'
#             start_idx = json_str.find('{')
#             end_idx = json_str.rfind('}')
#             if start_idx != -1 and end_idx != -1:
#                 json_str = json_str[start_idx:end_idx+1]
        
#         metadata = json.loads(json_str)
        
#         # Ensure key_challenges and core_strategies are lists
#         if "key_challenges" in metadata and isinstance(metadata["key_challenges"], str):
#             metadata["key_challenges"] = [c.strip() for c in metadata["key_challenges"].split(",")]
        
#         if "core_strategies" in metadata and isinstance(metadata["core_strategies"], str):
#             metadata["core_strategies"] = [s.strip() for s in metadata["core_strategies"].split(",")]
        
#         return metadata
        
#     except Exception as e:
#         logger.error(f"Error extracting metadata: {e}")
#         # Return default metadata if extraction fails
#         return {
#             "summary": "No summary available",
#             "industry": "Unknown",
#             "company_size": "Unknown",
#             "business_model": "Unknown",
#             "growth_stage": "Unknown",
#             "key_challenges": [],
#             "core_strategies": []
#         }

# def chunk_text(content: str, text_splitter: RecursiveCharacterTextSplitter) -> List[Document]:
#     """Split case study content into chunks for embedding."""
#     return text_splitter.create_documents([content])

# def compute_embeddings(chunks: List[Document], embeddings) -> List[np.ndarray]:
#     """Compute embeddings for text chunks."""
#     texts = [chunk.page_content for chunk in chunks]
#     return embeddings.embed_documents(texts)

# def insert_case_study(conn, case_study: Dict[str, Any]) -> int:
#     """Insert case study into database and return the ID."""
#     cursor = conn.cursor()
    
#     query = """
#     INSERT INTO case_studies (
#         title, 
#         source_url,
#         summary,
#         industry, 
#         company_size, 
#         business_model, 
#         growth_stage, 
#         key_challenges, 
#         core_strategies, 
#         source_file, 
#         content, 
#         raw_metadata
#     ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#     RETURNING id
#     """
    
#     try:
#         cursor.execute(query, (
#             case_study["title"],
#             case_study["source"],
#             case_study["metadata"].get("summary", ""),
#             case_study["metadata"].get("industry", "Unknown"),
#             case_study["metadata"].get("company_size", "Unknown"),
#             case_study["metadata"].get("business_model", "Unknown"),
#             case_study["metadata"].get("growth_stage", "Unknown"),
#             case_study["metadata"].get("key_challenges", []),
#             case_study["metadata"].get("core_strategies", []),
#             case_study["source_file"],
#             case_study["content"],
#             json.dumps(case_study["metadata"])
#         ))
        
#         case_study_id = cursor.fetchone()[0]
#         conn.commit()
#         return case_study_id
    
#     except Exception as e:
#         conn.rollback()
#         logger.error(f"Error inserting case study: {e}")
#         raise
#     finally:
#         cursor.close()

# def insert_chunks(conn, case_study_id: int, chunks: List[Document], embeddings_list: List[np.ndarray]):
#     """Insert chunks and their embeddings into database."""
#     cursor = conn.cursor()
    
#     # Prepare data for batch insert
#     chunk_data = []
#     for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_list)):
#         chunk_data.append((
#             case_study_id,
#             i,
#             chunk.page_content,
#             embedding
#         ))
    
#     query = """
#     INSERT INTO case_study_chunks (case_study_id, chunk_number, content, embedding)
#     VALUES %s
#     """
    
#     try:
#         execute_values(cursor, query, chunk_data)
#         conn.commit()
#     except Exception as e:
#         conn.rollback()
#         logger.error(f"Error inserting chunks: {e}")
#         raise
#     finally:
#         cursor.close()

# def process_case_studies(directory_path: str):
#     """Process all text files in the directory and populate the database."""
#     conn = connect_to_db()
#     llm, embeddings = setup_models()
    
#     # Create text splitter for chunking
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=CHUNK_SIZE,
#         chunk_overlap=CHUNK_OVERLAP
#     )
    
#     # Get all text files in the directory
#     file_paths = [os.path.join(directory_path, f) for f in os.listdir(directory_path) 
#                   if f.endswith('.txt') and os.path.isfile(os.path.join(directory_path, f))]
    
#     logger.info(f"Found {len(file_paths)} text files to process")
    
#     for file_path in tqdm(file_paths, desc="Processing case studies"):
#         try:
#             # Parse case study from file
#             case_study = parse_case_study(file_path)
            
#             # Extract metadata using LLM
#             metadata = extract_metadata(llm, case_study["content"], case_study["title"])
#             case_study["metadata"] = metadata
            
#             # Insert case study into database
#             case_study_id = insert_case_study(conn, case_study)
            
#             # Chunk text and compute embeddings
#             chunks = chunk_text(case_study["content"], text_splitter)
#             chunk_embeddings = compute_embeddings(chunks, embeddings)
            
#             # Insert chunks and embeddings into database
#             insert_chunks(conn, case_study_id, chunks, chunk_embeddings)
            
#             logger.info(f"Successfully processed case study: {case_study['title']}")
            
#         except Exception as e:
#             logger.error(f"Error processing {file_path}: {e}")
    
#     conn.close()