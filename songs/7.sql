SELECT AVG(energy) FROM
(SELECT * FROM songs WHERE artist_id in
(SELECT id FROM artists WHERE name = 'Drake'));
