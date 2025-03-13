SELECT DISTINCT f.origin_city as city
FROM flights as f
WHERE f.canceled <> 1
GROUP BY f.origin_city
HAVING MAX(f.actual_time) < 4*60
ORDER BY city;