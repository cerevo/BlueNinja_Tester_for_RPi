# coding: utf-8

import utils

import gevent 
import json
import time

def check(com, ws, logger, results):
	#USB電源OFF
	utils.command_send(com, 'U001\r', None)
	time.sleep(0.5)
	#USB電源ON
	utils.command_send(com, 'U000\r', None)
	#バッテリー充電Enable Hi
	utils.command_send(com, "B001\r", None)
	#TZ1電源SW ON
	line = utils.command_send(com, "P001\r", None)
	if not line:
		utils.websocket_send(ws, '{"tester":"Current","result":false}', results)
		return False

	time.sleep(1)

	#バッテリー充電Enable Lo
	utils.command_send(com, "B000\r", None)

	time.sleep(1)
	
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

	#TZ_D3V3(1/2)計測
	if check_3V3(com, logger) == False:
		utils.websocket_send(ws, '{"tester":"Voltage","result":false}', results)
		return False

	utils.websocket_send(ws, '{"tester":"Voltage","result":true}', results)
	
	#TZ1電源SW OFF
	utils.command_send(com, "P000\r", None)

	return True

def check_3V3(com, logger):
	#TZ_D3V3(1/2)計測
	line = utils.command_send(com, "V002\r", logger)
	line = line[line.find('{'):]
	res = json.loads(line)
	if res == None:
		return False
	#範囲チェック(治具No.1 3.1[V]-3.5[V])
	if (res['volt'] < 1906) or (res['volt'] > 2152):
		return False
	return True

def check_VSYS(com, logger):
	#TZ_VSYS(1/2)計測
	line = utils.command_send(com, "V001\r", logger)
	line = line[line.find('{'):]
	res = json.loads(line)
	if res == None:
		return False
	#範囲チェック(治具No.1 3.8[V]-4.2[V])
	if (res['volt'] < 2336) or (res['volt'] > 2583):
		return False
	return True

def check_CHG(com, logger):
	#CHG(1/2)計測
	line = utils.command_send(com, "V003\r", logger)
	line = line[line.find('{'):]
	res = json.loads(line)
	if res == None:
		return False
	#範囲チェック(治具No.1 3.8[V]-4.2[V])
	if (res['volt'] < 2336) or (res['volt'] > 2583):
		return False
	return True

def off(com):
	#USB電源OFF
	utils.command_send(com, 'U001\r', None)

