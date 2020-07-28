"""
tkinter_gui.py
Author: Ryan Schildknecht

SRS cross-reference
Functional Requirement 3.1.2 - The FDS client shall offer a GUI frontend for users.
Functional Requirement

"""

import tkinter as tk
from time import sleep
from concurrent.futures.thread import ThreadPoolExecutor
import threading
import cv2
import json
import phonenumbers
from Client.tcp_client import TCPClient


class CLERNFDS(tk.Frame):
    """
    This is what the client will be interacting with primarily

    GUI will hang until everything is done processing

    Threading a thread alongside this gui with the gui object as a parameter will allow that thread dynamic access
    to variables

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

    def __init__(self):
        """
        Initializes the entire GUI pulling json data from contacts and writing to cameras to display current index.
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
        title.grid(row=0, column=0, pady=10, columnspan=3)
        
        """ Contact Input Box """
        # Create Label
        input_label = tk.Label(self.root, text="Enter a Valid Contact Phone #")
        input_label.grid(row=1, column=0, columnspan=2, padx=15)
        self.contact_entry = tk.Entry(self.root, width=12)
        self.contact_entry.grid(row=2, column=0, padx=15, sticky="w")
        self.contact_entry.insert(tk.INSERT, "3145567823")
        # Contact Add Button
        add_btn = tk.Button(self.root, text="Add",
                            command=lambda: self.addContact())
        add_btn.grid(row=2, column=1, padx=15, sticky="w")

        """ Contact Delete Dropdown """
        # Create Label
        drop_down_label = tk.Label(self.root, text="Select a Contact to Remove")
        drop_down_label.grid(row=3, column=0, columnspan=2, padx=15)
        # Delete Contact Button
        del_btn = tk.Button(self.root, text="Delete",
                            command=lambda: self.__delete_contact())
        del_btn.grid(row=4, column=1, padx=15, sticky="w")
        # Pull Contact List && Also calls the update_dropdown function where the options are allocated
        self.contact_dropdown = 0
        self.__update_contacts()

        """ Camera Index Dropdown """
        # Select Camera Index Label
        drop_down_label = tk.Label(self.root, text="Select Camera Index")
        drop_down_label.grid(row=5, column=0, columnspan=2, padx=15)
        # Draws the index drop down && Allocate Camera Indexes and put it into cameras.txt
        self.index_drop_down = 0
        self.__update_index_drop_down()
        # Add an update button to refresh the drop down
        del_btn = tk.Button(self.root, text="Refresh",
                            command=lambda: self.__update_index_drop_down())
        del_btn.grid(row=6, column=1, sticky="w")

        # set a callback to handle when the window is closed
        self.root.wm_title("CLERN Fall Detection System")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.__on_close)

    def loop(self):
        self.is_running = True
        self.mainloop()

    def __generate_camera_indexes(self):
        """
        Gets all accessible camera indexes to a max of ten and puts them in a dict
        under self.cameras["indexes"]
        :return: None
        """
        # checks the first 10 indexes.
        index = 0
        arr = []
        i = 10
        while i > 0:
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                arr.append(index)
                cap.release()
            index += 1
            i -= 1
        self.cameras["indexes"] = arr

    def __update_index_drop_down(self):
        """
        Updates the dropdown selection of indexes
        :return: None
        """
        self.__generate_camera_indexes()
        print(self.cameras["indexes"])
        first = tk.StringVar(self.root)
        if len(self.cameras["indexes"]) == 0:
            first.set("0")
            self.selected_index = first.get()
            self.index_drop_down = tk.OptionMenu(self.root, first, 0,
                                                 command=lambda val: self.__update_selected_index(val))
        else:
            first.set(self.cameras["indexes"][0])
            self.selected_index = first.get()
            self.index_drop_down = tk.OptionMenu(self.root, first, *self.cameras['indexes'],
                                                 command=lambda val: self.__update_selected_index(val))
        self.index_drop_down.grid(row=6, column=0, padx=15, pady=(0,15), sticky="w")

    def __update_selected_index(self, val):
        """
        Helper function to updateIndexDropDown
        :param val: Camera index
        :return: None
        """
        self.selected_index = val

    def __update_contact_dropdown(self):
        """
        Updates the tkinter contact removal dropdown
        :return: None
        """
        first = tk.StringVar(self.root)
        if len(self.contact_list["contacts"]) == 0:
            first.set("---None---")
            self.selected_contact = first.get()
            self.contact_dropdown = tk.OptionMenu(self.root, first, None,
                                                  command=lambda val: self.__update_selected_contact(val))
        else:
            first.set(self.contact_list["contacts"][0])
            self.selected_contact = first.get()
            self.contactDropdown = tk.OptionMenu(self.root, first, *self.contact_list['contacts'],
                                                 command=lambda val: self.__update_selected_contact(val))
        self.contactDropdown.grid(row=4, column=0, padx=15, sticky="w")

    def __update_selected_contact(self, val):
        """
        Helper function to update_contact_dropdown
        :param val: Contact that has been selected
        :return: None
        """
        self.selected_contact = int(val)

    def __add_contact(self):
        """
        Validates phone number then adds it to the contacts.txt
        then updates the contact dropdown
        :return: None
        """
        contact = self.contact_entry.get()
        contact = phonenumbers.parse(contact, "US")

        print(contact)
        if phonenumbers.is_valid_number(contact):
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
            self.__update_contacts()
        else:
            print("Invalid Number")
            self.contact_entry.delete(0, tk.END)
            self.contact_entry.insert(0, "INVALID #")

    def __delete_contact(self):
        """
        Deletes contact selected on the contact dropdown
        :return: None
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
        self.__update_contacts()

    def __update_contacts(self):
        """
        Pulls the contacts from the contacts.txt and loads them onto memory
        :return: None
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
        threading.Thread(target=self.__update_server, args=(
            "contacts.txt",), daemon=True).start()
        # Update the dropdown
        self.__update_contact_dropdown()

    def __update_server(self, file_name):
        """
        Sends the contacts.txt
        :return: None
        """
        self.client.send_file(file_name)

    def __on_close(self):
        """
        Essentially the Destructor Call
        :return: None
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
    :param gui: The CLERN FDS GUI
    :return:
    """
    # past_contacts = None
    while True:
        sleep(1)  # Checks for changes every 5 seconds
        print("iteration")
        while gui.is_running:
            sleep(1)
            print(gui.selected_contact)
        break


if __name__ == "__main__":
    main = CLERNFDS()
    # an example of how to run the gui
    # TKINTER cannot be ran under process so it has to be either the last thing called or ran as a thread.
    t = ThreadPoolExecutor().submit(run_check, main)
    main.loop()
