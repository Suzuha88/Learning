import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    # For each person, need to calculate probs of them having a trait,
    # knowing number of genes,
    # and probs of getting this number
    p = 1
    mut = PROBS["mutation"]
    for person in people:
        if people[person]['name'] in one_gene:
            p *= PROBS["trait"][1][people[person]['name'] in have_trait]
            # no info about parents
            if not people[person]['mother'] and not people[person]['father']:
                p *= PROBS["gene"][1]
            # info about both parents
            else:
                # first of sum is father gives gene, second is mother gives gene
                if people[person]['mother'] in one_gene:
                    if people[person]['father'] in one_gene:
                        p *= 0.5 * 0.5 * 2
                    elif people[person]['father'] in two_genes:
                        p *= (1 - mut) * 0.5 + mut * 0.5
                    else:
                        p *= mut * 0.5 + 0.5 * (1 - mut)
                elif people[person]['mother'] in two_genes:
                    if people[person]['father'] in one_gene:
                        p *= 0.5 * mut + (1 - mut) * 0.5
                    elif people[person]['father'] in two_genes:
                        p *= (1 - mut) * mut * 2
                    else:
                        p *= mut * mut + (1 - mut) * (1 - mut)
                else:
                    if people[person]['father'] in one_gene:
                        p *= 0.5 * (1 - mut) + 0.5 * mut
                    elif people[person]['father'] in two_genes:
                        p *= (1 - mut) * (1 - mut) + mut * mut
                    else:
                        p *= mut * (1 - mut) * 2
        elif people[person]['name'] in two_genes:
            p *= PROBS["trait"][2][people[person]['name'] in have_trait]
            if not people[person]['mother'] and not people[person]['father']:
                p *= PROBS["gene"][2]
            else:
                if people[person]['mother'] in one_gene:
                    if people[person]['father'] in one_gene:
                        p *= 0.5 * 0.5
                    elif people[person]['father'] in two_genes:
                        p *= (1 - mut) * 0.5
                    else:
                        p *= mut * 0.5
                elif people[person]['mother'] in two_genes:
                    if people[person]['father'] in one_gene:
                        p *= 0.5 * (1 - mut)
                    elif people[person]['father'] in two_genes:
                        p *= (1 - mut) * (1 - mut)
                    else:
                        p *= mut * (1 - mut)
                else:
                    if people[person]['father'] in one_gene:
                        p *= 0.5 * mut
                    elif people[person]['father'] in two_genes:
                        p *= (1 - mut) * mut
                    else:
                        p *= mut * mut
        else:
            p *= PROBS["trait"][0][people[person]['name'] in have_trait]
            if not people[person]['mother'] and not people[person]['father']:
                p *= PROBS["gene"][0]
            else:
                if people[person]['mother'] in one_gene:
                    if people[person]['father'] in one_gene:
                        p *= 0.5 * 0.5
                    elif people[person]['father'] in two_genes:
                        p *= mut * 0.5
                    else:
                        p *= (1 - mut) * 0.5
                elif people[person]['mother'] in two_genes:
                    if people[person]['father'] in one_gene:
                        p *= 0.5 * mut
                    elif people[person]['father'] in two_genes:
                        p *= mut * mut
                    else:
                        p *= (1 - mut) * mut
                else:
                    if people[person]['father'] in one_gene:
                        p *= 0.5 * (1 - mut)
                    elif people[person]['father'] in two_genes:
                        p *= mut * (1 - mut)
                    else:
                        p *= (1 - mut) * (1 - mut)

    return p


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        # check number of genes for each person
        number_of_genes = 0
        if person in one_gene:
            number_of_genes = 1
        elif person in two_genes:
            number_of_genes = 2
        else:
            number_of_genes = 0

        # update dictionary
        probabilities[person]["trait"][person in have_trait] += p
        probabilities[person]["gene"][number_of_genes] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        probs_trait = list(probabilities[person]["trait"].values())
        probs_gene = list(probabilities[person]["gene"].values())

        # calculate normalization coeficients
        alpha_trait = 1 / sum(probs_trait)
        alpha_gene = 1 / sum(probs_gene)

        for k, v in probabilities[person]["trait"].items():
            probabilities[person]["trait"][k] = alpha_trait * v

        for k, v in probabilities[person]["gene"].items():
            probabilities[person]["gene"][k] = alpha_gene * v


if __name__ == "__main__":
    main()
