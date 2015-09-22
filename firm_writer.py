# coding: utf-8

import utils

import commands
import gevent
import json
import os
import time

MOUNT_POINT = '/mnt'
TZ1IF_DEV = '/dev/sda'
FIRM_IF = 'fw/lpc11u35_tz1000_if.bin'
FIRM_TESTER = 'fw/tz1_TESTER.bin'

#マウント済みかチェック(マウントされてればデバイス名が返る)
def check_mount():
	ret = commands.getstatusoutput('mount -l | awk "/CDP-TZ01B/ {print $1}"')
	return ret[1]

def check_type():
	if os.path.exists('%s/firmware.bin' % MOUNT_POINT):
		return "ISP"
	if os.path.exists('%s/detected' % MOUNT_POINT):
		return "Interface"
	return ""

def mount_tz1(dev):
	return commands.getstatusoutput('sudo mount -t vfat %s %s' % (dev, MOUNT_POINT))

def umount_tz1(dev):
	return commands.getstatusoutput("sudo umount %s" % dev)

def write_breakout(com):
	ret = False
	#マウント済みか確認
	mount = check_mount()
	if mount == '':
		mount = TZ1IF_DEV
		if os.path.exists(mount):
			ret = mount_tz1(mount)	#マウントされてなければマウント
			if ret[0] != 0:
				print("Mount failed: %s" % ret[1])
				return False
		else:
			print("Device %s is not exists." % mount)
			return False
	#ISPモードで起動してるか確認
	fwtype = check_type() 
	if fwtype == "Interface":
		return True	#すでに書き込まれている
	if fwtype == "":
		print("Invalid firmware written.")
		return False	#想定外のファームが書かれている
	#ファーム書き込みスクリプト実行
	res = commands.getstatusoutput("sudo ./LinuxNXPISP.sh %s" % FIRM_IF)
	if res[1].find('Firmware update complete!') > -1:
		ret = True
	
	umount_tz1(mount)

	#USB電源再投入
	utils.command_send(com, 'U001\r', None)
	time.sleep(0.2)
	utils.command_send(com, 'U000\r', None) 
	time.sleep(0.5)
	
	return ret

def write_tester():
	#マウント済みか確認
	mount = check_mount()
	if mount == '':
		mount = TZ1IF_DEV
		if os.path.exists(mount):
			ret = mount_tz1(mount)	#マウントされてなければマウント
			if ret[0] != 0:
				print("Mount failed: %s" % ret[1])
				return False
		else:
			print("Device %s is not exists." % mount)
			return False
	#インターフェースファームで起動してるか確認
	if check_type() == "ISP":
		print("Boot on ISP mode.")
		return False	#インターフェースのファームが動いてない
	#binファイルをコピー(書き込み)
	ret = commands.getstatusoutput("sudo cp %s %s" % (FIRM_TESTER, MOUNT_POINT))
	if ret[0] != 0:
		return False
	#アンマウント
	ret = umount_tz1(mount)
	#ファームウェア起動待ち
	while os.path.exists(mount) == True:
		pass
	while os.path.exists(mount) == False:
		pass
	return True

def erase_tester(com):
	com.flushInput()
	utils.command_send(com, 'P000\r', None) #電源SW   OFF
	utils.command_send(com, 'R001\r', None) #リセット ON
	utils.command_send(com, 'E001\r', None) #イレース ON
	time.sleep(0.1)
	utils.command_send(com, 'P001\r', None) #電源SW   ON
	utils.command_send(com, 'R000\r', None) #リセット OFF
	time.sleep(3)
	utils.command_send(com, 'P000\r', None) #電源SW   OFF
	
