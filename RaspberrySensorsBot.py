#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Telegram bot @RaspberyPi3Bot

"""
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Job
import telegram
import logging
import pickle
import os
from subprocess import call
import datetime

import sys
if not 'win' in sys.platform.lower():
    import RPi.GPIO as GPIO
    import Adafruit_DHT
    HOME_PATH='/home/pi/myscripts/'
    GPIO.setmode(GPIO.BCM)

    #DHT
    #Adafruit: instructions and wiring
    #https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/overview
    DHT_SENSOR_NAME=Adafruit_DHT.AM2302
    DHT_GPIO_PIN='26'

    GPIO_PIN_MQ2 = 23                                          
    GPIO_PIN_YL_69 = 25
    GPIO_PIN_HC_SR501 = 14                                          #Associate pin 26 to pir

    #LED 
    LED_ENABLE = 1
    LED_DISABLE = 0
    RGB_BLUE = 17

else:
    HOME_PATH='.\\'


TOKEN='111111111:QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ'

LOG_NAME=HOME_PATH+'pibot.log'

class Timers:
    def __init__(self):
        self.save_users=datetime.datetime.now()
        self.save_stats_commands=datetime.datetime.now()

class RaspberrySensorsBot:

    def __init__(self):
        self._timers=Timers()

        # Enable logging
        logging.basicConfig(
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        hdlr = logging.FileHandler(LOG_NAME)
        self.logger.addHandler(hdlr)

        if not 'win' in sys.platform.lower():
            GPIO.setup(GPIO_PIN_MQ2, GPIO.IN)                          #Set pin as GPIO in 
            GPIO.setup(GPIO_PIN_YL_69, GPIO.IN)                          #Set pin as GPIO in 
            GPIO.setup(GPIO_PIN_HC_SR501, GPIO.IN)                          #Set pin as GPIO in 

    
    def stats(self, update, cmd):
        pass    
    # Define a few command handlers. These usually take the two arguments bot and
    # update. Error handlers also receive the raised TelegramError object in error.
    def cmd_start(self, bot, update):
        self.stats(update, 'start')
        bot.sendMessage(update.message.chat_id, text='Hi, I am Raspberry Pi!\n\n/help')
    
    def cmd_help(self, bot, update):
        self.stats(update, 'help')
        chat_id=update.message.chat_id
        ans='I\'m Raspberry Pi Model B.\n'\
            'I can tell you about my hardware and soft.\n\n'\
            'You can send me such commands:\n\n'\
            '/hardware - info about my hardware\n'
        if not 'win' in sys.platform.lower():
            ans +='/os - OS installed\n'\
                '/temperature - CPU temperature\n'\
                '/webcam0 - make photo with 1st webcam\n'\
                '/webcam1 - make photo with 2nd webcam\n'\
                '/am2302 - temperature-humidity sensor\n'\
                '/mq_2 - gas sensor module\n'\
                '/hc_sr501 - infrared human body induction module\n'\
                '/yl_69 - soil moisture sensor\n\n'
        bot.sendMessage(update.message.chat_id, text=ans)
    
    def cmd_my_hardware(self, bot, update):
        self.stats(update, 'hardware')
        ans='1.2GHz 64-bit quad-core ARMv8 CPU\n'\
            '802.11n Wireless LAN\n'\
            'Bluetooth 4.1\n'\
            '1GB RAM\n'\
            '4 USB ports\n'\
            '40 GPIO pins\n'\
            'Full HDMI port\n'\
            'Ethernet port\n'\
            'Combined 3.5mm audio jack and composite video\n'\
            'Camera interface (CSI)\n'\
            'Display interface (DSI)\n'\
            'Micro SD card slot\n'\
            'VideoCore IV 3D graphics core\n'\
            '\n'\
            '2 USB webcams\n'\
            'Camera Module v2\n'\
            'AM2302/DHT22 - temperature-humidity sensor\n'
        bot.sendMessage(update.message.chat_id, text=ans)
    
    def cmd_my_OS(self, bot, update):
        self.stats(update, 'os')
        os_info = os.popen('hostnamectl').readlines()
        bot.sendMessage(update.message.chat_id, text='my OS:\n\n'+'\n'.join(map(str.strip, os_info)))
    
    def cmd_my_temperature(self, bot, update):
        self.stats(update, 'temperature')
        cpuTemp = str(round(int(open('/sys/class/thermal/thermal_zone0/temp').read())/1e3, 1))
        bot.sendMessage(update.message.chat_id, text='CPU temperature='+cpuTemp+ ' C')
        print (cpuTemp+'\n')
    
    def cmd_usbcam0(self, bot, update):
        self.stats(update, 'webcam0')
        GPIO.setup(RGB_BLUE, GPIO.OUT)
        GPIO.output(RGB_BLUE,LED_ENABLE)
        call(["fswebcam", "-d/dev/video0", "-r640x480","image0.jpg"])
        GPIO.output(RGB_BLUE,LED_DISABLE)
        #GPIO.cleanup()
        bot.sendPhoto(update.message.chat_id, photo=open('image0.jpg'))
    
    def cmd_usbcam1(self, bot, update):
        self.stats(update, 'webcam1')
        GPIO.setup(RGB_BLUE, GPIO.OUT)
        GPIO.output(RGB_BLUE,LED_ENABLE)
        call(["fswebcam", "-d/dev/video1", "-r640x480","image1.jpg"])
        GPIO.output(RGB_BLUE,LED_DISABLE)
        #GPIO.cleanup()
        bot.sendPhoto(update.message.chat_id, photo=open('image1.jpg'))
    
    def cmd_am2302(self, bot, update):
        self.stats(update, 'am2302')
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR_NAME, DHT_GPIO_PIN)
        bot.sendMessage(update.message.chat_id, text='AM2302 sensor. Temperature=%.1f  C, Humidity=%.1f%%' % (temperature, humidity))
    
    def cmd_sense_gas(self, bot, update):
        self.stats(update, 'sense_gas')
        if GPIO.input(GPIO_PIN_MQ2): #Check whether pir is HIGH
            mess='No gas'
        else:                            
            mess='Gas detected !!!!'                            
        bot.sendMessage(update.message.chat_id, text=mess)
    
    def cmd_sense_human_body(self, bot, update):
        self.stats(update, 'sense_human_body')
        if GPIO.input(GPIO_PIN_HC_SR501):                            #Check whether pir is HIGH
            mess='No body'
        else:                            
            mess='Somebody detected !!!!'                            
        bot.sendMessage(update.message.chat_id, text=mess)

    def cmd_sense_moisture(self, bot, update):
        self.stats(update, 'sense_moisture')
        if GPIO.input(GPIO_PIN_YL_69):                            #Check whether pir is HIGH
            mess='Low liquid'
        else:                            
            mess='liquid detected !!!!'                            
        bot.sendMessage(update.message.chat_id, text=mess)

    def echo(self, bot, update):
        self.stats(update, 'echo')
        in_mess=update.message.text
        if in_mess.find('temp')>=0:
            self.cmd_my_temperature(bot, update)
        elif in_mess.find('hardw')>=0:
            self.cmd_my_hardware(bot, update)
        elif in_mess.find('pict')>=0 or in_mess.find('foto')>=0 or in_mess.find('photo')>=0:
            self.cmd_usbcam0(bot, update)
        elif in_mess.find('inux')>=0:
            self.cmd_my_OS(bot, update)
        elif in_mess.find('help')>=0 or in_mess.find('ello')>=0 or in_mess.find('Hi')==0 or in_mess.find('hi')==0:
            self.cmd_help(bot, update)
        else:
            bot.sendMessage(update.message.chat_id, text='What do you mean: '+update.message.text)
    
    
    def error(self, bot, update, error):
        self.logger.warn('Update "%s" caused error "%s"' % (update, error))
    
    def add_command_handlers(self, dp):
        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("start", self.cmd_start))
        dp.add_handler(CommandHandler("help", self.cmd_help))
        dp.add_handler(CommandHandler("hardware", self.cmd_my_hardware))
        if not 'win' in sys.platform.lower():
            dp.add_handler(CommandHandler("os", self.cmd_my_OS))
            dp.add_handler(CommandHandler("temperature", self.cmd_my_temperature))
            dp.add_handler(CommandHandler("webcam0", self.cmd_usbcam0))
            dp.add_handler(CommandHandler("webcam1", self.cmd_usbcam1))
            dp.add_handler(CommandHandler("am2302", self.cmd_am2302))
            dp.add_handler(CommandHandler("mq_2", self.cmd_sense_gas))
            dp.add_handler(CommandHandler("hc_sr501", self.cmd_sense_human_body))
            dp.add_handler(CommandHandler("yl_69", self.cmd_sense_moisture))
    
    def activate(self):
        # Create the EventHandler and pass it your bot's token.
        updater = Updater(TOKEN)
    
        # Get the dispatcher to register handlers
        dp = updater.dispatcher
        
        self.add_command_handlers(dp)
        # on noncommand i.e message - echo the message on Telegram
        dp.add_handler(MessageHandler([Filters.text], self.echo))
        # log all errors
        dp.add_error_handler(self.error)
    
        # Start the Bot
        updater.start_polling()
    
        # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()


if __name__ == '__main__':
    rbot = RaspberrySensorsBot()
    rbot.activate()
    
