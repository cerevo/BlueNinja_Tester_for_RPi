# TZ1検査治具 RaspberryPiプログラム #
Pythonやシェルスクリプトで書いた検査プログラムとWebから実行できるI/F。  
実行の状況はWebSocketで送りつけてくるよ。

## 動作に必要なモノ
* Python 2.7.x  
  ヘッダ類も必要 
  以下はpipでインストールする
    * pyserial
    * gevent-websocket 
    * flask

```
    sudo aptitude install python-dev
    pip install pyserial gevent-websocket flask
```  

* BlueZ 5.3x http://www.bluez.org/  
  Raspbianのパッケージはバージョンが古くBLE対応が不十分  


```
    sudo aptitude install libglib2.0-dev libdbus-1-dev libical-dev libreadline6-dev libudev-dev
    tar xJf bluez-5.3x.tar.xz
    cd bluez-5.3x
    ./configure --disable-systemd --enable-library
    make
    sudo make install 
    sudo cp attrib/gatttool /usr/local/bin
```