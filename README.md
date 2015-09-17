# TZ1検査治具 RaspberryPiプログラム #
Pythonやシェルスクリプトで書いた検査プログラムとWebから実行できるI/F。  
実行の状況はWebSocketで送りつけてくるよ。

## 動作に必要なモノ
* Python 2.7.x  
  以下はpipでインストールする
    * gevent-websocket 
    * flask
* BlueZ 5.3x http://www.bluez.org/  
  Raspbianのパッケージはバージョンが古くBLE対応が不十分