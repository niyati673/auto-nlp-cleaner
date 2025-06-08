import os
import re
import string
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from bs4 import BeautifulSoup
import requests

nltk.download('punkt_tab')

INPUT_FILE = "input.xlsx"
OUTPUT_FILE = "Output.xlsx"
TEXT_DIR = "articles_text"
STOPWORDS_DIR = "StopWords"
MASTER_DICT = "MasterDictionary"

# Load Stop Words
def load_stopwords():
    stop_words = set()
    for file in os.listdir(STOPWORDS_DIR):
        with open(os.path.join(STOPWORDS_DIR, file), "r", encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    stop_words.add(line.strip().lower())
    return stop_words

# Load sentiment dictionaries
def load_sentiment_dict():
    with open(os.path.join(MASTER_DICT, "positive-words.txt"), "r") as f:
        positive_words = set(word.strip().lower() for word in f if word.strip() and not word.startswith(';'))
    with open(os.path.join(MASTER_DICT, "negative-words.txt"), "r") as f:
        negative_words = set(word.strip().lower() for word in f if word.strip() and not word.startswith(';'))
    return positive_words, negative_words

# Clean and tokenize text
def clean_text(text, stop_words):
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text,language='english')
    tokens = [t for t in tokens if t not in stop_words]
    return tokens

# Extract content from webpage
def extract_text(url):
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h1')
        article = soup.find_all('p')
        title_text = title.get_text().strip() if title else ""
        body_text = " ".join([p.get_text().strip() for p in article])
        return f"{title_text}\n{body_text}"
    except Exception as e:
        print(f"Error extracting {url}: {e}")
        return ""

# Count syllables in a word
def count_syllables(word):
    word = word.lower()
    vowels = "aeiou"
    count = 0
    if word and word[0] in vowels:
        count += 1
    for i in range(1, len(word)):
        if word[i] in vowels and word[i - 1] not in vowels:
            count += 1
    if word.endswith("es") or word.endswith("ed"):
        count -= 1
    if count <= 0:
        count = 1
    return count

# Count personal pronouns
def count_pronouns(text):
    return len(re.findall(r'\b(I|we|my|ours|us)\b', text, re.I)) - len(re.findall(r'\bUS\b', text))

# Compute all metrics
def compute_metrics(text, cleaned_tokens, pos_words, neg_words):
    sentences = sent_tokenize(text,language='english')
    word_count = len(cleaned_tokens)
    pos_score = sum(1 for word in cleaned_tokens if word in pos_words)
    neg_score = sum(1 for word in cleaned_tokens if word in neg_words)

    polarity = (pos_score - neg_score) / ((pos_score + neg_score) + 0.000001)
    subjectivity = (pos_score + neg_score) / (word_count + 0.000001)

    avg_sentence_len = word_count / (len(sentences) + 0.000001)
    complex_words = [w for w in cleaned_tokens if count_syllables(w) > 2]
    percentage_complex_words = len(complex_words) / (word_count + 0.000001)
    fog_index = 0.4 * (avg_sentence_len + percentage_complex_words)

    syllables_per_word = sum(count_syllables(w) for w in cleaned_tokens) / (word_count + 0.000001)
    avg_word_len = sum(len(w) for w in cleaned_tokens) / (word_count + 0.000001)
    personal_pronouns = count_pronouns(text)

    return {
        "POSITIVE SCORE": pos_score,
        "NEGATIVE SCORE": neg_score,
        "POLARITY SCORE": polarity,
        "SUBJECTIVITY SCORE": subjectivity,
        "AVG SENTENCE LENGTH": avg_sentence_len,
        "PERCENTAGE OF COMPLEX WORDS": percentage_complex_words,
        "FOG INDEX": fog_index,
        "AVG NUMBER OF WORDS PER SENTENCE": avg_sentence_len,
        "COMPLEX WORD COUNT": len(complex_words),
        "WORD COUNT": word_count,
        "SYLLABLE PER WORD": syllables_per_word,
        "PERSONAL PRONOUNS": personal_pronouns,
        "AVG WORD LENGTH": avg_word_len,
    }

def main():
    stop_words = load_stopwords()
    pos_words, neg_words = load_sentiment_dict()

    df = pd.read_excel(INPUT_FILE)
    results = []

    if not os.path.exists(TEXT_DIR):
        os.makedirs(TEXT_DIR)

    for _, row in df.iterrows():
        url_id = row["URL_ID"]
        url = row["URL"]

        print(f"Processing {url_id}: {url}")
        raw_text = extract_text(url)
        if not raw_text.strip():
            print(f" Skipping {url_id} due to empty or failed extraction.")
            continue
        text_path = os.path.join(TEXT_DIR, f"{url_id}.txt")
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(raw_text)

        cleaned_tokens = clean_text(raw_text, stop_words)
        metrics = compute_metrics(raw_text, cleaned_tokens, pos_words, neg_words)
        result_row = row.to_dict()
        result_row.update(metrics)
        results.append(result_row)

    result_df = pd.DataFrame(results)
    result_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n Analysis completed. Results saved to '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()
