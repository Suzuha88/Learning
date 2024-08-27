SELECT title FROM movies JOIN ratings on movies.id = movie_id WHERE id in
(SELECT movie_id FROM stars WHERE person_id in
(SELECT id FROM people WHERE name = 'Chadwick Boseman')) ORDER BY rating DESC LIMIT 5;
