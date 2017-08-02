"""

URL shortener server

"""
from flask import Flask, request, jsonify, redirect
import settings
import storage
from werkzeug.exceptions import BadRequest, NotFound
from urlparse import urlparse
app = Flask(__name__)


def validate_url(url):
    if url is None:
        raise BadRequest('Please supply "url" key')

    parsed = urlparse(url)
    if not parsed.scheme or 'http' not in parsed.scheme:
        raise BadRequest('This service only supports HTTP(S) URLs')

    if not parsed.netloc:
        raise BadRequest('Malformed URL, please check the format')


def sanitize_url(url):
    #TODO research external tools to do this properly
    url = url.replace('<', '%3C') \
             .replace('>', '%3E') \
             .replace('"', '%22') \
             .replace("'", '%27')
    return url
    

@app.errorhandler(400)
def bad_request(error=None):
    response = jsonify({
        'status': 400,
        'message': str(error)
    })
    response.status_code = 400
    return response


@app.route('/shorten_url', methods=['POST'])
def shorten_url():
    json = request.get_json()
    url = json.get('url')
    url = sanitize_url(url)
    validate_url(url)
    url_code = storage.store_url(url)
    shortened_url = settings.ROOT_URI + '/' + url_code
    response = {
        'shortened_url': shortened_url
    }
    return jsonify(response)


@app.route('/<url_code>', methods=['GET'])
def get_url(url_code):
    url = storage.get_url(url_code.lower())
    if url is None:
        raise NotFound('URL not found')

    return redirect(url, code=302)


if __name__ == '__main__':
    print settings.ROOT_URI
    app.run(host=settings.ROOT, port=settings.PORT)

