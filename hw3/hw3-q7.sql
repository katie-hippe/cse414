SELECT DISTINCT c.name AS carrier
FROM flights as f JOIN carriers as c on f.carrier_id = c.cid
WHERE f.origin_city = 'Seattle WA' AND f.dest_city = 'New York NY'
GROUP BY c.name
ORDER BY c.name ASC;