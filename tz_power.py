# coding: utf-8

import utils

import gevent 
import json
import time

def check(com, ws, logger, results):
	#TZ1電源SW ON
	line = utils.command_send(com, "P001\r", None)
	if not line:
		utils.websocket_send(ws, '{"tester":"Current","result":false}', results)
		return False
	#USB電源ON
	utils.command_send(com, 'U000\r', None)
	
	#バッテリー充電Enable
	utils.command_send(com, "B001\r", None)
	time.sleep(0.2)
	utils.command_send(com, "B000\r", None)
	
	#過電流検出チェック
	line = utils.command_send(com, "C000\r", logger)
	res = json.loads(line)
	if res == None:
		utils.websocket_send(ws, '{"tester":"Current","result":false}', results)
		return False
	if res['current'] == 1:
		utils.websocket_send(ws, '{"tester":"Current","result":false}', results)
		return False
	utils.websocket_send(ws, '{"tester":"Current","result":true}', results)

	#TZ_VSYS(1/2)計測
	line = utils.command_send(com, "V001\r", logger)
	res = json.loads(line)
	if res == None:
		utils.websocket_send(ws, '{"tester":"Voltage","result":false}', results)
		return False
	if (res['volt'] < 0) or (res['volt'] > 4095):
		utils.websocket_send(ws, '{"tester":"Voltage","result":false}', results)
		return False
	
	#TZ_D3V3(1/2)計測
	line = utils.command_send(com, "V002\r", logger)
	res = json.loads(line)
	if res == None:
		utils.websocket_send(ws, '{"tester":"Voltage","result":false}', results)
		return False
	if (res['volt'] < 0) or (res['volt'] > 4095):
		utils.websocket_send(ws, '{"tester":"Voltage","result":false}', results)
		return False
	
	#BATT(1/2)計測
	line = utils.command_send(com, "V003\r", logger)
	res = json.loads(line)
	if res == None:
		utils.websocket_send(ws, '{"tester":"Voltage","result":false}', results)
		return False
	if (res['volt'] < 0) or (res['volt'] > 4095):
		utils.websocket_send(ws, '{"tester":"Voltage","result":false}', results)
		return False

	utils.websocket_send(ws, '{"tester":"Voltage","result":true}', results)
	
	#TZ1電源SW OFF
	utils.command_send(com, "P000\r", None)

	return True

