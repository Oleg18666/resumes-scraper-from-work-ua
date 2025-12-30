# resumes-scraper-from-work-ua
script for scraping resumes from work.ua web site
<p>Main script  has name <i>"resume_scraper_from_work_ua.py"</i>. When executed, it will scrap
<b>IT specialists resumes</b>(only if they have photo in them) from ukrainian site 'www.work.ua' 
    and save them to Postgres database.<br/>
    This particular version of the script scraping only resumes in 'Kyiv' region, but you can change it by changing
    link inside 'category_city_url' variable. 
 </p>
   <b>Scraped fields:</b> 
    <li>person_name</li>
    <li>resume_date - date, when resume was uploaded to the site (Will not scrap same resume for particular date twice).</li>
    <li>photo - person's photo in binary format</li>
    <li>position - position, resume applying for</li>
    <li>salary- desired salary</li> 
    <li> employment_type - (full_time, part_time,from_home)</li>
    <li>birthday - person's birthday</li>
    <li>personal information - work_experience, education, additional_education, skills, languages,
                    recommendations, additional_info(some filds can be empty).</li> 
   <p> <b>NOTE:</b> before running <i>"resume_scraper_from_work_ua.py"</i> script,
   you need to create and set up a Postgresql database (use <i>'create_postgresql_db.py'</i> script for this purpose).
    Also, you need to <b>download and install:</b> requests, BeautifulSoup and psycopg2 libraries.<br/>
    You'll find examples of html code from scraping pages in this repository.</p>


## Pipeline Architecture

This repository contains a scalable ETL pipeline for scraping Work.ua resumes:

### Project Structure
```
resumes-scraper-from-work-ua/
├── config/
│   └── settings.py          # Configuration (DB, queue, scraping settings)
├── workua_scraper/
│   ├── __init__.py
│   ├── models.py            # Data models (Resume, ResumeCard, Task)
│   ├── client.py            # HTTP client with retry logic
│   ├── parser_search.py     # Search results page parser
│   ├── parser_resume.py     # Individual resume page parser
│   ├── repository.py        # Database access layer
│   ├── queue.py             # Queue abstraction (RabbitMQ/Redis/Postgres)
│   └── pipeline.py          # Pipeline orchestration
├── scripts/
│   ├── run_scheduler.py     # Task scheduler (generates search pages)
│   └── run_worker.py        # Worker processes (parse & save)
├── migrations/
│   └── schema.sql           # PostgreSQL database schema
├── requirements.txt
└── README.md
```

### Database Schema (PostgreSQL)

- **resumes** - Main resume data (id, name, position, salary, employment_type, etc.)
- **resume_details** - Extended text fields (experience, education, skills)
- **resume_photos** - Binary photo storage with hash-based deduplication
- **search_pages** - Tracks scraping progress by page
- **resume_tasks** - Task queue (alternative to external broker)

### Pipeline Flow

1. **Scheduler** (`run_scheduler.py`):
   - Generates search page tasks based on categories, cities, days filter
   - Pushes tasks to queue (RabbitMQ/Redis/Postgres)

2. **Search Worker**:
   - Fetches search page HTML
   - Parses resume cards (ID, position, person name, city, education)
   - Creates resume page tasks

3. **Resume Worker**:
   - Fetches full resume HTML
   - Extracts all fields (experience, skills, languages, etc.)
   - Downloads and stores photo (if present)
   - Saves to PostgreSQL with UPSERT on (resume_id, resume_date)

### Key Features

- **Queue-based architecture**: Decouples discovery from scraping
- **Deduplication**: Unique constraint on (resume_id, resume_date)
- **Retry logic**: Configurable retries with exponential backoff
- **Scalable**: Run multiple workers in parallel
- **Configurable**: Categories, cities, filters via config/settings.py
