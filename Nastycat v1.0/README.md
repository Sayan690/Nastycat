# NASTYCAT

NastyCat is a tool completely made using python for replacing NetCat utility. It uses the pwntools framework to do so.

CREDIT - The concept of this tool is from Black Hat Python by Justin Seitz.

## Features

It is very likely to original NetCat.
- It can connect to a server and deliver data on both sides.
- It can also listen for connections on a specific port.

A great feature includes execute mode.
- When specified with listening mode, it executes specified command on local system and starts a server. When someone connects to it, delivers the output.
- Else it will execute the command and send output to the server.

Also includes an upload mode.
- When connected to a server, sends the contents of the specified file to the server.
- When in listening mode, receives the client output and saves it to the specified file.

## Examples

```bash
python3 ./nastycat.py 192.168.3.41 -p 4444 # connect to server at port 4444
```
```bash
python3 ./nastycat.py -l # listens on default port 4444
```
```bash
python3 ./nastycat.py -lp 5555 # listens on port 5555
```
```bash
python3 ./nastycat.py -e "cat /etc/passwd" 192.168.3.41 -p 8080 # sends the output to port 8080
```
```bash
python3 ./nastycat.py -le "cat /etc/passwd" # listens on port 4444 and sends the output when client connects
```
```bash
python3 ./nastycat.py -lu test.txt # receive client data and save it to specified file.
```
```bash
python3 ./nastycat.py -u file.txt 192.168.3.41 -p 8080 # read the file contents and send it to the server.
```
```bash
echo -ne "GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n" | python3 ./nastycat.py google.com 80 # same old school method of invoking web requests.
```

## Setup

Run the setup file and it will automatically setup everything.

Note - This script may require root priviledges on some scenarios.

## Contribution
Any body can voluntarily contribute to this project if he/she has a better idea.
If so, please contact me on my [Insta Handle](https://www.instagram.com/sayanray385/).
