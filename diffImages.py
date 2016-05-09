#!/usr/bin/python
import logging
import getopt
import time
import cv2
import sys
import os


def diffImg(t0, t1, t2):
    d1 = cv2.absdiff(t2, t1)
    d2 = cv2.absdiff(t1, t0)
    return cv2.bitwise_and(d1, d2)


def epoch_now():
    gmtime = time.gmtime()
    return gmtime[3] * 3600 + gmtime[4]*60 + gmtime[5]


def epoch(gmtime):
    return gmtime[3] * 3600 + gmtime[4]*60 + gmtime[5]


def hasBeenXSec(s):
    if (epoch_now() - epoch(global_gmtime) > s):
        return True
    return False


def usage():
    print ""
    print "usage: " + sys.argv[0]
    print ""


def createIfNotExists(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def setup():
    global cam
    global cameraNum
    cam = cv2.VideoCapture(0)
    # cam2 = cv2.VideoCapture(2)

    global winName
    winName = "Movement Indicator"
    cv2.namedWindow(winName, cv2.WINDOW_AUTOSIZE)

    global counter
    counter = 0
    global timer
    timer = 2

    # Read three images first:
    global t_minus
    t_minus = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)
    global t
    t = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)
    global color_frame
    color_frame = cam.read()[1]
    global t_plus
    t_plus = cv2.cvtColor(color_frame, cv2.COLOR_RGB2GRAY)

    global global_gmtime
    global_gmtime = time.gmtime()
    # cam2_frame = cam2.read()[1]

    global frame
    frame = diffImg(t_minus, t, t_plus)

    global threshhold
    threshhold = 0

    global init
    init = True
    global initSum
    initSum = 0
    global initCount
    initCount = 0


def parseArgs():
    global directory
    directory = "./security/"
    global log
    log = "DEBUG"
    global cameraNum
    cameraNum = 0
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd:l:c:", ["help",
                                   "directory=", "log=", "camera="])
    except getopt.GetoptError:
        print "Invalid Parameter"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--directory"):
            directory = arg
        elif opt in ("-l", "--log"):
            if arg in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
                log = arg
            else:
                print "Invalid log parameter. Should be DEBUG, INFO, WARNING,\
                       ERROR, or CRITICAL"
                usage()
                sys.exit(3)
        elif opt in ("-c", "--camera"):
            cameraNum = arg


def startLogger(dir):
    # Start logging in dir/monitor.log
    if log == "DEBUG":
        logging.basicConfig(filename=dir+"monitor.log", level=logging.DEBUG)
    elif log == "INFO":
        logging.basicConfig(filename=dir+"monitor.log", level=logging.INFO)
    elif log == "WARNING":
        logging.basicConfig(filename=dir+"monitor.log", level=logging.WARNING)
    elif log == "ERROR":
        logging.basicConfig(filename=dir+"monitor.log", level=logging.ERROR)
    elif log == "CRITICAL":
        logging.basicConfig(filename=dir+"monitor.log", level=logging.CRITICAL)
    else:
        # Shound never get here.
        print "Bad logging level. Exiting."
        sys.exit(-1)

    logging.info("["+time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "] " +
                 "Starting logging")


def main():
    parseArgs()
    createIfNotExists(directory)
    startLogger(directory)
    setup()

if __name__ == "__main__":
    main()


while True:
    global init
    global threshhold
    global frame
    if(init and hasBeenXSec(5)):
        threshhold = initSum / initCount + 1000
        init = False
        print "System initialized. Beginning capture."
        # print "Threshhold = " + `threshhold`
    frame = diffImg(t_minus, t, t_plus)
    movement = cv2.countNonZero(frame)

    if(not init):
        if(movement > threshhold):
            if(hasBeenXSec(timer)):
                # print("Motion Detected!!! #" + `counter`)
                logging.debug("["+time.strftime("%Y-%m-%d %H:%M:%S",
                              time.gmtime()) + "] " + "Image #" + repr(counter)
                              + " captured.")
                # cv2.imshow("Camera 2",cam2_frame)
                global_gmtime = time.gmtime()
                cv2.imwrite(directory + "frame" + repr(counter) + ".jpg",
                            color_frame)
                counter += 1
    else:
        initSum += movement
        initCount += 1
        t_minus = t
        t = t_plus
        color_frame = cam.read()[1]
        t_plus = cv2.cvtColor(color_frame, cv2.COLOR_RGB2GRAY)
        continue

    cv2.imshow(winName, frame)
    cv2.imshow("Real", color_frame)

    # Read next image
    t_minus = t
    t = t_plus
    color_frame = cam.read()[1]
    t_plus = cv2.cvtColor(color_frame, cv2.COLOR_RGB2GRAY)
    # cam2_frame = cam2.read()[1]

    key = cv2.waitKey(10)
    if key == 27:
        cv2.destroyWindow(winName)
        break

print "Goodbye"
