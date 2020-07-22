import os
import time
import cv2
from Client.archive import Archive
from Client.tcp_client import TCPClient
from Client.test.test_gui import CLERNFDS
from concurrent.futures import ThreadPoolExecutor


def main():
    # Ensure proper directories exist
    if not (os.path.exists('Frames')):
        os.mkdir('Frames')
    # Start The ClientGUI
    gui = CLERNFDS(["fall.mp4"])
    # Init the Client being used to submit files
    client = TCPClient()
    # Get the frame deliverance loop started
    transThread = ThreadPoolExecutor().submit(frame_processes, gui, client, )
    # Run the mainloop

    gui.loop()
    transThread.result()
    print("Program Closed")


def frame_processes(gui, frameClient):
    while not gui.is_running:
        pass
    # Frame Deliverance
    while gui.is_running:
        print("New Index")
        index = gui.selected_index

        cap = cv2.VideoCapture(index)

        frameCount = 0
        archiveCount = 0
        frames = []

        # open the cap (throwaway values)
        ret, frame = cap.read()
        cv2.imwrite("mask.jpg", frame)
        frameClient.send_file("mask.jpg")
        it = time.time()
        while index == gui.selected_index and cap.isOpened() and gui.is_running:
            ret, frame = cap.read()
            frameCount += 1
            if frameCount % 3 == 0:
                file_name = 'Frames/' + str(time.time()) + '.jpg'
                cv2.imwrite(file_name, frame)
                frames.append(file_name)
                print(f'{file_name} saved')
            if frameCount == 30:
                archiveCount += 1
                __deliver(frames, archiveCount, frameClient)
                frames.clear()
                frameCount = 0
                if archiveCount == 10:
                    archiveCount = 0
                print(f"{time.time() - it} seconds to collect and deliver archive.")
                it = time.time()
            time.sleep(.02)  # time between frames in 30 fps for when putting in a mp4
        cap.release()


def __deliver(frames, count, client):
    """
    Creates an Archive of Collected Frames.
    Sends that Archive
    :param frames:
    :param client:
    :return:
    """
    img_zip = Archive(str(count) + ".zip")
    file_name = img_zip.file_name
    for frame in frames:
        img_zip.add(frame)
        print(f"{frame} added")
        # deleting files once added to zip
        if os.path.exists(frame):
            os.remove(frame)
        else:
            print(f"{frame} does not exist")
    # sending frames to server
    img_zip.close()
    client.send_file(img_zip.file_name)
    os.remove(file_name)


if __name__ == "__main__":
    main()
