from socket import *
import argparse
import time

def parse_args():
    parser = argparse.ArgumentParser(description = 'Simpleperf Server')
    parser.add_argument('-s', '--server', action = 'store_true', help = 'Enable server mode')
    parser.add_argument('-b', '--bind', type = str, default = 'localhost', help = 'Server IP address')
    parser.add_argument('-p', '--port', type = int, default = 8088, help = 'Server port number')
    parser.add_argument('-f', '--format', type = str, default = 'MB', help = 'Summary format (B/KB/MB)')
    parser.add_argument('-c', '--client', action='store_true', help='enable client mode')
    parser.add_argument('-I', '--serverip', type=str, default = 'localhost', help='IP address of server')

    return parser.parse_args()

def start_server(host_name, port_number, format):
    # Create a TCP socket
    server_socket = socket(AF_INET, SOCK_STREAM)

    # Bind socket to the server
    server_socket.bind((host_name, port_number))

    # Listen for incoming connections
    server_socket.listen(1)
    print(f"A simpleperf server is listening on port {port_number}")

    while True:
        # Waiting for a client to connect
        client_socket, client_address = server_socket.accept()
        print(f"A simpleperf client with {client_address[0]}:{client_address[1]} is connected with {host_name}:{port_number}")
        """
        # Requesting start time from client
        client_socket.send("START_TIME".encode('utf-8'))
        start_time = client_socket.recv(1024).decode('utf-8')

        # Starting value for the incoming bytes
        total_received_bytes = 0

        while True:
            # Receiving the bytes from the client
            received_bytes = client_socket.recv(1000)
            if not received_bytes:
                break

            # Accumulated values of bytes 
            total_received_bytes = total_received_bytes + len(received_bytes)
        
        # Requesting end time from client
        client_socket.send("END_TIME".encode('utf-8'))
        end_time = client_socket.recv(1024).decode('utf-8')
        

        # Duration of the interval
        duration = end_time - start_time

        print(duration)

        # Formating the values of the bytes in either Bytes, Kilobytes or Megabytes
        if format == "B":
            total_received_bytes_string = f"{total_received_bytes} Bytes"
        elif format == "KB":
            total_received_bytes_string = f"{total_received_bytes / 1000} KB"
        else:
            total_received_bytes_string = f"{total_received_bytes / 1000000} MB"
        
        # Calculate the rate of incoming trafic in megabites per second
        rate = (total_received_bytes * 8e-6) / duration
        
        headers = ["ID", "Interval", "Received", "Rate"]

        data = [f"{client_address[0]}{client_address[1]}", f"0.0 - {duration:.1f}", f"{total_received_bytes_string}", f"{rate:.2f Mbps}"],
        
        # Print the headers
        print("{:<10}{:<10}{:<10}{:<10}".format(*headers))

        # Print the data
        for row in data:
            print("{:<10}{:<10}{:<10}{:<10}".format(*row))
        
        """
        """
        client_socket.send(b"ACK: BYE")
        client_socket.close()
        server_socket.close()
        """
        message = client_socket.recv(1024).decode('utf-8')
        print(message)
        client_socket.send("Hei hei, client!".encode('utf-8'))	

def start_client(host_name, port_number):
    # Create a TCP socket
    client_socket = socket(AF_INET, SOCK_STREAM)

    # Connect to the server
    client_socket.connect((host_name, port_number))

    client_socket.send("Hei hei, server!".encode('utf-8'))
    message = client_socket.recv(1024).decode('utf-8')
    print(message)


    """
    while True:
        request = client_socket.recv(1024).decode('utf-8')

        if request == 'START_TIME':
            start_time = time.time()
            client_socket.send(start_time).encode('utf-8')

        if request == 'END_TIME':
            end_time = time.time()
            client_socket.send(end_time).encode('utf-8')
    """    


if __name__ == '__main__':
    args = parse_args()
    if args.server:
        start_server(args.bind, args.port, args.format)
    
    if args.client:
        start_client(args.serverip, args.port)