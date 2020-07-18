"""
tkinter_gui_test.py
Author: Ryan Schildknecht
"""
import tkinter as tk
from time import sleep
from PIL import ImageTk, Image
from concurrent.futures.thread import ThreadPoolExecutor
import threading
import cv2
import json
import phone_numbers
from Client.tcp_client import TCPClient


class CLERNFDS(tk.Frame):
    """
    This is what the client will be interacting with primarily

    Needs to be the last thing running since the threading on tkinter is horrible and my solution is hacky

    GUI will hang until everything is done processing

    Threading a thread alongside this gui with the gui object as a parameter will allow that thread dynamic access
    to variables

    Multiprocessing alongside tkinter is not possible, only multithreading is.

    Video pauses when a drop down is selected
    (my guess is that it pauses the mainloop as well, so it is unavoidable without a custom mainloop)
    """
    # GUI has separate client object for concurrent delivery.
    client = None
    # For concurrent processes to end when the GUI closes
    is_running = False
    # Memory Location for contact list
    contact_list = dict()

    # Video feed
    video = None
    stop_event = None
    frame = None
    video_running = False
    # actual viewpoint of video preview.
    panel = None

    # selected contact
    selected_contact = None

    # selected index
    selected_index = None
    # available cameras
    cameras = dict()

    def __init__(self, video_array):
        """
        Initializes the entire GUI pulling json data from contacts and writing to cameras to display current index.
        :param videoStream: :param outputPath:
        """
        # I put this inside of the class because there is no real use of inheritance in this application of tkinter
        parent = tk.Tk()
        parent.resizable(0, 0)
        super(CLERNFDS, self).__init__(parent)
        # Instantiate Client Object
        self.client = TCPClient()

        # initialize the root window
        self.root = parent

        # Create Title
        title = tk.Label(self.root, text="CLERN FDS", font=("Helvetica", 20))
        title.grid(row=0, column=0, columnspan=3)
        # Contact Input Box
        # Create Label
        input_label = tk.Label(self.root, text="Enter a Valid Contact Phone #")
        input_label.grid(row=1, column=0, columnspan=2, padx=10)
        self.contact_entry = tk.Entry(self.root, width=12)
        self.contact_entry.grid(row=2, column=0, padx=5, sticky="w")
        self.contact_entry.insert(tk.INSERT, "3145567823")
        # Contact Add Button
        add_btn = tk.Button(self.root, text="Add",
                           command=lambda: self.add_contact())
        add_btn.grid(row=2, column=1, sticky="w")

        # Contact Delete Dropdown
        # Create Label
        drop_down_label = tk.Label(self.root, text="Select a Contact to Remove")
        drop_down_label.grid(row=3, column=0, columnspan=2, padx=10)
        # Delete Contact Button
        del_btn = tk.Button(self.root, text="Delete",
                           command=lambda: self.delete_contact())
        del_btn.grid(row=4, column=1, sticky="w")
        # Pull Contact List && Also calls the updateDropDown function where the options are allocated
        self.update_contacts()

        # Camera Index Dropdown
        self.test_videos = video_array
        # Select Camera Index Label
        drop_down_label = tk.Label(self.root, text="Select Camera Index")
        drop_down_label.grid(row=5, column=0, columnspan=2, padx=10)
        # Draws the index drop down && Allocate Camera Indexes and put it into cameras.txt
        self.update_index_drop_down()
        # Add an update button to refresh the drop down
        del_btn = tk.Button(self.root, text="Refresh",
                           command=lambda: self.update_index_drop_down())
        del_btn.grid(row=6, column=1, sticky="w")

        # instantiate a thread that updates the video feed
        self.update_preview()

        # set a callback to handle when the window is closed
        self.root.wm_title("CLERN Fall Detection System")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.on_close)

    def loop(self):
        self.is_running = True
        self.mainloop()

    def update_preview(self):
        if self.video_running:
            self.stop_event.set()
            self.video.join(timeout=1.5)
        video = cv2.VideoCapture(self.selected_index)
        self.stop_event = threading.Event()
        self.video = threading.Thread(
            target=self.video_loop, args=(video,), daemon=True)
        self.video.start()

    def generate_camera_indexes(self):
        """
        Gets all accessible camera indexes to a max of ten and puts them in a dict
        under self.cameras["indexes"]
        :return:
        """
        self.cameras["indexes"] = self.test_videos

    def update_index_drop_down(self):
        """
        Updates the dropdown selection of indexes
        :return:
        """
        self.generate_camera_indexes()
        print(self.cameras["indexes"])
        first = tk.StringVar(self.root)
        if len(self.cameras["indexes"]) == 0:
            first.set("0")
            self.selected_index = first.get()
            self.index_drop_down = tk.OptionMenu(self.root, first, 0,
                                               command=lambda val: self.update_selected_index(val))
        else:
            first.set(self.cameras["indexes"][0])
            self.selected_index = first.get()
            self.index_drop_down = tk.OptionMenu(self.root, first, *self.cameras['indexes'],
                                               command=lambda val: self.update_selected_index(val))
        self.index_drop_down.grid(row=6, column=0, padx=5, sticky="w")

    def update_selected_index(self, val):
        """
        Helper function to update_index_drop_down
        :param val:
        :return:
        """
        self.selected_index = val
        self.update_preview()  # changes video preview to current index.

    def update_contact_drop_down(self):
        """
        Updates the tkinter contact removal dropdown
        :return:
        """
        first = tk.StringVar(self.root)
        if len(self.contact_list["contacts"]) == 0:
            first.set("---None---")
            self.selected_contact = first.get()
            self.contact_drop_down = tk.OptionMenu(self.root, first, None,
                                                 command=lambda val: self.update_selected_contact(val))
        else:
            first.set(self.contact_list["contacts"][0])
            self.selected_contact = first.get()
            self.contact_drop_down = tk.OptionMenu(self.root, first, *self.contact_list['contacts'],
                                                 command=lambda val: self.update_selected_contact(val))
        self.contact_drop_down.grid(row=4, column=0, padx=5, sticky="w")

    def update_selected_contact(self, val):
        """
        Helper function to update_contact_drop_down
        :param val:
        :return:
        """
        self.selected_contact = int(val)

    def add_contact(self):
        """
        Validates phone number then adds it to the contacts.txt
        then updates the contact dropdown
        :return:
        """
        contact = self.contact_entry.get()
        contact = phone_numbers.parse(contact, "US")

        print(contact)
        if phone_numbers.is_valid_number(contact):
            self.contact_list['contacts'].append(contact.national_number)
            while True:
                try:
                    with open("contacts.txt", 'w') as json_file:
                        print("Contact Added")
                        json.dump(self.contact_list, json_file)
                        json_file.close()
                    break
                except Exception as e:
                    print("***Error: File Currently Open*** errmsg=%s" % e)
            self.update_contacts()
        else:
            print("Invalid Number")
            self.contact_entry.delete(0, tk.END)
            self.contact_entry.insert(0, "INVALID #")

    def delete_contact(self):
        """
        Deletes contact selected on the contact dropdown
        :return:
        """
        print(self.selected_contact)
        print(self.contact_list['contacts'])
        if self.selected_contact == "---None---":
            print("Contact List is empty")
            return
        self.contact_list['contacts'].remove(int(self.selected_contact))
        while True:
            try:
                with open("contacts.txt", 'w') as json_file:
                    print("%s Deleted" % self.selected_contact)
                    json.dump(self.contact_list, json_file)
                    json_file.close()
                break
            except Exception as e:
                print("***Error: File Currently Open*** errmsg=%s" % e)
        self.update_contacts()

    def update_contacts(self):
        """
        Pulls the contacts from the contacts.txt and loads them onto memory
        :return:
        """
        while True:
            try:
                with open('contacts.txt') as json_file:
                    self.contact_list = json.load(json_file)
                    print("Contacts Updated")
                    json_file.close()
                break
            except Exception as e:
                print("***Error*** errmsg=%s" % e)
        # Update the servers end.
        threading.Thread(target=self.update_server, args=(
            "contacts.txt",), daemon=True).start()
        # Update the dropdown
        self.update_contact_drop_down()

    def update_server(self, file_name):
        """
        Sends the contacts.txt
        :return:
        """
        self.client.send_file(file_name)

    def video_loop(self, vs):
        """
        Pulls video from the video stream from given index selected
        :return:
        """
        self.video_running = True
        try:
            while not self.stop_event.is_set():
                # grab the frame from the video
                ret, self.frame = vs.read()
                if self.frame is None:
                    print("No Video Feed.")
                    break
                image = cv2.resize(self.frame, (852, 480))
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                # if the panel is not None, we need to initialize it
                if self.panel is None:
                    self.panel = tk.Label(image=image)
                    self.panel.image = image
                    self.panel.grid(row=1, rowspan=100,
                                    column=2, padx=20, pady=5)
                # otherwise, simply update the panel
                else:
                    self.panel.configure(image=image)
                    self.panel.image = image
                cv2.waitKey(20)
            vs.release()
            self.video_running = False
        except Exception as e:
            print(
                '***CLERN FDS GUI*** - "[%s] Error while running video_loop"' % e)
        self.video_running = False

    def on_close(self):
        """
        Essentially the Destructor Call
        :return:
        """
        print("CLERN FDS closing...")
        # stop concurrent processes
        self.is_running = False
        # set the stop event
        self.stop_event.set()
        # GUI Hangs until the program it is running inside comes to an end
        self.root.quit()


def run_check(gui):
    """
    Concurrent runtime loop that runs alongside the CLERN GUI
    :param gui:
    :param client:
    :return:
    """
    pastContacts = None
    while True:
        sleep(1)  # Checks for changes every 5 seconds
        print("iteration")
        while gui.is_running == True:
            sleep(1)
            print(gui.selected_contact)
        break


if __name__ == "__main__":
    main = CLERNFDS(["test1.mp4", "test2.mp4"])
    # an example of how to run the gui
    # TKINTER cannot be ran under process so it has to be either the last thing called or ran as a thread.
    # t = ThreadPoolExecutor().submit(runCheck, main)
    main.loop()

    # main.mainloop()
    # client.sendFile("contacts.txt")
    #
    # t = ThreadPoolExecutor().submit(client.sendFile, "contacts.txt")

    # print(p, p.is_alive())
