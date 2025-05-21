# Access DB and load data
import os
from dotenv import load_dotenv
import pyodbc
import pandas as pd
import numpy as np

# Visualization
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import missingno as msno

# Text processing
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

# Get credentials from .env file
server = os.getenv("DB_SERVER")
database = os.getenv("DB_DATABASE")
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")

# Define the connection string
conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password}"
)

# Connect and load a table
conn = pyodbc.connect(conn_str)
query = "SELECT * FROM fulldb"
df = pd.read_sql(query, conn)

# Preview the data
print(df.head())

#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################

df2 = pd.read_csv('testcsv.csv')
print(df2.head())

import nltk

# Download necessary NLTK datasets
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

# Convert date columns to datetime
df2['CreatedOn'] = pd.to_datetime(df2['CreatedOn'], errors='coerce')

# Drop irrelevant columns
drop_columns = ['DeletedBy', 'DeletedOn', 'UpdatedBy', 'UpdatedOn', 'IsActive']
df2 = df2.drop(columns=drop_columns, errors='ignore')

import nltk
nltk.data.path.append('/custom/path/to/nltk_data')
nltk.download('punkt', download_dir='/custom/path/to/nltk_data')

if 'CreatedOn' in df2.columns:
    df2['CreatedOn'] = pd.to_datetime(df2['CreatedOn'], errors='coerce')

import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')


# Initialize NLP tools
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Function to preprocess text
def preprocess_text(text):
    text = str(text).lower()  # Convert to lowercase
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = text.translate(str.maketrans("", "", string.punctuation))  # Remove punctuation
    tokens = word_tokenize(text)  # Tokenization
    tokens = [word for word in tokens if word not in stop_words]  # Stopword removal
    tokens = [lemmatizer.lemmatize(word) for word in tokens]  # Lemmatization
    return " ".join(tokens)

import nltk
from sqlalchemy import create_engine
nltk.download('punkt_tab')
# Apply preprocessing
df2['Cleaned_Review'] = df2['ReviewAny'].apply(preprocess_text)

# Apply sentiment scoring (TextBlob only)
df2['TextBlob_Sentiment'] = df2['Cleaned_Review'].apply(lambda x: TextBlob(x).sentiment.polarity)

# Categorize sentiment
df2['Sentiment_Label'] = df2['TextBlob_Sentiment'].apply(lambda x: 'Positive' if x > 0 else ('Negative' if x < 0 else 'Neutral'))

df2.head()

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Step 1: Preprocess text (optional - but good practice)
def clean_text(text):
    if pd.isnull(text):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)  # Remove non-alphabetic characters
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    return text

df2['Cleaned_Review'] = df2['ReviewAny'].apply(clean_text)

# Step 2: Calculate VADER polarity
df2['VADER_Compound'] = df2['Cleaned_Review'].apply(lambda x: analyzer.polarity_scores(x)['compound'])

# Inspect and trim spaces just in case
df2.columns = df2.columns.str.strip()
df2.columns = df2.columns.str.strip()        # remove whitespace
df2.columns = df2.columns.str.lower()        # convert to lowercase

# Adjust your code:
def assign_label(row):
    score = row['AverageScore']  # make sure this matches exactly
    vader = row['VADER_Compound']
    
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

print(df2.head())

# Insert df2 data into the database fulldb table

# Create a SQLAlchemy engine
engine = create_engine(f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server")

# Insert data into the database
df2.to_sql('fulldb', con=engine, if_exists='append', index=False)

print("Data inserted into fulldb table successfully.")