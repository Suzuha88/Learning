-- Keep a log of any SQL queries you execute as you solve the mystery.

--took place on July 28, 2023 and that it took place on Humphrey Street.
SELECT * FROM crime_scene_reports WHERE year = 2023 AND month =  7 AND day = 28;
SELECT * FROM interviews WHERE month = 7 AND day = 28;



--Sometime within ten minutes of the theft, I saw the thief get into a car in the bakery parking lot and drive away.
SELECT license_plate FROM bakery_security_logs WHERE day = 28 AND hour = 10 AND minute > 15 AND minute < 30 AND activity = 'exit';


--Earlier this morning, before I arrived at Emma's bakery, I was walking by the ATM on Leggett Street and saw the thief there withdrawing some money.
SELECT account_number FROM atm_transactions WHERE year = 2023 AND month = 7 AND day = 28 AND transaction_type = 'withdraw' AND atm_location = 'Leggett Street';

--As the thief was leaving the bakery, they called someone who talked to them for less than a minute.
SELECT caller FROM phone_calls WHERE year = 2023 AND month = 7 AND day = 28 AND duration < 60;
SELECT receiver FROM phone_calls WHERE year = 2023 AND month = 7 AND day = 28 AND duration < 60;

--In the call, I heard the thief say that they were planning to take the earliest flight out of Fiftyville tomorrow. The thief then asked the person on the other end of the phone to purchase the flight ticket.
--Earliest flight:
SELECT id FROM flights WHERE year = 2023 AND month = 7 AND day = 29 ORDER BY hour LIMIT 1;

SELECT name FROM people WHERE id IN
    (SELECT person_id FROM bank_accounts WHERE account_number IN
        (SELECT account_number FROM atm_transactions WHERE year = 2023 AND month = 7 AND day = 28 AND transaction_type = 'withdraw' AND atm_location = 'Leggett Street'))
    AND phone_number IN
    (SELECT caller FROM phone_calls WHERE year = 2023 AND month = 7 AND day = 28 AND duration < 60)
    AND license_plate IN
    (SELECT license_plate FROM bakery_security_logs WHERE day = 28 AND hour = 10 AND minute > 15 AND minute < 30 AND activity = 'exit')
    AND passport_number IN
    (SELECT passport_number FROM passengers WHERE flight_id IN
        (SELECT id FROM flights WHERE year = 2023 AND month = 7 AND day = 29 ORDER BY hour LIMIT 1));


SELECT city FROM airports WHERE id IN
    (SELECT destination_airport_id FROM flights WHERE year = 2023 AND month = 7 AND day = 29 ORDER BY hour LIMIT 1);

SELECT name FROM people WHERE phone_number IN
    (SELECT receiver FROM phone_calls WHERE year = 2023 AND month = 7 AND day = 28 AND duration < 60
    AND caller IN
        (SELECT phone_number FROM people WHERE id IN
            (SELECT person_id FROM bank_accounts WHERE account_number IN
                (SELECT account_number FROM atm_transactions WHERE year = 2023 AND month = 7 AND day = 28 AND transaction_type = 'withdraw' AND atm_location = 'Leggett Street'))
            AND phone_number IN
            (SELECT caller FROM phone_calls WHERE year = 2023 AND month = 7 AND day = 28 AND duration < 60)
            AND license_plate IN
            (SELECT license_plate FROM bakery_security_logs WHERE day = 28 AND hour = 10 AND minute > 15 AND minute < 30 AND activity = 'exit')
            AND passport_number IN
            (SELECT passport_number FROM passengers WHERE flight_id IN
            (SELECT id FROM flights WHERE year = 2023 AND month = 7 AND day = 29 ORDER BY hour LIMIT 1))));
