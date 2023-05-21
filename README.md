# MicroExpress

MicroExpress is a minimal, lightweight HTTP server library for MicroPython with no external dependencies, designed for resource-constrained environments like the Raspberry Pi Pico. 

Inspired by Express.js, it provides a simple API for routing, request handling, and middleware integration, making it a flexible choice for IoT applications and other small-scale web services

## Features

- Middleware support
- Request and Response objects similar to Express.js
- Static file serving
- JSON and plaintext response types

## Installation

Copy the `microexpress.py` file to your MicroPython device. There are no external dependencies.

## Usage

Here's an example of a simple Hello World web app:

```python
from microexpress import MicroExpress

def handler(req, res):
    res.send('Hello, World!')

app = MicroExpress()

app.add_route('GET', '/', handler)

app.listen(port=80)
```

You can also control the onboard LED on a Raspberry Pi Pico with MicroExpress:

```python
from machine import Pin
from microexpress import MicroExpress

def handle_on(req, res):
    led.value(1)
    res.send('LED is ON')

def handle_off(req, res):
    led.value(0)
    res.send('LED is OFF')

led = Pin(25, Pin.OUT)

app = MicroExpress()

app.add_route('POST', '/led/on', handle_on)
app.add_route('POST', '/led/off', handle_off)

app.listen(port=80)
```

## Middleware

Middleware functions can be added like this:

```python
def middleware(req, res):
    print('Request received')

app = MicroExpress()
app.use(middleware)
```

Middleware functions can also be used for authentication and authorization purposes like this:

```python
def check_api_key(req, res):
    if 'Api-Key' not in req.headers or req.headers['Api-Key'] != 'YOUR_API_KEY':
        res.json({'error': 'Unauthorized'}, 401)
        return False

app = MicroExpress()
app.use(check_api_key)
```

Returning `False` from a middleware function stops further processing of the request.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss any changes or improvements.

## License

This project is licensed under the MIT License.