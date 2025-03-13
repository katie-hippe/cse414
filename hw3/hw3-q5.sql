WITH m AS (
	SELECT DISTINCT dest_city 
	FROM flights 
	WHERE origin_city = 'Seattle WA'
),
n AS (
	SELECT DISTINCT f2.dest_city 
	FROM flights AS f1 JOIN flights as f2 
		ON f1.dest_city = f2.origin_city 
	WHERE f1.origin_city = 'Seattle WA'
)

SELECT DISTINCT f3.dest_city AS city
FROM flights AS f1 
	JOIN flights AS f2 ON f2.origin_city = f1.dest_city
	JOIN flights as f3 ON f3.origin_city = f2.dest_city

WHERE f3.dest_city <> 'Seattle WA'
	AND f3.dest_city NOT IN (SELECT dest_city FROM m) 
	AND f3.dest_city NOT IN (SELECT dest_city FROM n) 
ORDER BY city ASC;