#!/usr/bin/env python
# coding: utf-8

from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from flask import Flask, render_template, request
from werkzeug.exceptions import abort

import time

app = Flask(__name__)
app.debug = True

serial_no = ""

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/start')
def start():
	ws = request.environ['wsgi.websocket'] 
	if not ws:
		abort(400)
	serial_no = ws.receive()
	if serial_no.startswith('TZ1'):
		ws.send('{"tester":"Start","result":true}')
	else:
		ws.send('{"tester":"Start","result":false}')

@app.route('/power')
def power():
	ws = request.environ['wsgi.websocket'] 
	if not ws:
		abort(400)
	ws.receive()
	time.sleep(0.5)
	ws.send('{"tester":"Current","result":true}')
	time.sleep(0.5)
	ws.send('{"tester":"Voltage","result":true}')

@app.route('/bbfirm')
def brakeout_firm():
	ws = request.environ['wsgi.websocket'] 
	if not ws:
		abort(400)
	time.sleep(1)
	ws.send('{"tester":"BrakeoutBoardFirm","result":true}')

@app.route('/tzfirm')
def tz1_firm():
	ws = request.environ['wsgi.websocket'] 
	if not ws:
		abort(400)
	time.sleep(10)
	ws.send('{"tester":"TZ1Firm","result":true}')

@app.route('/switch')
def switch():
	ws = request.environ['wsgi.websocket'] 
	if not ws:
		abort(400)
	time.sleep(0.5)
	ws.send('{"tester":"SW1","result":true}')
	time.sleep(0.5)
	ws.send('{"tester":"SW2","result":true}')

@app.route('/io')
def io():
	ws = request.environ['wsgi.websocket'] 
	if not ws:
		abort(400)
	time.sleep(0.1)
	ws.send('{"tester":"DI","result":true}')
	time.sleep(0.1)
	ws.send('{"tester":"ADC","result":true}')
	time.sleep(0.1)
	ws.send('{"tester":"UART","result":true}')
	time.sleep(0.1)
	ws.send('{"tester":"I2C","result":true}')
	time.sleep(0.1)
	ws.send('{"tester":"9-Axis","result":true}')
	time.sleep(0.1)
	ws.send('{"tester":"Airpressure","result":true}')
	time.sleep(0.1)
	ws.send('{"tester":"Charger","result":true}')

@app.route('/usb')
def usb():
	ws = request.environ['wsgi.websocket'] 
	if not ws:
		abort(400)
	time.sleep(1)
	ws.send('{"tester":"USB","result":true}')

@app.route('/ble')
def ble():
	ws = request.environ['wsgi.websocket'] 
	if not ws:
		abort(400)
	time.sleep(1)
	ws.send('{"tester":"BLE","result":true,"RSSI":-50}')

@app.route('/rtc')
def rtc():
	ws = request.environ['wsgi.websocket'] 
	if not ws:
		abort(400)
	ws.send('{"tester":"RTC","result":true,"seconds":120}')

if __name__ == '__main__':
	http_server = WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
	http_server.serve_forever()
