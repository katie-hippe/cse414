WITH m AS (
	SELECT f1.origin_city AS origin_city,
	MAX(f1.actual_time) AS time 
	FROM flights AS f1
	GROUP BY f1.origin_city)
SELECT DISTINCT f.origin_city AS origin_city,
	f.dest_city AS dest_city,
	f.actual_time AS time 
FROM flights AS f, m 
WHERE f.origin_city = m.origin_city AND f_actual_time = m.time 
ORDER BY f.origin_city, f.dest_city;
