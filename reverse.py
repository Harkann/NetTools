"""
Use reverse DNS to query for the hostname of ALL the ipv4 on the internet.
(it may take you some time...)
"""

import socket
from multiprocessing import Pool, Process, Queue
from format import Storage, Listener

try:
	import settings_local as stg
except:
	import settings as stg

stor = Storage(stg.uri, stg.user, stg.password)
queue = Queue()
lst = Listener(queue, stor)

def reverse(ips):
	to_write = ''
	for l in range(256):
		ip_add = '{}.{}.{}.{}'.format(ips[0], ips[1], ips[2], l)
		try:
			host = socket.gethostbyaddr(ip_add)[0]
			queue.put([ip_add, host])
		except:
			pass

if __name__ == "__main__":
	ips = []
	for i in range(256):
		if i not in [0,10,127]+[x for x in range(224,240)]+[y for y in range(240,256)]:
			for j in range(256):
				for k in range(256):
					ips.append([i,j,k])
	l = Process(target=lst.start)
	l.start()
	with Pool(stg.nb_work) as p:
		p.map(reverse, ips)
	l.stop()
	l.join()