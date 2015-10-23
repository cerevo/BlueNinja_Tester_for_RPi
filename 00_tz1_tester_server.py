#!/usr/bin/env python
# coding: utf-8

from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from flask import Flask, render_template, redirect, request
from werkzeug.exceptions import abort

import time

import utils
import tz_power 
import firm_writer
import tester

#UI_DEBUG = True
UI_DEBUG = False

LOGS_PATH = './logs'
RESULTS_PATH = './results'

app = Flask(__name__)
app.debug = True

serial_no = ""

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/start')
def start():
	global serial_no
	ws = request.environ['wsgi.websocket'] 
	msg = ''
	if not ws:
		abort(400)

	serial_no = ws.receive()
	if serial_no.startswith('TZ1'):
		msg = '{"tester":"Start","result":true, "serial_no":"%s"}' % serial_no
	else:
		serial_no = 'invalid_serial'
		msg = '{"tester":"Start","result":false, "serial_no":"%s"}' % serial_no
	
	results = utils.logger_init('%s/%s.json' % (RESULTS_PATH, serial_no), 'wb')
	utils.websocket_send(ws, msg, results)
	utils.logger_term(results)
	return 'OK'

@app.route('/power')
def power():
	global serial_no
	ws = request.environ['wsgi.websocket'] 
	if not ws:
		abort(400)
	ws.receive()
	logger = utils.logger_init('%s/%s.json' % (LOGS_PATH, serial_no), 'wb')
	results = utils.logger_init('%s/%s.json' % (RESULTS_PATH, serial_no))
	if UI_DEBUG:
		time.sleep(0.5)
		utils.websocket_send(ws, '{"tester":"Current","result":true}', results)
		time.sleep(0.5)
		utils.websocket_send(ws, '{"tester":"Voltage","result":true}', results)
	else:
		com = utils.command_open()
		if com:
			tz_power.check(com, ws, logger, results)
			utils.command_close(com)
		else:
			utils.websocket_send(ws, '{"tester":"Current","result":false}', results)
			utils.websocket_send(ws, '{"tester":"Voltage","result":false}', results)
	utils.logger_term(logger)
	utils.logger_term(results)
	return 'OK'

@app.route('/bbfirm')
def brakeout_firm():
	global serial_no
	ws = request.environ['wsgi.websocket'] 
	if not ws:
		abort(400)
	results = utils.logger_init('%s/%s.json' % (RESULTS_PATH, serial_no))
	if UI_DEBUG:
		time.sleep(1)
		utils.websocket_send(ws, '{"tester":"BreakoutBoardFirm","result":true}', results)
	else:
		com = utils.command_open()
		if firm_writer.write_breakout(com):
			utils.websocket_send(ws, '{"tester":"BreakoutBoardFirm","result":true}', results)
		else:
			utils.websocket_send(ws, '{"tester":"BreakoutBoardFirm","result":false}', results)
		utils.command_close(com)
	utils.logger_term(results)
	return 'OK'

@app.route('/tzfirm')
def tz1_firm():
	global serial_no
	ws = request.environ['wsgi.websocket'] 
	if not ws:
		abort(400)
	results = utils.logger_init('%s/%s.json' % (RESULTS_PATH, serial_no))
	if UI_DEBUG:
		utils.websocket_send(ws, '{"tester":"TZ1Firm","result":true}', results)
	else:
		com = utils.command_open()

		if firm_writer.write_tester(com):
			utils.websocket_send(ws, '{"tester":"TZ1Firm","result":true}', results)
		else:
			utils.websocket_send(ws, '{"tester":"TZ1Firm","result":false}', results)
		utils.command_close(com)
	utils.logger_term(results)
	return 'OK'

@app.route('/switch')
def switch():
	global serial_no
	ws = request.environ['wsgi.websocket'] 
	if not ws:
		abort(400)
	results = utils.logger_init('%s/%s.json' % (RESULTS_PATH, serial_no))
	if UI_DEBUG:
		time.sleep(0.5)
		utils.websocket_send(ws, '{"tester":"SW1","result":true}', results)
		time.sleep(0.5)
		utils.websocket_send(ws, '{"tester":"SW2","result":true}', results)
	else:
		com = utils.command_open()
		tester.tester_sw(com, results, ws)
		utils.command_close(com)
	utils.logger_term(results)
	return 'OK'

@app.route('/io')
def io():
	global serial_no
	ws = request.environ['wsgi.websocket'] 
	if not ws:
		abort(400)
	logger = utils.logger_init('%s/%s.json' % (LOGS_PATH, serial_no))
	results = utils.logger_init('%s/%s.json' % (RESULTS_PATH, serial_no))
	if UI_DEBUG:
		time.sleep(0.1)
		utils.websocket_send(ws, '{"tester":"DI","result":true}', results)
		time.sleep(0.1)
		utils.websocket_send(ws, '{"tester":"ADC","result":true}', results)
		time.sleep(0.1)
		utils.websocket_send(ws, '{"tester":"UART","result":true}', results)
		time.sleep(0.1)
		utils.websocket_send(ws, '{"tester":"I2C","result":true}', results)
		time.sleep(0.1)
		utils.websocket_send(ws, '{"tester":"9-Axis","result":true}', results)
		time.sleep(0.1)
		utils.websocket_send(ws, '{"tester":"Airpressure","result":true}', results)
		time.sleep(0.1)
		utils.websocket_send(ws, '{"tester":"Charger","result":true}', results)
	else:
		com = utils.command_open()
		tester.tester_io(com, logger, results, ws)
		utils.command_close(com)
	utils.logger_term(logger)
	utils.logger_term(results)
	return 'OK'

@app.route('/usb')
def usb():
	global serial_no
	ws = request.environ['wsgi.websocket'] 
	if not ws:
		abort(400)
	results = utils.logger_init('%s/%s.json' % (RESULTS_PATH, serial_no))
	if UI_DEBUG:
		time.sleep(1)
		utils.websocket_send(ws, '{"tester":"USB","result":true}', results)
	else:
		com = utils.command_open()
		tester.tester_usb(com, results, ws)
		utils.command_close(com)
	utils.logger_term(results)
	return 'OK'

@app.route('/ble')
def ble():
	global serial_no
	ws = request.environ['wsgi.websocket'] 
	if not ws:
		abort(400)
	results = utils.logger_init('%s/%s.json' % (RESULTS_PATH, serial_no))
	if UI_DEBUG:
		time.sleep(1)
		utils.websocket_send(ws, '{"tester":"BLE","result":true,"RSSI":-50}', results)
	else:
		com = utils.command_open()
		tester.tester_ble(com, results, ws)
		utils.command_close(com)
	utils.logger_term(results)
	return 'OK'

@app.route('/rtc')
def rtc():
	ws = request.environ['wsgi.websocket'] 
	if not ws:
		abort(400)
	logger = utils.logger_init('%s/%s.json' % (LOGS_PATH, serial_no))
	results = utils.logger_init('%s/%s.json' % (RESULTS_PATH, serial_no))
	if UI_DEBUG:
		utils.websocket_send(ws, '{"tester":"RTC","result":true,"seconds":120}', results)
	else:
		com = utils.command_open()
		tester.tester_rtc(com, logger, results, ws)
		utils.command_close(com)
	utils.logger_term(results)
	utils.logger_term(logger)
	return 'OK'

@app.route('/term')
def term():
	ws = request.environ['wsgi.websocket'] 
	if not ws:
		abort(400)
	results = utils.logger_init('%s/%s.json' % (RESULTS_PATH, serial_no))
	if UI_DEBUG:
		pass
	else:
		com = utils.command_open()
		tester.tester_terminate(com)	#ファームウェア停止
		firm_writer.erase_tester(com)	#ファームウェア消去
		tz_power.off(com)		#USB電源OFF
		utils.command_close(com)
	utils.websocket_send(ws, '{"tester":"Terminated","result":true}', results)
	utils.logger_term(results)

	return 'OK'

@app.route('/reboot')
def reboot():
	ws = request.environ['wsgi.websocket'] 
	if not ws:
		abort(400)
	utils.system_reboot()
	return 'OK'

@app.route('/shutdown')
def shutdown():
	ws = request.environ['wsgi.websocket'] 
	if not ws:
		abort(400)
	utils.system_shutdown()
	return 'OK'

@app.route('/download_log')
def download_log():
	ret = utils.logger_archive()
	if ret[0] == 0:
		return  redirect("/%s" % ret[1])
	abort(500)

if __name__ == '__main__':
	http_server = WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
	http_server.serve_forever()
