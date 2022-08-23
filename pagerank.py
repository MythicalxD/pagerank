import os
import re
import sys
import random
from random import choices

DAMPING = 0.85
SAMPLES = 10000


def main():
    print("Hello world !")
    if len(sys.argv) != 2:
        sys.exit("Usage: python pg.py corpus")
    corpus = crawl(sys.argv[1])

    print("")
    print(corpus)
    print("")

    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    print("")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")

    print("")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    print("")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
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
    page_probability = dict()

    # Getting a list of links in `page`
    pages_list = list(corpus.get(page))

    if (len(pages_list) != 0):
        # Since all pages are Equally likely dividing damping_factor by length of list
        pages_visit_probability = damping_factor/len(pages_list)

        # every page gets an additional 0.05 because with probability 0.15 we choose randomly among all three of the pages.
        all_pages_probability = (1 - damping_factor) / (len(pages_list) + 1)

        # Making Dictionary
        page_probability[page] = all_pages_probability

        for pages in pages_list:
            page_probability[pages] = pages_visit_probability + \
                all_pages_probability

    elif(len(pages_list) == 0):
        # if a page has no links, we can pretend it has links to all pages in the corpus, including itself.
        list_all_pages = corpus.keys()

        all_pages_probability_same = 1/len(list_all_pages)
        
        # page list is Empty ! so make it contain all corpus key
        pages_list = list(corpus.keys())

        for pages in pages_list:
            page_probability[pages] = all_pages_probability_same

    """
    The return value of the function should be a Python dictionary with one key for each page in the corpus.
    Each key should be mapped to a value representing that page’s estimated PageRank.
    The values in this dictionary should sum to 1.
    
    """

    return page_probability


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.

    """

    estimated_page_rank = dict()

    times_page_visited = dict()

    all_pages_list = corpus.keys()
    for page in all_pages_list:
        times_page_visited[page] = 0

    # First sample will be generated Randomly
    # To get a Random pair from [corpus] i will use choice

    page, linked_pages = random.choice(list(corpus.items()))

    # First sample is the page randomly choosen
    first_sample = page

    print("First Sample : ", first_sample)

    # Next smaple should be genrated from the previous sample based on the previous sample's transition model.
    # we need to use the transitional model to get the probabilities of the the previous sample.

    # Repeate for n observations
    prev_sample_transition_model = transition_model(
        corpus, first_sample, damping_factor)

    print("")
    print("First Sample Transitional Model : ", prev_sample_transition_model)
    print("")

    for i in range(n):

        # we will split each pages and their respective weights
        #pages, weights = list(prev_sample_transition_model.items())

        # Select a random page having probability distribution `weights`
        next_sample_list = random.choices(list(prev_sample_transition_model.keys(
        )), weights=prev_sample_transition_model.values(), k=1)

        next_sample = next_sample_list[0]

        times_visited = times_page_visited.get(next_sample)
        times_page_visited[next_sample] = times_visited + 1

        prev_sample_transition_model = transition_model(
            corpus, next_sample, damping_factor)

    '''
    For example, if the transition probabilities are 
    {"1.html": 0.05, "2.html": 0.475, "3.html": 0.475}, 
    then 5% of the time the next sample generated should be "1.html", 
    47.5% of the time the next sample generated should be "2.html", 
    and 47.5% of the time the next sample generated should be "3.html".
    '''

    # Calculation probability (i.e times each page was visited in n rounds)
    for key in times_page_visited.keys():
        probability = int(times_page_visited.get(key)) / n
        estimated_page_rank[key] = probability

    return estimated_page_rank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    estimated_pake_rank = dict()
    on_run_page_ranks = dict()

    # The function should begin by assigning each page a rank of 1 / N, where N is the total number of pages in the corpus.
    total_pages = len(corpus)
    initial_page_rank = 1/total_pages

    for add_pages in corpus.keys():
        on_run_page_ranks[add_pages] = initial_page_rank

    remaining_probability = (1 - damping_factor)/total_pages

    # Calculation probability for page `p`

    # get the first page
    first_page_list = list(corpus.keys())
    first_page = first_page_list[0]

    diff = 1.00000
    n = 0
    store = 1.001

    while (diff >= 0.0001):
        for page in corpus.keys():
            # For every page `i` that exists
            # TODO check for empty set
            
            # `page` is the current Page
            number_of_incoming_arrows = []

            for check_page in corpus.keys():
                if page in corpus.get(check_page):
                    # Check page are other pages, and the current page is found in the set !
                    # Make a list: how many nodes are pointing towards this page (A)
                    number_of_incoming_arrows.append(check_page)

            # Loop and add every calculation (Summation)
            summation = 0
            for get_page in number_of_incoming_arrows:
                number_get_page_pointing_to = len(list(corpus.get(get_page)))
                summation = summation + \
                    on_run_page_ranks.get(get_page)/number_get_page_pointing_to

            page_rank_of_current_page = remaining_probability + damping_factor*summation
            # set the value
            on_run_page_ranks[page] = page_rank_of_current_page

        diff = abs(round(store - list(on_run_page_ranks.values())[0], 4))
        #print("STORE : ", store, " ON RUN : ", list(on_run_page_ranks.values())[0], " DIFF : ", diff)
        store = list(on_run_page_ranks.values())[0]

        estimated_pake_rank = on_run_page_ranks

    return estimated_pake_rank


if __name__ == "__main__":
    main()
