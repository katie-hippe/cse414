SELECT f.origin_city AS origin_city, 
	(CAST(count AS NUMERIC(10,2)) * 100 / CAST(count(f.fid)
	AS NUMERIC(10,2))) AS percentage
FROM flights AS f LEFT JOIN 
	(SELECT origin_city, count(fid) AS count 
	FROM flights 
	WHERE actual_time < 1.5*60 OR (actual_time IS NULL) 
	GROUP BY origin_city) AS m 
ON f.origin_city = m.origin_city
GROUP BY f.origin_city, count
ORDER BY percentage ASC;