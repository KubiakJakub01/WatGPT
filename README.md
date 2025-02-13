# WatGPT
The Military University of Technology in Warsaw chatbot

## Database Structure

### pdf_chunks Table
Stores text chunks extracted from PDFs. Schema (from db_utils.py):
sql CREATE TABLE pdf_chunks (  chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,  heading TEXT NOT NULL,  content TEXT NOT NULL,  source_file TEXT,  page_number INTEGER,  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ); 
Columns:
- chunk_id: Auto-incrementing unique ID.
- heading: Title/section from PDF (e.g., "Academic Calendar").
- content: Extracted text chunk.
- source_file: PDF file path (e.g., "wat_data/informator_2024.pdf").
- page_number: Page number in the PDF where the chunk was found.


### Timetable Tables
1. block_hours: Defines lecture block times (e.g., block1 = 08:00-09:35).
```sql 
CREATE TABLE block_hours (  block_id TEXT PRIMARY KEY, -- e.g., "block1"  start_time TEXT NOT NULL, -- "08:00"  end_time TEXT NOT NULL -- "09:35" );
```

2. groups: Student groups (e.g., "WCY24IV1N2").
```sql
CREATE TABLE groups (  group_id INTEGER PRIMARY KEY AUTOINCREMENT,  group_code TEXT NOT NULL UNIQUE );
```

3. teachers: Instructor details.
```sql
CREATE TABLE teachers (  teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,  full_name TEXT NOT NULL, -- "Olejniczak Jarosław"  short_code TEXT -- Optional abbreviation (e.g., "OJ") );
```

4. courses: Course metadata.
```sql
CREATE TABLE courses (  course_id INTEGER PRIMARY KEY AUTOINCREMENT,  course_code TEXT NOT NULL, -- Short code (e.g., "MumII")  course_name TEXT -- Full name (optional) );
```

5. lessons: Scheduled lessons linked to groups/teachers/courses.
```sql
CREATE TABLE lessons (  lesson_id INTEGER PRIMARY KEY AUTOINCREMENT,  group_id INTEGER NOT NULL,  course_id INTEGER NOT NULL,  teacher_id INTEGER,  block_id TEXT NOT NULL, -- References block_hours  lesson_date TEXT NOT NULL, -- "YYYY-MM-DD" or "YYYY_MM_DD"  room TEXT, -- "308"  building TEXT, -- "65"  info TEXT, -- Additional notes  FOREIGN KEY (group_id) REFERENCES groups(group_id),  ... ); 
```


## Running the Code
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the setup script to extract PDF data and populate the database:
```bash
python db_setup.py
```
This will:
- Create chunks.db (SQLite database).
- Extract text from PDFs in wat_data/ and store in pdf_chunks.
- Scrape timetable data from the provided URL and populate timetable tables.

3. Verify data with the example script:
```bash
python db_usage_example.py
```
Outputs all PDF chunks and lessons for group "WCY24IV1N2".


## Checking the Database
Use SQLite CLI or a tool like DB Browser for SQLite:
bash sqlite3 chunks.db 
Example queries:
```sql
SELECT * FROM pdf_chunks LIMIT 5; -- View first 5 PDF chunks SELECT * FROM lessons WHERE group_id = 1; -- Lessons for group_id=1 
```


## Data Formats
### PDF Chunks (from read_calendar_pdf.py/read_structured_pdf.py):
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


## Notes
- Adjust pdf_path_1/pdf_path_2 in db_setup.py if PDF paths change.
- Timetable URL in db_setup.py can be modified to scrape different groups.
- Foreign keys (e.g., group_id) ensure relational integrity between tables.