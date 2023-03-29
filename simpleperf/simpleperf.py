from socket import *
import argparse
import time
import sys
import threading

def parse_args():
    parser = argparse.ArgumentParser(description = 'Simpleperf Server')
    parser.add_argument('-s', '--server', action = 'store_true', help = 'Enable server mode')
    parser.add_argument('-b', '--bind', type = str, default = 'localhost', help = 'Server IP address')
    parser.add_argument('-p', '--port', type = int, default = 8088, help = 'Server port number')
    parser.add_argument('-f', '--format', type = str, default = 'MB', help = 'Summary format (B/KB/MB)')
    parser.add_argument('-c', '--client', action='store_true', help='enable client mode')
    parser.add_argument('-I', '--serverip', type=str, default = 'localhost', help='IP address of server')
    parser.add_argument('-t', '--time', type = int, default = 25, help='IP address of server')
    parser.add_argument('-i', '--interval', type = int, help = 'Print statistics per specidied interval in seconds')
    parser.add_argument('-n', '--num', type = str, help = 'Transfer number of bytes')
    parser.add_argument('-P', '--parallel', type=int, default=1, help='Number of parallel connections to the server (1-5)')

    return parser.parse_args()

def handle_server(client_socket, client_address, input_format):
    with client_socket:
        # Starting time
        start_time = time.time()

        # Starting value of received Bytes
        total_received_bytes = 0

        while True:
            # Receiving the Bytes from the client
            received_bytes = client_socket.recv(1000)

            # Accumulated values of Bytes 
            total_received_bytes = total_received_bytes + len(received_bytes)

            # Receving confirmation that the transfer is complete
            if received_bytes.decode() == "BYE":
                # Send the client an acknowledgement of the confirmation
                client_socket.sendall("ACK: BYE".encode())
                break
        
        # Ending time 
        end_time = time.time()

        # Duration of the interval
        duration =  end_time - start_time

        # Formating the values of the bytes in either Bytes, Kilobytes or Megabytes
        if format == "B":
            total_received_bytes_format = total_received_bytes
        elif format == "KB":
            total_received_bytes_format = total_received_bytes / 1000
        else:
            total_received_bytes_format = total_received_bytes / 1000000

        # Calculate the rate of incoming trafic in megabites per second
        rate = (total_received_bytes * 8e-6) / duration

        # Printing the data in server
        headers = ["ID", "Interval", "Received", "Rate"]
        data = [[f"{client_address[0]}:{client_address[1]}", f"0.0 - {duration:.1f}", f"{total_received_bytes_format:.2f} {input_format}", f"{rate:.2f} Mbps"],]
        
        format_row = "{:>20}" * (len(headers))
        print(format_row.format(*headers))
        for row in data:
            print(format_row.format(*row))

def start_server(args):
    ip_address = args.bind
    port_number = args.port
    input_format = args.format

    # Create a TCP socket
    with socket(AF_INET, SOCK_STREAM) as server_socket:
        # Bind socket to the server
        server_socket.bind((ip_address, port_number))

        # Listen for incoming connections
        server_socket.listen()
        print(f"A simpleperf server is listening on port {port_number}")    

        while True:
            # Waiting for a client to connect
            client_socket, client_address = server_socket.accept()
            print(f"A simpleperf client with {client_address[0]}:{client_address[1]} is connected with {ip_address}:{port_number}")

            # Create a new thread to handle the connection
            thread = threading.Thread(target=handle_server, args=(client_socket, client_address, input_format))
            thread.start()

def handle_client(client_socket, client_ip_address, client_port_number, input_time, input_format, input_interval_time, input_num):
    if input_num is not None:
        if input_num[-2:] == "KB":
            num_bytes = int(input_num[:-2]) * 1000
        elif input_num[-2:] == "MB":
            num_bytes = int(input_num[:-2]) * 1000000
        elif input_num[-1:] == "B":
            num_bytes = int(input_num[:-1])
        else:
            sys.exit("Error: Invalid data format for '-n' flag. Format must be a integer followed by either in B, KB or MB")
        input_time = None

    # Starting the timer
    start_time = time.time()

    # Time of last interval
    current_time = start_time

    # Starting value of sent Bytes
    total_sent_bytes = 0

    # Starting value of sent Bytes in interval
    interval_sent_bytes = 0
    
    bytes = b"0" * 1000

    # Printing the data in server
    headers = ["ID", "Interval", "Transfer", "Bandwidth"]
    
    format_row = "{:>20}" * (len(headers))
    print(format_row.format(*headers))

    # Transfer the Bytes
    while(input_time is None and total_sent_bytes < num_bytes) or (input_time is not None and (time.time() - start_time) < input_time):
        sending_bytes = client_socket.send(bytes)

        # Updates the values of sent Bytes
        total_sent_bytes += sending_bytes

        # Updates the values of sent Bytes in interval
        interval_sent_bytes = interval_sent_bytes + sending_bytes

        if input_interval_time is not None and (time.time() - current_time >= input_interval_time):
            current_time = current_time + input_interval_time
            elapsed_time = current_time - start_time

            interval_rate = (interval_sent_bytes * 8e-6) / input_interval_time 

            # Formating the values of the bytes in either Bytes, Kilobytes or Megabytes
            if input_format == "B":
                interval_sent_bytes_format = interval_sent_bytes
            elif input_format == "KB":
                interval_sent_bytes_format = interval_sent_bytes / 1000
            else:
                interval_sent_bytes_format = interval_sent_bytes / 1000000

            data = [[f"{client_ip_address}:{client_port_number}", f"{elapsed_time - input_interval_time:.1f} - {elapsed_time:.1f}", f"{interval_sent_bytes_format:.2f} {input_format}", f"{interval_rate:.2f} Mbps"],]
            for row in data:
                print(format_row.format(*row))

            interval_sent_bytes = 0 

    # Send a message to the server to indicate that the transfer is complete
    client_socket.sendall("BYE".encode())

    response = client_socket.recv(1024).decode()
    if response == "ACK: BYE":
        end_time = time.time()
        duration = end_time - start_time

            # Formating the values of the bytes in either Bytes, Kilobytes or Megabytes
        if input_format == "B":
            total_sent_bytes_format = total_sent_bytes
        elif input_format == "KB":
            total_sent_bytes_format = total_sent_bytes / 1000
        else:
            total_sent_bytes_format = total_sent_bytes / 1000000

        # Calculate the rate of incoming trafic in megabites per second
        rate = (total_sent_bytes * 8e-6) / duration

        data = [[f"{client_ip_address}:{client_port_number}", f"0.0 - {duration:.1f}", f"{total_sent_bytes_format:.2f} {input_format}", f"{rate:.2f} Mbps"],]
        for row in data:
            print(format_row.format(*row))

    # Close the client socket
    client_socket.close()

def start_client(args):
    ip_address = args.serverip
    port_number = args.port
    input_time = args.time
    input_format = args.format
    input_interval_time = args.interval
    input_num = args.num
    input_parallel = args.parallel

    if input_parallel < 1 or input_parallel > 5:
        sys.exit("Error: Invalid data format for '-P' flag. Number of parallel connections must be a integer between 1 and 5")

    connection_list = []

    for i in range(input_parallel):
        # Create a TCP socket
        client_socket = socket(AF_INET, SOCK_STREAM)

        # Connect to the server
        client_socket.connect((ip_address, port_number))
        print(f"Client connected with server {ip_address}:{port_number}")

        client_ip_address, client_port_number = client_socket.getsockname()

        thread = threading.Thread(target=handle_client, args=(client_socket, client_ip_address, client_port_number, input_time, input_format, input_interval_time, input_num))
        connection_list.append(thread)
        thread.start()
    
    for j in connection_list:
        j.join()
    
if __name__ == '__main__':
    args = parse_args()
    if args.server:
        start_server(args)
    elif args.client:
        start_client(args)
    else:
        print("Error: You must run either in server or client mode")