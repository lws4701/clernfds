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
            file_name = 'Frames/' + str(time.time()) + '.jpg'
            print("test")
            files.append(file_name)
            cv2.imwrite(file_name, frame)

            # comment this out if you dont want to see the video
            cv2.imshow('Preview', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        if len(files) >= 5:
            sendFiles(files, client)

    # Release everything if job is finished
    cap.release()
    cv2.destroyAllWindows()


def sendFiles(files, client):
    # creating zip of frames to send
    img_zip = Archive()
    parent_dir = os.getcwd()
    for i in range(5):
        temp_file_name = files.pop()
        img_zip.add(temp_file_name)
        # deleting files once added to zip
        if os.path.exists(temp_file_name):
            os.remove(temp_file_name)
        else:
            print("%s does not exist" % temp_file_name)
    # sending frames to server
    os.chdir(parent_dir)
    client.connect()
    client.sendFile(img_zip.file_name)
    client.close()


if __name__ == '__main__':
    main()
