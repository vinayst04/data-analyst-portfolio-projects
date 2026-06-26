# Airline Customer Sentiment and Complaint Analytics Dashboard

This project analyzes airline tweets to compare sentiment, complaint reasons, airline-level negative rates, daily trends and hourly negative tweet patterns.

## Tools Used

- Python and Pandas for text cleaning and feature creation
- MySQL for SQL analysis
- Power BI for dashboard building

## Dataset

- Source file: `data/raw/Tweets.csv`
- Cleaned file: `data/processed/airline_sentiment_clean.csv`
- Rows: 14,640

## Work Completed

- Cleaned tweet text by removing links, mentions and hashtag symbols.
- Renamed columns for easier analysis.
- Created `sentiment_score`, `is_negative`, `is_positive`, `high_confidence_flag`, `tweet_date`, `tweet_hour`, `tweet_weekday`, `tweet_clean`, and `tweet_word_count`.
- Created summary files for complaint reasons and negative tweet keywords.
- Wrote SQL queries for sentiment KPIs, airline comparison, complaint reasons, daily trend, hourly pattern, location summary and retweets.
- Built a two-page Power BI dashboard for sentiment overview and complaint deep dive.

## Key Results

- Total Tweets: `14,640`
- Negative Tweets: `9,178`
- Neutral Tweets: `3,099`
- Positive Tweets: `2,363`
- Negative Tweet Share: `62.69%`
- Average Sentiment Confidence: `0.90`
- Top complaint reason: `Customer Service Issue`

## Power BI Report

https://app.powerbi.com/view?r=eyJrIjoiNGE5YjJmMTctMGMyZi00MTIzLWE0NmItZTQwMGE2ZjcxZWU1IiwidCI6IjgxM2E3NTMyLWI4YmEtNDNhZi1iMWYyLWRiMWFlMGY2NzA1YiJ9

## Important Files

- `src/clean_airline_sentiment.py`
- `sql/airline_sentiment_queries.sql`
- `dashboard/powerbi_measures.dax`
- `dashboard/Airline_Sentiment_Dashboard.pbix`
- `outputs/query_results_csv/`

## Run Python Cleaning

```bash
pip install -r requirements.txt
python src/clean_airline_sentiment.py
```
