from flask import Flask, request, Response
import requests
from urllib.parse import urljoin, urlparse
import mimetypes
import os

app = Flask(__name__)

TARGET = "https://past-pinniped-uuuuuu7gco-5c3491b7.koyeb.app/"

CHUNK = 1024 * 1024

@app.route('/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@app.route('/<path:path>', methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
def proxy(path):
    url = f"{TARGET}/{path}".replace("//", "/").replace(":/", "://")

    headers = {k: v for k, v in request.headers if k.lower() != 'host'}
    body = request.get_data() if request.method not in ["GET", "HEAD"] else None

    resp = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        data=body,
        cookies=request.cookies,
        allow_redirects=False,
        stream=True
    )

    excluded_headers = ['transfer-encoding', 'connection']
    response_headers = []
    for name, value in resp.headers.items():
        if name.lower() not in excluded_headers:
            if name.lower() == "location":
                parsed = urlparse(value)
                new_location = urljoin(request.host_url, parsed.path.lstrip("/"))
                response_headers.append((name, new_location))
            else:
                response_headers.append((name, value))

    def generate():
        for chunk in resp.iter_content(CHUNK):
            yield chunk

    return Response(
        generate(),
        resp.status_code,
        response_headers
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
