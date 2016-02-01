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
		off(com)
		return False
	time.sleep(1)
	
	#過電流検出チェック
	line = utils.command_send(com, "C000\r", logger)
	res = json.loads(line)
	if res == None:
		utils.websocket_send(ws, '{"tester":"Current","result":false}', results)
		off(com)
		return False
	if res['current'] != 0:
		utils.websocket_send(ws, '{"tester":"Current","result":false}', results)
		off(com)
		return False
	utils.websocket_send(ws, '{"tester":"Current","result":true}', results)

	cnt = 0
	ret = True
	while True:
		#バッテリー充電Enable Hi
		utils.command_send(com, "B001\r", None)
		time.sleep(0.5)
		#バッテリー充電Enable Lo
		utils.command_send(com, "B000\r", None)
		time.sleep(0.5)
		res, v = check_CHG(com, logger)
		if res:
			utils.websocket_send(ws, '{"tester":"VCHG","result":true, "volt":"%.2fV"}' % v, results)
			break
		cnt = cnt + 1
		if cnt >= 5:
			if v != None:
				utils.websocket_send(ws, '{"tester":"VCHG","result":false, "volt":"%.2fV"}' % v, results)
			else:
				utils.websocket_send(ws, '{"tester":"VCHG","result":false, "volt":"-"}', results)
			ret = False
			break
		time.sleep(0.5)

	#TZ_VSYS(1/2)計測
	res, v = check_VSYS(com, logger)
	if res:
		utils.websocket_send(ws, '{"tester":"VSYS","result":true, "volt":"%.2fV"}' % v, results)
	else:
		if v != None:
			utils.websocket_send(ws, '{"tester":"VSYS","result":false, "volt":"%.2fV"}' % v, results)
		else:
			utils.websocket_send(ws, '{"tester":"VSYS","result":false, "volt":"-"}', results)
		ret = False
	
	#TZ_D3V3(1/2)計測
	res, v = check_3V3(com, logger)
	print v
	#if check_3V3(com, logger):
	if res:
		utils.websocket_send(ws, '{"tester":"V3D3","result":true, "volt":"%.2fV"}' % v, results)
	else:
		if v != None:
			utils.websocket_send(ws, '{"tester":"V3D3","result":false, "volt":"%.2fV"}' % v, results)
		else:
			utils.websocket_send(ws, '{"tester":"V3D3","result":false, "volt":"-"}', results)
		ret = False

	if ret == False:
		off(com)
	
	#TZ1電源SW OFF
	utils.command_send(com, "P000\r", None)

	return ret

def check_3V3(com, logger):
	#TZ_D3V3(1/2)計測
	line = utils.command_send(com, "V002\r", logger)
	line = line[line.find('{'):]
	res = json.loads(line)
	if res == None:
		return (False, None)
	#範囲チェック(治具No.1 3.12[V]-3.44[V])
	v = (float(res['volt']) / float(config.REF_33)) * 3.3
	print "Lower:%d, Upper:%d D3V3:%d %f" % (config.LOWER_3V3, config.UPPER_3V3, res['volt'], v)
	if (res['volt'] < config.LOWER_3V3) or (res['volt'] > config.UPPER_3V3):
		return (False, v)
	return (True, v)

def check_VSYS(com, logger):
	#TZ_VSYS(1/2)計測
	line = utils.command_send(com, "V001\r", logger)
	line = line[line.find('{'):]
	res = json.loads(line)
	if res == None:
		return (False, None)
	#範囲チェック(治具No.1 3.81[V]-4.05[V])
	v = (float(res['volt']) / float(config.REF_33)) * 3.3
	print "Lower:%d, Upper:%d VSYS:%d %f" % (config.LOWER_VSYS, config.UPPER_VSYS, res['volt'], v)
	if (res['volt'] < config.LOWER_VSYS) or (res['volt'] > config.UPPER_VSYS):
		return (False, v)
	return (True, v)

def check_CHG(com, logger):
	#CHG(1/2)計測
	line = utils.command_send(com, "V003\r", logger)
	line = line[line.find('{'):]
	res = json.loads(line)
	if res == None:
		return (False, None)
	#範囲チェック(治具No.1 3.80[V]-4.04[V])
	v = (float(res['volt']) / float(config.REF_33)) * 3.3
	print "Lower:%d, Upper:%d VCHG:%d %f" % (config.LOWER_CHG, config.UPPER_CHG, res['volt'], v)
	if (res['volt'] < config.LOWER_CHG) or (res['volt'] > config.UPPER_CHG):
		return (False, v)
	return (True, v)

def off(com):
	#USB電源OFF
	utils.command_send(com, 'U001\r', None)

