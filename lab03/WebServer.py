#!/bin/usr/python3
# Exercise 4 for COMP3331 Lab 3 - Week 4
# Anthony Xu - z5165674

import sys
import socket


# Collect file name from data received from GET request, will only iterate through the first line
# Data has form: GET /[filename] HTTP/1.1 etc...
# Skip the everything from the start to the first "/"
# Stores the file name, stops loop and returns file name
def get_filename(data):
    word = ''
    slash = 0
    
    for character in data:
        # Start storing the characters when it hits the first slash
        if slash == 1:
            # End loop when the whole file name has been stored
            if character == ' ':
                break
            word += character
        # Check if next character will be the first letter of file name 
        if character == '/':
            slash += 1
        
    # Join file name into string
    fname = ''.join([word])

    return fname

# Checks if the file given is a HTML or PNG file
# Based on the assumption that these are the only two files being tested
def is_html(file_name):
    # Split file name into two parts from the "."
    file_type = file_name.split('.')[1]

    if file_type == 'html':
        return True
    elif file_type == 'png':
        return False

    return True


def main():
    # Check whether or not a single port was entered
    if len(sys.argv) != 2:
        print("Usage: python3 WebServer.py [port]")
        sys.exit(1)

    # Collect the port that the web server will be listening on
    port = int(sys.argv[1])
    host = '127.0.0.1'
    server_address = (host, port)

    # Create a socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind socket to local host and port
    server_socket.bind(server_address)
    # Tell socket to listen to browser
    server_socket.listen(1)

    # Listens and waits for any communication with the browser
    while True:
        # Returns connection between server and client and the address of the client
        connection, socket_address = server_socket.accept()
        try:
            # Receive data from the client
            received_data = connection.recv(1024).decode()
            # Find file name ffrom data received
            file_name = get_filename(received_data)

            # Server will send differently depending on file type
            if not is_html(file_name):
                # Open file and read binary
                f = open(file_name, 'rb')
                # Read all data from image
                file_data = f.read()
                f.close()

                # Send headers - let browser know request was successful
                connection.send('HTTP/1.1 200 OK\r\n'.encode())
                # Let browser know a PNG image is being sent over
                connection.send('Content-type: image/png\r\n\r\n'.encode())

                # Send data of image
                connection.send(bytes(file_data))

            else:
                # Open file to read text
                f = open(file_name)
                file_data = f.read()
                f.close()

                # Same as above, let browser know request was successful
                connection.send('HTTP/1.1 200 OK\r\n'.encode())
                # Let browser know a HTML file is being sent over
                connection.send('Content-type: text/html\r\n\r\n'.encode())

                # Iterate through file and send data over to browser
                for i in range(0, len(file_data)):
                    connection.send(file_data[i].encode())

            # Close connection when finished sending to browser
            connection.close()

        # Exception when file cannot be found in current directory
        except:
            # Let browser know request failed
            connection.send('HTTP/1.1 404 Not Found\r\n'.encode())
            connection.send('Content-type: text/html\r\n\r\n'.encode())
            connection.send('<html><head></head><body><h1>404 Not Found</h1></body></html>'.encode())
            connection.close()
    
    # Close server socket when complete
    server_socket.close()


if __name__ == '__main__':
    main()

