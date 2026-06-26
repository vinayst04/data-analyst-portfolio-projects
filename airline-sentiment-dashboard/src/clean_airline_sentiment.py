import html

import pandas as pd


raw_file = "data/raw/Tweets.csv"
clean_file = "data/processed/airline_sentiment_clean.csv"
keyword_file = "data/processed/negative_tweet_keywords.csv"
reason_file = "data/processed/negative_reason_summary.csv"


df = pd.read_csv(raw_file)

df = df[[
    "tweet_id",
    "airline_sentiment",
    "airline_sentiment_confidence",
    "negativereason",
    "negativereason_confidence",
    "airline",
    "retweet_count",
    "text",
    "tweet_created",
    "tweet_location",
    "user_timezone",
]].copy()

df = df.rename(columns={
    "airline_sentiment": "sentiment",
    "airline_sentiment_confidence": "sentiment_confidence",
    "negativereason": "negative_reason",
    "negativereason_confidence": "negative_reason_confidence",
    "text": "tweet_text",
})

clean_tweets = []
for tweet in df["tweet_text"]:
    tweet = html.unescape(str(tweet))
    words = tweet.split()

    clean_words = []
    for word in words:
        if word.startswith("http"):
            continue
        if word.startswith("www."):
            continue
        if word.startswith("@"):
            continue

        word = word.replace("#", "")
        clean_words.append(word)

    clean_tweets.append(" ".join(clean_words))

df["tweet_clean"] = clean_tweets

df["negative_reason"] = df["negative_reason"].fillna("Not Negative")
df["negative_reason_confidence"] = df["negative_reason_confidence"].fillna(0)

df["tweet_location_clean"] = df["tweet_location"].fillna("Unknown").astype(str).str.strip()
df.loc[df["tweet_location_clean"] == "", "tweet_location_clean"] = "Unknown"

df["user_timezone_clean"] = df["user_timezone"].fillna("Unknown").astype(str).str.strip()
df.loc[df["user_timezone_clean"] == "", "user_timezone_clean"] = "Unknown"

tweet_dates = pd.to_datetime(df["tweet_created"], errors="coerce", utc=True)
df["tweet_datetime_utc"] = tweet_dates.dt.strftime("%Y-%m-%d %H:%M:%S")
df["tweet_date"] = tweet_dates.dt.strftime("%Y-%m-%d")
df["tweet_hour"] = tweet_dates.dt.hour.fillna(0).astype(int)
df["tweet_weekday"] = tweet_dates.dt.day_name()

df["sentiment_score"] = df["sentiment"].map({
    "positive": 1,
    "neutral": 0,
    "negative": -1,
})

df["is_negative"] = (df["sentiment"] == "negative").astype(int)
df["is_positive"] = (df["sentiment"] == "positive").astype(int)
df["high_confidence_flag"] = (df["sentiment_confidence"] >= 0.80).astype(int)

word_counts = []
for tweet in df["tweet_clean"]:
    words_in_tweet = 0
    current_word = ""

    for letter in str(tweet):
        if letter.isalpha():
            current_word = current_word + letter
        else:
            if current_word != "":
                words_in_tweet = words_in_tweet + 1
                current_word = ""

    if current_word != "":
        words_in_tweet = words_in_tweet + 1

    word_counts.append(words_in_tweet)
df["tweet_word_count"] = word_counts

final_columns = [
    "tweet_id",
    "airline",
    "sentiment",
    "sentiment_score",
    "sentiment_confidence",
    "negative_reason",
    "negative_reason_confidence",
    "retweet_count",
    "tweet_text",
    "tweet_clean",
    "tweet_created",
    "tweet_datetime_utc",
    "tweet_date",
    "tweet_hour",
    "tweet_weekday",
    "tweet_location_clean",
    "user_timezone_clean",
    "is_negative",
    "is_positive",
    "high_confidence_flag",
    "tweet_word_count",
]

df = df[final_columns]
df.to_csv(clean_file, index=False)

negative_df = df[df["sentiment"] == "negative"]

reason_df = negative_df["negative_reason"].value_counts().reset_index()
reason_df.columns = ["negative_reason", "negative_tweets"]
reason_df["reason_percent"] = (reason_df["negative_tweets"] / len(negative_df) * 100).round(2)
reason_df.to_csv(reason_file, index=False)

stopwords = {
    "the", "and", "for", "you", "your", "that", "this", "with", "have",
    "was", "were", "are", "but", "not", "from", "they", "there", "their",
    "what", "when", "where", "why", "how", "can", "could", "would", "should",
    "flight", "flights", "airline", "airlines", "http", "https", "amp",
    "united", "southwestair", "delta", "usairways", "americanair", "jetblue",
    "get", "got", "now", "just", "been", "still", "will", "more", "than",
    "then", "about", "into", "out", "all", "our", "its", "too", "very",
    "please", "thanks", "thank", "today", "tomorrow", "yesterday", "time",
    "hours", "hour",
}

all_words = []
for tweet in negative_df["tweet_clean"]:
    current_word = ""

    for letter in str(tweet).lower():
        if letter.isalpha():
            current_word = current_word + letter
        else:
            if len(current_word) >= 3 and current_word not in stopwords:
                all_words.append(current_word)
            current_word = ""

    if len(current_word) >= 3 and current_word not in stopwords:
        all_words.append(current_word)

word_count = {}
for word in all_words:
    if word in word_count:
        word_count[word] = word_count[word] + 1
    else:
        word_count[word] = 1

keyword_rows = []
for word, count in word_count.items():
    keyword_rows.append({
        "keyword": word,
        "count": count,
    })

keyword_df = pd.DataFrame(keyword_rows)
keyword_df = keyword_df.sort_values("count", ascending=False).head(40)
keyword_df.to_csv(keyword_file, index=False)


print("Airline sentiment files created.")
print("Rows:", len(df))
print("Negative tweet %:", round(df["is_negative"].mean() * 100, 2))
print("Top complaint reason:", reason_df.iloc[0]["negative_reason"])
