# coding: utf-8

import utils

import gevent 
import json
import time

def check(com, ws, logger, results):
	#TZ1電源SW ON
	utils.send_command(com, "P001\r", None)
	
	#バッテリー充電Enable
	utils.send_command(com, "B001\r", None)
	time.sleep(0.2)
	utils.send_command(com, "B000\r", None)
	
	#過電流検出チェック
	line = utils.send_command(com, "C000\r", logger)
	res = json.loads(line)
	if res == None:
		utils.websocket_send(ws, '{"tester":"Current","result":false}', results)
		return False
	if res['current'] == False:
		utils.websocket_send(ws, '{"tester":"Current","result":false}', results)
		return False
	utils.websocket_send(ws, '{"tester":"Current","result":true}', results)

	#TZ_VSYS(1/2)計測
	line = utils.send_command(com, "V001\r", logger)
	res = json.loads(line)
	if res == None:
		utils.websocket_send(ws, '{"tester:"Voltage","result":false}', results)
		return False
	if (res['volt'] < 0) or (res['voit'] > 4095):
		utils.websocket_send(ws, '{"tester:"Voltage","result":false}', results)
		return False
	
	#TZ_D3V3(1/2)計測
	line = utils.send_command(com, "V002\r", logger)
	res = json.loads(line)
	if res == None:
		utils.websocket_send(ws, '{"tester:"Voltage","result":false}', results)
		return False
	if (res['volt'] < 0) or (res['voit'] > 4095):
		utils.websocket_send(ws, '{"tester:"Voltage","result":false}', results)
		return False
	
	#BATT(1/2)計測
	line = utils.send_command(com, "V003\r", logger)
	res = json.loads(line)
	if res == None:
		utils.websocket_send(ws, '{"tester:"Voltage","result":false}', results)
		return False
	if (res['volt'] < 0) or (res['voit'] > 4095):
		utils.websocket_send(ws, '{"tester:"Voltage","result":false}', results)
		return False

	utils.websocket_send(ws, '{"tester:"Voltage","result":true}', results)
	
	#TZ1電源SW OFF
	utils.send_command(com, "P000\r", None)

	return True

