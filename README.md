# auto-nlp-cleaner
auto-nlp-cleaner is a Python pipeline that automates web scraping, text cleaning, and NLP preprocessing from blog URLs. It extracts article content, removes noise, tokenizes text using NLTK, and stores cleaned tokens in Excel—ready for sentiment analysis or ML tasks.

## 🔍 Overview

This tool automates the following steps:
- Web scraping of article content from a list of URLs
- HTML parsing and main content extraction
- Text cleaning (lowercasing, removing punctuation, symbols, numbers, etc.)
- Tokenization and stopword removal using NLTK
- Exporting cleaned, tokenized text into a structured Excel file

---

## 📁 Input

An Excel file named `input.xlsx` containing:
- `URL`: Blog article link
- `ID`: Unique identifier (e.g., `Netclan20241017`)

---

## 🧪 Output

An Excel file named `output.xlsx` containing:
- `ID`: From input
- `URL`: Original blog URL
- `Cleaned_Text`: Final processed, tokenized text

---

## ⚙️ Dependencies

Install the following Python libraries before running the script:

pip install pandas requests beautifulsoup4 nltk openpyxl

🧠 Technologies Used
pandas – Excel read/write and data handling

requests – Fetching web page HTML

beautifulsoup4 – Parsing and extracting HTML

nltk – Tokenization and stopword removal

re – Text pattern cleaning (regex)

openpyxl – Excel output support

🚀 How to Run

Make sure input.xlsx is in the project folder.

python main.py

The output will be saved as output.xlsx.
