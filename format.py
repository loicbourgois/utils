from flask import jsonify as flask_jsonify
import time
import bleach


def jsonify(data):
    start = time.time()
    response = flask_jsonify(data)
    duration_jsonify = time.time() - start
    start = time.time()
    data = response.get_data().decode()
    data = bleach.clean(data)
    # data = data.replace("&amp;", "&")
    # https://github.com/mozilla/bleach/issues/192
    # &gt; for > and &lt; for <
    response.set_data(data)
    duration_bleach = time.time() - start
    response.headers['duration_jsonify'] = duration_jsonify
    response.headers['duration_bleach'] = duration_bleach
    return response