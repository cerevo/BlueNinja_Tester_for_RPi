# coding: utf-8
import commands
import os
import os.path
import serial
import sys
import datetime

COM_DEV  = '/dev/ttyUSB0'
COM_BOUD = 9600

#ログ出力
def logger_init(path, mode='ab'):
	return open(path, mode)

def logger_term(logger):
	logger.close()

def logger_put(logger, msg):
	if logger:
		logger.write(msg)

def logger_archive():
	path = "static/logs.txz"
	ret = commands.getstatusoutput("tar cJf %s logs/" % path);
	return [ret[0], path]

#コマンド送信
def command_open(timeout=5):
	try:
		com = serial.Serial(COM_DEV, COM_BOUD)
		com.timeout = timeout 
	except:
		com = None
	return com

def command_close(com):
	com.close()

def command_send(com, cmd, logger):
	com.flushInput()
	com.write(cmd)
	line = com.readline()
	if logger != None:
		logger.write(line.replace('\0', ''))
	return line

#Websocket送信
def websocket_send(ws, cmd, logger):
	ws.send(cmd)
	if logger:
		logger.write('%s\r\n' % cmd)

#OS
def system_shutdown():
	ret = commands.getstatusoutput("sudo shutdown -h now")
	return ret[0]

def system_reboot():
	ret = commands.getstatusoutput("sudo shutdown -r now")
	return ret[0]
