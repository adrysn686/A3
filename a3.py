# a3.py

# Starter code for assignment 2 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# AUDREY SUN
# AUDRES6@UCI.EDU
# 32241248

from tkinter import simpledialog
#from ds_messenger import DirectMessage
#from ds_messenger import DirectMessenger, DirectMessage
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from notebook import Notebook
from ds_messenger import DirectMessenger

class DirectMessage:
    '''This DirectMessage class formats a message object'''
    def __init__(self, recipient=None, message=None, sender=None, timestamp=None):
        self.recipient = recipient
        self.message = message
        self.sender = sender
        self.timestamp = timestamp

class Body(tk.Frame):
    '''This Body class builds the UI of the program'''
    def __init__(self, root, recipient_selected_callback=None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._contacts = [str]
        self._select_callback = recipient_selected_callback
        # After all initialization is complete,
        # call the _draw method to pack the widgets
        # into the Body instance
        self._draw()

    def node_select(self, event):
        '''Node Select is when user selects someone from the tree selection'''
        index = int(self.posts_tree.selection()[0])
        entry = self._contacts[index]
        if self._select_callback is not None:
            self._select_callback(entry)

    def insert_contact(self, contact: str):
        '''insert_contact is when a contact is inserted in the tree selection'''
        self._contacts.append(contact)
        id = len(self._contacts) - 1
        self._insert_contact_tree(id, contact)

    def _insert_contact_tree(self, id, contact: str):
        if len(contact) > 25:
            entry = contact[:24] + "..."
        id = self.posts_tree.insert('', id, id, text=contact)

    def insert_user_message(self, message:str):
        '''insert_user_message is when a user message is inserted'''
        self.entry_editor.insert(1.0, message + '\n', 'entry-right')

    def insert_contact_message(self, message:str):
        '''insert_contact_message is when a user message is inserted'''
        self.entry_editor.insert(1.0, message + '\n', 'entry-left')

    def get_text_entry(self) -> str:
        '''get_text_entry is when you get text from the user'''
        return self.message_editor.get('1.0', 'end').rstrip()

    def set_text_entry(self, text:str):
        '''set_text_entry is when you get set text from the user'''
        self.message_editor.delete(1.0, tk.END)
        self.message_editor.insert(1.0, text)

    def _draw(self):
        posts_frame = tk.Frame(master=self, width=250)
        posts_frame.pack(fill=tk.BOTH, side=tk.LEFT)

        self.posts_tree = ttk.Treeview(posts_frame)
        self.posts_tree.bind("<<TreeviewSelect>>", self.node_select)
        self.posts_tree.pack(fill=tk.BOTH, side=tk.TOP,
                             expand=True, padx=5, pady=5)

        entry_frame = tk.Frame(master=self, bg="")
        entry_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

        editor_frame = tk.Frame(master=entry_frame, bg="red")
        editor_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        scroll_frame = tk.Frame(master=entry_frame, bg="blue", width=10)
        scroll_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=False)

        message_frame = tk.Frame(master=self, bg="yellow")
        message_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=False)

        self.message_editor = tk.Text(message_frame, width=0, height=5)
        self.message_editor.pack(fill=tk.BOTH, side=tk.LEFT,
                                 expand=True, padx=0, pady=0)

        self.entry_editor = tk.Text(editor_frame, width=0, height=5)
        self.entry_editor.tag_configure('entry-right', justify='right')
        self.entry_editor.tag_configure('entry-left', justify='left')
        self.entry_editor.pack(fill=tk.BOTH, side=tk.LEFT,
                               expand=True, padx=0, pady=0)

        entry_editor_scrollbar = tk.Scrollbar(master=scroll_frame,
                                              command=self.entry_editor.yview)
        self.entry_editor['yscrollcommand'] = entry_editor_scrollbar.set
        entry_editor_scrollbar.pack(fill=tk.Y, side=tk.LEFT,
                                    expand=False, padx=0, pady=0)
    def clear_messages(self):
        """Clears all messages from the chat"""
        self.entry_editor.delete(1.0, tk.END)  # Clears the entire content


class Footer(tk.Frame):
    '''Footer class is the footer of the program, where users can click send'''
    def __init__(self, root, send_callback=None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._send_callback = send_callback
        self._draw()

    def send_click(self):
        '''when users click send'''
        if self._send_callback is not None:
            self._send_callback()

    def _draw(self):
        save_button = tk.Button(master=self, text="Send", width=20)
        # You must implement this.
        # Here you must configure the button to bind its click to
        # the send_click() function.
        save_button.config(command=self.send_click)
        save_button.pack(fill=tk.BOTH, side=tk.RIGHT, padx=5, pady=5)

        self.footer_label = tk.Label(master=self, text="Ready.")
        self.footer_label.pack(fill=tk.BOTH, side=tk.LEFT, padx=5)


class NewContactDialog(tk.simpledialog.Dialog):
    '''This is when a new user is configured and shows the UI of the login'''
    def __init__(self, root, title=None, user=None, pwd=None, server=None):
        self.root = root
        self.server = server
        self.user = user
        self.pwd = pwd
        super().__init__(root, title)

    def body(self, frame):
        '''Contains the UI of the login'''
        self.server_label = tk.Label(frame, width=30, text="DS Server Address")
        self.server_label.pack()
        self.server_entry = tk.Entry(frame, width=30)
        self.server_entry.insert(tk.END, self.server)
        self.server_entry.pack()

        self.username_label = tk.Label(frame, width=30, text="Username")
        self.username_label.pack()
        self.username_entry = tk.Entry(frame, width=30)
        self.username_entry.insert(tk.END, self.user)
        self.username_entry.pack()

        self.password_label = tk.Label(frame, width=30, text="Password")
        self.password_label.pack()
        self.password_entry = tk.Entry(frame, width=30, show = '*')
        self.password_entry.insert(tk.END, self.pwd)
        self.password_entry.pack()

        # You need to implement also the region for the user to enter
        # the Password. The code is similar to the Username you see above
        # but you will want to add self.password_entry['show'] = '*'
        # such that when the user types, the only thing that appears are
        # * symbols.
        #self.password...


    def apply(self):
        self.user = self.username_entry.get()
        self.pwd = self.password_entry.get()
        self.server = self.server_entry.get()


class MainApp(tk.Frame):
    '''This contains the main functionality of the program'''
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root
        self.username = ''
        self.password = ''
        self.server = ''
        self.recipient = ''
        self.direct_messenger = None
        self.notebook = None
        self.contact_exist = False
        # You must implement this! You must configure and
        # instantiate your DirectMessenger instance after this line.
        #self.direct_messenger = ... continue!

        # After all initialization is complete,
        # call the _draw method to pack the widgets
        # into the root frame
        self.base_path = Path.home() / "OneDrive" / "Desktop" / f"{self.username}.dsu"
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._draw()

        #self.root.after(100, self.initialize_user)
    
    def send_message(self):
        '''When users send a message'''
        if not self.direct_messenger:
            self.footer.footer_label.config(text = "no connection!")
            return
        message = self.body.get_text_entry()
        try:
            msg = DirectMessage(recipient=self.recipient, sender=self.username, message=message)
        
            if self.direct_messenger.send(msg.message, msg.recipient):
                # Save locally
                self.notebook.add_message(msg)
                self.notebook.save()
                self.body.insert_user_message(f"You: {message}")
                self.body.set_text_entry("")


        except Exception as e:
            self.footer.footer_label.config(text=f"Error: {e}")

    def add_contact(self):
        ''''When users add a contact'''
        # You must implement this!
        # Hint: check how to use tk.simpledialog.askstring to retrieve
        # the name of the new contact, and then use one of the body
        # methods to add the contact to your contact list
        contact = simpledialog.askstring("Add contact", "Enter username:")
        if contact:
            self.body.insert_contact(contact)
            
            # Add to notebook and save
            if self.notebook:
                self.notebook.add_contact(contact)
                try:
                    self.notebook.save()
                    self.footer.footer_label.config(text=f"Added {contact}")
                except Exception as e:
                    self.footer.footer_label.config(text=f"Error saving: {e}")

    def recipient_selected(self, recipient):
        '''When the user clicks on a recipient'''
        self.recipient = recipient
        #this is to check if you're logged in

        #this clear all the current messages first
        self.body.clear_messages()

        # This loads local messages first
        local_msgs = self.notebook.get_messages(recipient)
        for msg in local_msgs:
            if (msg.sender == self.username and msg.recipient == self.recipient) or (msg.sender == self.recipient and msg.recipient == None):
                if msg.sender == self.username:
                    self.body.insert_user_message(f"You: {msg.message}")
                else:
                    self.body.insert_contact_message(f"{msg.sender}: {msg.message}")
            else:
                continue

        if self.direct_messenger:
            #retrieve all messages from the current user 
            #if the notebook exists, then load --> return a message list 
            #else: (try retrieve_all)
            try:
                message_list = self.direct_messenger.retrieve_all()
                for msg in message_list:
                    #if msg.recipient == self.recipient or msg.recipient == self.username:
                    #if (msg.recipient == self.recipient) or (msg.sender == self.recipient):
                    if (msg.sender == self.username and msg.recipient == self.recipient) or (msg.sender == self.recipient and msg.recipient == None):
                        if msg.sender == self.recipient:
                            self.body.insert_contact_message(f"{msg.sender}: {msg.message}")
                        else:
                            self.body.insert_user_message(f"You: {msg.message}")
                    #if msg.sender == self.username:
                        #self.body.insert_user_message(f"YOU: {msg.message}")
                    #this meand you're receiving a message 
                    self.notebook.save()
            except Exception as e:
                self.footer.footer_label.config(text=f"Error retrieving messages: {e}")

    def configure_server(self):
        '''this is when the server is configured and notebook is loaded'''
        ud = NewContactDialog(self.root, "Configure Account",
                              self.username, self.password, self.server)
        self.username = ud.user
        self.password = ud.pwd
        self.server = ud.server.strip()    
        #start the notebook (for local)
        notebook_dir = Path.home() / "dsu_files"
        notebook_dir.mkdir(exist_ok=True)
        nb_path = notebook_dir / f"{self.username}.dsu"

        try:
            self.direct_messenger = DirectMessenger(self.server, self.username, self.password)
            #self.direct_messenger.start_client("127.0.0.1", "3001")
            #print(ud.server)
            self.direct_messenger.connect()
            self.direct_messenger._authenticate()
            self.footer.footer_label.config(text="You've been connected!")
        except Exception as e:
            self.footer.footer_label.config(text="There's a connection error")

        #if notebook exists, load the contacts into GUI
        if nb_path.exists():
            self.notebook = Notebook(self.username, self.password, self.server)
            self.notebook.load(nb_path)
            for contact in self.notebook.get_contacts():
                if type(contact) == str:
                    self.body.insert_contact(contact)
            self.footer.footer_label.config(text="Loaded contacts!")

            #self.direct_messenger.start_client("127.0.0.1", "3001")
            #print(ud.server)
        else:
            self.notebook = Notebook(self.username, self.password, self.server)
            self.notebook.save(nb_path)

    def publish(self, message:str, sender:str):
        '''When the message gets published'''
        if not sender or not message:
            return
        if sender != self.username:
            self.body.insert_contact_message(f"{sender}: {message}")
        else:
            self.body.insert_user_message(f"YOU: {message}")

    def check_new(self):
        '''Checks for new/unread messages'''
        if self.direct_messenger:
            try:
                msg_list = self.direct_messenger.retrieve_new()
                for msg in msg_list:
                    if msg.sender and msg.message:
                        self.publish(msg.message, msg.sender)
                        #add message to me locally 
                        self.notebook.add_message(msg)
                        self.notebook.save()
                        if (msg.sender not in self.body._contacts) and (msg.sender not in self.notebook.contacts) and (msg.sender != self.username):
                            self.body.insert_contact(msg.sender)
                            self.notebook.add_contact(msg.sender)
            except Exception as e:
                print(f"error {e}")      
        self.after(3000, self.check_new)

    def _draw(self):
        # Build a menu and add it to the root frame.
        menu_bar = tk.Menu(self.root)
        self.root['menu'] = menu_bar
        menu_file = tk.Menu(menu_bar)

        menu_bar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='New')
        menu_file.add_command(label='Open...')
        menu_file.add_command(label='Close')

        settings_file = tk.Menu(menu_bar)
        menu_bar.add_cascade(menu=settings_file, label='Settings')
        settings_file.add_command(label='Add Contact',
                                command=self.add_contact)
        settings_file.add_command(label='Configure DS Server',
                                command=self.configure_server)

        # The Body and Footer classes must be initialized and
        # packed into the root window.
        self.body = Body(self.root,
                        recipient_selected_callback=self.recipient_selected)
        self.body.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        self.footer = Footer(self.root, send_callback=self.send_message)
        self.footer.pack(fill=tk.BOTH, side=tk.BOTTOM)


if __name__ == "__main__":
    # All Tkinter programs start with a root window. We will name ours 'main'.
    main = tk.Tk()

    # 'title' assigns a text value to the Title Bar area of a window.
    main.title("ICS 32 Distributed Social Messenger")

    # This is just an arbitrary starting point. You can change the value
    # around to see how the starting size of the window changes.
    main.geometry("720x480")

    # adding this option removes some legacy behavior with menus that
    # some modern OSes don't support. If you're curious, feel free to comment
    # out and see how the menu changes.
    main.option_add('*tearOff', False)

    # Initialize the MainApp class, which is the starting point for the
    # widgets used in the program. All of the classes that we use,
    # subclass Tk.Frame, since our root frame is main, we initialize
    # the class with it.
    app = MainApp(main)

    # When update is called, we finalize the states of all widgets that
    # have been configured within the root frame. Here, update ensures that
    # we get an accurate width and height reading based on the types of widgets
    # we have used. minsize prevents the root window from resizing too small.
    # Feel free to comment it out and see how the resizing
    # behavior of the window changes.
    main.update()
    main.minsize(main.winfo_width(), main.winfo_height())
    id = main.after(2000, app.check_new)
    print(id)
    # And finally, start up the event loop for the program (you can find
    # more on this in lectures of week 9 and 10).
    main.mainloop()
