# a3.py

# Starter code for assignment 2 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# AUDREY SUN
# AUDRES6@UCI.EDU
# 32241248

from ds_messenger import DirectMessenger, DirectMessage

def main():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    direct_messenger = DirectMessenger(username= username, password= password)
    direct_messenger.start_client("127.0.0.1", "3001")
    while True:
        msg = input("enter message (enter Q to quit): ")
        if msg == 'Q':
            break
        recipient = input("enter recipient: ")
        direct_messenger.send(msg, recipient)
        #each object in msg list is an object of DirectMessage
        msg_list = direct_messenger.retrieve_all()
        for msg in msg_list:
            #receiving a message
            if msg.sender != None:
                print(f"Message from {msg.sender}: {msg.message}")
            #sending a message 
            else:
                print(f"Sent to {msg.recipient}: {msg.message}")

        #direct_messenger.retrieve_new()

if __name__=="__main__":
    main()


