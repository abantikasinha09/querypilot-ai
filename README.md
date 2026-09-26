 🤖 QueryPilot AI — Natural Language to SQL Analytics Assistant

QueryPilot AI is an AI-powered Text-to-SQL application that allows users to interact with a relational database using natural language. Instead of manually writing SQL queries, users can ask questions such as “Which country has the most customers?” The system uses an LLM-powered agent to understand the question, inspect the database schema, generate SQL, execute it, and return an understandable answer along with the generated SQL and query results.

## Features

- Natural Language Database Queries
- AI-Powered SQL Generation using a Groq-hosted LLM through LangChain
- Generated SQL Visibility
- Interactive Query Results in a structured table
- Automatic Visualization: suitable results are converted into bar charts
- Read-Only SQL Validation before separate result-viewer execution
- Destructive operations blocked at the app validation layer: INSERT, UPDATE, DELETE, DROP, ALTER, etc.
- Database Explorer for tables and columns
- Query History for the current application session
- Technical Details showing model, framework, database, and SQL validation
- Interactive Streamlit Interface

## How It Works

```text
User Question
      ↓
QueryPilot AI / LangChain Agent
      ↓
Database Tools
(List Tables → Inspect Schema → Execute SQL)
      ↓
Groq LLM (openai/gpt-oss-120b)
      ↓
Generated SQL Query
      ↓
SQLite Chinook Database
      ↓
Results + Natural Language Answer + SQL + Chart
```

## Architecture

```text
User
  ↓
Streamlit Interface
  ↓
QueryPilot AI Agent
  ↓
LangChain + Groq LLM + SQL Database Toolkit
  ↓
SQLite / Chinook Database
  ↓
Query Results
  ↓
Answer + Generated SQL + Visualization
```

## Tech Stack

- Python
- LangChain
- LangGraph
- Groq
- GPT-OSS 120B
- SQLAlchemy
- SQLite
- Streamlit
- Pandas
- Rich
- uv

## Database

QueryPilot AI uses the Chinook SQLite sample digital music store database.

### Main Tables

- Customer
- Invoice
- InvoiceLine
- Track
- Album
- Artist
- Genre
- MediaType
- Playlist
- Employee

## Example Questions

- How many customers are from Canada?
- Which country has the most customers?
- Who are the top 5 best-selling artists?
- Which employee generated the most revenue?
- What are the most popular music genres?
- Which customers have spent the most money?

## SQL Safety

The application includes application-level validation for SQL used by the separate result viewer.

Only queries beginning with `SELECT` or `WITH` are accepted.

The following destructive operations are rejected:

- `INSERT`
- `UPDATE`
- `DELETE`
- `DROP`
- `ALTER`
- `CREATE`
- `TRUNCATE`

### Important

This validation is an application-level safeguard and should not be treated as a complete database security boundary for the agent’s own tool execution. In a production deployment, the database should use a dedicated read-only connection and appropriate database permissions.

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/abantikasinha09/querypilot-ai.git
cd querypilot-ai
```

### Install Dependencies

Install dependencies using uv:

```bash
uv sync
```

## Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
LANGCHAIN_TRACING_V2=false
LANGCHAIN_PROJECT=querypilot-ai
```

Never commit `.env` or expose your API key.

## Run from CLI

```bash
uv run python agent.py "How many customers are from Canada?"
```

## Run the Streamlit Application

```bash
uv run streamlit run app.py
```

## Project Structure

```text
querypilot-ai/
│
├── app.py
├── agent.py
├── chinook.db
├── README.md
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
└── tutorial.ipynb
```

`chinook.db` and `.env` are excluded from Git using `.gitignore`.

## Query Processing Flow

1. User enters a natural-language question.
2. QueryPilot AI receives the question.
3. The agent inspects available database tables.
4. The agent inspects the relevant table schemas.
5. The Groq LLM generates the SQL query.
6. The SQL query is executed against the database.
7. Query results are returned.
8. A natural-language answer is generated.
9. Streamlit displays the answer, SQL, results, and visualization.

## Project Goals

- Convert natural language into SQL
- Allow non-SQL users to explore relational databases
- Demonstrate agent-based database interaction
- Make generated SQL visible and understandable
- Present database results in an accessible format
- Explore safe handling of read-only analytical queries

## Future Improvements

- Database-level read-only permissions
- Improved SQL validation and query analysis
- Support for multiple databases
- CSV export
- Advanced visualizations
- Persistent query history
- Authentication
- Query caching
- Automated SQL evaluation
- Cloud deployment
- Query performance monitoring

## Author

**Abantika Sinha**

GitHub: https://github.com/abantikasinha09

Project Repository: https://github.com/abantikasinha09/querypilot-ai



