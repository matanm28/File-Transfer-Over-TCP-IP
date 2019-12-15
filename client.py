import socket
from socket import SHUT_WR
import sys
import os
import time
import pickle


def listen_mode(dest_ip, dest_port, my_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((dest_ip, dest_port))
    sock.send(listener_message(my_port).encode())
    my_ip = sock.getsockname()[0]
    sock.close()
    download_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    download_sock.bind((my_ip, my_port))
    download_sock.listen(1)
    while True:
        client_socket, client_address = download_sock.accept()
        # print ("connection from: " + client_address[0] + " " + client_address[1].__str__())
        wanted_file = client_socket.recv(1024).decode()
        file = open(wanted_file, "rb")
        binary_data = file.read(1024)
        while binary_data:
            client_socket.send(binary_data)
            binary_data = file.read(1024)
        file.close()
        client_socket.close()


def listener_message(my_port):
    path = os.getcwd()
    flag = True
    message = "1 " + my_port.__str__() + " "
    temp_list = listOfFiles(path)
    with os.scandir(path) as listOfEntries:
        for entry in listOfEntries:
            if entry.is_file():
                if flag:
                    message += entry.name
                    flag = False
                else:
                    message += " "
                    message += entry.name
    return message


def user_mode(dest_ip, dest_port):
    message = "2 "
    request = input("Search: ")
    if len(request) is 0:
        request = "\n"
    message += request
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((dest_ip, dest_port))
    sock.send(message.encode())
    sock.shutdown(SHUT_WR)
    data = sock.recv(1024).decode()
    info = data
    while data:
        data = sock.recv(1024).decode()
        info += data
    sock.close()
    file_list = list(info.split(" "))
    if len(file_list) == 1 and file_list[0] == request != "\n":
        print("There are no results for " + request + ".")
    else:
        user_range = print_files(file_list)
        try:
            choice = int(input("Choose: "))
        except:
            choice = 0
        if 1 <= choice < user_range:
            choice = (choice - 1) * 3
            file_name = file_list[choice]
            down_ip = file_list[choice + 1]
            down_port = int(file_list[choice + 2])
            down_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            down_sock.connect((down_ip, down_port))
            down_sock.send(file_name.encode())
            with open(file_name, "wb") as my_file:
                while True:
                    file_data = down_sock.recv(1024)
                    my_file.write(file_data)
                    if len(file_data) is 0:
                        break
            my_file.close()
            down_sock.close()
        else:
            print("illegal input")


def listOfFiles(path):
    files = []
    with os.scandir(path) as listOfEntries:
        for entry in listOfEntries:
            if entry.is_file():
                files.append(entry.name)
    return files


def print_files(files):
    count = 1
    if len(files) >= 3:
        for i in range(len(files)):
            if i % 3 is 0:
                print(count.__str__() + " " + files[i])
                count += 1
    else:
        print("\n")
    return count


mode = sys.argv[1]
dest_ip = sys.argv[2]
dest_port = int(sys.argv[3])
if mode is "0":
    my_port = int(sys.argv[4])
while True:
    if mode is "0":
        # listen mode
        listen_mode(dest_ip, dest_port, my_port)
    elif mode is "1":
        user_mode(dest_ip, dest_port)
    else:
        print("illegal request")
        break
