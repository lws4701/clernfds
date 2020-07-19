import cv2
import os

os.listdir('./Office2')
cap = cv2.VideoCapture()
cap.set(cv2.CAP_PROP_FPS, 5)

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret == True:
        cv2.imwrite('Frames/office.jpg', frame)

        # comment this out if you dont want to see the video
        # cv2.imshow('Preview', frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
    else:
        break

# Release everything if job is finished
cap.release()
cv2.destroyAllWindows()
