import socket
import threading
import json , pickle

#users_dict = {} ##   { 'navaneet' : 'navneetkapaswd'  , 'kush' : 'kushkapaswd'  }
#group_dict = {} ##   {  '1' : ['navaneeet' , ' kush'] , '2' : ['kush ']        }

Address = socket.gethostbyname(socket.gethostname())

usrname = None
users_dict_file = open("users_dict.pkl","rb")
users_dict = pickle.load(users_dict_file)
users_dict_file.close()

def search_user(usrname) :
    for user in users_dict :
        if usrname == user :
            return True
    return False

count = 0
while True :
    if count > 3 :
        print("Authentication failed more than 3 times")
        sys.exit()
    print("Are you a new user ? \n Type Y or N " )
    yes_or_no = input() 
    if yes_or_no == "y" or yes_or_no ==  "Y" :
        usrname = input("Select Username : ")
        if search_user(usrname) == True :
            print("Username already exists , Please select some other username ")
            continue
        else :
            passwd = input("Select Password : ")
            users_dict[usrname] = passwd
            print("Signed up !!!" + "\n" + "Logged in !!!")
            break

    elif yes_or_no == "n" or yes_or_no == "N" :
        print("Login : ")
        usrname = input("Enter Username : ")
        passwd = input("Enter Password : ")
        if search_user(usrname) == False or  ( search_user(usrname) == True and passwd != users_dict[usrname] ) :
            print("Wrong Credentials")
            continue 
        else :
            print("Logged in !!!")
            break
    count += 1

user_dict_file = open("users_dict.pkl", "wb")
pickle.dump(users_dict , user_dict_file)
user_dict_file.close()

# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((Address, 4589))

# Listening to Server and Sending Nickname
def receive():
    while True :
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = client.recv(1024).decode('ascii')
            if message == 'ACK':
                client.send(usrname.encode('ascii'))
            else:
                print(message)
        except:
            # Close Connection When Error
            print("An error occured!")
            client.close()
            break

# Sending Messages To Server
def write():
    while True: 
        #message = '{}: {}'.format(usrname, input(''))
        message = input()
        if message.split()[0] == "SEND" :                 # SEND navneet hello navneet!! 
            for_len_prps = message.split()
            if len(for_len_prps) < 3 :
                print("Invalid syntax for SEND command , require min 3 args")
                continue
            client.send(message.encode('ascii'))
            #msg = client.recv(1024).decode('ascii')
            #print(msg)

        elif message.split()[0] == "GROUP" :              # GROUP 1 hello everyone in gorup 1 !
            for_len_prps = message.split()
            if len(for_len_prps) < 3 :
                print("Invalid syntax for GROUP command , require min 3 args")
                continue
            client.send(message.encode('ascii'))
            #msg=client.recv(1024).decode('ascii')
            #print(msg)

        elif message.split()[0] == "LIST" :               # LIST
            for_len_prps = message.split()
            if len(for_len_prps) != 1 :
                print("Invalid command , only 1 argument is required for LIST command ")
                continue
            client.send(message.encode('ascii')) 

        elif message.split()[0]  == "CREATE" :             # CREATE 1
            for_len_prps = message.split()
            if len(for_len_prps) != 2 :
                print("Invalid command , Must pass only 2 args for CREATE coomand")
                continue    
            client.send(message.encode('ascii'))

        elif message.split()[0] == "JOIN" :                # JOIN 2
            for_len_prps = message.split()
            if len(for_len_prps) != 2 :
                print("Inavlid Syntax for JOIN command, Must pass 2 args")
                continue
            client.send(message.encode('ascii'))
        else :
            print("Command Inavalid")
            continue 
        #client.send(message.encode('ascii'))  


# Starting Threads For Listening And Writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

