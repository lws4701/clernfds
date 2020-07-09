from Client.archive import Archive
from Client.tcp_client import TCPClient
import cv2
import time
import os


def main():
    files = []
    client = TCPClient()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 5)

    if not (os.path.exists('./Frames')):
        os.mkdir('Frames')

    while cap.isOpened():
        ret, frame = cap.read()
        if ret == True:
            filename = 'Frames/' + str(time.time()) + '.jpg'
            print("test")
            files.append(filename)
            cv2.imwrite(filename, frame)

            # comment this out if you dont want to see the video
            cv2.imshow('Preview', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        if len(files) >= 5:
            sendFiles(files, client)


    # Release everything if job is finished
    cap.release()
    cv2.destroyAllWindows()


def sendFiles(files,client):
    #creating zip of frames to send
    imgZip = Archive()
    parentDir = os.getcwd()
    for i in range(5):
        tempFilename = files.pop()
        imgZip.add(tempFilename)
        #deleting files once added to zip
        if os.path.exists(tempFilename):
            os.remove(tempFilename)
        else:
            print("%s does not exist" % tempFilename)
    #sending frames to server
    os.chdir(parentDir)
    client.connect()
    client.sendFile(imgZip.fileName)
    client.close()

if __name__ == '__main__':
    main()