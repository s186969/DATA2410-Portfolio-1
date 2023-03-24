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
    parser.add_argument('-t', '--time', type = int, default = 5, help='IP address of server')

    return parser.parse_args()

def start_server(args):
    ip_address = args.bind
    port_number = args.port
    format = args.format

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
                interval =  end_time - start_time

                # Formating the values of the bytes in either Bytes, Kilobytes or Megabytes
                if format == "B":
                    total_received_bytes_format = total_received_bytes
                elif format == "KB":
                    total_received_bytes_format = total_received_bytes / 1000
                else:
                    total_received_bytes_format = total_received_bytes / 1000000

                # Calculate the rate of incoming trafic in megabites per second
                rate = (total_received_bytes * 8e-6) / interval

                # Printing the data in server
                headers = ["ID", "Interval", "Received", "Rate"]
                data = [[f"{client_address[0]}:{client_address[1]}", f"0.0 - {interval:.1f}", f"{total_received_bytes_format:.2f} {format}", f"{rate:.2f} Mbps"],]
                
                format_row = "{:>20}" * (len(headers))
                print(format_row.format(*headers))
                for row in data:
                    print(format_row.format(*row))

def start_client(args):
    ip_address = args.serverip
    port_number = args.port
    duration = args.time
    format = args.format

    # Create a TCP socket
    with socket(AF_INET, SOCK_STREAM) as client_socket:

        # Connect to the server
        client_socket.connect((ip_address, port_number))
        print(f"Client connected with server {ip_address}:{port_number}")

        # Starting the timer
        start_time = time.time()

        # Starting value of sent Bytes
        total_sent_bytes = 0

        bytes = b"0" * 1000

        # Transfer the Bytes
        while(time.time() - start_time) < duration:
            sending_bytes = client_socket.send(bytes)

            # Updates the vaules of sent Bytes
            total_sent_bytes += sending_bytes

        # Send a message to the server to indicate that the transfer is complete
        client_socket.sendall("BYE".encode())

        response = client_socket.recv(1024).decode()
        if response == "ACK: BYE":
            end_time = time.time()
            interval = end_time - start_time

             # Formating the values of the bytes in either Bytes, Kilobytes or Megabytes
            if format == "B":
                total_sent_bytes_format = total_sent_bytes
            elif format == "KB":
                total_sent_bytes_format = total_sent_bytes / 1000
            else:
                total_sent_bytes_format = total_sent_bytes / 1000000

            # Calculate the rate of incoming trafic in megabites per second
            rate = (total_sent_bytes * 8e-6) / interval

            # Printing the data in server
            headers = ["ID", "Interval", "Transfer", "Bandwidth"]
            data = [[f"{ip_address}:{port_number}", f"0.0 - {interval:.1f}", f"{total_sent_bytes_format:.2f} {format}", f"{rate:.2f} Mbps"],]
            
            format_row = "{:>20}" * (len(headers))
            print(format_row.format(*headers))
            for row in data:
                print(format_row.format(*row))

if __name__ == '__main__':
    args = parse_args()
    if args.server:
        start_server(args)
    elif args.client:
        start_client(args)
    else:
        print("Error: You must run either in server or client mode")