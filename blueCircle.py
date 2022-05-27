import cv2


def findBlueCircle(frame, is_mask=False):
    imgHsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    min_p = (100, 100, 100)
    max_p = (150, 255, 255)
    
    mask = cv2.inRange(imgHsv, min_p, max_p)
    if is_mask:
        return mask
    
    contours = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    circle = None

    if contours:
        contours = contours[0]
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        c = contours[0]
        circle = cv2.boundingRect(c)
        (x, y, w, h) = circle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 3)
    return circle
