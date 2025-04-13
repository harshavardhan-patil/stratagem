import os
import json
from typing import Dict, List, Any, Literal, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains import LLMChain
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
import psycopg2
from psycopg2.extras import RealDictCursor
from pgvector.psycopg2 import register_vector
import regex as re
from dotenv import load_dotenv
from src.data.constants import CATEGORIES
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Database connection parameters
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
dbname = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
# Model Settings
model_provider = os.getenv("MODEL_PROVIDER", "ollama")  # 'ollama' or 'openai'
llm_model = os.getenv("LLM_MODEL", "Gemma3")  # Default for ollama
embedding_model = os.getenv("EMBEDDING_MODEL", "mxbai-embed-large")  # Default embedding model

def get_db_connection_string():
    """Create a database connection string for SQLAlchemy."""
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

def get_embedding_model():
    """Initialize embedding model based on environment settings."""
    embeddings = None
    
    from langchain_ollama import OllamaEmbeddings
    
    embeddings = OllamaEmbeddings(
        model=embedding_model
    )

    return embeddings

def get_llm():
    """Initialize LLM model based on environment settings."""
    llm = None

    if model_provider.lower() == "openai":
        llm = ChatOpenAI(
            model_name=os.getenv("LLM_MODEL", "gpt-4"),
            temperature=0.1
        )
    else:  # Default to ollama
        llm = ChatOllama(
            model=llm_model,
            temperature=0.1
        )

    return llm

def extract_business_categories(
    customer_input: str, 
) -> Dict[str, List[str]]:
    """
    Analyze customer input and extract relevant business categories
    using LangChain and an LLM.
    """
    # Implementation remains the same as before
    llm = get_llm()
    
    # Create a prompt for analyzing the customer input
    category_prompt = ChatPromptTemplate.from_template("""
    Analyze the following business description and identify the most relevant categories that apply.
    For each category, select up to 3 most relevant options.
    
    Business Description:
    {business_description}
    
    Available categories and options:
    - Industry: {industry_options}
    - Company Size: {company_size_options}
    - Business Model: {business_model_options}
    - Growth Stage: {growth_stage_options}
    - Key Challenges: {key_challenges_options}
    - Core Strategies: {core_strategies_options}
    
    Respond with a JSON with category names as keys and lists of selected options as values.
    Format: 
    {{
      "industry": ["option1", "option2"],
      "company_size": ["option1"],
      "business_model": ["option1", "option2"],
      "growth_stage": ["option1"],
      "key_challenges": ["option1", "option2", "option3"],
      "core_strategies": ["option1", "option2", "option3"]
    }}
    
    Make sure all selected options match exactly from the provided lists.
    """)
    
    # Create the chain
    chain = LLMChain(llm=llm, prompt=category_prompt)
    
    # Run the chain
    result = chain.invoke({
        "business_description": customer_input,
        "industry_options": ", ".join(CATEGORIES["industry"]),
        "company_size_options": ", ".join(CATEGORIES["company_size"]),
        "business_model_options": ", ".join(CATEGORIES["business_model"]),
        "growth_stage_options": ", ".join(CATEGORIES["growth_stage"]),
        "key_challenges_options": ", ".join(CATEGORIES["key_challenges"]),
        "core_strategies_options": ", ".join(CATEGORIES["core_strategies"])
    })
    
    # Parse the JSON result - with proper error handling
    try:
        categories = extract_json_from_text(result["text"])
        # Validate that all returned values are in our predefined categories
        for category, values in categories.items():
            if category in CATEGORIES:
                categories[category] = [v for v in values if v in CATEGORIES[category]]
        return categories
    except json.JSONDecodeError:
        # Fallback in case of parsing errors
        return {k: [] for k in CATEGORIES.keys()}

def extract_json_from_text(text):
    """Extract JSON from text using regular expressions."""
    try:
        # Match the JSON object with nested structures
        json_match = re.search(r'\{(?:[^{}]|(?R))*\}', text)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        else:
            raise ValueError("No JSON object found in text.")
    except Exception as e:
        print("Error:", e)
        return None

def categories_to_text(categories: Dict[str, List[str]]) -> str:
    """Convert categories dictionary to a text string for embedding."""
    text_parts = []
    
    for category, values in categories.items():
        if values:
            formatted_category = category.replace("_", " ")
            values_str = ", ".join(values)
            text_parts.append(f"{formatted_category}: {values_str}")
    
    return ". ".join(text_parts)

def category_based_similarity_search(
    categories: Dict[str, List[str]], 
    limit: int = 5,
    similarity_threshold: float = 0.6
) -> List[Dict[str, Any]]:
    """
    Find the most similar case studies based on category embeddings using vector similarity.
    
    Args:
        categories: Dictionary of category names and their values
        limit: Maximum number of results to return
        similarity_threshold: Minimum similarity score (0-1) to include in results
        
    Returns:
        List of case studies with similarity scores
    """
    # Get embedding model
    embedding_model = get_embedding_model()
    
    # Generate embedding for the input categories
    categories_text = categories_to_text(categories)
    query_embedding = embedding_model.embed_query(categories_text)
    
    # Connect to database
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    register_vector(conn)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Query similar case studies using vector similarity
    query = """
    SELECT 
        cs.id,
        cs.title,
        cs.source_url,
        cs.summary,
        cs.industry,
        cs.company_size,
        cs.business_model,
        cs.growth_stage,
        cs.key_challenges,
        cs.core_strategies,
        cs.content,
        1 - (csce.categories_embedding <=> %s::vector) as similarity_score
    FROM 
        case_study_category_embeddings csce
    JOIN 
        case_studies cs ON cs.id = csce.case_study_id
    WHERE 
        1 - (csce.categories_embedding <=> %s::vector) > %s
    ORDER BY 
        similarity_score DESC
    LIMIT %s
    """
    
    try:
        cursor.execute(query, (
            query_embedding,
            query_embedding,
            similarity_threshold,
            limit
        ))
        
        results = cursor.fetchall()
        
        # Convert results to list of dictionaries
        case_studies = []
        for row in results:
            # Convert from RealDictRow to plain dict
            case_study = dict(row)
            # Round similarity score for readability
            case_study['similarity_score'] = round(case_study['similarity_score'], 4)
            case_studies.append(case_study)
        
        return case_studies
    
    except Exception as e:
        print(f"Error querying similar case studies: {e}")
        return []
    
    finally:
        cursor.close()
        conn.close()

def query_relevant_case_studies(
    categories: Dict[str, List[str]],
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Find relevant case studies based on extracted categories.
    First tries vector similarity search, then falls back to traditional filtering if needed.
    
    Args:
        categories: Dictionary of category names and their values
        limit: Maximum number of results to return
        
    Returns:
        List of relevant case studies
    """
    # First, try vector similarity search
    similar_case_studies = category_based_similarity_search(
        categories=categories,
        limit=limit,
        similarity_threshold=0.5  # Lower threshold to ensure we get results
    )
    
    # If we got enough results, return them
    if len(similar_case_studies) >= limit:
        return similar_case_studies
    


    case_studies = []
    query_params = []
    for category, values in categories.items():
        if values:  # Only include non-empty categories
            if category in ['key_challenges', 'core_strategies']:
                # These are array fields, need special handling
                conditions = []
                for value in values:
                    conditions.append(f"{category} && ARRAY['{value}']")
                if conditions:
                    query_params.append(f"({' OR '.join(conditions)})")
            else:
                # Regular string fields
                value_list = [f"'{v}'" for v in values]
                query_params.append(f"{category} IN ({', '.join(value_list)})")
    
    # Create the WHERE clause
    where_clause = " OR ".join(query_params) if query_params else "1=1"
    
    # Execute direct SQL query
    sql_query = f"""
    SELECT 
        id, 
        title, 
        summary,
        industry, 
        company_size, 
        business_model, 
        growth_stage, 
        key_challenges, 
        core_strategies,
        content
    FROM 
        case_studies
    WHERE 
        {where_clause}
    LIMIT {limit - len(similar_case_studies)}
    """

    # Connect directly with psycopg2 to get more structured results
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    with conn.cursor() as cursor:
        cursor.execute(sql_query)
        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            case_study = {}
            for i, value in enumerate(row):
                case_study[columns[i]] = value
            # Add a dummy similarity score for consistency
            case_study['similarity_score'] = 0.0
            case_studies.append(case_study)
    conn.close()
    
    # Combine results from both methods, ensuring no duplicates
    all_studies = similar_case_studies.copy()
    existing_ids = {study['id'] for study in all_studies}
    
    for study in case_studies:
        if study['id'] not in existing_ids:
            all_studies.append(study)
            existing_ids.add(study['id'])
            if len(all_studies) >= limit:
                break
    
    return all_studies

def get_rich_case_studies(customer_input: str,):
    categories = extract_business_categories(customer_input,)
    return query_relevant_case_studies(categories)
