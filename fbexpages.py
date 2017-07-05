import json
import datetime
import csv
import time
import re
import fbprocess as fb

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request


def request_until_succeed(url):
    """Request URL."""
    req = Request(url)
    success = False
    while success is False:
        try:
            response = urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception as e:
            print(e)
            time.sleep(5)

            print("Error for URL {}: {}".format(url, datetime.datetime.now()))
            print("Retrying.")

    return response.read()


def create_param(p, v):
    """Create additional parameter.

    Create additional parameter string if parameter
    has value.
    Input
        p: parameter
        v: url parameter
    Output
        s: parameter string
    """
    if p is not '':
        s = "&" + v + "={}".format(p)
    else:
        s = ''

    return s


def get_page_feed_url(base_url, group=0):
    # Construct the URL string; see http://stackoverflow.com/a/37239851 for
    # Reactions parameters
    fields = (
        "&fields=message,link,created_time,type,name,id," +
        "comments.summary(true),shares,reactions.summary(true)"
    )

    if group == 1:
        fields += ",from"

    return base_url + fields


def get_reactions(base_url):
    reaction_types = ['like', 'love', 'wow', 'haha', 'sad', 'angry']
    reactions_dict = dict()   # dict of {status_id: tuple<6>}

    for reaction_type in reaction_types:
        fields = "&fields=reactions.type({}).limit(0).summary(total_count)".format(
            reaction_type.upper())

        url = base_url + fields

        data = json.loads(request_until_succeed(url))['data']
        data_processed = set()  # set() removes rare duplicates in statuses
        for status in data:
            id = status['id']
            count = status['reactions']['summary']['total_count']
            data_processed.add((id, count))

        for id, count in data_processed:
            if id in reactions_dict:
                reactions_dict[id][reaction_type] = count
            else:
                reactions_dict[id] = dict()
                reactions_dict[id][reaction_type] = count

    return reactions_dict


def extract_page_posts(page_id, access_token, since_date, until_date):
    """Extract posts on a page."""

    posts = list()
    has_next_page = True
    num_processed = 0
    scrape_starttime = datetime.datetime.now()
    after_id = ''
    base = "https://graph.facebook.com/v2.9"
    node = "/{}/posts".format(page_id)
    parameters = "/?limit={}&access_token={}".format(100, access_token)
    since = create_param(since_date, 'since')
    until = create_param(until_date, 'until')

    print("Scraping {} Facebook Page: {}\n".format(page_id, scrape_starttime))

    while has_next_page:
        after = create_param(after_id, 'after')
        base_url = base + node + parameters + after + since + until

        url = get_page_feed_url(base_url)
        statuses = json.loads(request_until_succeed(url))
        reactions = get_reactions(base_url)

        for status in statuses['data']:
            if 'reactions' in status:
                status['reactions_summary'] = reactions[status['id']]
            posts.append(status)

            num_processed += 1
            if num_processed % 100 == 0:
                print("{} Statuses Processed: {}".format
                        (num_processed, datetime.datetime.now()))

        # if there is no next page, we're done.
        if 'paging' in statuses:
            after_id = statuses['paging']['cursors']['after']
        else:
            has_next_page = False

    print("\nDone!\n{} Statuses Processed in {}".format(
            num_processed, datetime.datetime.now() - scrape_starttime))

    return posts


if __name__ == '__main__':
    posts = list()
    page_id = "CitizensAdvice"

    # input date formatted as YYYY-MM-DD
    since_date = "2017-01-01"
    until_date = "2017-07-05"


    access_token = fb.auth_api('facebook')

    """
    or use your facebook credentials directly

    app_id = ""
    app_secret = ""

    access_token = app_id + "|" + app_secret
    """

    page_posts = extract_page_posts(page_id, access_token, since_date, until_date)
    for post in page_posts:
        posts.append(post)

    output = fb.write_json(posts, page_id + '.json')
