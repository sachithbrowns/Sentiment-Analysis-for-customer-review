import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pandas as pd
import os
from dotenv import load_dotenv
import pyodbc
from sqlalchemy import create_engine
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load environment variables
load_dotenv()
server = os.getenv("DB_SERVER")
database = os.getenv("DB_DATABASE")
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
analyzer = SentimentIntensityAnalyzer()

def preprocess_text(text):
    text = str(text).lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words]
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return " ".join(tokens)

def clean_text(text):
    if pd.isnull(text):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def assign_label(row):
    score = row.get('averagescore', 0)
    vader = row.get('vader_compound', 0)
    if vader > 0.2:
        vader_sentiment = 'Positive'
    elif vader < -0.2:
        vader_sentiment = 'Negative'
    else:
        vader_sentiment = 'Neutral'

    if score < 3 or vader_sentiment == 'Negative':
        return 'Negative (priority)'
    elif vader_sentiment == 'Neutral':
        return 'Neutral (informational)'
    else:
        return 'Positive (not a complaint)'

def process_csv(file_path):
    df = pd.read_csv(file_path)
    if 'CreatedOn' in df.columns:
        df['CreatedOn'] = pd.to_datetime(df['CreatedOn'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    df.drop(columns=['DeletedBy', 'DeletedOn', 'UpdatedBy', 'UpdatedOn', 'IsActive'], errors='ignore', inplace=True)
    df.columns = df.columns.str.strip().str.lower()

    df['cleaned_review'] = df['reviewany'].apply(preprocess_text)
    df['textblob_sentiment'] = df['cleaned_review'].apply(lambda x: TextBlob(x).sentiment.polarity)
    df['sentiment_label'] = df['textblob_sentiment'].apply(lambda x: 'Positive' if x > 0 else ('Negative' if x < 0 else 'Neutral'))
    df['cleaned_review'] = df['reviewany'].apply(clean_text)
    df['vader_compound'] = df['cleaned_review'].apply(lambda x: analyzer.polarity_scores(x)['compound'])
    df['final_label'] = df.apply(assign_label, axis=1)

    # Ensure df only includes columns already existing in the database
    allowed_columns = get_table_columns('fulldb')
    df = df[[col for col in df.columns if col in allowed_columns]]
    return df

def get_table_columns(table_name):
    query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'"
    with pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    ) as conn:
        return [row[0].lower() for row in conn.cursor().execute(query).fetchall()]

def insert_to_db(df):
    engine = create_engine(f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server")
    df.to_sql('fulldb', con=engine, if_exists='append', index=False, method='multi')

class SentimentAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SentimentAnalyzer")
        self.root.geometry("600x400")
        self.root.configure(bg="#e6f2ff")

        self.label = tk.Label(root, text="SentimentAnalyzer - CSV to SQL", font=("Helvetica", 16, "bold"), bg="#e6f2ff")
        self.label.pack(pady=20)

        self.upload_btn = tk.Button(root, text="Upload CSV", command=self.upload_file, font=("Arial", 12), bg="#4da6ff", fg="white")
        self.upload_btn.pack(pady=10)

        self.progress = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(pady=20)

        self.status_label = tk.Label(root, text="", font=("Arial", 12), bg="#e6f2ff")
        self.status_label.pack(pady=10)

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                self.status_label.config(text="Processing CSV file...")
                self.root.update_idletasks()
                self.progress['value'] = 25

                df = process_csv(file_path)

                self.progress['value'] = 60
                self.status_label.config(text="Inserting data into database...")
                self.root.update_idletasks()

                insert_to_db(df)

                self.progress['value'] = 100
                self.status_label.config(text="Data inserted into fulldb table successfully.")
                messagebox.showinfo("Success", "Data has been successfully inserted into the database.")

            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.status_label.config(text="An error occurred.")
                self.progress['value'] = 0

if __name__ == '__main__':
    root = tk.Tk()
    app = SentimentAnalyzerApp(root)
    root.mainloop()