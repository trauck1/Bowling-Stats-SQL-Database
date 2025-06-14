**Bowling Score Database Project**

A Python-based web scraping and database management system for collecting, processing, and storing bowling game data from SyncPassport bowling score websites.

**Overview**

This project automates the collection of over 400 bowling game data by scraping bowling score websites and storing the processed information in a MySQL database. The system extracts detailed game statistics including scores, strikes, spares, and player information from HTML tables on bowling score websites.

**Features**

Web Scraping: Automated extraction of bowling game data from SyncPassport websites
Data Processing: Parsing of bowling scorecard formats including:

Frame-by-frame score analysis

Strike and spare detection

10th frame special scoring rules

Incomplete game filtering



**Database Integration**: MySQL database storage with structured data organization


**Calculation of key bowling metrics:**

Total game scores

Strike counts and opportunities

Spare counts and opportunities

Player performance tracking



**Files**

*bowlingDataBaseStartup.py*

The main database initialization script that:


Creates the initial MySQL database and table structure

Processes a predefined list of bowling URLs

Scrapes and stores all historical bowling data

Sets up the complete database schema

*insertURLs.py*

An interactive script for adding new bowling sessions:


Prompts user for new URLs to process

Connects to existing database

Adds new game data without duplicating the database setup

**Database Schema**

The system creates a games table with the following structure:

ColumnTypeDescriptiongameIDintUnique identifier for each gamenamevarchar(255)Player namedatedateDate of the bowling sessionscoreintTotal game scorestrikesintNumber of strikes achievedstrikeOsintTotal strike opportunitiessparesintNumber of spares achievedspareOsintTotal spare opportunitiesurlvarchar(255)Source URL for the game data

**Web Scraping Implementation**
The web scraper uses BeautifulSoup to parse HTML content from SyncPassport bowling websites:
Data Extraction Process

**HTML Parsing**: Extracts score tables with class ss-data
Game Row Processing: Identifies individual game rows with class notranslate
Frame Analysis: Processes each of the 10 bowling frames:

Handles standard frames (1-9) and special 10th frame rules
Parses ball-by-ball scoring notation (X for strikes, / for spares, - for misses)
Converts HTML scorecard format to numerical data



**Scoring Logic**

Strike Detection: Identifies 'X' markers and converts to pin counts
Spare Calculation: Processes '/' notation and calculates remaining pins
10th Frame Handling: Special logic for bonus balls in the final frame
Data Validation: Filters out incomplete games automatically

**Installation & Setup**
Prerequisites

pip install mysql-connector-python beautifulsoup4 requests

MySQL Database Setup

Ensure MySQL server is running

Update database credentials in the connection configuration:

pythonmydb = mysql.connector.connect(
    host="127.0.0.1",
    user="your_username",
    passwd="your_password"
)


**Initial Database Creation**

Run the startup script to create the database and populate initial data:
python bowlingDataBaseStartup.py

**Adding New Data**

Use the interactive script to add new bowling sessions:
python insertURLs.py
Usage Examples
Scraping a New Bowling Session

Run insertURLs.py

Enter the SyncPassport URL when prompted

Type 'END' when finished adding URLs

The script will automatically process and store the data


**Data Processing Flow**

URL Input: SyncPassport bowling score page URL

Date Extraction: Automatically extracts session date from page header

Game Parsing: Processes each player's scorecard

Statistical Calculation: Computes strikes, spares, and total scores

Database Storage: Inserts processed data with unique game IDs

**Key Functions**

getAllGames(): Scrapes all game data from a given URL

gameFormatter(): Converts raw HTML data to structured game arrays

calculateScores(): Implements bowling scoring rules and calculates totals

strikeCounter() & spareCounter(): Count successful strikes and spares

strikeOpportunityCounter() & spareOpportunityCounter(): Track total opportunities

dateFormatter(): Converts date strings to MySQL-compatible format


**URL Format**

The system is designed to work with SyncPassport bowling websites with URLs containing session identifiers and encoded event IDs.
Future Enhancements
Potential improvements could include:

Player performance analytics and trending
Data visualization and reporting features
Support for additional bowling website formats
Automated scheduling for regular data collection
Export functionality for statistical analysis

**Dependencies**

mysql-connector-python: MySQL database connectivity
beautifulsoup4: HTML parsing and web scraping
requests: HTTP request handling for web scraping
