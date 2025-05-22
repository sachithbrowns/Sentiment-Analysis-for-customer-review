# 📝 Customer Review Sentiment Analysis System

This project performs **end-to-end sentiment analysis** on customer feedback data. It includes data ingestion, preprocessing, sentiment scoring using both TextBlob and VADER models, and stores the enriched data in a SQL Server database. A Power BI dashboard visualizes the sentiment trends.

---

## 📁 Repository Structure

```bash
├── Dummy data/                # Sample or placeholder dataset
    ├──── Data.csv             # Raw dataset for processing
    ├──── EDA.csv              # Dataset used for exploratory analysis
├── .gitignore                 # Git ignore settings
├── Dashboard PNG.png          # BI report screenshot
├── EDA.ipynb                  # Exploratory Data Analysis notebook
├── Sentiment4ApiData.py       # Initial ETL script
├── app.py                     # GUI app for storing processed data with seniment analysis  to databse from  CSV files of API data
├── requirement.txt            # Required Python libraries
```

---


## 📊 Project Pipeline

![Process Pipeline](https://github.com/sachithbrowns/Sentiment-Analysis-for-customer-review/blob/ecc6362e5615fbe41bcaea2fbaa83dfe1b63b793/Images/Process%20Pipeline.png?raw=true)


---

## 🧠 Sentiment Analysis Details

* **TextBlob** is used to compute sentiment polarity (`textblob_sentiment`).
* **VADER** computes a compound score (`vader_compound`).
* A **hybrid rule-based label** is generated using average score and sentiment to derive a final label:

  * `Negative (priority)`
  * `Neutral (informational)`
  * `Positive (not a complaint)`

---

## 🖥️ GUI Application

A **Tkinter-based GUI** (`app.py`) allows users to:

* Upload a CSV file
* Clean and process the feedback
* Assign sentiment labels
* Insert data into the SQL Server database

---

## 🧪 Exploratory Data Analysis

See `EDA.ipynb` for analysis of:

* Review length
* Sentiment distribution
* Time trends
* Score vs. Sentiment relationship

---

## 🛢️ Database Setup

### ✅ Create SQL Server Database & Table

Use the following commands to create the required database and table.

```sql
-- Create the database
CREATE DATABASE FeedbackDB;
GO

-- Use the new database
USE FeedbackDB;
GO

-- Create the main table to store processed feedback
CREATE TABLE fulldb (
    reviewany NVARCHAR(MAX),
    averagescore FLOAT,
    createdon DATETIME,
    cleaned_review NVARCHAR(MAX),
    textblob_sentiment FLOAT,
    sentiment_label VARCHAR(20),
    vader_compound FLOAT,
    final_label VARCHAR(50)
);
```

---

## 📌 Requirements

Install required dependencies using:

```bash
pip install -r requirement.txt
```

Required libraries include:

* `pandas`
* `nltk`
* `textblob`
* `vaderSentiment`
* `sqlalchemy`
* `pyodbc`
* `python-dotenv`
* `tkinter` (built-in with Python)

---

## 📈 Power BI Dashboard

A sample Power BI report is included (`Dashboard PNG.png`) showcasing:

![Process Pipeline](https://github.com/sachithbrowns/Sentiment-Analysis-for-customer-review/blob/ecc6362e5615fbe41bcaea2fbaa83dfe1b63b793/Images/Dashboard%20PNG.png?raw=true)



* Total sentiment distribution
* Trends over time
* Customer review patterns
* Division wise customer expression

---

## 🔄 API Ingestion Script

Pulls real-time review data from an API and stores it into `Data.csv`, which can then be processed via the GUI app. We used `Sentiment4ApiData.py` For initial establishment of historical data.

---

## 💡 Future Improvements

* Automate daily ingestion using Azure Functions
* Deploy as web app using Flask/Streamlit
* Add model training for custom sentiment models
* Improve multilingual support

---

## 🧑‍💻 Author

**Sachith Yamannage**

Sentiment Analysis | Data Science | SQL Server | Python NLP
