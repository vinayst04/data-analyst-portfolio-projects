-- Airline Sentiment Dashboard: Simple SQL Checks
-- Table name: airline_tweets


-- Query 1: Overall sentiment KPIs
SELECT
    COUNT(*) AS total_tweets,
    SUM(is_negative) AS negative_tweets,
    SUM(is_positive) AS positive_tweets,
    ROUND(100.0 * SUM(is_negative) / COUNT(*), 2) AS negative_tweet_percent,
    ROUND(AVG(sentiment_confidence), 2) AS average_sentiment_confidence
FROM airline_tweets;


-- Query 2: Sentiment split
SELECT
    sentiment,
    COUNT(*) AS total_tweets,
    ROUND(AVG(sentiment_confidence), 2) AS average_confidence
FROM airline_tweets
GROUP BY sentiment
ORDER BY total_tweets DESC;


-- Query 3: Sentiment by airline
SELECT
    airline,
    COUNT(*) AS total_tweets,
    SUM(is_negative) AS negative_tweets,
    SUM(is_positive) AS positive_tweets,
    ROUND(100.0 * SUM(is_negative) / COUNT(*), 2) AS negative_tweet_percent
FROM airline_tweets
GROUP BY airline
ORDER BY negative_tweet_percent DESC;


-- Query 4: Complaint reasons
-- Only negative tweets have complaint reasons.
SELECT
    negative_reason,
    COUNT(*) AS negative_tweets
FROM airline_tweets
WHERE sentiment = 'negative'
GROUP BY negative_reason
ORDER BY negative_tweets DESC;


-- Query 5: Complaint reasons by airline
SELECT
    airline,
    negative_reason,
    COUNT(*) AS negative_tweets
FROM airline_tweets
WHERE sentiment = 'negative'
GROUP BY airline, negative_reason
ORDER BY airline, negative_tweets DESC;


-- Query 6: Daily sentiment trend
SELECT
    tweet_date,
    sentiment,
    COUNT(*) AS total_tweets
FROM airline_tweets
GROUP BY tweet_date, sentiment
ORDER BY tweet_date, sentiment;


-- Query 7: Negative tweet rate by hour
-- Shows which tweet hours have a higher negative tweet percentage.
SELECT
    tweet_hour,
    COUNT(*) AS total_tweets,
    SUM(is_negative) AS negative_tweets,
    ROUND(100.0 * SUM(is_negative) / COUNT(*), 2) AS negative_tweet_percent
FROM airline_tweets
GROUP BY tweet_hour
ORDER BY tweet_hour;


-- Query 8: High confidence negative tweet examples
SELECT
    airline,
    negative_reason,
    sentiment_confidence,
    retweet_count,
    tweet_clean
FROM airline_tweets
WHERE sentiment = 'negative'
  AND sentiment_confidence >= 0.90
ORDER BY retweet_count DESC
LIMIT 25;
