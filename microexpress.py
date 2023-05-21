from usocket import socket, AF_INET, SOCK_STREAM
from builtins import len, open, OSError
from ujson import dumps, loads


class Request:
    def __init__(self, headers, body, params):
        self.headers = headers
        self.body = body
        self.params = params


class Response:
    def __init__(self, client):
        self.client = client
        self.headers = {
            'Connection': 'close',
            'Cache-Control': 'max-age=0, no-cache, must-revalidate, proxy-revalidate',
        }

    def set_header(self, key, value):
        self.headers[key] = value

    def send(self, body, content_type='text/plain', status_code=200):
        self.__finalize_response(body, content_type, status_code)

    def html(self, html, status_code=200):
        self.__finalize_response(html, 'application/html', status_code)

    def json(self, data, status_code=200):
        self.__finalize_response(dumps(data), 'application/json', status_code)

    def __finalize_response(self, body, content_type, status_code):
        self.headers['Content-Type'] = content_type
        self.headers['Content-Length'] = len(body)

        self.client.write(f'HTTP/1.1 {status_code} {self.__get_status_message(status_code)}\r\n')
        for key, value in self.headers.items():
            self.client.write(f'{key}: {value}\r\n')
        self.client.write('\r\n' + body)
        self.client.close()

    def __get_status_message(self, status_code):
        status_messages = {
            200: 'OK',
            201: 'Created',
            204: 'No Content',
            400: 'Bad Request',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not Found',
            500: 'Internal Server Error'
        }
        return status_messages.get(status_code, '')


class MicroExpress:
    def __init__(self):
        self.routes = {}
        self.middleware = []

    def add_route(self, method, path, handler):
        self.routes[(method, path)] = handler

    def use(self, middleware_func):
        self.middleware.append(middleware_func)

    def serve_static(self, path, content_type='text/html'):
        def handler(req, res):
            try:
                with open(path, 'r') as f:
                    content = f.read()
                res.send(content, content_type)
            except OSError:
                self.__handle_not_found(req, res)
        return handler

    def listen(self, port=80, backlog=1):
        server = socket(AF_INET, SOCK_STREAM)
        server.bind(('0.0.0.0', port))
        server.listen(backlog)

        while True:
            client, addr = server.accept()
            self.__handle_request(client)

    def __handle_request(self, client):
        req = client.recv(1024).decode('utf-8')
        method, path, _ = req.split(' ', 2)
        path, params = self.__parse_path_and_params(path)
        body, headers = self.__parse_request(req)

        if (method, path) in self.routes:
            handler = self.routes[(method, path)]
        else:
            handler = self.__handle_not_found

        request = Request(headers, body, params)
        response = Response(client)

        try:
            for middleware_func in self.middleware:
                result = middleware_func(request, response)
                if result is False:
                    client.close()
                    return

            handler(request, response)
        except:
            self.__handle_server_error(request, response)

    @staticmethod
    def __parse_request(req):
        headers, body = req.split('\r\n\r\n')
        headers = headers.split('\r\n')[1:]
        headers = {k: v for k, v in (h.split(': ') for h in headers)}
        if headers.get('Content-Type') == 'application/json':
            body = loads(body)
        return body, headers

    @staticmethod
    def __parse_path_and_params(path):
        if '?' in path:
            path, param_string = path.split('?', 1)
            param_pairs = param_string.split('&')
            params = {k: v for k, v in (p.split('=') for p in param_pairs)}
        else:
            params = {}
        return path, params

    @staticmethod
    def __handle_not_found(_, response):
        response.json({'error': 'Not Found'}, 404)

    @staticmethod
    def __handle_server_error(_, response):
        response.json({'error': 'Internal Server Error'}, 500)
