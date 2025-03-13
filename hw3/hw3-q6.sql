SELECT c.name AS carrier
FROM carriers AS c 
WHERE EXISTS (SELECT DISTINCT f.carrier_id
				FROM flights as f
				WHERE f.carrier_id = c.cid 
					AND f.origin_city = 'Seattle WA' 
					AND f.dest_city = 'New York NY')
GROUP BY c.name
ORDER BY c.name;