import csv
import sys


def main():

    # Check for command-line usage
    if (len(sys.argv) != 3):
        print("USAGE: python dna.py [DATABASE] [SEQUENCE]")
        sys.exit(1)

    # Read database file into a variable
    people = []  # list of dicts
    col = []  # list of keys for dicts
    with open(sys.argv[1]) as database:
        csv_reader = csv.reader(database, delimiter=',')
        for i, row in enumerate(csv_reader):
            if i == 0:
                for title in row:
                    col.append(title)
            else:
                person = {}
                for j, content in enumerate(row):
                    person[col[j]] = content
                people.append(person)

    # Read DNA sequence file into a variable
    with open(sys.argv[2]) as seq_file:
        sequence = (seq_file.readline()).strip()

    # Find longest match of each STR in DNA sequence
    matches = {}
    for str in col[1:]:
        s = str
        i = 0
        while (s in sequence):
            s = s + str
            i += 1
        matches[str] = i

    # Check database for matching profiles
    for person in people:
        number_of_matches = 0
        for str in col[1:]:
            if int(person[str]) == matches[str]:
                number_of_matches += 1

        if number_of_matches == len(col[1:]):  # matched all STRs
            print(person["name"])
            sys.exit(0)

    print("No match")
    sys.exit(0)


main()
