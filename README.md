# WatGPT
The Military University of Technology in Warsaw chatbot

Current data sources for web scraping in excel:
https://1drv.ms/x/c/82f573414933f60c/EVgTXJyG6LVMvUQtJyMjDxoBvfdNat9JczEBHSaQ3rHPPw

## Installation

To install and set up the project, you can use the Python Poetry package manager. Follow the steps below:

**NOTE**: These instructions are tailored for Linux systems.

1. Make sure you have Python installed on your system. You can download it from the official Python website: [python.org](https://www.python.org/downloads/).

2. Install Poetry by running the following command in your terminal or command prompt:

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
    ```

   Then, export the Poetry binary directory to your system's PATH:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
    ```
   Optionaly you can add this line to your `~/.bashrc`.

   Then you can run the following command to apply the changes:
   ```bash
   source ~/.bashrc
   ```

   Also you can install `poetry-exec-plugin` to enable running scripts from the `pyproject.toml` file:
   ```bash
   poetry self add poetry-exec-plugin
   ```

3. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/KubiakJakub01/WatGPT.git
   cd WatGPT
    ```

4. Install the project dependencies using Poetry:

   ```bash
   poetry install --with dev
    ```

5. To activate the virtual environment, run the following command:

   ```bash
   source $(poetry env info --path)/bin/activate
    ```
    Optionaly you can add the following line to your `.bashrc`:
    ```bash
    alias activate="source $(poetry env info --path)/bin/activate"
    ```
    Then you can activate the virtual environment by running:
    ```bash
    activate
    ```
  
6. Setting Up Pre-commit Hooks:

	To ensure code quality and consistency, you can set up pre-commit hooks using the `pre-commit` tool. Follow these steps:

	```bash
	pre-commit install
	```

	Now, the pre-commit hooks will automatically run on every commit, ensuring that your code adheres to the specified standards.

## Database Structure

### pdf_chunks Table
Stores text chunks extracted from PDFs. Schema (from db_utils.py):
```sql 
CREATE TABLE pdf_chunks (  
  chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,  
  heading TEXT NOT NULL,  content TEXT NOT NULL,  
  source_file TEXT,  page_number INTEGER,  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
);
```
Columns:
- chunk_id: Auto-incrementing unique ID.
- heading: Title/section from PDF (e.g., "Academic Calendar").
- content: Extracted text chunk.
- source_file: PDF file path (e.g., "wat_data/informator_2024.pdf").
- page_number: Page number in the PDF where the chunk was found.


### Timetable Tables
1. block_hours: Defines lecture block times (e.g., block1 = 08:00-09:35).
```sql 
CREATE TABLE block_hours (  
  block_id TEXT PRIMARY KEY, -- e.g., "block1"  
  start_time TEXT NOT NULL, -- "08:00"  
  end_time TEXT NOT NULL -- "09:35" 
);
```

2. groups: Student groups (e.g., "WCY24IV1N2").
```sql
CREATE TABLE groups (  
  group_id INTEGER PRIMARY KEY AUTOINCREMENT,  
  group_code TEXT NOT NULL UNIQUE 
);
```

3. teachers: Instructor details.
```sql
CREATE TABLE teachers (  
  teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,  
  full_name TEXT NOT NULL, -- "Olejniczak Jarosław"  
  short_code TEXT -- Optional abbreviation (e.g., "OJ") 
);
```

4. courses: Course metadata.
```sql
CREATE TABLE courses (  
  course_id INTEGER PRIMARY KEY AUTOINCREMENT,  
  course_code TEXT NOT NULL, -- Short code (e.g., "MumII")  
  course_name TEXT -- Full name (optional) 
);
```

5. lessons: Scheduled lessons linked to groups/teachers/courses.
```sql
CREATE TABLE lessons (  
  lesson_id INTEGER PRIMARY KEY AUTOINCREMENT,  
  group_id INTEGER NOT NULL,  
  course_id INTEGER NOT NULL,  
  teacher_id INTEGER,  
  block_id TEXT NOT NULL, -- References block_hours  
  lesson_date TEXT NOT NULL, -- "YYYY-MM-DD" or "YYYY_MM_DD"  
  room TEXT, -- "308"  
  building TEXT, -- "65"  
  info TEXT, -- Additional notes  
  FOREIGN KEY (group_id) REFERENCES groups(group_id),  ... 
); 
```


## Running the Code
Make sure to activate the poetry environment before running these scripts:
```bash
source $(poetry env info --path)/bin/activate
```
or run command with `poetry run` ex.:
```bash
poetry run python -m watgpt.scripts.create_chunk_db
```

### Chunk Database

1. **Create Chunk Database**
	Run the setup script to extract PDF data and populate the database:
	```bash
	python -m watgpt.scripts.create_chunk_db
	```
	This will:
	- Create chunks.db (SQLite database).
	- Extract text from PDFs in wat_data/ and store in pdf_chunks.
	- Scrape timetable data from the provided URL and populate timetable tables.

2. **Query Chunk Database**:
	Query data with the example script:
	```bash
	python -m watgpt.scripts.query_chunk_db
	```
	Outputs all PDF chunks and lessons for group `WCY24IV1N2`.

### Vector Database

1. **Create Vector Database**:
	To create the vector database, run the following script:
	```bash
	python -m watgpt.scripts.create_vector_db
	```
	This will:
	- Create `vectors.db` (SQLite database).
	- Convert text chunks from `chunks.db` into vector representations.
	- Store these vectors in the `vectors` table.

2. **Query Vector Database**:
	To query the vector database, use the following script:
	```bash
	python -m watgpt.scripts.query_vector_db -h
	```
	This script will:
	- Accept a query text input.
	- Convert the query into a vector.
	- Find and return the most similar text chunks from the `vectors` table.

## Checking the Database
Use SQLite CLI or a tool like DB Browser for SQLite:
bash sqlite3 chunks.db 
Example queries:
```sql
SELECT * FROM pdf_chunks LIMIT 5; 
-- View first 5 PDF chunks SELECT * FROM lessons WHERE group_id = 1; -- Lessons for group_id=1 
```


## Data Formats
### PDF Chunks (from watgpt/reader/read_calendar_pdf.py & read_structured_pdf.py):
- heading: Section title (e.g., "ORGANIZACJA ZAJĘĆ W ROKU AKADEMICKIM 2024/2025
/STUDIA STACJONARNE CYWILNE/").
- content: Text grouped into chunks of ~5 rows or sentences.
- source_file: Path to the original PDF.
- page_number: Page where the chunk was extracted.


### Timetable Data (from timetable_scraper.py):
- date: Format YYYY_MM_DD (e.g., "2024_10_05").
- block_id: Lecture block (e.g., "block1").
- course_code: Short code (e.g., "MumII").
- teacher_name: Full name parsed from scraped info.
- room: Room number (e.g., "308").
- building: Building number (e.g., "65").
