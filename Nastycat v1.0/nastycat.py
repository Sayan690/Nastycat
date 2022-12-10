#!/usr/bin/python3

import os
import sys
import argparse
import termcolor
import threading
import subprocess

from pwn import *

class Netcat:
	def __init__(self):
		self.isatty = not os.isatty(sys.stdin.fileno())
		self.args()
		self.run()

	def args(self):
		parser = argparse.ArgumentParser(description='Netcat tool.', formatter_class=argparse.RawDescriptionHelpFormatter, add_help=False, epilog='''Example:
  ./%(prog)s 192.168.3.41 -p 4444 # connect to server at port 4444.
  ./%(prog)s -lp 4444 # listen on port 4444 for possible reverse connection.
  ./%(prog)s -le "cat /etc/passwd" # executes the command and sends output to client.
  ./%(prog)s -lu output.txt # receive client data and save it in specified file.''')

		parser._positionals.title = 'positionals'
		parser._optionals.title = 'optionals'

		parser.add_argument('-h', '--help', action='help', help='Shows the help message.')
		parser.add_argument(metavar='target', dest='target', help='Target host. (default - 0.0.0.0)', nargs='?', default='0.0.0.0')
		parser.add_argument('-p', '--port', type=int, metavar='', help='Target port. (default - 4444)', default=4444)
		parser.add_argument('-l', '--listen', action='store_true', help='Invokes listening mode.')
		parser.add_argument('-e', '--execute', help='Execute a command and sends output to client.', metavar='')
		parser.add_argument('-u', '--upload', help='Gets the client data and saves in specified file.')

		self.args = parser.parse_args()

		if self.args.port > 65535:
			sys.stderr.write('[!] Exception: Wrong port.\n')
			sys.exit(1)

	def run(self):
		if self.args.listen:
			self.listen()

		else:
			try:
				self.remote()
			except (KeyboardInterrupt, IndexError):
				sys.exit(0)

	def get_headers(self, io):
		headers = io.recv().decode()
		if headers:
			print(headers.replace('\r', ''), end='')

	def getinp(self, io):
		while True:
			if self.isatty:
				self.cmd = sys.stdin.read().encode()

			else:
				self.cmd = input(termcolor.colored('$ ' , 'red')).encode()

			io.send(self.cmd)

	def getoutput(self, io):
		while True:
			try:
				if not self.isatty:
					out = io.recv().decode().replace('\r', '')
				else:
					out = io.recv().replace(b'\r', b'')

				if out:
					print(out, end='')
				if self.isatty:
					print()
			except EOFError:
				raise SystemExit
				break
				sys.exit()

	def remote(self):
		io = remote(self.args.target, self.args.port, timeout=10)
		if self.args.execute:
			out = subprocess.getoutput(self.args.execute)
			io.send(out.encode())
		
		try:
			thread = threading.Thread(target=self.getoutput, args=(io,), daemon=True)
			thread.start()
			if not self.args.upload:
				self.getinp(io)
			else:
				try:
					f = open(self.args.upload, 'rb')
					data = f.read()
					io.send(data)
					print(io.recv(timeout=5).decode())
				except FileNotFoundError:
					raise SystemExit
					error('File not found.')

				except:
					io.close()
					sys.exit(0)

		except (KeyboardInterrupt, SystemExit):
			sys.exit(0)

	def listen(self):
		if self.args.execute:
			out = subprocess.getoutput(self.args.execute)
			while True:
				try:
					io = listen(self.args.port)
					io.wait_for_connection()
					io.send(out.encode())
					io.close()
				except KeyboardInterrupt:
					break
					sys.exit(0)

		elif self.args.upload:
			io = listen(self.args.port)
			io.wait_for_connection()
			out = io.recv(timeout=5).replace(b'\r', b'')
			io.sendline(b'File saved.')
			try:
				with open(self.args.upload, 'wb') as f:
					f.write(out)
					f.close()

			except PermissionError:
				error('Permission denied.')

		else:
			try:
				io = listen(self.args.port)
				io.wait_for_connection()
				io.interactive()
			except KeyboardInterrupt:
				sys.exit(0)

if __name__ == '__main__':
	try:
		Netcat()

	except exception.PwnlibException as e:
		pass
	except EOFError:
		sys.exit()