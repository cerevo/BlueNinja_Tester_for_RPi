# coding: utf-8

import config
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
	
	#TZ1電源SW ON
	line = utils.command_send(com, "P001\r", None)
	if not line:
		utils.websocket_send(ws, '{"tester":"Current","result":false}', results)
		return False
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

	cnt = 0
	while True:
		#バッテリー充電Enable Hi
		utils.command_send(com, "B001\r", None)
		time.sleep(0.5)
		#バッテリー充電Enable Lo
		utils.command_send(com, "B000\r", None)
		time.sleep(0.5)
		if check_CHG(com, logger):
			break
		cnt = cnt + 1
		if cnt > 10:
			utils.websocket_send(ws, '{"tester":"Voltage","result":false}', results)
			return False
		time.sleep(1)

	#TZ_VSYS(1/2)計測
	if check_VSYS(com, logger) == False:
		utils.websocket_send(ws, '{"tester":"Voltage","result":false}', results)
		return False
	
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
	#範囲チェック(治具No.1 3.12[V]-3.44[V])
	if (res['volt'] < config.LOWER_3V3) or (res['volt'] > config.UPPER_3V3):
		return False
	return True

def check_VSYS(com, logger):
	#TZ_VSYS(1/2)計測
	line = utils.command_send(com, "V001\r", logger)
	line = line[line.find('{'):]
	res = json.loads(line)
	if res == None:
		return False
	#範囲チェック(治具No.1 3.81[V]-4.05[V])
	if (res['volt'] < config.LOWER_VSYS) or (res['volt'] > config.UPPER_VSYS):
		return False
	return True

def check_CHG(com, logger):
	print "L:%d, U:%d" % (config.LOWER_CHG, config.UPPER_CHG)
	#CHG(1/2)計測
	line = utils.command_send(com, "V003\r", logger)
	line = line[line.find('{'):]
	res = json.loads(line)
	if res == None:
		return False
	#範囲チェック(治具No.1 3.80[V]-4.04[V])
	if (res['volt'] < config.LOWER_CHG) or (res['volt'] > config.UPPER_CHG):
		return False
	return True

def off(com):
	#USB電源OFF
	utils.command_send(com, 'U001\r', None)

