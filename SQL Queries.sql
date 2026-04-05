
use dash;

-- TOTAL NO OF FLIGHTS IN DATABSE
SELECT COUNT(*) FROM flight;

-- no of airlines
SELECT COUNT(DISTINCT(airline)) FROM flight;

-- avg ticket price
SELECT ROUND(AVG(price)) FROM flight;

-- most expensive ticket
SELECT (MAX(price)) FROM flight;

-- cheapest ticket
SELECT (MIN(price)) FROM flight;

-- avg ticket price
SELECT ROUND(AVG(duration)) FROM flight;



-- total flights by route
SELECT source_city , destination_city ,
CONCAT(source_city , '-' , destination_city) AS 'route',
 COUNT(*) AS 'no_of_flights' FROM flight
GROUP BY source_city , destination_city
ORDER BY COUNT(*) DESC ;

-- avg price by airline
SELECT airline , 
ROUND(AVG(price)) AS 'price'
FROM flight
GROUP BY airline 
ORDER BY price DESC ;

-- avg price when days left to departure

SELECT days_left ,
ROUND(AVG(price)) AS 'price' 
FROM flight
GROUP BY days_left ;


-- flight shar by airline
SELECT airline , COUNT(*) AS 'total_flights',
( COUNT(*) * 100 / (SELECT COUNT(*) FROM flight) ) AS 'percentage_share'
FROM flight
GROUP BY airline;

-- filter values for airline
SELECT DISTINCT(airline) FROM flight;

## page 2

-- - **Box Plot** — Price distribution by airline (shows median, outliers, spread — much better than just avg)
SELECT airline ,price FROM flight;

-- **Histogram** — Price distribution overall (how prices are spread ₹1k to ₹1.2L)

SELECT price FROM flight;

-- - **Bar Chart** — Avg price by number of stops (zero vs one vs two+)
SELECT stops , ROUND(AVG(price)) AS 'avg_price' FROM flight
GROUP BY stops ;

-- - **Scatter Plot** — Duration vs Price (colored by airline — do longer flights cost more?)
SELECT duration , price FROM flight;

-- **Line Chart** — Avg price vs Days Left (1–49), broken by class (Economy line vs Business line)
SELECT days_left , AVG(price) AS 'avg_price' FROM flight
WHERE class = 'Economy'
GROUP BY days_left ;

-- Business

SELECT days_left , AVG(price) AS 'avg_price' FROM flight
WHERE class = 'Business'
GROUP BY days_left ;


-- - **Heatmap** — Avg price: Source City × Destination City grid
SELECT source_city , destination_city , avg(price) AS 'avg_price' FROM flight
GROUP BY source_city , destination_city ;

## page 3

-- **Heatmap** — Number of flights: Source City × Destination City (busiest routes)
SELECT source_city , destination_city , COUNT(*) AS 'count' FROM flight
GROUP BY source_city , destination_city ;

-- **Horizontal Bar** — Top 10 routes by avg price
SELECT  ROUND(AVG(price)) AS 'avg_price',
CONCAT(source_city , '-' ,destination_city) AS 'route' FROM flight
GROUP BY source_city , destination_city
ORDER BY avg_price DESC LIMIT 10;

-- - **Horizontal Bar** — Top 10 routes by flight count
SELECT  (COUNT(*)) AS 'count',
CONCAT(source_city , '-' ,destination_city) AS 'route' FROM flight
GROUP BY source_city , destination_city
ORDER BY count DESC LIMIT 10;

-- **Bar Chart** — Avg duration per route (which route takes longest)

SELECT  FLOOR(AVG(duration)) AS 'avg_duration',
CONCAT(source_city , '-' ,destination_city) AS 'route' FROM flight
GROUP BY source_city , destination_city
ORDER BY avg_duration DESC ;

-- - **Stacked Bar** — Stops breakdown per route (how many routes have direct flights)
SELECT stops , COUNT(*) AS 'count' FROM flight
GROUP BY stops;


## page 3

-- - **Bar Chart** — Flights count by Departure Time slot (Morning, Evening, etc.)
SELECT departure_time , COUNT(*) AS 'count'
FROM flight
GROUP BY departure_time ;

-- Avg price by Departure Time slot 

SELECT departure_time , ROUND(AVG(price)) AS 'avg_price'
FROM flight
GROUP BY departure_time ;

--     # - **Heatmap** — Departure Time × Arrival Time → flight count (which combos are most common)
SELECT departure_time , arrival_time , COUNT(*) AS 'count' 
FROM flight
GROUP BY departure_time , arrival_time;

-- Avg price by Arrival Time slot
SELECT arrival_time , ROUND(AVG(price)) AS 'avg_price'
FROM flight
GROUP BY arrival_time;

-- Departure time breakdown per airline
SELECT  COUNT(*) AS 'count',
CONCAT(airline ,'-' ,departure_time) AS 'airline-departureTime'
FROM flight
GROUP BY departure_time , airline ;

## page 5

-- - **Radar Chart** — Airline comparison across: avg price, avg duration, % direct flights, % business class, flight count (normalized) — this is a premium, portfolio-worthy chart

SELECT airline , AVG(price) AS 'avg_price' , CEIL(AVG(duration)) AS 'avg_duration',
COUNT(*) * 100 / (SELECT COUNT(*) FROM flight) AS 'percentage_share',
COUNT(*) AS 'flight_count'  ,
SUM(CASE WHEN class = 'Economy' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) 
        AS economy_percentage,
SUM(CASE WHEN class = 'Business' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) 
        AS business_percentage
FROM flight
GROUP BY airline ;

-- - **Stacked Bar** — Stops distribution per airline (who runs most direct flights)

SELECT airline , stops , count(*) AS 'no_of_flights' FROM flight
GROUP BY airline , stops ;

--     # - **Grouped Bar** — Class split per airline (Economy vs Business count)
SELECT class , airline , COUNT(*) AS 'no_of_flights'  
FROM flight
GROUP BY class , airline ;

-- Summary stats table: airline | total flights | avg price | avg duration | % direct | % business

SELECT airline , COUNT(*) AS 'total_flights' , ROUND(AVG(price)) AS 'avg_price' , FLOOR(AVG(duration)) AS 'avg_duration' ,
ROUND(COUNT(*) * 100 / (SELECT COUNT(*) FROM flight),2) AS '% business'
FROM flight
GROUP BY airline;


SELECT airline , COUNT(*) AS 'total_flights' , ROUND(AVG(price)) AS 'avg_price' , FLOOR(AVG       (duration)) AS 'avg_duration' ,
                        ROUND(COUNT(*) * 100 / (SELECT COUNT(*) FROM flight),2) AS 'business_percentage',
                       SUM(CASE WHEN class = 'Economy' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) 
                                AS economy_percentage,
                        SUM(CASE WHEN class = 'Business' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) 
                                AS business_percentage,
                       MAX(price) AS 'max_ticket_price',
                       MIN(price) AS 'min_ticket_price'
                        FROM flight
                        GROUP BY airline;
                        
SELECT MAX(price) AS 'price' FROM flight;





