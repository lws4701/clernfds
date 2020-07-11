'''
****************POSSIBLE DELETE*******************
File Name: start_server.py
Authors: CLERN Development Team
Last Modified: 11 Jul 2020
Description: This file acts as the mainloop for the full CLERN server
'''
from Server.file_server import start_server
from Server.tf_detect import DetectorAPI
from multiprocessing import Process
import os
import time
DATAMODEL = "test/faster_rcnn_inception_v2_coco/frozen_inference_graph.pb"
DETECTTHRESHOLD = 0.7


def listdir_nohidden(path):
    '''For listing only visible files'''
    fileList = []
    for f in os.listdir(path):
        if not f.startswith(('.')) and not(f.endswith('.zip')):
            fileList.append(f)
    return fileList


def main():
    file_server = Process(target=start_server)
    # Start the file server
    print("Readying model...")
    dapi = DetectorAPI(path_to_ckpt=DATAMODEL)
    print("Model ready...")
    file_server.start()

    while not(os.path.exists('./archives')):
        pass
    os.chdir('./archives')
    parent_dir = os.getcwd()
    while True:
        while True and len(listdir_nohidden('.')) != 0:
            dir_list = sorted(listdir_nohidden('.'))
            os.chdir(dir_list[0])
            frame_packet = sorted(listdir_nohidden('.'))
            current_coords = dapi.processPacket(frame_packet, DETECTTHRESHOLD)
            print(current_coords)
            [os.remove(x) for x in frame_packet]
            os.chdir(parent_dir)
            os.rmdir(dir_list[0])
        pass


if __name__ == "__main__":
    main()
