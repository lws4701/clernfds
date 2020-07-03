'''
File Name: start_server.py
Authors: CLERN Development Team
Last Modified: 3 Jul 2020
Description: This file acts as the mainloop for the full CLERN server
'''
from Server.file_server import start_server
from Server.tf_detect import DetectorAPI
from multiprocessing import Process
import os

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

    threshold = DETECTTHRESHOLD

    while not(os.path.exists('./archives')):
        pass
    os.chdir('./archives')
    while len(listdir_nohidden('.')) == 0:
        pass
    while True:
        dir_list = sorted(listdir_nohidden('.'))
        frame_packet = sorted(listdir_nohidden(dir_list[0]))
        current_coords = dapi.processPacket(frame_packet)
        print(current_coords)


if __name__ == "__main__":
    main()
