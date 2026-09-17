# Investment Radar

## What It Does
Investment Radar is a research tool for exploring startup investment records and reviewing startup applicants. It discovers publicly available KPMG Türkiye investment reports, extracts investment data from HTML pages and PDFs, and stores the records in PostgreSQL.

The application helps users examine applicants’ reported investment histories and discover other funded startups in the available reports. It supports research and human review; it does not make investment decisions.

## Main Features
- Automatically discovers relevant investment report pages from KPMG Türkiye sitemaps.
- Extracts startup, investor, sector, date, amount, and stage information from HTML and PDF reports.
- Groups repeated references to the same investment while keeping separate funding rounds visible.
- Imports startup applications from CSV and matches applicant names with investment records.
- Provides searchable views for applicants, startups, and investors.
- Supports applicant comparison, review notes, and data-quality checks.
- Offers a local AI research assistant for natural-language questions and follow-up questions.
- Displays interpreted filters and matching investment records so users can check the evidence.

## How It Works
1. The crawler finds candidate KPMG Türkiye startup investment reports through the site's XML sitemaps.
2. HTML and PDF parsers extract investment records. The application retains source links and, where available, PDF page information.
3. Records are normalized and stored in PostgreSQL. References to the same investment are grouped without removing their original source records.
4. Startup applications imported from CSV are matched with the investment records.
5. The Streamlit dashboard presents applicant, startup, investor, comparison, and review views.
6. For an AI research question, the local model converts the question into structured filters. Python validates those filters and searches the stored records. The model then summarizes the matching results, while the dashboard shows the underlying evidence.

The local model does not generate or execute SQL.

## Technologies
- Python, Requests, Beautiful Soup, pdfplumber, pandas
- PostgreSQL, SQLAlchemy, psycopg
- Streamlit
- Ollama with the locally installed Qwen3.5 4B model
- pytest for automated tests

## Local Setup
1. Create and activate a Python virtual environment.
2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Create a PostgreSQL database and add a local `.env` file with these variables:

   ```dotenv
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   ```

4. Create the database tables:

   ```bash
   python create_tables.py
   ```

5. Start the dashboard:

   ```bash
   streamlit run dashboard.py
   ```

The AI Research Assistant additionally requires Ollama to be running locally with the `qwen3.5:4b` model installed. Database credentials in `.env` must never be committed to Git.

## Testing

Run the automated test suite with:

```bash
python -m pytest -q
```

## Data and Privacy Limitations
Investment results are limited to the reports that were accessible and imported. A missing record does not prove that a startup has never received investment. Reported deal amounts may describe an entire funding round rather than one investor's contribution.

The local AI assistant uses database search results to answer questions; it does not make investment recommendations or decisions. Its responses should be checked against the evidence records and source links shown in the dashboard. Personal applicant contact information is excluded from the AI context.

The repository should contain only fictional applicant examples. Real application data, database credentials, and other confidential information must not be committed.