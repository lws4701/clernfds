import sys
import tkinter as tk
from time import sleep
from PIL import ImageTk, Image
import threading
import multiprocessing
import cv2
import json
import phonenumbers
import os


class CLERNFDS(tk.Frame):
    def __init__(self, videoStream, outputPath):
        # I put this inside of the class because there is no real use of inheritance in this application of tkinter
        parent = tk.Tk()
        parent.resizable(0, 0)

        super(CLERNFDS, self).__init__(parent)
        # List of Contacts
        self.contactList = dict()
        # store the video stream object and output path, then initialize
        # the most recently read frame, thread for reading frames, and
        # the thread stop event
        self.vs = videoStream
        self.outputPath = outputPath
        self.frame = None
        self.thread = None
        self.stopEvent = None

        # initialize the root window and image panel
        self.root = parent
        self.panel = None

        # Create Title
        title = tk.Label(self.root, text="CLERN FDS", font=("Helvetica", 20))
        title.grid(row=0, column=0, columnspan=3)
        # Contact Input Box
        # Create Label
        inputLabel = tk.Label(self.root, text="Enter a Valid Contact Phone #")
        inputLabel.grid(row=1, column=0, columnspan=2, padx=10)
        self.contactEntry = tk.Entry(self.root, width=12)
        self.contactEntry.grid(row=2, column=0, padx=5, sticky="w")
        self.contactEntry.insert(tk.INSERT, "3145567823")
        # Contact Add Button
        addBtn = tk.Button(self.root, text="Add", command=lambda: self.addContact())
        addBtn.grid(row=2, column=1, sticky="w")

        # Contact Delete Dropdown
        self.selectedContact = None
        # Create Label
        dropDownLabel = tk.Label(self.root, text="Select a Contact to Remove")
        dropDownLabel.grid(row=3, column=0, columnspan=2, padx=10)
        # Delete Contact Button
        delBtn = tk.Button(self.root, text="Delete", command=lambda: self.deleteContact())
        delBtn.grid(row=4, column=1, sticky="w")
        # Pull Contact List && Also calls the updateDropDown function where the options are allocated
        self.updateContacts()

        # Camera Index Dropdown
        self.selectedIndex = None
        # Allocate Camera Indexes and put it into cameras.txt
        self.cameras = dict()
        # self.generateCameraIndexes() //Called inside of update dropdown
        # Select Camera Index Label
        dropDownLabel = tk.Label(self.root, text="Select Camera Index")
        dropDownLabel.grid(row=5, column=0, columnspan=2, padx=10)
        # Draws the index drop down
        self.updateIndexDropDown()
        # Add an update button to refresh the drop down
        delBtn = tk.Button(self.root, text="Refresh", command=lambda: self.updateIndexDropDown())
        delBtn.grid(row=6, column=1, sticky="w")

        # MULTITHREADING
        # start a thread that constantly pools the video for
        # the most recently read frame
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()

        # set a callback to handle when the window is closed
        self.root.wm_title("CLERN Fall Detection System")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

    def generateCameraIndexes(self):
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
        self.cameras["index"] = arr
        while True:
            try:
                with open("cameras.txt", 'w') as json_file:
                    json.dump(self.cameras, json_file)
                    print("Indexes Updated")
                    json_file.close()
                break
            except Exception as e:
                print("***Error: File Currently Open*** errmsg=" % e)

    def updateIndexDropDown(self):
        self.generateCameraIndexes()
        print(self.cameras["index"])
        first = tk.StringVar(self.root)
        if len(self.cameras["index"]) == 0:
            first.set("NULL")
            self.selectedIndex = first.get()
            self.indexDropdown = tk.OptionMenu(self.root, first, None,
                                               command=lambda val: self.updateSelectedIndex(val))
        else:
            first.set(self.cameras["index"][0])
            self.selectedIndex = first.get()
            self.indexDropdown = tk.OptionMenu(self.root, first, *self.cameras['index'],
                                               command=lambda val: self.updateSelectedIndex(val))
        self.indexDropdown.grid(row=6, column=0, padx=5, sticky="w")

    def updateSelectedIndex(self, val):
        self.selectedIndex = val

    def updateContactDropDown(self):
        first = tk.StringVar(self.root)
        if len(self.contactList["contacts"]) == 0:
            first.set("---None---")
            self.selectedContact = first.get()
            self.contactDropdown = tk.OptionMenu(self.root, first, None,
                                                 command=lambda val: self.updateSelectedContact(val))
        else:
            first.set(self.contactList["contacts"][0])
            self.selectedContact = first.get()
            self.contactDropdown = tk.OptionMenu(self.root, first, *self.contactList['contacts'],
                                                 command=lambda val: self.updateSelectedContact(val))
        self.contactDropdown.grid(row=4, column=0, padx=5, sticky="w")

    def updateSelectedContact(self, val):
        self.selectedContact = int(val)

    def addContact(self):
        contact = self.contactEntry.get()
        contact = phonenumbers.parse(contact, "US")

        print(contact)
        if phonenumbers.is_valid_number(contact):
            self.contactList['contacts'].append(contact.national_number)
            while True:
                try:
                    with open("contacts.txt", 'w') as json_file:
                        print("Contact Added")
                        json.dump(self.contactList, json_file)
                        json_file.close()
                    break
                except Exception as e:
                    print("***Error: File Currently Open*** errmsg=" % e)
            self.updateContacts()
        else:
            print("Invalid Number")
            self.contactEntry.delete(0, tk.END)
            self.contactEntry.insert(0, "INVALID #")

    def deleteContact(self):
        print(self.selectedContact)
        print(self.contactList['contacts'])
        if self.selectedContact == "---None---":
            print("Contact List is empty")
            return
        self.contactList['contacts'].remove(int(self.selectedContact))
        while True:
            try:
                with open("contacts.txt", 'w') as json_file:
                    print("%s Deleted" % self.selectedContact)
                    json.dump(self.contactList, json_file)
                    json_file.close()
                break
            except Exception as e:
                print("***Error: File Currently Open*** errmsg=" % e)

        self.updateContacts()

    def updateContacts(self):
        while True:
            try:
                with open('contacts.txt') as json_file:
                    self.contactList = json.load(json_file)
                    print("Contacts Updated")
                    json_file.close()
                break
            except Exception as e:
                print("***Error: File Currently Open*** errmsg=" % e)
        self.updateContactDropDown()

    def videoLoop(self):
        try:
            while not self.stopEvent.is_set():
                # grab the frame from the video
                ret, self.frame = self.vs.read()
                if self.frame is None:
                    print("No Video Feed.")
                    break
                image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                # if the panel is not None, we need to initialize it
                if self.panel is None:
                    self.panel = tk.Label(image=image)
                    self.panel.image = image
                    self.panel.grid(row=1, rowspan=100, column=2, padx=20, pady=5)

                # otherwise, simply update the panel
                else:
                    self.panel.configure(image=image)
                    self.panel.image = image
                cv2.waitKey(30)
            self.vs.release()

        except Exception as e:
            print('***CLERN FDS GUI*** - "[%s] Error while running videoLoop"' % e)

    def onClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("CLERN FDS closing...")
        self.stopEvent.set()
        # GUI Hangs until the program it is running in comes to an end
        self.root.quit()


def processTest():
    for i in range(11):
        sleep(1)
        print(i)


if __name__ == "__main__":
    vs = cv2.VideoCapture("test.mp4")
    main = CLERNFDS(vs, "./")
    p = multiprocessing.Process(target=processTest)
    p.start()
    main.mainloop()
    p.terminate()
    sleep(0.1)
    print(p, p.is_alive())