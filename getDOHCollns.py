# MODIFY TO MAKE FASTER!
from concurrent.futures.thread import ThreadPoolExecutor

from robobrowser import RoboBrowser
import re
from pprint import pprint
import time

start_time = time.time()
# Session with login cookies, set in sign_in()
global_session = None

# Base url of the website we scrape
base_url = 'https://doh.arcabc.ca/'

"""
List of futures created by the executor. This list
is important as it allows to join the threads and
wait for the Thread pool to complete its work.
"""
futures = []

"""
List of pids and corresponding collection, map allows for constant time lookup
No locker used since this code is executed using CPython
so there is a GIL lock already
"""
pidList = {}
"""
Url dict to track whether a URL has been seen before
Used to determine non_collection_child
"""
url_dict = {}

"""
Threadpool. 100 workers is suitable.
Maybe increase with a better machine and better network speed
"""
executor = ThreadPoolExecutor(max_workers=100)

# Regular expression declarations for extracting link hrefs
let_str = r'/islandora/object/\D+?%3A\D+?.*?$'  # [a-z]+%3A[a-z]+'
num_str = r'/islandora/object/\D*?%3A\d*?$'  # [a-z]+%3A[0-9]+


class Collection(object):
    def __init__(self, title="Unknown", href="Unknown url",
                 pid="my:pid", non_collection_child=False, parent=None):
        """
        Constructor for a collection object
        :param title: the scraped title of the object
        :param href: the url that to directly access the object
        :param pid: the arca pid of this object, identified by the url
        :param non_collection_child: contains items that are not collections
        :param parent: the parent of this collection object
        """
        self.title = title
        self.href = href
        self.pid = pid
        self.non_collection_child = non_collection_child
        self.children = []
        self.parent = parent

    def append_child(self, child_colln):
        """
        Append a child to this collection object,
        making it a parent of the appended object
        :param child_colln: the child object
        """
        self.children.append(child_colln)

    def get_children(self):
        """
        get the children of this collection object
        :return: the array of children collection objects
        """
        return self.children


def sign_in():
    """
    Signs into the DOH website and sets the global session
    to allow other browser instances to access the cookies
    """
    # Set user and pass
    username_str = 'Sharon Hanna'
    password_str = '0re02oo2'
    # Create Non-JS browser
    browser = RoboBrowser(parser='html.parser')
    # Open login page
    browser.open('https://doh.arcabc.ca/user/login')
    # Get the login form
    form = browser.get_form(id='user-login')
    # Set the username & password
    form['name'].value = username_str
    form['pass'].value = password_str
    # Submit the form
    browser.submit_form(form)
    # Set the global session
    global global_session
    global_session = browser.session


def get_collns(url, parent_colln):
    """
    Scrapes the collections at the given url and appends them as children
    to the parent_collection
    :param url: the url to scrape
    :param parent_colln: the parent collection whose children the url contains
    :return: None. The method internally adds children and so nothing needs to be returned.
    """
    # Create a new browser instance and open the URL
    browser = RoboBrowser(session=global_session, parser='html.parser')
    browser.open(url)

    # Collection objects with pids ending in numbers
    num_link = browser.find("a", href=re.compile(num_str))

    if num_link is not None and url in url_dict:
        url_dict[url].non_collection_child = True

    # Collection objects with pids ending in letters
    let_links = browser.find_all("a", href=re.compile(let_str))
    if len(let_links) > 0:
        for lnk in let_links:
            # For each collection object url, if there is an image
            # then scrape it
            img = lnk.find("img")
            if img is not None:
                # hrefs are relative, so append to the base url
                src = base_url + lnk['href']
                """
                The pid at the end of the url e.g.
                /islandora/object/a:b then a:b is the pid
                This can be extracted from the URL by parsing
                """
                pid = src.split("/")[6].replace("%3A", ":")
                # The title attribute of the link tag
                tit = lnk['title']
                # Avoid scraping a resource more than once
                if pid not in pidList:
                    # Create a new collection with its scraped data
                    c = Collection(tit, src, pid, False, parent_colln)
                    # Add this collection to the pid list
                    pidList[pid] = c
                    # Add this collection as a child to its parent
                    parent_colln.append_child(c)

                    """
                    The first collection found that belongs to an href
                    set in the dict to set non_collection_child later if the url is
                    found again                    
                    """
                    if src not in url_dict:
                        url_dict[src] = c

                    # Submit this url to be scraped in a new thread
                    futures.append(executor.submit(get_collns, src, c))
    """
    No information required from the actual function
    All the information can be reached from the parent
    collection object    
    """
    return None


def build_coll_list(parent_colln, coll_list=[]):
    """
    builds the collection list (pre-order traversal of a tree)
    :param parent_colln: the root of the tree
    :param coll_list: the list to populate with the traversed elements
    """
    coll_list.append(parent_colln)

    for coll in parent_colln.get_children():
        build_coll_list(coll, coll_list)


def get_parent_from_file():
    """
    Will load the tree from tree.dat
    :return: the parent of the tree
    """
    # The parent that is found in the file
    to_return = None
    with open('tree.dat', 'r') as f:
        # Read the title first
        title = f.readline()
        # Keep going while there is a title
        while title:
            title = title.rstrip()
            href = f.readline().rstrip()
            pid = f.readline().rstrip()
            # Since the boolean is stored as a String,
            # this converts it to a Python boolean
            non_collection_child = f.readline().rstrip() == 'True'

            parent = f.readline().rstrip()

            # If it's 'None', set to None, otherwise the appropriate
            # collection object from the pidList
            parent = None if parent == 'None' else pidList[parent]

            c = Collection(title, href, pid, non_collection_child, parent)
            if parent is None:
                to_return = c
            else:
                # Append this as a child to its parent
                parent.append_child(c)

            # Save in pidList
            pidList[c.pid] = c
            # Reads title of next object
            title = f.readline()

    return to_return


def save_tree(parent):
    """
    Saves the tree to tree.dat
    :param parent: the parent of the tree
    :return: None
    """
    with open('tree.dat', 'w') as f:
        # Recursively save the tree
        def save(collection):
            f.write(collection.title + "\n")
            f.write(collection.href + "\n")
            f.write(collection.pid + "\n")
            f.write(str(collection.non_collection_child) + "\n")
            # If it's the root, parent is None
            if collection.parent is not None:
                f.write(collection.parent.pid + "\n")
            else:
                f.write('None\n')

            for child_coll in collection.get_children():
                save(child_coll)

        save(parent)


def get_parent():
    """
    Initiates scraping process. Will save the
    tree to tree.dat file.
    :return: the parent of the tree
    """
    # Sign in and set global session
    sign_in()
    """
    The parent collection object that allows access to all
    other collection objects
    """
    parent = Collection('Digitized Okanagan History', 'https://doh.arcabc.ca/islandora/object/doh%3Aroot',
                        'doh:root', False, None)

    # Initiate the scraping process
    get_collns('https://doh.arcabc.ca/islandora/object/doh%3Aroot', parent)

    # Loop runs until thread pool is done finishing its work
    while len(futures) > 0:
        # .result() of a future object blocks until content is returned
        futures.pop().result()

    # Shutdown executor
    executor.shutdown()

    # Save the tree
    save_tree(parent)

    # Return the list
    return parent

    # # Print the tree
    # for coll in coll_list:
    #     if coll.non_collection_child is True:
    #         pprint(vars(coll))
    #         print()
    #
    # end_time = time.time()
    # print("This process took how long?? " + str(end_time - start_time) + " seconds")
    # # Safely shutdown the executor (will wait for all threads to finish)
    # executor.shutdown()
