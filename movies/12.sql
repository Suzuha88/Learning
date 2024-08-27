SELECT title FROM movies WHERE id IN
    (SELECT movie_id FROM stars WHERE person_id in
        (SELECT id FROM people WHERE name = 'Bradley Cooper'))
    AND id IN
    (SELECT movie_id FROM stars WHERE person_id in
        (SELECT id FROM people WHERE name = 'Jennifer Lawrence'));
