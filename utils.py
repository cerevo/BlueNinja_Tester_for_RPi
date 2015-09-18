# coding: utf-8
import os
import os.path
import serial
import sys

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

#コマンド送信
def command_open():
	try:
		com = serial.Serial(COM_DEV, COM_BOUD)
	except:
		com = None
	return com

def command_close(com):
	com.close()

def command_send(com, cmd, logger):
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

