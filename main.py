from flask import Flask, request, Response
import requests

app = Flask(__name__)
TARGET = "https://past-pinniped-uuuuuu7gco-5c3491b7.koyeb.app/"

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
def proxy(path):
    url = TARGET.rstrip('/') + '/' + path.lstrip('/')
    headers = {k: v for k, v in request.headers if k.lower() != 'host'}
    resp = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        params=request.args,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        stream=True
    )
    excluded = {'content-encoding', 'content-length', 'transfer-encoding', 'connection'}
    headers_out = [(k, v) for k, v in resp.raw.headers.items() if k.lower() not in excluded]
    return Response(resp.content, resp.status_code, headers_out)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
