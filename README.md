# StrataGem

StrataGem is the business advisor you've always wished for :)

We analyze your business data, generate comprehensive strategy plans, and build tailored presentations for different stakeholders

Built in Bitcamp 2025 @ UMD

## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         src and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── src   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes src a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

--------

## How to Setup
1. Setup your virtual environment and install dependencies
```bash
python venv -m .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2. Setup Docker containers
```bash
docker compose up -d
```
3. Create DB Schema
```bash
python src/initial_setup.py
```
4. Ingest case study data or skip this and create your own!
```bash
docker exec -i strategic-synthesis-ai-postgres-1 psql -U postgres -d strats_db < strats_db.dump
```
5. Run Streamlit and enjoy your free (mostly) business advisor
```bash
streamlit run app.py
```


## Inspiration
Ever notice how many awesome ideas pop up every day, but only a few become the next big thing? It's not because people aren't creative enough or don't care enough. Often, it's just that they're missing the know-how to grow their idea into something bigger. That's exactly why we created our solution! 
StrataGem has answers for all your business growth challenges. We wanted to help bridge that gap between having a brilliant idea and building a successful business - whether you're an existing business looking to level up or a brand new startup finding your footing.

## What it does
We're like that friend who actually listens when you talk about your business dreams! We take the time to understand what makes your business special - your big goals, what you're passionate about, and what matters most to you.
Then, our clever AI digs through hundreds of real-world success and failure stories to cook up strategies that fit YOU like a glove. No more one-size-fits-all advice that feels like it could apply to literally anyone with a business card!
Got a small business that's hit a wall? We'll help you climb over it.
Running a fresh-out-of-the-box startup? We'll help you dodge those first-year disasters that nobody warns you about.
Whether you've been grinding away for years or just took the leap last month, StrataGem is here to transform your brilliant idea into something that makes people go "Wow, how did they get so big so fast?

## How we built it
1. We started off by scraping a ton of high-quality business case studies specific to a few industries. This was harder than expected since, a lot of them are pay-walled.
2. Next we setup a Postgres DB and cleaned and ingested this data. We then used BART to classify the case studies on certain predefined categories like industry, business size etc.
3. We then created embeddings using Ollama and stored it in our DB with pgvector extension
4. Finally we setup a Langchain x Streamlit app with access to Google Gemini models, and used a RAG based system to provide these LLMs with some rich human context,

## Challenges we ran into
**Data Extraction:** One of the biggest hurdles we encountered was sourcing quality data. There are only a limited number of sites that provide access to past business case studies, and even fewer that offer them in a usable format. Extracting the relevant information took significant time and effort. We had to fine-tune our model to filter out noise and capture only the insights that truly mattered for our strategy generation.

**Scoping:** We were skeptical about completing everything we had in mind to begin with, and features kept being added and removed. Thanks to Lucas from Microsoft/Cloudforce for letting us pick his brain on this. Ultimately we managed to pull through and finish the project.

**API Limits:** Another significant challenge we faced was working within the constraints of API rate limits. Shoutout to Google for a generous access to the Gemini API which enabled us to use SOTA LLMs for this project

## Accomplishments that we're proud of
StrataGem was an amalgamation and mutation of a bunch of ideas that we spent hours brainstorming. We are extremely happy with how it turned out and especially so of the fact that we managed to implement everything from actual human made case studies as our DB, complex RAG and a PPT generator all in one day :)

## What we learned
Throughout the development of this project, we were regularly reminded of the massive potential that GenAI has and how we barely scratch the surface in our everyday lives. We definitely look forward to building highly-complex AI orchestrated systems in the future.

## What's next for StrataGem
One of the main things we would like to address is the privacy of business sensitive data being shared with  LLM providers and how we could scope this.
We plan to have StrataGem accessible via an live Streamlit app as well as improve the small but mighty repository of business case studies that we currently have. We would also love to integrate/connect the PowerPoint generation part with Microsoft Copilot's existing capability. 
