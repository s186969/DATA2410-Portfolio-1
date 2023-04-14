from socket import *
import argparse
import time
import sys
import threading
import ipaddress

# This function will parse the command-line arguments and perform basic error checking
def parse_args():
    # Defines and parses the command-line argument
    parser = argparse.ArgumentParser(description = 'Simpleperf')
    # '-s' flag: Enables the server mode
    parser.add_argument('-s', '--server', action = 'store_true', help = 'Enable server mode')

    # '-c' flag: Enables the client mode
    parser.add_argument('-c', '--client', action = 'store_true', help = 'Enable client mode')

    # '-b' flag: Sets the IP address of the server to bind to. Default value is '127.0.0.1'
    parser.add_argument('-b', '--bind', type = str, default = '127.0.0.1', help = 'Server IP address')

    # '-I' flag: Sets the IP address of the server that the client will connect to. Default value is '127.0.0.1'
    parser.add_argument('-I', '--serverip', type= str, default = '127.0.0.1', help = 'IP address of server')

    # '-p' flag: Sets the port number that the server will listen on or the client will connect to. The default value is 8088
    parser.add_argument('-p', '--port', type = int, default = 8088, help = 'Server port number')

    # '-f' flag: Sets the format for the summary data that will be printed. The default value is MB
    parser.add_argument('-f', '--format', type = str, default = 'MB', help = 'Summary format (B/KB/MB)')

    # '-t' flag: Sets the duration in seconds for which the data should be generated. The default value is 25
    parser.add_argument('-t', '--time', type = int, default = 25, help = 'Duration in seconds for which data should be generated')

    # '-i' flag: Sets the interval in seconds at which statistics should be printed
    parser.add_argument('-i', '--interval', type = int, help = 'Print statistics per specidied interval in seconds')

    # '-n' flag: Sets the number of bytes that should be transferred by the client
    parser.add_argument('-n', '--num', type = str, help = 'Transfer number of bytes')

    # '-P' flag: Sets the number between 1-5 of parallel connections to the server. The default value is 1
    parser.add_argument('-P', '--parallel', type = int, default = 1, help = 'Number of parallel connections to the server (1-5)')

    # Parsing the command-line arguments
    args = parser.parse_args()

    # Checks conditions for flags
    validate_args(args)

    # Returns the parsed command-line arguments
    return args

# This function will validate the arguments from above
def validate_args(args):
    # Checks if both '-s' flag and '-c' flag are enabled at the same time
    if args.server and args.client:
        sys.exit("Error: You cannot run both server and client mode at the same time")

    # Checks if neither '-s' flag nor '-c' flag is enabled
    if not (args.server or args.client):
        sys.exit("Error: You must run either in server or client mode")

    # Checks if '-b' flag have a valid IP address
    try:
        ipaddress.ip_address(args.bind)
    except ValueError:
        sys.exit("Error: Invalid IP address for '-b' flag")

    # Checks if '-I' flag have a valid IP address
    try:
        ipaddress.ip_address(args.serverip)
    except ValueError:
        sys.exit("Error: Invalid IP address for '-I' flag")
    
    # Checks if the port number for the '-p' flag is between 1024 and 65535
    if args.port < 1024 or args.port > 65535:
        sys.exit("Error: Invalid value for '-p' flag. The port must be an integer in the range [1024, 65535]")
    
    # Checks if the format for the '-f' flag is correct
    if args.format not in ["B", "KB", "MB"]:
        sys.exit("Error: Invalid value for '-f' flag. Format must be either B, KB, or MB")
    
    # Checks if the value for the '-t' flag is a positive integer
    if args.time is not None and args.time < 1:
        sys.exit("Error: Invalid value for '-t' flag. Duration in seconds must be a positive integer")
    
    # Checks if the value for the '-i' flag is a positive integer
    if args.interval is not None and args.interval < 1:
        sys.exit("Error: Invalid value for '-i' flag. Duration in seconds must be a positive integer")

    # Checks if the format for the '-n' is correct
    if args.num is not None and (args.num[-2:] not in ["KB", "MB"] and args.num[-1:] != "B"):
        sys.exit("Error: Invalid value for '-n' flag. Format must be an integer followed by either B, KB, or MB")

    # Checks if the value for the '-P' flag is between 1 and 5
    if args.parallel < 1 or args.parallel > 5:
        sys.exit("Error: Invalid value for '-P' flag. Number of parallel connections must be a integer between 1 and 5")

# This function convert a given value to the specified format
def format_values(value, input_format):
    # If the specified format is in bytes, it will convert and return the values in bytes
    if input_format == "B":
        return value
    # If the specified format is in kilobytes, it will convert and return the values in bytes
    elif input_format == "KB":
        return value / 1000
    # If the specified format is in megabytes, it will convert and return the values in bytes
    else:
        return value / 1000000
    
# This function will extract the integer in the string from the '-n' flag
def format_num(input_num):
    # If the string consist a integer with a unit in kilobytes, it will the extract the integer and return the value in bytes
    if input_num[-2:] == "KB":
        return int(input_num[:-2]) * 1000
    # If the string consist a integer with a unit in megabytes, it will the extract the integer and return the value in bytes
    elif input_num[-2:] == "MB":
        return int(input_num[:-2]) * 1000000
    # If the string consist a integer with a unit in bytes, it will the extract the integer and return the value in bytes
    elif input_num[-1:] == "B":
        return int(input_num[:-1])
    
# This function will print the given data in a formatted table row
def print_table(data):
    # The format of the row
    format_row = "{:>20}" * (len(data))

    # Prints out the data element in a single row
    print(format_row.format(*data))

# This function handles the packages in the server, where it will receives from the client
def handle_server(client_socket, client_address, input_format):
    # Using the client socket
    with client_socket:
        # Starting time at when a client connects and sends the bytes
        start_time = time.time()

        # Starting value of received Bytes
        total_received_bytes = 0

        # Continues to receive the bytes from the client
        while True:
            # Receiving the bytes from the client
            received_bytes = client_socket.recv(1000)

            # Accumulated values of Bytes 
            total_received_bytes = total_received_bytes + len(received_bytes)

            # Receving confirmation that the transfer is complete
            if "BYE" in received_bytes.decode(): 
                # Send the client an acknowledgement of the confirmation
                client_socket.sendall("ACK: BYE".encode())

                # Ending the loop
                break
        
        # Ending time at when the server has acknowledged the completion of the transfer
        end_time = time.time()

        # Duration of the transfer
        duration =  end_time - start_time

        # Formating the values of the bytes in either bytes, kilobytes or megabytes
        total_received_bytes_format = format_values(total_received_bytes, input_format)

        # Calculate the rate of incoming trafic in megabites per second
        rate = (total_received_bytes * 8e-6) / duration

        # Defining the headers of the table
        headers = ["ID", "Interval", "Received", "Rate"]
        
        # Defining the data of the table
        data = [[f"{client_address[0]}:{client_address[1]}", f"0.0 - {duration:.1f}", f"{total_received_bytes_format:.2f} {input_format}", f"{rate:.2f} Mbps"],]
        
        # Printing the values in a table format
        print_table(headers)
        for row in data:
            print_table(row)
    
    # Closes the socket connection with the client
    client_socket.close()

# This function starts the server and listens for incoming connections
def start_server(args):
    # Defining the IP address using the '-b' flag
    ip_address = args.bind
    
    # Defining the port number using the '-p' flag
    port_number = args.port

    # Defining the specified format to be shown using'-f' flag
    input_format = args.format

    # Creates a TCP socket
    with socket(AF_INET, SOCK_STREAM) as server_socket:
        # Bind socket to the server
        server_socket.bind((ip_address, port_number))

        # Listen for incoming connections
        server_socket.listen()

        # Defining the message that confirms that the server is listening
        server_message = f"A simpleperf server is listening on port {port_number}"

        # Defining the lines to be used in the message 
        server_message_line = f"-" * len(server_message)

        # Prints out the message that the server is listening
        print(server_message_line)
        print(server_message)
        print(server_message_line)

        # Waiting for a client to connect    
        while True:
            # Accepting a connection request from a client
            client_socket, client_address = server_socket.accept()

            # Printing a message to indicate that the client is connected to the server
            print(f"A simpleperf client with {client_address[0]}:{client_address[1]} is connected with {ip_address}:{port_number}")

            # Creates a new thread to handle the connection
            thread = threading.Thread(target=handle_server, args=(client_socket, client_address, input_format))

            # Initiates the thread
            thread.start()

# This function handles the packages in the client, where it will transfer to the server
def handle_client(client_socket, client_ip_address, client_port_number, input_time, input_format, input_interval_time, input_num):
    # If the '-n' flag is enabled
    if input_num is not None:
        # Defining the bytes to be sent
        num_bytes = format_num(input_num)

        # Voids the '-t' flag
        input_time = None

    # Starting time at when the client sends the bytes
    start_time = time.time()

    # Time of last interval
    current_time = start_time

    # Starting value of sent bytes
    total_sent_bytes = 0

    # Starting value of sent bytes in a interval
    interval_sent_bytes = 0
    
    # Amount of bytes to be sent 
    bytes = b"0" * 1000

    # Transfer the bytes to the server in a loop
    while(input_time is None and total_sent_bytes < num_bytes) or (input_time is not None and (time.time() - start_time) < input_time):
        # Sending the bytes to the server
        sending_bytes = client_socket.send(bytes)

        # Updates the values of sent bytes
        total_sent_bytes += sending_bytes

        # Updates the values of sent bytes in a interval
        interval_sent_bytes = interval_sent_bytes + sending_bytes

        # Calculates values of bytes in intervals 
        if input_interval_time is not None and (time.time() - current_time >= input_interval_time):
            # Updates the current time of the last interval
            current_time = current_time + input_interval_time

            # Elapsed time of the interval
            elapsed_time = current_time - start_time

            # Calculates the rate of the interval in megabites per second
            interval_rate = (interval_sent_bytes * 8e-6) / input_interval_time 

            # Formating the values of the bytes in either bytes, kilobytes or megabytes
            interval_sent_bytes_format = format_values(interval_sent_bytes, input_format)

            # Defining the data of the table
            data = [[f"{client_ip_address}:{client_port_number}", f"{elapsed_time - input_interval_time:.1f} - {elapsed_time:.1f}", f"{interval_sent_bytes_format:.2f} {input_format}", f"{interval_rate:.2f} Mbps"],]

            # Printing the values in a table format
            for row in data:
                print_table(row)

            # Reset the values of bytes
            interval_sent_bytes = 0 

    # Send a message to the server to indicate that the transfer is complete
    client_socket.sendall("BYE".encode())

    # Defining the response message from the server
    response = client_socket.recv(1024).decode()

    # If the client receives a response that consist of 'ACK: BYE'
    if response == "ACK: BYE":

        # Ending time at when the client has received the acknowledgment
        end_time = time.time()

        # Duration of the transfer
        duration = end_time - start_time

        # Formating the values of the bytes in either bytes, kilobytes or megabytes
        total_sent_bytes_format = format_values(total_sent_bytes, input_format)

        # Calculates the rate in megabites per second
        rate = (total_sent_bytes * 8e-6) / duration

        # Defining the data of the table
        data = [[f"{client_ip_address}:{client_port_number}", f"0.0 - {duration:.1f}", f"{total_sent_bytes_format:.2f} {input_format}", f"{rate:.2f} Mbps"],]
        
        # Printing the values in a table format
        for row in data:
            print_table(row)

    # Close the client socket
    client_socket.close()

# This function connects the client to the server
def start_client(args):
    # Defining the IP address using the '-I' flag
    ip_address = args.serverip

    # Defining the port number using the '-p' flag
    port_number = args.port

    # Defining the specified duration using the '-t' flag
    input_time = args.time

    # Defining the specified format to be shown using the '-f' flag
    input_format = args.format

    # Defining the interval in seconds using the '-i' flag
    input_interval_time = args.interval

    # Defining the amount of bytes to be sent using the '-n' flag
    input_num = args.num

    # Defining the amount of parallel connections using the '-P' flag
    input_parallel = args.parallel
        
    # Defining the headers of the table 
    headers = ["ID", "Interval", "Transfer", "Bandwidth"]

    # Defining the list to be used when we append parallel connections
    connection_list = []

    # Iterate for each parallel connection
    for i in range(input_parallel):
        # Create a TCP socket
        client_socket = socket(AF_INET, SOCK_STREAM)

        # Connect to the server
        client_socket.connect((ip_address, port_number))

        # Prints out a confirmation that the client is connected to the server
        print(f"Client connected with server {ip_address}:{port_number}")
    
        # Gets the client's IP address and port number
        client_ip_address, client_port_number = client_socket.getsockname()

        # If this is the last connection, print the headers of the table
        if i == input_parallel - 1:
            print_table(headers)

        # Creates a new thread to handle the connection
        thread = threading.Thread(target=handle_client, args=(client_socket, client_ip_address, client_port_number, input_time, input_format, input_interval_time, input_num))
        
        # Appends the thread
        connection_list.append(thread)

        # Initiates the thread
        thread.start()

    # Awaiting for all the threads to finish
    for j in connection_list:
        j.join()

# This is the main entry point of the program
if __name__ == '__main__':
    # Parses the command line arguments using the argparse module
    args = parse_args()
    
    # If the server flag is present, start the server
    if args.server:
        start_server(args)

    # If the client flag is present, start the client
    elif args.client:
        start_client(args)