import os
import psycopg2
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector

load_dotenv()

# Get database connection parameters from environment variables
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
dbname = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")

emb_size = 1024  # for mxbai-embed-large

def connect_to_db():
    """Establish connection to PostgreSQL database."""
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    register_vector(conn)
    return conn

def setup_db():
    """ One-time setup of Postgres database for business strategy generator """
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # Create database if it doesn't exist
    cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{dbname}'")
    if not cursor.fetchone():
        cursor.execute(f"CREATE DATABASE {dbname}")

    # Connect to the newly created database
    conn.close()
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    cursor = conn.cursor()

    # Enable pgvector extension
    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create tables for business case studies
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS case_studies (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        source_url TEXT,
        summary TEXT,
        industry TEXT NOT NULL,
        company_size TEXT,  -- startup/SMB/enterprise
        business_model TEXT, -- B2B/B2C/marketplace
        growth_stage TEXT,   -- early/scaling/mature/turnaround
        key_challenges TEXT[],
        core_strategies TEXT[],
        source_file TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        raw_metadata JSONB
    )
    """)   

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS case_study_chunks (
        id SERIAL PRIMARY KEY,
        case_study_id INTEGER REFERENCES case_studies(id),
        chunk_number INTEGER NOT NULL,
        content TEXT NOT NULL,
        embedding vector({emb_size}),
        UNIQUE(case_study_id, chunk_number)
    )
    """)

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS case_study_category_embeddings (
        id SERIAL PRIMARY KEY,
        case_study_id INTEGER REFERENCES case_studies(id) UNIQUE,
        categories_json JSONB NOT NULL,
        categories_embedding vector({emb_size}),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)


    # Create indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_case_studies_industry ON case_studies(industry)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_case_studies_company_size ON case_studies(company_size)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_case_studies_business_model ON case_studies(business_model)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_case_studies_growth_stage ON case_studies(growth_stage)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_case_study_chunks_case_study_id ON case_study_chunks(case_study_id)")
    cursor.execute(f"""
    CREATE INDEX IF NOT EXISTS idx_case_study_category_embeddings 
    ON case_study_category_embeddings USING ivfflat (categories_embedding vector_cosine_ops)
    """)
    
    # Vector similarity search index
    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_case_study_chunks_embedding ON case_study_chunks USING ivfflat (embedding vector_cosine_ops)")

    conn.commit()
    conn.close()

    print("Database setup completed successfully.")