#!/usr/bin/env bash

LOG_DIR=/home/pi/RobotFriend/logs
mkdir -p $LOG_DIR
SERIAL_LOG=$LOG_DIR/serial-MQTT.log
SCREEN_LOG=$LOG_DIR/screen.log
SOUND_LOG=$LOG_DIR/sound.log
MAIN_LOG=$LOG_DIR/main.log
FOLLOW_LOG=$LOG_DIR/follow.log
LIGHTWEB_LOG=$LOG_DIR/light-web.log

source /home/pi/catpy/bin/activate
cd /home/pi/RobotFriend &&

sleep 1 &&

(sleep 0.5 && python serial-MQTT.py >> $SERIAL_LOG 2>&1) &
(sleep 0.6 && python follow.py >> $FOLLOW_LOG 2>&1) &
(sleep 0.7 && python main.py >> $MAIN_LOG 2>&1) &
(sleep 2.5 && python sound.py >> $SOUND_LOG 2>&1) &
(sleep 0.9 && python3 light-web.py >> $LIGHTWEB_LOG 2>&1) &
(sleep 1.0 && python screen.py >> $SCREEN_LOG 2>&1) &

wait