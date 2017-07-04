import fbprocess as fb
import json


def main():
    """Example code for functions.

    fb.read_json: Helper function to read json
    fb.extract_first_name: Returns the first name with 2 or more characters
    fb.md_5_hash: Theodore's hashing function
    fb.create_csv: Creates flattened csv data
        (extract elements from further down the hierarchy using dot notion)
    fb.write_csv: Helper function to write out the csv file
    """

    posts = fb.read_json('CitizensAdvice.json')

    for post in posts:
        first_reaction = post['reactions']['data'][0]
        post['first_react_name'] = fb.extract_value('name', first_reaction, fb.extract_first_name)
        post['first_react_hash_id'] = fb.extract_value('id', first_reaction, fb.md_5_hash)

    csv_fields = ([
        'name',
        'first_react_name',
        'first_react_hash_id',
        'reactions.summary.total_count',
        'reactions_summary.love',
        'reactions_summary.like',
        'reactions_summary.wow',
        'reactions_summary.haha',
        'reactions_summary.sad',
        'reactions_summary.angry',
        'shares.count',
        'link',
        'created_time',
        'message',
        'type',
        'id'
    ])

    csv = fb.create_csv(posts, csv_fields)

    write_file = fb.write_csv(csv, 'CitizensAdvice.csv')

    return True


if __name__ == '__main__':
    main()
