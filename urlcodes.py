"""
This module contains functions to perform translation between integer URL ID's and string URL codes.

>> get_url_code(123)
'dr'
>> get_url_id('dr')
123

"""
import string


ALPHABET = string.lowercase + ''.join([str(x) for x in range(1, 10)])


def get_url_code(url_id):
    """ Get a URL code from an integer ID

    Arguments:
        url_id: positive integer ID

    Returns:
        A string of characters from the alphabet corresponding to the ID

    """
    url_id -= 1
    if url_id == 0:
        return ALPHABET[0]

    base = len(ALPHABET)
    result_chars = []
    while url_id:
        residual = url_id % base
        result_chars.append(ALPHABET[residual])
        url_id /= base
    return ''.join(result_chars)[::-1]


def get_url_id(url_code):
    """ Get a URL ID from a string URL code

    Arguments:
        url_code: a string URL code

    Returns:
        A positive integer URL ID
        
    """
    result = 0
    base = len(ALPHABET)
    char_idx_lookup = {c: i for i, c in enumerate(ALPHABET)}
    for i, char in enumerate(url_code[::-1]):
        result += char_idx_lookup[char] * (base ** i)

    return result + 1
    

if __name__ == '__main__':
    #TODO Implement proper tests
    for url_id in range(1, 100):
        url_code = get_url_code(url_id)
        assert url_id == get_url_id(url_code)

