SELECT m.dest_city AS city
FROM flights AS f
JOIN (SELECT origin_city, dest_city FROM flights
	WHERE dest_city <> 'Seattle WA'
	AND dest_city NOT IN 

	(SELECT dest_city FROM flights
	WHERE origin_city = 'Seattle WA')
	GROUP BY origin_city, dest_city) AS m 

ON f.dest_city = m.origin_city
WHERE f.origin_city = 'Seattle WA'
GROUP BY m.dest_city
ORDER BY m.dest_city ASC;