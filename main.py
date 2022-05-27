from sys import maxsize
import cv2
import uuid
import time
from centerRedCircle import centerRedCircle
import numpy
from typing import List
import json
from websocket import create_connection
import math


vid = cv2.VideoCapture("rtsp://admin:P@ssw0rd@192.168.88.18/1")
cv2.namedWindow('Cerling')

cascade_stone = cv2.CascadeClassifier("./cascade.xml")

STEP_STONE = 25
STEP_STONE_FRAME = 2
POINT = 0
stone_first_color = None

with open("app.conf", "r") as f:
    CONFIG = json.loads(f.read())

RED_ROUND = CONFIG["red_round"]
BLUE_ROUND = CONFIG["blue_round"]
BLUE_CENTER_TOP = int(BLUE_ROUND[0] + (BLUE_ROUND[2] / 2))
CENTER_RED_ROUND = CONFIG["center_circle"]
GAME_FIELD = CONFIG["game_field"]
RADIUS =   CENTER_RED_ROUND[1] - BLUE_ROUND[1]

IS_STARTING_CALIBRATE = False
INDEX_STARTING_CALIBRATE = 100

STONE_LIST = []

NORMILIZE_STACK = []
INDEX_MAX_START_NORMILIZE = 30
INDEX_START_NORMILIZE = INDEX_MAX_START_NORMILIZE


old_count_stone = 0
count_stone_normalaze = 0


ret, frame = vid.read()


def range_color(change: List[int], range: List[List[int]]):
    return numpy.sum(change > range[0]) == 3 and numpy.sum(change < range[1]) == 3

while(True):
    ret, frame = vid.read()

    if not isinstance(frame, numpy.ndarray):
        vid = cv2.VideoCapture("rtsp://admin:P@ssw0rd@192.168.88.18/1")
        continue
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rectangles = cascade_stone.detectMultiScale(gray, scaleFactor=1.01, minSize=(155, 155), maxSize=(180,180))
    
    count_stone = 0

    for (x, y, w, h) in rectangles:
        
        x = math.floor(x / STEP_STONE_FRAME) * STEP_STONE_FRAME
        y = math.floor(y / STEP_STONE_FRAME) * STEP_STONE_FRAME
        w = math.floor(w / STEP_STONE_FRAME) * STEP_STONE_FRAME
        h = math.floor(h / STEP_STONE_FRAME) * STEP_STONE_FRAME
        

        rect_stone = frame[y + STEP_STONE:y+h - STEP_STONE, x + STEP_STONE:x+w - STEP_STONE]

        avg_color_stone = numpy.mean(numpy.mean(rect_stone, axis=1), axis=0)
        
        if numpy.sum(numpy.isnan(avg_color_stone)) == 3:
            continue

        yellow_stone = range_color(avg_color_stone, [ numpy.array([70,160,190]), numpy.array([170,255,255]) ])
        green_stone = range_color(avg_color_stone, [ numpy.array([70,115,0]), numpy.array([170,255,75]) ])
        
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 3)
        
        
        name_color = None
        
        if yellow_stone:
            name_color = "yellow"
        if green_stone:
            name_color = "green"
        
        if not yellow_stone and not green_stone:
            continue
        
        count_stone += 1
        center_stone = ( x + int(w / 2), y + int(h / 2) )
        cv2.circle(frame, ( x + int(w / 2), y + int(h / 2) ), 5, (255, 0, 0), 2)

        right_bottom_rect = (CENTER_RED_ROUND[0], center_stone[1])
        bottom_distance = abs(right_bottom_rect[0] - center_stone[0])
        right_distance = abs(right_bottom_rect[1] - CENTER_RED_ROUND[1])

        distance = int(((bottom_distance ** 2) + (right_distance ** 2))  ** 0.5)
        if distance - ((int(w / 2) + int(h / 2)) / 3 ) > RADIUS:
            
            continue
        
        cv2.putText(frame, str(distance), (center_stone[0], center_stone[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 1, cv2.LINE_AA)

        STONE_LIST.append({
            "color": name_color,
            "distance": distance,
        })
        
        

    NORMILIZE_STACK.append(count_stone)
    INDEX_START_NORMILIZE -= 1
    
    
    
    if INDEX_START_NORMILIZE == 0:
        INDEX_START_NORMILIZE = INDEX_MAX_START_NORMILIZE
        count_stone_normalaze = sum(NORMILIZE_STACK) / INDEX_MAX_START_NORMILIZE
        NORMILIZE_STACK.clear()
        
        STONE_LIST = sorted(STONE_LIST, key=lambda x: x['distance'])
        
        POINT = 0
        
        stone_first_color = None
        for index, stone in enumerate(STONE_LIST):
            if index == 0:
                stone_first_color = stone['color']
                POINT += 1
            elif stone_first_color != stone['color']:
                break
            else:
                POINT += 1
        
        if abs(count_stone_normalaze - old_count_stone) > 0.80:
            old_count_stone = round(count_stone_normalaze)
            
            if IS_STARTING_CALIBRATE:
                pass
            
        
                
    
    if INDEX_STARTING_CALIBRATE >= 0 and IS_STARTING_CALIBRATE == False:
        INDEX_STARTING_CALIBRATE -= 1
    else:
        IS_STARTING_CALIBRATE = True
    
    
    cv2.putText(frame, str(POINT), (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 3, cv2.LINE_AA)
    cv2.putText(frame, str(stone_first_color), (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 3, cv2.LINE_AA)
    cv2.putText(frame, str(RADIUS), (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 3, cv2.LINE_AA)
    
    STONE_LIST.clear()
    
    print("stone", count_stone)
    print("old", old_count_stone)
    print("normalize", count_stone_normalaze)
    
    
    cv2.rectangle(frame, (RED_ROUND[0], RED_ROUND[1]), (RED_ROUND[0] + RED_ROUND[2], RED_ROUND[1] + RED_ROUND[3]), (255, 0, 0), 3)
    cv2.rectangle(frame, (BLUE_ROUND[0], BLUE_ROUND[1]), (BLUE_ROUND[0] + BLUE_ROUND[2], BLUE_ROUND[1] + BLUE_ROUND[3]), (255, 0, 0), 3)
    cv2.circle(frame, ( BLUE_CENTER_TOP, BLUE_ROUND[1] ), 5, (255, 0, 0), 2)

    
    
    frame = cv2.resize(frame, (1280, 800))
    cv2.imshow('Cerling', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()