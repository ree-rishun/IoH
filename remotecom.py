# -*- coding: utf-8 -*-
# import
import requests
import time
import sys
import wiringpi
import RPi.GPIO as GPIO
import ipget
# エラーが起きたらpip3でライブラリのインストールを

# 宣言
    # line notify
url = 'https://notify-api.line.me/api/notify'
my_token = 'xxxxx'  # 管理者用のトークン
my_headers = {'Authorization': 'Bearer ' + my_token}
cl_token = 'xxxxx'  # クライアント用のトークン
cl_headers = {'Authorization': 'Bearer ' + cl_token}
    # GPIO Pin
SPICLK = 11
SPIMOSI = 10
SPIMISO = 9
SPICS = 8
    # IP Address
IPADD = ipget.ipget()

# GPIO config
GPIO.setmode(GPIO.BCM)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICS, GPIO.OUT)


# ADC関数
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    if adcnum > 7 or adcnum < 0:
        return -1
    GPIO.output(cspin, GPIO.HIGH)
    GPIO.output(clockpin, GPIO.LOW)
    GPIO.output(cspin, GPIO.LOW)

    commandout = adcnum
    commandout |= 0x18  # スタートビット＋シングルエンドビット
    commandout <<= 3    # LSBから8ビット目を送信するようにする
    for i in range(5):
        # LSBから数えて8ビット目から4ビット目までを送信
        if commandout & 0x80:
            GPIO.output(mosipin, GPIO.HIGH)
        else:
            GPIO.output(mosipin, GPIO.LOW)
        commandout <<= 1
        GPIO.output(clockpin, GPIO.HIGH)
        GPIO.output(clockpin, GPIO.LOW)
    adcout = 0
    # 13ビット読む（ヌルビット＋12ビットデータ）
    for i in range(13):
        GPIO.output(clockpin, GPIO.HIGH)
        GPIO.output(clockpin, GPIO.LOW)
        adcout <<= 1
        if i>0 and GPIO.input(misopin)==GPIO.HIGH:
            adcout |= 0x1
    GPIO.output(cspin, GPIO.HIGH)
    return adcout


# LINE notify 起動通知
start_message = {'message': "\nIP：" + IPADD.ipaddr("wlan0") + "\n起動しました。"}
res = requests.post(url, data=start_message, headers=my_headers)  # Post for LINE Notify

# main loop
while True:
    try:
        # ADCから値を取得
        inputVal = readadc(0, SPICLK, SPIMOSI, SPIMISO, SPICS)

        if(inputVal == 4095):
            message = {'message': "インターフォンが押されました。"}
            res = requests.post(url, data=message, headers=my_headers)  # Post for LINE Notify
            print(res)
            time.sleep(5)
        time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit):
        exit()