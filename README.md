# Simpleperf
Simpleperf is a command-line tool for measuring network throughput between a client and a server. The tool allows users to run both server and client modes and can measure data transfer rates over a specified time interval.

## Requirements
* Python 3.6 or higher

## Installation
To install Simpleperf, you can download the script directly from GitHub or clone the repository to your local machine using the following command:

```
git clone https://github.com/s186969/DATA2410-Portfolio-1.git
```

Once the repository has been cloned, you can run the script using Python 3:

```
python3 simpleperf.py <arguments>
```

## Usage
Simpleperf accepts several command-line arguments, which are listed below:

```
-s, --server      Enables server mode
-c, --client      Enables client mode
-b, --bind        Selects the IP address of the server's interface
-I, --serverip    Selects the IP address of server
-p, --port        Selects port number
-f, --format      Format of the output data (B/KB/MB)
-t, --time        Selects a duration in seconds for which data should be generated
-i, --interval    Prints statistics per specified interval in seconds
-n, --num         Transfers number of bytes (B/KB/MB)
-P, --parallel    Creates parallel connections to connect to the server (1-5)
```

To run the tool in server mode, use the -s flag:
```
python3 simpleperf.py -s -b <ip_address> -p <port_number> -f <byte_format>
```

To run the tool in client mode, use the -c flag:
```
python3 simpleperf.py -c -I <ip_address> -p <port_number> -f <byte_format> -t <seconds>
```

For a full list of available options, use the -h flag:
```
python3 simpleperf.py -h
```

## Examples
To run the server on the local machine and listening on port number 8080, use the following command:
```
python3 simpleperf.py -s 127.0.0.1 -p 8080
```

To connect the client to the server at IP address 127.0.0.1 with port number 8080 and transfer data for 60 seconds while printing the output in KB, use the following command:

```
python3 simpleperf.py -c -I 127.0.0.1 -p 8080 -t 60 -f KB
```

To connect the client with above mentioned server and print the data in intervals of 5 seconds while the data transfers for 60 seconds, use the following command:
```
python3 simpleperf.py -c -I 127.0.0.1 -p 8080 -t 60 -i 5
```

To connect the client with above mentioned server and transfering 2000 MB data in chucks of 1000 bytes, use the following command:
```
python3 simpleperf.py -c -I 127.0.0.1 -p 8080 -n 2000MB
```

To connect the client with above mentioned server with three connections in parallel, use the following command:
```
python3 simpleperf.py -c -I 127.0.0.1 -p 8080 -P 3
```

To connect the client with above mentioned server with two connections in parallel, transfering 5000MB data while printing the data in a interval of 10 seconds in a format of B, use the following command:
```
python3 simpleperf.py -c -I 127.0.0.1 -p 8080 -f B -i 10 -n 5000MB -P 2
```
