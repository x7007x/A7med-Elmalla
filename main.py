from flask import Flask, request, Response
import requests

app = Flask(__name__)
TARGET = "https://brave-terese-uuuuuu7gco-4c4942e9.koyeb.app"

@app.route('/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@app.route('/<path:path>', methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
def proxy(path):
    url = f"{TARGET}/{path}"
    headers = {k: v for k, v in request.headers if k.lower() != 'host'}
    resp = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )
    response_headers = [(name, value) for name, value in resp.headers.items()]
    return Response(resp.content, resp.status_code, response_headers)

if __name__ == "__main__":
    app.run()
