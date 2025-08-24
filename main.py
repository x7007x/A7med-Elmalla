from flask import Flask, request, Response
import requests
from urllib.parse import urljoin, urlparse
import os

app = Flask(__name__)

TARGET = "https://past-pinniped-uuuuuu7gco-5c3491b7.koyeb.app/"

@app.route('/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@app.route('/<path:path>', methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
def proxy(path):
    url = f"{TARGET}{path}"
    
    headers = {k: v for k, v in request.headers if k.lower() != 'host'}
    body = request.get_data() if request.method not in ["GET", "HEAD"] else None
    
    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=body,
            cookies=request.cookies,
            allow_redirects=False,
            stream=True,
            timeout=30
        )

        excluded_headers = ['transfer-encoding', 'connection', 'content-encoding']
        response_headers = []
        
        for name, value in resp.headers.items():
            if name.lower() not in excluded_headers:
                if name.lower() == "location":
                    parsed = urlparse(value)
                    if parsed.netloc and TARGET in value:
                        new_location = urljoin(request.host_url, parsed.path.lstrip("/"))
                        if parsed.query:
                            new_location += f"?{parsed.query}"
                        response_headers.append((name, new_location))
                    else:
                        response_headers.append((name, value))
                else:
                    response_headers.append((name, value))

        content_type = resp.headers.get('content-type', '').lower()
        
        if any(media_type in content_type for media_type in ['audio/', 'video/', 'image/', 'application/octet-stream']):
            def generate():
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
            
            response = Response(generate(), resp.status_code, response_headers)
            response.headers['Accept-Ranges'] = 'bytes'
            return response
        else:
            return Response(resp.content, resp.status_code, response_headers)
            
    except requests.exceptions.RequestException as e:
        return Response(f"Proxy Error: {str(e)}", 502)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
