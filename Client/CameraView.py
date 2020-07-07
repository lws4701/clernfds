import cv2
import time

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS,5)

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        cv2.imwrite('Frames/'+str(time.time())+'.jpg',frame)

        # comment this out if you dont want to see the video
        cv2.imshow('Preview',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()
cv2.destroyAllWindows()