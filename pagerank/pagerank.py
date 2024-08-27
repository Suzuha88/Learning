import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    model = {filename: (1 - damping_factor) / len(corpus)
             for filename in corpus}

    if corpus[page] == set():
        for filename in corpus:
            model[filename] = 1/len(corpus)
        return model

    for filename in corpus[page]:
        model[filename] += damping_factor/len(corpus[page])

    return model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    print(corpus)
    samples = {filename: 0 for filename in corpus}
    first_page = random.choice(list(corpus.keys()))
    samples[first_page] = 1
    transition_models = {filename: transition_model(
        corpus, filename, damping_factor) for filename in corpus}

    previous_page = first_page
    for i in range(0, n):
        choice = weight_choice(transition_models[previous_page])
        samples[choice] += 1
        previous_page = choice

    return {filename: amount / n for (filename, amount) in samples.items()}


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    corpus_formatted = dict()
    for filename in corpus:
        if len(corpus[filename]) == 0:
            corpus_formatted[filename] = {
                filename for filename in corpus.keys()}
        else:
            corpus_formatted[filename] = corpus[filename]

    N = len(corpus_formatted)
    ranks = {filename: 1/N for filename in corpus_formatted}
    done = {filename: False for filename in corpus_formatted}

    while True:
        for filename in corpus_formatted:
            links_to_page = [other_filename for other_filename in corpus_formatted.keys(
            ) if filename in corpus_formatted[other_filename]]

            sum = 0
            for link in links_to_page:
                sum += ranks[link] / len(corpus_formatted[link])

            new_rank = (1 - damping_factor) / N + damping_factor * sum
            old_rank = ranks[filename]
            ranks[filename] = new_rank

            if abs(old_rank - new_rank) < 0.001:
                done[filename] = True

            if all(done.values()):
                return ranks


def weight_choice(transition_model):
    keys = list(transition_model.keys())
    values = list(transition_model.values())

    values_transformed = []

    for i, value in enumerate(values):
        if i > 0:
            values_transformed.append(values_transformed[i - 1] + value)
        else:
            values_transformed.append(values[i])

    model_transformed = dict(zip(keys, values_transformed))
    r = random.random()

    for k, v in model_transformed.items():
        if r < v:
            return k


if __name__ == "__main__":
    main()
