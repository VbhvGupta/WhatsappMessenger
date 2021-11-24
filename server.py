import socket
import threading
import pickle

# Connection Data
host = socket.gethostbyname(socket.gethostname())
port = 4589

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Lists For Clients and Their Nicknames
clients = []    # 
nicknames = []  # [ 'navi' , 'kush' ]
groups = {}
client_user_dict = {}
users_dict = {}
#print(type(dictionary_data))
a_file = open("users_dict.pkl", "wb")
pickle.dump(users_dict, a_file)
a_file.close()

groups_dict ={ }
b_file = open("groups_dict.pkl" , "wb")
pickle.dump(groups_dict,b_file)
b_file.close()

# Sending Messages To All Connected Clients
def broadcast(message):
    print("message inside broadcast : ",message.decode('ascii')) #######
    for client in clients:
        client.send(message)

def check_group_existence(group_name ):
    print("groups_dict in check_group_exixtence:", groups_dict)  ######
    if len(groups_dict) > 0 :
        for grpname in groups_dict:
            if grpname == group_name:
                return True
    return False            

def user_exists(usrname) :
    for usr in nicknames :
        if usr == usrname:
            return True
    return False

def create_Group(group_name , usrname):
    print("groups_dict in create_Group:" ,groups_dict)  ######
    if len(groups_dict) > 0 :  
        for grpname in groups_dict:
            if group_name == grpname:
                message = "Group already exist, Create unique group name!"
                return
        groups_dict[group_name] = []
        groups_dict[group_name].append(usrname)
    else :
        groups_dict[group_name] = []
        groups_dict[group_name].append(usrname) 
    print("groups_dict in create_Group:", groups_dict)  ######   

def send_group_to_peer():
    if len(groups_dict) == 0 :
        return "No groups exists"
    str_2_send = ""
    for grp in groups_dict :
        str_2_send += str(grp) 
        no_of_people = len(groups_dict[grp])
        str_2_send += "\t " + str(no_of_people) + "\n"
    return str_2_send

    #client.send(pickled_groups_dict.encode('ascii'))

def personal_msg(user_Name,msg):
    if user_exists(user_Name) == False :
        return "Username is not in the database"
    for usr in client_user_dict :
        if usr == user_Name :
            client = client_user_dict[usr]
            client.send(msg.encode('ascii'))
            return "Message sent"
    return "Could not locate the user , Try again"

def send_msg_to_grp(grp_name,msg) :
    if check_group_existence(grp_name) == False:
        return "Group doesn't exist"
    user_list = groups_dict[grp_name]
    if len(user_list) == 0 :
        return "No clients in the group"
    for usr in user_list :
        if user_exists(usr) :
            client = client_user_dict[usr]
            client.send(msg.encode('ascii'))
    return "message sent to the group "+str(grp_name)


# Handling Messages From Clients
def handle(client,usrname):
    while True:
        try:
            # Broadcasting Messages
            message = client.recv(1024).decode('ascii')
            print(message)
            message = message.split(' ')
            # print(message)
            temp = message[0]

            if temp == "SEND":
                #send message to specific user
                user_Name = message[1]
                print("usrname : " ,  user_Name) ######
                msg = message[2:]              ###### hello there
                msg = ' '.join(map(str, msg))
                print("msg afterwrds : " , msg)
                ack = personal_msg(user_Name,msg)
                #client.sent(ack.encode('ascii'))

            elif temp == "CREATE":
                #create grpup
                group_name = message[1]
                print("group name :", group_name )
                flag = check_group_existence(group_name)
                print("Flag" , flag)
                if flag:
                    msg = "Group already exist, Create unique group name!"
                    broadcast(msg.encode('ascii'))
                else:
                    create_Group(group_name , usrname)
                    msg = "Group Created"
                    print("msg inside CREATE" , msg)
                    client.send(msg.encode('ascii'))

            elif temp == "LIST":
                lst_2_send = send_group_to_peer()
                client.send(lst_2_send.encode('ascii'))

            elif temp == "JOIN":
                group_name = message[1]
                print("group name in JOIN" , group_name)
                flag = check_group_existence(group_name)
                msg = ""
                if flag:
                    if usrname in groups_dict[group_name]:
                        msg = "Already joined group"
                    else:
                        groups_dict[group_name].append(usrname)
                        msg = "Group joined !!"
                else:
                    msg = "Group you're trying to join doesn't exist"
                print("msg in JOIN : ",msg)
                client.send(msg.encode('ascii'))  

            elif temp == "GROUP":
                grp_name = message[1]
                print("grpname : ",grp_name)
                msg = message[2:]
                msg = ' '.join(map(str, msg))
                print("msg in GROUP", msg)
                ack = send_msg_to_grp(grp_name,msg)
                #client.send(ack.encode('ascii'))
        except:
            # Removing And Closing Clients
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast('{} left!'.format(nickname).encode('ascii'))
            nicknames.remove(nickname)
            break

# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Request And Store Nickname
        client.send('ACK'.encode('ascii'))
        usrname = client.recv(1024).decode('ascii')
        nicknames.append(usrname)
        clients.append(client)

        client_user_dict[usrname] = client

        # Print And Broadcast Nickname
        print("Username is {}".format(usrname))
        broadcast("{} joined!".format(usrname).encode('ascii'))
        client.send('Connected to server!'.encode('ascii'))

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,usrname))
        thread.start()

receive()
