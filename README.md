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
python3 simpleperf.py [arguments]
```

## Usage
```
-s, --server      Enables server mode
-c, --client      Enables client mode
-b, --bind        Selects the IP address of the server's interface
-I, --serverip    Selects the IP address of server
-p, --port        Selects port number
-f, --format      Format of the output data (B/KB/MB)
-t, --time        Selects a duration in seconds for which data should be generated
-i, --interval    Prints statistics per specified interval in seconds
-n, --num         Transfers number of bytes
-P, --parallel    Creates parallel connections to connect to the server
```