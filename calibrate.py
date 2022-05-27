from sys import maxsize
import cv2
import uuid
import time
from centerRedCircle import centerRedCircle
from blueCircle import findBlueCircle
import numpy
from typing import List
import json


vid = cv2.VideoCapture("rtsp://admin:P@ssw0rd@192.168.88.18/1")
cv2.namedWindow('mouseRGB')


conf = {
    "screen": None,
    "red_round": None,
    "game_field": None,
    "center_circle": None,
}


ret, frame = vid.read()

conf['screen'] = frame.shape[0:2]
conf['red_round'] = centerRedCircle(frame)
conf['blue_round'] = findBlueCircle(frame)
(circle_x, circle_y, circle_w, circle_h) = conf['red_round']
conf['center_circle'] = (circle_x + int(circle_w / 2), circle_y + int(circle_h / 2))


min_p = (200, 200, 200)
max_p = (255, 255, 255)

mask = cv2.inRange(frame, min_p, max_p)

contours = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

if contours:
    contours = contours[0]
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    c = contours[0]
    conf['game_field'] = cv2.boundingRect(c)
    (x, y, w, h) = conf['game_field']

with open("app.conf", 'w') as f:
    print(json.dumps(conf))
    f.write(json.dumps(conf))
