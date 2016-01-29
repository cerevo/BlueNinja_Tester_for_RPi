# coding: utf-8

import config
import utils

import commands
import datetime
import gevent
import json
import serial
import sys
import time 

import tz_power

def tester_sw(com, results, ws):
	com.timeout = 5
	#電源SW ON
	utils.command_send(com, 'P001\r', None)
	#ADC電源ON
	utils.command_send(com, 'A001\r', None)
	#起動待ち
	line = com.readline()
	print(line)
	if line.find('TZ1 TEST PROGRAM') == -1:
		tz_power.off(com)
		msg = '{"tester":"RUN","result":false}'
		utils.websocket_send(ws, msg, results)
		
		return False
	utils.websocket_send(ws, '{"tester":"RUN","result":true}', results)

	#電源SW OFF
	utils.command_send(com, 'P000\r', None)

	#SW1(GPIO_1)チェック
	com.timeout = 20
	line = com.readline()
	print(line)
	if line.find('POWER INIT') == -1:
		tz_power.off(com)
		utils.websocket_send(ws, '{"tester":"SW1","result":false}', results)
		return False
	utils.websocket_send(ws, '{"tester":"SW1","result":true}', results)

	#SW2(GPIO_6)チェック
	com.timeout = 20
	line = com.readline()
	print(line)
	if line.find("RUNNING") == -1:
		tz_power.off(com)
		utils.websocket_send(ws, '{"tester":"SW2","result":false}', results)
		return False

	#Testerファーム起動完了
	utils.websocket_send(ws, '{"tester":"SW2","result":true}', results)

def tester_io(com, logger, results, ws):

	#IOモードへ切り替え
	utils.command_send(com, 'm001\r', None)
	time.sleep(0.5)

	#DIチェック
	di_res = True
	##治具のDOを設定 (101010....)
	io_pattern = {'7':1,'8':0,'9':1,'16':0,'17':1,'18':0,'19':1,'20':0,'21':1,'22':0,'23':1}
	for key in io_pattern.iterkeys():
		cmd = ""
		if io_pattern[key] == 0:
			cmd = "OL"	
		else:
			cmd = "OH"
		utils.command_send(com, "%s%s\r" % (cmd, key.zfill(2)), None)
	##TZ1のDIを読む
	line = utils.command_send(com, 'g000\r', logger)	
	res = json.loads(line)
	di_res = di_res and (res['gpio'] == io_pattern)

	##治具のDOを設定 (010101....)
	io_pattern = {'7':0,'8':1,'9':0,'16':1,'17':0,'18':1,'19':0,'20':1,'21':0,'22':1,'23':0}
	for key in io_pattern.iterkeys():
		cmd = ""
		if io_pattern[key] == 0:
			cmd = "OL"	
		else:
			cmd = "OH"
		utils.command_send(com, "%s%s\r" % (cmd, key.zfill(2)), None)
	##TZ1のDIを読む
	line = utils.command_send(com, 'g000\r', logger)	
	res = json.loads(line)
	di_res = di_res and (res['gpio'] == io_pattern)

	utils.websocket_send(ws, '{"tester":"DI","result":true}', results)
	if di_res:
		utils.websocket_send(ws, '{"tester":"DI","result":true}', results)
	else:
		utils.websocket_send(ws, '{"tester":"DI","result":false}', results)

	#ADCチェック
	adc_res = True
	adc_val = [0, 0, 0, 0, 0]
	try:
		##ADCC12 Ch0
		line = utils.command_send(com, 'a000\r', logger)
		line = line[line.find('{'):]
		res = json.loads(line)
		if res:
			adc_val[0] = res['adc']
		##ADCC12 Ch1
		line = utils.command_send(com, 'a001\r', logger)
		line = line[line.find('{'):]
		res = json.loads(line)
		if res:
			adc_val[1] = res['adc']
		##ADCC12 Ch2
		line = utils.command_send(com, 'a002\r', logger)
		line = line[line.find('{'):]
		res = json.loads(line)
		if res:
			adc_val[2] = res['adc']
		##ADCC12 Ch3
		line = utils.command_send(com, 'a003\r', logger)
		line = line[line.find('{'):]
		res = json.loads(line)
		if res:
			adc_val[3] = res['adc']
		##ADCC24 Ch2
		line = utils.command_send(com, 'a102\r', logger)
		line = line[line.find('{'):]
		res = json.loads(line)
		if res:
			adc_val[4] = res['adc']
	
		## 判定
		### ADCC12 Ch0
		adc_res = adc_res and (adc_val[0] < 64000) and (adc_val[0] > 48000)
		### ADCC12 Ch1
		adc_res = adc_res and (adc_val[1] < adc_val[0])
		### ADCC12 Ch2
		adc_res = adc_res and (adc_val[2] < adc_val[1])
		### ADCC12 Ch3
		adc_res = adc_res and (adc_val[3] < adc_val[2]) and (adc_val[3] > 16000)
		### ADCC24 Ch2
		adc_res = adc_res and (adc_val[4] < 1800000) and (adc_val[4] > 800000)
		### 判定結果通知
		if adc_res:
			utils.websocket_send(ws, '{"tester":"ADC","result":true}', results)
		else:
			utils.websocket_send(ws, '{"tester":"ADC","result":false}', results)
	except:
		utils.websocket_send(ws, '{"tester":"ADC","result":false}', results)

	#ADC電源OFF
	utils.command_send(com, 'A000\r', None)

	## UART Echo
	time.sleep(0.1)
	echo_msg = 'The quick brown fox jumps over the lazy dog\n'
	com_echo = serial.Serial('/dev/ttyACM0', 9600)
	com_echo.timeout = 5
	com_echo.flushInput()
	com_echo.write(echo_msg)
	line = com_echo.readline()
	logger.write('{"cmd":"UART","send":"%s","recv":"%s"}\r\n' % (echo_msg.strip(), line.strip()))
	if line == echo_msg:
		utils.websocket_send(ws, '{"tester":"UART","result":true}', results)
	else:
		utils.websocket_send(ws, '{"tester":"UART","result":false}', results)
	com_echo.close()

	## I2C PingPong
	line = utils.command_send(com, 'i000\r', logger)
	try:
		line = line[line.find('{'):]
		res = json.loads(line)
		if res:
			if res['recv'] == 'PONG':
				utils.websocket_send(ws, '{"tester":"I2C","result":true}', results)
			else:
				utils.websocket_send(ws, '{"tester":"I2C","result":false}', results)
		else:
			utils.websocket_send(ws, '{"tester":"I2C","result":false}', results)
	except:
		utils.websocket_send(ws, '{"tester":"I2C","result":false}', results)
		
	## 9軸センサ
	sens_9axis_res = True
	line = utils.command_send(com, '9000\r', logger)
	try:
		line = line.strip()
		print(line)
		res = json.loads(line)
		if res:
			##ジャイロ
			sens_9axis_res = sens_9axis_res and (res['gyro'][0] > -100) and (res['gyro'][0] < 100)
			sens_9axis_res = sens_9axis_res and (res['gyro'][1] > -100) and (res['gyro'][1] < 100)
			sens_9axis_res = sens_9axis_res and (res['gyro'][2] > -100) and (res['gyro'][2] < 100)
			##加速度
			sens_9axis_res = sens_9axis_res and (res['accel'][0] > -200) and (res['accel'][0] < 200)
			sens_9axis_res = sens_9axis_res and (res['accel'][1] > -200) and (res['accel'][1] < 200)
			sens_9axis_res = sens_9axis_res and (res['accel'][2] > 1843) and (res['accel'][2] < 2253)	#1.0G +-10%
			##地磁気
			sens_9axis_res = sens_9axis_res and not ((res['magnetometer'][0] == 0) and (res['magnetometer'][1] == 0) and (res['magnetometer'][2] == 0))
			##判定結果通知
			if sens_9axis_res:
				utils.websocket_send(ws, '{"tester":"9-Axis","result":true}', results)
			else:
				utils.websocket_send(ws, '{"tester":"9-Axis","result":false}', results)
		else:
			utils.websocket_send(ws, '{"tester":"9-Axis","result":false}', results)
	except:
		print "Exception: ", sys.exc_info()[0]
		utils.websocket_send(ws, '{"tester":"9-Axis","result":false}', results)
		
	# 気圧センサー
	sens_ap_res = True
	line = utils.command_send(com, 'p000\r', logger)
	try:
		line = line[line.find('{'):]
		res = json.loads(line)
		if res:
			sens_ap_res = ((res['airpressure'] / 256) > 80000) and ((res['airpressure'] / 256) < 120000)
			if sens_ap_res:
				utils.websocket_send(ws, '{"tester":"Airpressure","result":true}', results)
			else:
				utils.websocket_send(ws, '{"tester":"Airpressure","result":false}', results)
		else:
			utils.websocket_send(ws, '{"tester":"Airpressure","result":false}', results)
	except:
		print "Exception: ", sys.exc_info()[0]
		utils.websocket_send(ws, '{"tester":"Airpressure","result":false}', results)
		
	# 充電ICステータス
	line = utils.command_send(com, 'c000\r', logger)
	try:
		line = line[line.find('{'):]
		res = json.loads(line)
		if res:
			if res['reg'][0] == 0x10:
				#充電中ステータスでFailなし
				utils.websocket_send(ws, '{"tester":"Charger","result":true}', results)
			else:
				utils.websocket_send(ws, '{"tester":"Charger","result":false}', results)
		else:
			utils.websocket_send(ws, '{"tester":"Charger","result":false}', results)
	except:
		print "Exception: ", sys.exc_info()[0]
		utils.websocket_send(ws, '{"tester":"Charger","result":false}', results)

	#選択モードへ切り替え
	utils.command_send(com, 'm000\r', None)

def tester_usb(com, results, ws):
	# USBモードへ切り替え
	utils.command_send(com, 'm002\r', None)

	# USB認識チェック
	for i in range(0, 10):
		ret = commands.getstatusoutput('lsusb -d 0930:1703')
		if len(ret[1]) > 0:
			msg = '{"tester":"USB","result":true}'
			utils.websocket_send(ws, msg, results)
			break;
	else:
		msg = '{"tester":"USB","result":false}'
		utils.websocket_send(ws, msg, results)

	# 選択モードへ切り替え
	utils.command_send(com, 'm000\r', None)

def tester_ble(com, results, ws):
	# BLEモードへ切り替え
	utils.command_send(com, 'm003\r', None)

	# BLEスキャン
	ret = commands.getstatusoutput('./get_rssi.sh %s' % config.TESTER_SUFFIX)
	if ret[0] == 0:
		rssi = ret[1].split()[1]
		msg = '{"tester":"BLE","result":true,"RSSI":%s}' % rssi
	else:
		msg = '{"tester":"BLE","result":false}'
	utils.websocket_send(ws, msg, results)

	# 選択モードへ切り替え
	utils.command_send(com, 'm000\r', None)

def tester_rtc(com, logger, results, ws):
	start_time = datetime.datetime(2015, 1, 1, 0, 0, 0)
	line = utils.command_send(com, 'r000\r', logger)
	res = json.loads(line)
	if res:
		now_time = datetime.datetime(res['year'], res['month'], res['day'], res['hour'], res['minute'], res['second'])
		delta = now_time - start_time
		if delta.seconds > 1:
			msg = '{"tester":"RTC","result":true,"seconds":%d}' % delta.seconds
		else:
			msg = '{"tester":"RTC","result":false,"seconds":%d}' % delta.seconds
		utils.websocket_send(ws, msg, results)
	else:
		msg = '{"tester":"RTC","result":false}'
		utils.websocket_send(ws, msg, results)
	
def tester_terminate(com):
	utils.command_send(com, 'm999\r', None)

