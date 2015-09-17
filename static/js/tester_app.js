//Panel
var panelMessage;
//Input
var inputSerial;
//Button
var btnStart;
//text
var textMessage;
//Result labels
var resCurrent;
var resVoltage;
var resBrakeoutBoardFirm;
var resTZ1Firm;
var resSwitch;
var resDI;
var resADC;
var resUART;
var resI2C;
var res9Axis;
var resAirpressure;
var resCharger;
var resUSB;
var resBLE;
var resRTC;
//Websocket
var wsStart;
var wsPower;
var wsBbFirm;
var wsTzFirm;
var wsSwitch1;
var wsSwitch2;
var wsIo;
var wsUSB;
var wsBLE;
var wsRTC;

var serialNo;
var urlBase;

function result_reset()
{
	$('div.label').each(function(i, elem) {
		$(elem).removeClass('label-info');
		$(elem).removeClass('label-success');
		$(elem).removeClass('label-danger');

		$(elem).addClass('label-default');
	});

	res_ble_set_rssi('---');
	res_rtc_set_sec('---');
}

function result_check_success()
{
	var res = true;
	$('div.label').each(function(i, elem) {
		res &= $(elem).hasClass('label-success');
	});
	return res;
}

function message_set_running()
{
	btnStart.prop('disabled', true);
	inputSerial.prop('disabled', true);

	textMessage.removeClass('text-success');
	textMessage.removeClass('text-danger');
	textMessage.text(serialNo + ": TEST RUNNING");
}

function message_set_all_success()
{
	btnStart.prop('disabled', false);
	inputSerial.prop('disabled', false);

	textMessage.addClass('text-success');
	textMessage.text(serialNo + ": TEST ALL SUCCESS");
}

function message_set_failed()
{
	btnStart.prop('disabled', false);
	inputSerial.prop('disabled', false);

	textMessage.addClass('text-danger');
	textMessage.text(serialNo + ": TEST FAILED");
}

function res_ble_set_rssi(rssi)
{
	$('#resBLE_RSSI').text(rssi + ' dB');
}

function res_rtc_set_sec(sec)
{
	$('#resRTC_SECONDS').text(sec + " sec.");
}

/**/
function wsStart_onmessage(e)
{
	var json = $.parseJSON(e.data);
	if (json.result) {
		message_set_running();
		wsPower = new WebSocket(urlBase + '/power');
		wsPower.onmessage = wsPower_onmessage;
		wsPower.onopen = function() {
			resCurrent.removeClass('label-default');
			resCurrent.addClass('label-info');
			resVoltage.removeClass('label-default');
			resVoltage.addClass('label-info');
			wsPower.send('');
		}
	}
}

/**/
function wsPower_onmessage(e)
{
	var json = $.parseJSON(e.data);
	switch (json.tester) {
		case 'Current':
			resCurrent.removeClass('label-info');
			if (json.result) {
				resCurrent.addClass('label-success');
			} else {
				resCurrent.addClass('label-danger');
			}
			break;
		case 'Voltage':
			resVoltage.removeClass('label-info');
			if (json.result) {
				resVoltage.addClass('label-success');
				//ブレイクアウトボードのファーム書き込み実行
				wsBbFirm = new WebSocket(urlBase + '/bbfirm');
				wsBbFirm.onmessage = wsBbFirm_onmessage
				wsBbFirm.onopen = function() {
					resBrakeoutBoardFirm.removeClass('label-default');
					resBrakeoutBoardFirm.addClass('label-info');
					wsBbFirm.send('');
				};
			} else {
				message_set_failed();
				resCurrent.addClass('label-danger');
			}
			break;
	}
}

/**/
function wsBbFirm_onmessage(e)
{
	var json = $.parseJSON(e.data);
	resBrakeoutBoardFirm.removeClass('label-info');
	if (json.result) {
		resBrakeoutBoardFirm.addClass('label-success');
		/* Testerファームウェアの書き込み実行 */
		wsTzFirm = new WebSocket(urlBase + '/tzfirm');
		wsTzFirm.onmessage = wsTzFirm_onmessage;
		wsTzFirm.onopen = function() {
			resTZ1Firm.removeClass('label-default');
			resTZ1Firm.addClass('label-info');
			wsTzFirm.send('');
		};
	} else {
		message_set_failed();
		resBrakeoutBoardFirm.addClass('label-danger');
	}
}

/**/
function wsTzFirm_onmessage(e)
{
	var json = $.parseJSON(e.data);
	resTZ1Firm.removeClass('label-info');
	if (json.result) {
		resTZ1Firm.addClass('label-success');
		/* ファームウェア実行開始操作待ち */
		wsSwitch = new WebSocket(urlBase + '/switch');
		wsSwitch.onmessage = wsSwitch_onmessage;
		wsSwitch.onopen = function() {
			resSwitch1.removeClass('label-default');
			resSwitch1.addClass('label-info');
			resSwitch2.removeClass('label-default');
			resSwitch2.addClass('label-info');
			wsSwitch.send('');
		};
	} else {
		message_set_failed();
		resTZ1Firm.addClass('label-danger');
	}
}

/**/
function wsSwitch_onmessage(e)
{
	var json = $.parseJSON(e.data);
	switch (json.tester) {
	case 'SW1':
		resSwitch1.removeClass('label-info');
		if (json.result) {
			resSwitch1.addClass('label-success');
		} else {
			resSwitch2.addClass('label-danger');
			message_set_failed();
		}
		break;
	case 'SW2':
		resSwitch2.removeClass('label-info');
		if (json.result) {
			resSwitch2.addClass('label-success');
			/* IO系テスト実行 */
			wsIo = new WebSocket(urlBase + '/io');
			wsIo.onmessage = wsIo_onmessage;
			wsIo.onopen = function() {
				resDI.removeClass('label-default');
				resDI.addClass('label-info');
				resADC.removeClass('label-default');
				resADC.addClass('label-info');
				resUART.removeClass('label-default');
				resUART.addClass('label-info');
				resI2C.removeClass('label-default');
				resI2C.addClass('label-info');
				res9Axis.removeClass('label-default');
				res9Axis.addClass('label-info');
				resAirpressure.removeClass('label-default');
				resAirpressure.addClass('label-info');
				resCharger.removeClass('label-default');
				resCharger.addClass('label-info');
				wsIo.send('');
			};
		} else {
			message_set_failed();
			resSwitch2.addClass('label-danger');
		}
	}
}

/**/
function wsIo_onmessage(e)
{
	var json = $.parseJSON(e.data);
	switch (json.tester) {
	case 'DI':
		resDI.removeClass('label-info');
		if (json.result) {
			resDI.addClass('label-success');
		} else {
			resDI.addClass('label-danger');
		}
		break;
	case 'ADC':
		resADC.removeClass('label-info');
		if (json.result) {
			resADC.addClass('label-success');
		} else {
			resADC.addClass('label-danger');
		}
		break;
	case 'UART':
		resUART.removeClass('label-info');
		if (json.result) {
			resUART.addClass('label-success');
		} else {
			resUART.addClass('label-danger');
		}
		break;
	case 'I2C':
		resI2C.removeClass('label-info');
		if (json.result) {
			resI2C.addClass('label-success');
		} else {
			resI2C.addClass('label-danger');
		}
		break;
	case '9-Axis':
		res9Axis.removeClass('label-info');
		if (json.result) {
			res9Axis.addClass('label-success');
		} else {
			res9Axis.addClass('label-danger');
		}
		break;
	case 'Airpressure':
		resAirpressure.removeClass('label-info');
		if (json.result) {
			resAirpressure.addClass('label-success');
		} else {
			resAirpressure.addClass('label-danger');
		}
		break;
	case 'Charger':
		resCharger.removeClass('label-info');
		if (json.result) {
			resCharger.addClass('label-success');
		} else {
			resCharger.addClass('label-danger');
		}
		/* USBテスト実行(IOテストの結果に関係なく実行) */
		wsUSB = new WebSocket(urlBase + '/usb');
		wsUSB.onmessage = wsUSB_onmessage;
		wsUSB.onopen = function() {
			resUSB.removeClass('label-default');
			resUSB.addClass('label-info');
			wsUSB.send('');
		};
		break;
	}
}

/**/
function wsUSB_onmessage(e)
{
	var json = $.parseJSON(e.data);
	resUSB.removeClass('label-info');
	if (json.result) {
		resUSB.addClass('label-success');
	} else {
		resUSB.addClass('label-danger');
	}
	/* BLEテスト実行(USBテストの結果に関係なく実行) */
	wsBLE = new WebSocket(urlBase + '/ble');
	wsBLE.onmessage = wsBLE_onmessage;
	wsBLE.onopen = function() {
		resBLE.removeClass('label-default');
		resBLE.addClass('label-info');
		wsBLE.send('');
	};
}

/**/
function wsBLE_onmessage(e)
{
	var json = $.parseJSON(e.data);
	resBLE.removeClass('label-info');
	if (json.result) {
		resBLE.addClass('label-success');
		res_ble_set_rssi(json.RSSI);
	} else {
		resBLE.addClass('label-danger');
	}
	/* RTCテスト実行(BLEテストの結果に関係なく実行) */
	wsRTC = new WebSocket(urlBase + '/rtc');
	wsRTC.onmessage = wsRTC_onmessage;
	wsRTC.onopen = function() {
		resRTC.removeClass('label-default');
		resRTC.addClass('label-info');
		wsRTC.send('');
	};
}

/**/
function wsRTC_onmessage(e)
{
	var json = $.parseJSON(e.data);
	resRTC.removeClass('label-info');
	if (json.result) {
		resRTC.addClass('label-success');
		res_rtc_set_sec(json.seconds);
	} else {
		resRTC.addClass('label-danger');
	}
	if (result_check_success()) {
		message_set_all_success();
	} else {
		message_set_failed();
	}		
}

$(function() {
	//Panel
	panelMessage = $('#panelMessage');
	//Input
	inputSerial = $("#inputSerial");
	//Button
	btnStart = $("#btnStart");
	//Text
	textMessage = $('#textMessage');
	//Result labels
	resCurrent = $("#resCurrent");
	resVoltage = $("#resVoltage");
	resBrakeoutBoardFirm = $("#resBrakeoutBoardFirm");
	resTZ1Firm = $("#resTZ1Firm");
	resSwitch1 = $("#resSwitch1");
	resSwitch2 = $("#resSwitch2");
	resDI = $("#resDI");
	resADC = $("#resADC");
	resUART = $("#resUART");
	resI2C = $("#resI2C");
	res9Axis = $("#res9Axis");
	resAirpressure = $("#resAirpressure");
	resCharger = $("#resCharger");
	resUSB = $("#resUSB");
	resBLE = $("#resBLE");
	resRTC = $("#resRTC");

	urlBase = 'ws://' + $(location).attr('host');

	btnStart.click(function() {
		serialNo = 'TZ159' + ('00000' + inputSerial.val()).slice(-5);
		result_reset();
		wsStart  = new WebSocket(urlBase + '/start');
		wsStart.onmessage = wsStart_onmessage;
		wsStart.onopen = function() {
			wsStart.send(serialNo);
		};
	});
});
