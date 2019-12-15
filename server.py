import socket
import sys
import pickle
import os


class server:
    def __init__(self, source_ip, source_port):
        self._source_ip = source_ip
        self._source_port = source_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self._source_ip, self._source_port))
        self.socket.listen(5)
        # holds sender_info: files list
        self.user_dict = {}

    def run(self):
        while True:
            client_socket, client_address = self.socket.accept()
            # print ("connection from: " + client_address[0] + " " + client_address[1].__str__())
            data = client_socket.recv(1024).decode()
            message = data
            while data:
                data = client_socket.recv(1024).decode()
                message += data
            if message[0] is "1":
                self.handle_listener(message[2:], client_socket, client_address)
            elif message[0] is "2":
                self.handle_user(message[2:], client_socket)
            else:
                print("Error")
            # print ("client disconnected")

    def handle_user(self, req_file, connection):
        list_to_send = []
        if req_file is not '\n':
            for sender_info in self.user_dict.keys():
                for file in self.user_dict[sender_info]:
                    if req_file in file:
                        # list_to_send.append(file)
                        # list_to_send.append(sender_info[0])
                        # list_to_send.append(sender_info[1].__str__())
                        list_to_send.append((file, sender_info[0], sender_info[1].__str__()))
        else:
            list_to_send.append(req_file)
        if len(list_to_send) is 0:
            list_to_send.append(req_file)
        list_to_send.sort(key=lambda x: x[0])
        list_to_send = [element for item in list_to_send for element in item]
        data_to_send = " ".join(list_to_send)
        connection.send(data_to_send.encode())
        connection.close()

    def handle_listener(self, message, connection, client_info):
        my_list = message.split(" ", 1)
        client_port = int(my_list[0])
        files_list = my_list[1].split(" ")
        self.user_dict[(client_info[0], client_port)] = files_list
        connection.close()


source_ip = '0.0.0.0'
source_port = int(sys.argv[1])
server = server(source_ip, source_port)
server.run()
