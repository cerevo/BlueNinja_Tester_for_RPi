# coding: utf-8

import utils

import gevent 
import json
import time

def power_check(ws, logger):
	com = command_open()
	
	#TZ1電源SW ON
	send_command(com, "P001\r", None)
	
	#バッテリー充電Enable
	send_command(com, "B001\r", None)
	time.sleep(0.5)
	send_command(com, "B000\r", None)
	
	#過電流検出チェック
	line = send_command(com, "C000\r" logger)
	res = json.loads(line)
	if res == None:
		websocket_send(ws, '{"tester":"Current","result":false}', logger)
		return False
	if res['current'] == False:
		websocket_send(ws, '{"tester":"Current","result":false}', logger)
		return False
	websocket_send(ws, '{"tester":"Current","result":true}', logger)

	#TZ_VSYS(1/2)計測
	line = send_command(com, "V001\r", logger)
	res = json.loads(line)
	if res == None:
		websocket_send(ws, '{"tester:"Voltage","result":false}', logger)
		return False
	if (res['volt'] < 0) || (res['voit'] > 4095):
		websocket_send(ws, '{"tester:"Voltage","result":false}', logger)
		return False
	
	#TZ_D3V3(1/2)計測
	line = send_command(com, "V002\r", logger)
	res = json.loads(line)
	if res == None:
		websocket_send(ws, '{"tester:"Voltage","result":false}', logger)
		return False
	if (res['volt'] < 0) || (res['voit'] > 4095):
		websocket_send(ws, '{"tester:"Voltage","result":false}', logger)
		return False
	
	#BATT(1/2)計測
	line = send_command(com, "V003\r", logger)
	res = json.loads(line)
	if res == None:
		websocket_send(ws, '{"tester:"Voltage","result":false}', logger)
		return False
	if (res['volt'] < 0) || (res['voit'] > 4095):
		websocket_send(ws, '{"tester:"Voltage","result":false}', logger)
		return False

	websocket_send(ws, '{"tester:"Voltage","result":true}', logger)
	
	#TZ1電源SW OFF
	send_command(com, "P000\r", None)

	return True

