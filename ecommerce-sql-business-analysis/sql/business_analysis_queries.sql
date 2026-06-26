-- Olist E-commerce SQL Business Analysis
-- Same outputs as the original SQL file, written in a simpler step-by-step style.


-- Query 1: Overall business KPIs
-- One line = one metric.
SELECT
    (SELECT COUNT(DISTINCT order_id) FROM olist_orders) AS total_orders,
    (SELECT COUNT(DISTINCT order_id) FROM olist_orders WHERE order_status = 'delivered') AS delivered_orders,
    (SELECT COUNT(DISTINCT customer_unique_id) FROM olist_customers) AS unique_customers,
    (SELECT COUNT(DISTINCT seller_id) FROM olist_order_items) AS active_sellers,
    (SELECT ROUND(SUM(price), 2) FROM olist_order_items) AS product_revenue,
    (SELECT ROUND(SUM(freight_value), 2) FROM olist_order_items) AS freight_value,
    (SELECT ROUND(SUM(price + freight_value), 2) FROM olist_order_items) AS order_item_total_value;


-- Query 2: Monthly revenue trend
-- Step 1: get monthly totals.
-- Step 2: add previous month revenue.
-- Step 3: subtract to get revenue change.
WITH monthly AS (
    SELECT
        LEFT(o.order_purchase_timestamp, 7) AS year_month,
        COUNT(DISTINCT o.order_id) AS orders,
        ROUND(SUM(oi.price), 2) AS product_revenue
    FROM olist_orders o
    JOIN olist_order_items oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY year_month
),
with_previous_month AS (
    SELECT
        year_month,
        orders,
        product_revenue,
        LAG(product_revenue) OVER (ORDER BY year_month) AS previous_month_revenue
    FROM monthly
)
SELECT
    year_month,
    orders,
    product_revenue,
    previous_month_revenue,
    ROUND(product_revenue - previous_month_revenue, 2) AS revenue_change
FROM with_previous_month
ORDER BY year_month;


-- Query 3: Top product categories by revenue
SELECT
    CASE
        WHEN t.product_category_name_english IS NOT NULL THEN t.product_category_name_english
        WHEN p.product_category_name IS NOT NULL THEN p.product_category_name
        ELSE 'unknown'
    END AS category,
    COUNT(DISTINCT oi.order_id) AS orders,
    COUNT(*) AS items_sold,
    ROUND(SUM(oi.price), 2) AS product_revenue,
    ROUND(AVG(oi.price), 2) AS average_item_price
FROM olist_order_items oi
LEFT JOIN olist_products p
    ON oi.product_id = p.product_id
LEFT JOIN product_category_translation t
    ON p.product_category_name = t.product_category_name
GROUP BY category
ORDER BY product_revenue DESC
LIMIT 15;


-- Query 4: Revenue by customer state
SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS orders,
    COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
    ROUND(SUM(oi.price), 2) AS product_revenue,
    ROUND(SUM(oi.price) / COUNT(DISTINCT o.order_id), 2) AS revenue_per_order
FROM olist_orders o
JOIN olist_customers c
    ON o.customer_id = c.customer_id
JOIN olist_order_items oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY product_revenue DESC;


-- Query 5: Top sellers by revenue
-- Step 1: calculate seller revenue.
-- Step 2: rank sellers by revenue.
WITH seller_sales AS (
    SELECT
        s.seller_id,
        s.seller_city,
        s.seller_state,
        COUNT(DISTINCT oi.order_id) AS orders,
        ROUND(SUM(oi.price), 2) AS product_revenue
    FROM olist_order_items oi
    JOIN olist_sellers s
        ON oi.seller_id = s.seller_id
    GROUP BY s.seller_id, s.seller_city, s.seller_state
)
SELECT
    RANK() OVER (ORDER BY product_revenue DESC) AS seller_rank,
    seller_id,
    seller_city,
    seller_state,
    orders,
    product_revenue
FROM seller_sales
ORDER BY seller_rank
LIMIT 15;


-- Query 6: Seller revenue share
-- Share = seller revenue / total revenue.
SELECT
    seller_id,
    ROUND(SUM(price), 2) AS product_revenue,
    ROUND(100.0 * SUM(price) / (SELECT SUM(price) FROM olist_order_items), 2) AS revenue_share_percent
FROM olist_order_items
GROUP BY seller_id
ORDER BY product_revenue DESC
LIMIT 20;


-- Query 7: Repeat customer analysis
-- Step 1: count orders per customer.
-- Step 2: label customer as one-time or repeat.
-- Step 3: count each group.
WITH order_counts AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM olist_orders o
    JOIN olist_customers c
        ON o.customer_id = c.customer_id
    GROUP BY c.customer_unique_id
),
customer_type_table AS (
    SELECT
        CASE
            WHEN order_count = 1 THEN 'One-time customer'
            ELSE 'Repeat customer'
        END AS customer_type
    FROM order_counts
)
SELECT
    customer_type,
    COUNT(*) AS customers,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customer_type_table), 2) AS customer_percent
FROM customer_type_table
GROUP BY customer_type
ORDER BY customers DESC;


-- Query 8: Payment method analysis
SELECT
    payment_type,
    COUNT(*) AS payment_records,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(payment_value), 2) AS total_payment_value,
    ROUND(AVG(payment_value), 2) AS average_payment_value,
    ROUND(AVG(payment_installments), 2) AS average_installments
FROM olist_order_payments
GROUP BY payment_type
ORDER BY total_payment_value DESC;


-- Query 9: Delivery performance summary
-- Step 1: mark each delivered order as late or not late.
-- Step 2: summarize delivery days and late order count.
WITH delivered_orders AS (
    SELECT
        order_id,
        DATEDIFF(order_delivered_customer_date, order_purchase_timestamp) AS delivery_days,
        CASE
            WHEN date(order_delivered_customer_date) > date(order_estimated_delivery_date)
            THEN 1
            ELSE 0
        END AS is_late
    FROM olist_orders
    WHERE order_status = 'delivered'
      AND order_delivered_customer_date IS NOT NULL
)
SELECT
    COUNT(order_id) AS delivered_orders,
    ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
    SUM(is_late) AS late_orders,
    ROUND(100.0 * SUM(is_late) / COUNT(order_id), 2) AS late_delivery_percent
FROM delivered_orders;


-- Query 10: Late delivery by state
WITH delivered_orders AS (
    SELECT
        o.order_id,
        c.customer_state,
        DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp) AS delivery_days,
        CASE
            WHEN date(o.order_delivered_customer_date) > date(o.order_estimated_delivery_date)
            THEN 1
            ELSE 0
        END AS is_late
    FROM olist_orders o
    JOIN olist_customers c
        ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
)
SELECT
    customer_state,
    COUNT(order_id) AS delivered_orders,
    SUM(is_late) AS late_orders,
    ROUND(100.0 * SUM(is_late) / COUNT(order_id), 2) AS late_delivery_percent,
    ROUND(AVG(delivery_days), 2) AS avg_delivery_days
FROM delivered_orders
GROUP BY customer_state
HAVING delivered_orders >= 100
ORDER BY late_delivery_percent DESC;


-- Query 11: Review score analysis
SELECT
    r.review_score,
    COUNT(DISTINCT r.order_id) AS reviewed_orders,
    ROUND(AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)), 2) AS avg_delivery_days,
    ROUND(SUM(oi.price), 2) AS product_revenue
FROM olist_order_reviews r
JOIN olist_orders o
    ON r.order_id = o.order_id
LEFT JOIN olist_order_items oi
    ON r.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY r.review_score
ORDER BY r.review_score;


-- Query 12: Category review performance
SELECT
    CASE
        WHEN t.product_category_name_english IS NOT NULL THEN t.product_category_name_english
        WHEN p.product_category_name IS NOT NULL THEN p.product_category_name
        ELSE 'unknown'
    END AS category,
    COUNT(DISTINCT oi.order_id) AS orders,
    ROUND(SUM(oi.price), 2) AS product_revenue,
    ROUND(AVG(r.review_score), 2) AS average_review_score
FROM olist_order_items oi
JOIN olist_products p
    ON oi.product_id = p.product_id
LEFT JOIN product_category_translation t
    ON p.product_category_name = t.product_category_name
LEFT JOIN olist_order_reviews r
    ON oi.order_id = r.order_id
GROUP BY category
HAVING orders >= 100
ORDER BY average_review_score DESC, product_revenue DESC
LIMIT 20;


-- Query 13: Top category each month
-- Step 1: revenue by month and category.
-- Step 2: max revenue for each month.
-- Step 3: join both tables to keep the top category.
WITH monthly_category AS (
    SELECT
        LEFT(o.order_purchase_timestamp, 7) AS year_month,
        CASE
            WHEN t.product_category_name_english IS NOT NULL THEN t.product_category_name_english
            WHEN p.product_category_name IS NOT NULL THEN p.product_category_name
            ELSE 'unknown'
        END AS category,
        ROUND(SUM(oi.price), 2) AS product_revenue
    FROM olist_orders o
    JOIN olist_order_items oi
        ON o.order_id = oi.order_id
    LEFT JOIN olist_products p
        ON oi.product_id = p.product_id
    LEFT JOIN product_category_translation t
        ON p.product_category_name = t.product_category_name
    WHERE o.order_status = 'delivered'
    GROUP BY year_month, category
),
max_per_month AS (
    SELECT
        year_month,
        MAX(product_revenue) AS max_revenue
    FROM monthly_category
    GROUP BY year_month
)
SELECT
    mc.year_month,
    mc.category,
    mc.product_revenue
FROM monthly_category mc
JOIN max_per_month mm
    ON mc.year_month = mm.year_month
   AND mc.product_revenue = mm.max_revenue
ORDER BY mc.year_month;


-- Query 14: High value orders
WITH order_totals AS (
    SELECT
        o.order_id,
        c.customer_state,
        o.order_status,
        COUNT(*) AS items,
        ROUND(SUM(oi.price), 2) AS product_revenue,
        ROUND(SUM(oi.freight_value), 2) AS freight_value,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS order_total
    FROM olist_orders o
    JOIN olist_customers c
        ON o.customer_id = c.customer_id
    JOIN olist_order_items oi
        ON o.order_id = oi.order_id
    GROUP BY o.order_id, c.customer_state, o.order_status
)
SELECT
    order_id,
    customer_state,
    order_status,
    items,
    product_revenue,
    freight_value,
    order_total
FROM order_totals
ORDER BY order_total DESC
LIMIT 20;


-- Query 15: Customer state ranking
-- Step 1: summarize each state.
-- Step 2: rank states by revenue.
WITH state_sales AS (
    SELECT
        c.customer_state,
        COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
        COUNT(DISTINCT o.order_id) AS orders,
        ROUND(SUM(oi.price), 2) AS product_revenue
    FROM olist_orders o
    JOIN olist_customers c
        ON o.customer_id = c.customer_id
    JOIN olist_order_items oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_state
)
SELECT
    RANK() OVER (ORDER BY product_revenue DESC) AS revenue_rank,
    customer_state,
    unique_customers,
    orders,
    product_revenue,
    ROUND(product_revenue / orders, 2) AS revenue_per_order
FROM state_sales
ORDER BY revenue_rank;
