from socket import *
import argparse
import time
import sys
import threading
import ipaddress

# Parse the command-line arguments and perform basic error checking
def parse_args():
    parser = argparse.ArgumentParser(description = 'Simpleperf')
    parser.add_argument('-s', '--server', action = 'store_true', help = 'Enable server mode')
    parser.add_argument('-c', '--client', action='store_true', help='Enable client mode')
    parser.add_argument('-b', '--bind', type = str, default = '127.0.0.1', help = 'Server IP address')
    parser.add_argument('-I', '--serverip', type=str, default = '127.0.0.1', help='IP address of server')
    parser.add_argument('-p', '--port', type = int, default = 8088, help = 'Server port number')
    parser.add_argument('-f', '--format', type = str, default = 'MB', help = 'Summary format (B/KB/MB)')
    parser.add_argument('-t', '--time', type = int, default = 25, help='Duration in seconds for which data should be generated')
    parser.add_argument('-i', '--interval', type = int, help = 'Print statistics per specidied interval in seconds')
    parser.add_argument('-n', '--num', type = str, help = 'Transfer number of bytes')
    parser.add_argument('-P', '--parallel', type=int, default=1, help='Number of parallel connections to the server (1-5)')

    args = parser.parse_args()

    # Check conditions for flags
    validate_args(args)

    return args

def validate_args(args):
        # Check if both '-s' flag and '-c' flag are enabled at the same time
    if args.server and args.client:
        sys.exit("Error: You cannot run both server and client mode at the same time")

    # Check if neither '-s' flag nor '-c' flag is enabled
    if not (args.server or args.client):
        sys.exit("Error: You must run either in server or client mode")

    # Check if '-b' flag have a valid IP address
    try:
        ipaddress.ip_address(args.bind)
    except ValueError:
        sys.exit("Error: Invalid IP address for '-b' flag")

    # Check if '-I' flag have a valid IP address
    try:
        ipaddress.ip_address(args.serverip)
    except ValueError:
        sys.exit("Error: Invalid IP address for '-I' flag")
    
    # Check if the port number for the '-p' flag is between 1024 and 65535
    if args.port < 1024 or args.port > 65535:
        sys.exit("Error: Invalid value for '-p' flag. The port must be an integer in the range [1024, 65535]")
    
    # Check if the format for the '-f' flag is correct
    if args.format not in ["B", "KB", "MB"]:
        sys.exit("Error: Invalid value for '-f' flag. Format must be either B, KB, or MB")
    
    # Check if the value for the '-t' flag is a positive integer
    if args.time < 1:
        sys.exit("Error: Invalid value for '-t' flag. Duration in seconds must be a positive integer")
    
    # Check if the value for the '-i' flag is a positive integer
    if args.interval is not None and args.interval < 1:
        sys.exit("Error: Invalid value for '-i' flag. Duration in seconds must be a positive integer")

    # Check if the format for the '-n' is correct
    if args.num is not None and (args.num[-2:] not in ["KB", "MB"] and args.num[-1:] != "B"):
        sys.exit("Error: Invalid value for '-n' flag. Format must be an integer followed by either B, KB, or MB")

    # Check if the value for the '-P' flag is between 1 and 5
    if args.parallel < 1 or args.parallel > 5:
        sys.exit("Error: Invalid value for '-P' flag. Number of parallel connections must be a integer between 1 and 5")

def format_values(value, input_format):
    if input_format == "B":
        return value
    elif input_format == "KB":
        return value / 1000
    else:
        return value / 1000000
    
def format_num(input_num):
    if input_num[-2:] == "KB":
        return int(input_num[:-2]) * 1000
    elif input_num[-2:] == "MB":
        return int(input_num[:-2]) * 1000000
    elif input_num[-1:] == "B":
        return int(input_num[:-1])
    
def print_table(data):
    format_row = "{:>20}" * (len(data))
    print(format_row.format(*data))

# Handle an individual connection to the server
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
            if "BYE" in received_bytes.decode(): 
                # Send the client an acknowledgement of the confirmation
                client_socket.sendall("ACK: BYE".encode())
                break
        
        # Ending time 
        end_time = time.time()

        # Duration of the interval
        duration =  end_time - start_time

        # Formating the values of the bytes in either Bytes, Kilobytes or Megabytes
        total_received_bytes_format = format_values(total_received_bytes, input_format)

        # Calculate the rate of incoming trafic in megabites per second
        rate = (total_received_bytes * 8e-6) / duration

        # Printing the data in server
        headers = ["ID", "Interval", "Received", "Rate"]
        data = [[f"{client_address[0]}:{client_address[1]}", f"0.0 - {duration:.1f}", f"{total_received_bytes_format:.2f} {input_format}", f"{rate:.2f} Mbps"],]
        
        print_table(headers)
        for row in data:
            print_table(row)

    client_socket.close()

# Start the server and listen for incoming connections
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
        server_message = f"A simpleperf server is listening on port {port_number}"
        server_message_line = f"-" * len(server_message)
        print(server_message_line)
        print(server_message)
        print(server_message_line)

        while True:
            # Waiting for a client to connect
            client_socket, client_address = server_socket.accept()
            print(f"A simpleperf client with {client_address[0]}:{client_address[1]} is connected with {ip_address}:{port_number}")

            # Create a new thread to handle the connection
            thread = threading.Thread(target=handle_server, args=(client_socket, client_address, input_format))
            thread.start()

# Handle the client connection and send data to the server
def handle_client(client_socket, client_ip_address, client_port_number, input_time, input_format, input_interval_time, input_num):
    if input_num is not None:
        num_bytes = format_num(input_num)
        input_time = None

    # Starting the timer
    start_time = time.time()

    # Time of last interval
    current_time = start_time

    # Starting value of sent Bytes
    total_sent_bytes = 0

    # Starting value of sent Bytes in interval
    interval_sent_bytes = 0
    
    # Amount of bytes to be sent 
    bytes = b"0" * 1000

    # Transfer the Bytes
    while(input_time is None and total_sent_bytes < num_bytes) or (input_time is not None and (time.time() - start_time) < input_time):
        sending_bytes = client_socket.send(bytes)

        # Updates the values of sent Bytes
        total_sent_bytes += sending_bytes

        # Updates the values of sent Bytes in interval
        interval_sent_bytes = interval_sent_bytes + sending_bytes

        # Calculates values of bytes in intervals 
        if input_interval_time is not None and (time.time() - current_time >= input_interval_time):
            current_time = current_time + input_interval_time
            elapsed_time = current_time - start_time

            interval_rate = (interval_sent_bytes * 8e-6) / input_interval_time 

            # Formating the values of the bytes in either Bytes, Kilobytes or Megabytes
            interval_sent_bytes_format = format_values(interval_sent_bytes, input_format)

            data = [[f"{client_ip_address}:{client_port_number}", f"{elapsed_time - input_interval_time:.1f} - {elapsed_time:.1f}", f"{interval_sent_bytes_format:.2f} {input_format}", f"{interval_rate:.2f} Mbps"],]
            for row in data:
                print_table(row)

            # Reset the values of bytes
            interval_sent_bytes = 0 

    # Send a message to the server to indicate that the transfer is complete
    client_socket.sendall("BYE".encode())

    response = client_socket.recv(1024).decode()
    if response == "ACK: BYE":
        end_time = time.time()
        duration = end_time - start_time

            # Formating the values of the bytes in either Bytes, Kilobytes or Megabytes
        total_sent_bytes_format = format_values(total_sent_bytes, input_format)

        # Calculate the rate of incoming trafic in megabites per second
        rate = (total_sent_bytes * 8e-6) / duration

        data = [[f"{client_ip_address}:{client_port_number}", f"0.0 - {duration:.1f}", f"{total_sent_bytes_format:.2f} {input_format}", f"{rate:.2f} Mbps"],]
        for row in data:
            print_table(row)

    # Close the client socket
    client_socket.close()

# Connect to the server and start sending data
def start_client(args):
    ip_address = args.serverip
    port_number = args.port
    input_time = args.time
    input_format = args.format
    input_interval_time = args.interval
    input_num = args.num
    input_parallel = args.parallel
        
    headers = ["ID", "Interval", "Transfer", "Bandwidth"]
    connection_list = []

    for i in range(input_parallel):
        # Create a TCP socket
        client_socket = socket(AF_INET, SOCK_STREAM)

        # Connect to the server
        client_socket.connect((ip_address, port_number))
        print(f"Client connected with server {ip_address}:{port_number}")
    
        client_ip_address, client_port_number = client_socket.getsockname()

        # Printing the headers in client
        if i == input_parallel - 1:
            print_table(headers)

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