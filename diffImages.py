import cv2, time

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


cam = cv2.VideoCapture(0t)
#cam2 = cv2.VideoCapture(2)

winName = "Movement Indicator"
cv2.namedWindow(winName, cv2.CV_WINDOW_AUTOSIZE)

counter = 0
timer = 2

# Read three images first:
t_minus = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)
t = cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)
color_frame = cam.read()[1]
t_plus = cv2.cvtColor(color_frame, cv2.COLOR_RGB2GRAY)
global_gmtime = time.gmtime()
#cam2_frame = cam2.read()[1]

frame = diffImg(t_minus, t, t_plus)
threshhold = 0


init = True

initSum = 0
initCount = 0


while True:
  if(init and hasBeenXSec(5)):
    threshhold = initSum / initCount + 1000
    init = False
    print "System initialized. Beginning capture."
    print "Threshhold = " + `threshhold`
  frame = diffImg(t_minus, t, t_plus)
  movement = cv2.countNonZero(frame)
  
  if(not init):
    if(movement > threshhold):
      if(hasBeenXSec(timer)):
        print("Motion Detected!!! #" + `counter`)
        #cv2.imshow("Camera 2",cam2_frame)
        global_gmtime = time.gmtime()
        cv2.imwrite("/home/kyle/Pictures/security/frame"+`counter`+".jpg",color_frame)
        counter+=1
  else:
    initSum += movement
    initCount += 1
    t_minus = t
    t = t_plus
    color_frame = cam.read()[1]
    t_plus = cv2.cvtColor(color_frame, cv2.COLOR_RGB2GRAY)
    continue

  
  cv2.imshow( winName, frame )
  cv2.imshow( "Real", color_frame)

  # Read next image
  t_minus = t
  t = t_plus
  color_frame = cam.read()[1]
  t_plus = cv2.cvtColor(color_frame, cv2.COLOR_RGB2GRAY)
  #cam2_frame = cam2.read()[1]

  key = cv2.waitKey(10)
  if key == 27:
    cv2.destroyWindow(winName)
    break

print "Goodbye"

