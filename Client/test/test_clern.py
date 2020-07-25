import os
import shutil
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
    gui = CLERNFDS(['./fall-vids/fall-11.mp4'])
    # Init the Client being used to submit files
    client = TCPClient()
    # Get the frame deliverance loop started
    t = ThreadPoolExecutor()
    t.submit(frame_processes, gui, client, )
    # Run the mainloop

    gui.loop()
    t.shutdown()

    clear_frames()
    print("Program Closed")


def clear_frames():
    """ Clear all frames in the ./Frames folder"""

    if os.path.exists("./Frames"):
        for filename in os.listdir("./Frames"):
            file_path = os.path.join("./Frames", filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


def frame_processes(gui, frame_client):
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
        cv2.imwrite('mask.jpg', frame)
        frame_client.send_file("mask.jpg")
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
                __deliver(frames, archiveCount, frame_client)
                frames.clear()
                frameCount = 0
                if archiveCount == 10:
                    archiveCount = 0
                print(f"{time.time() - it} seconds to collect and deliver archive.")
                it = time.time()
            time.sleep(.02)  # time between frames in 30 fps for when putting in a mp4
        cap.release()
        clear_frames()


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
