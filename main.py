from flask import Flask, request, Response
import requests

app = Flask(__name__)
TARGET = "https://brave-terese-uuuuuu7gco-4c4942e9.koyeb.app"

@app.route('/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@app.route('/<path:path>', methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
def proxy(path):
    url = f"{TARGET}/{path}"
    headers = {k: v for k, v in request.headers if k.lower() != 'host'}
    body = request.get_data() if request.method not in ["GET", "HEAD"] else None
    resp = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        data=body,
        cookies=request.cookies,
        allow_redirects=False
    )
    excluded_headers = ['transfer-encoding', 'connection']
    response_headers = [(name, value) for name, value in resp.headers.items() if name.lower() not in excluded_headers]
    return Response(resp.content, resp.status_code, response_headers)
