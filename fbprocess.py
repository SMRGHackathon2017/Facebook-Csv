import hashlib
import re
import json
import csv
import os.path


def auth_api(a):
    """Produce authorization key.

    Reads keys from ~/.api.keys.json
    Input
        a: API auth required
    Output
        t: Access token
    """
    home = os.path.expanduser('~')
    keys_path = home + '/.api.keys.json'
    auth = read_json(keys_path)

    if a in auth:
        if a == 'facebook':
            t = auth[a]['app_id'] + "|" + auth[a]['app_secret']
        else:
            pass
    else:
        t = "No API details provided"

    return t


def read_json(f):
    """Read JSON file.

    Input
        f: path to json file
    Output
        d: dictionary containing json
    """
    with open(f) as json_file:
        d = json.load(json_file)
    return d


def write_json(d, f):
    """Write JSON file.

    Input
        d: json object
        f: path to output json file
    Output
        writes file to disk
    """
    with open(f, 'w') as json_file:
        json.dump(d, json_file)
    return True


def write_csv(d, f):
    """Write csv file back to disk.

    Input
        d: tuple containing (header, data)
        f: filename for csv file.
    Output
        File written to disk
    """
    with open(f, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(d[0])
        for row in d[1]:
            row_encode = list()
            for x in row:
                if type(x) == unicode:
                    row_encode.append(x.encode('utf8'))
                else:
                    row_encode.append(x)
            writer.writerow(row_encode)
    return True


def md_5_hash(i):
    """MD5 Hash values.

    Input
        i: input to be hashed
    Output
        h: hashed value
    """
    h = hashlib.md5(i.encode('utf-8')).hexdigest()
    return h


def extract_first_name(s):
    """Extract first name from string.

    Extracts the first name with a name string that
    contains 2 or more numbers.

    Input
        s: string containing name
    Output
        name: string containing first name (or None if not names > 1)
    """
    clean_name = re.sub(r'\s+', r' ', s).split()

    for name in clean_name:
        if len(name) > 1:
            return name.title()
        else:
            pass

    return None


def unicode_decode(text):
    """Convert to unicode.

    Input
        text: text for convertion
    Output
        converted text (not unicode left encoded)
    """

    try:
        return text.encode('utf-8').decode()
    except UnicodeDecodeError:
        return text.encode('utf-8')


def extract_value(k, d, f=''):
    """Extract value from dictionary if exists.

    Optional apply function to value once extracted

    Inputs
        k: key form key/value pair in dictionary
        d: dictionary to extract from
        f: (optional) function to apply to the value
    Output
        v: Value if key exists in dictionary or the empty string
    """
    if k in d:
        if f != '':
            p = f(d[k])
        else:
            p = d[k]

        if type(p) == str:
            v = unicode_decode(p)
        else:
            v = p
    else:
        v = unicode_decode('')
    return v

def extract_dict(d, f):
    """Extract value from dictionary chain.

    Inputs
        d: Top level dictionary
        f: List of dictionary element including final required value
           e.g. ['reactions', 'summary', 'total_count']
    Output:
        required value if at end of chain otherwise recursivly call function
        till rearch the end of the chain
    """
    if len(f) == 1:
        return extract_value(f[0], d)
    else:
        if f[0] in d:
            return extract_dict(d[f[0]], f[1:])
        else:
            return unicode_decode('')


def create_csv(d, f):
    """Create a flattened csv from a python dictionary.

    Inputs
        d: dictionary of JSON object
        f: list of fields for csv file
           (use dots to extract from deeper within the dictionary
    Outputs
        csv: tuple of (list of headers, list of data rows)
    """
    csv_data = list()
    csv_head = [unicode(x) for x in f]

    for row in d:
        row_data = list()
        for field in f:
            fields = field.split('.')
            row_data.append(extract_dict(row, fields))
        csv_data.append(row_data)

    csv = (csv_head, csv_data)
    return csv


if __name__ == '__main__':

    assert md_5_hash('hello') == '5d41402abc4b2a76b9719d911017c592'
    assert extract_first_name('vic reeves') == 'Vic'
    assert extract_first_name('john f kennedy') == 'John'
    assert extract_first_name('g william norman') == 'William'
    assert extract_first_name('g d harold saxon') == 'Harold'
    print "All tests successful"
