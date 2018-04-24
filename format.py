

class Listener():
	"""
	Listen to a queue and format the ip and hostnames
	before passing them to a storage
	"""
	self.running = False

	def __init__(self, q, storage):
		self.storage = storage
		self.q = q

	def _format_from_queue(self, ip, host):
		"""
		Format the domains to create the nodes in the storage
		"""
		h_lst = host.split('.')
		h_lst.reverse()
		for i in range(1,len(h_lst)):
			prec = h_lst[:i]
			cur = h_lst[:i+1]
			print(prec, cur)
			prec.reverse()
			cur.reverse()
			self.storage.store(['.'.join(prec), '.'.join(cur), None])
		self.storage.store([None, host, ip])

	def start(self):
		self.running = True
		print("Listener started")
		while self.running:
			try:
				item = self.q.get_nowait()
				self._format_from_queue(*item)
				print(item)
			except:
				pass
		print("Listener stopped")

	def stop(self):
		self.running = False


class Storage():
	"""
	Store the items passed by the Listener into a database
	"""
	def __init__(self, uri="bolt://localhost:7687", user="neo4j", password=""):
		try:
			import neo4j.v1
		except:
			print("Module required not found")
			exit(1)
		self.driver = neo4j.v1.GraphDatabase.driver(uri, auth=(user, password))


	def store(self, lst):
		with self.driver.session() as tx:
			if lst[0] is not None:
				tx.run('MERGE (:Domain {name: $name})', name=lst[0])
				tx.run('MERGE (:Domain {name: $name})', name=lst[1])
				tx.run('MATCH (a:Domain) WHERE a.name = {name_a} \
					    MATCH (b:Domain) WHERE b.name = {name_b} \
					    MERGE (b)-[:SUBDOMAIN]->(a)', name_a=lst[0], name_b=lst[1])
			else:
				tx.run('MERGE (:Domain {name: $name})', name=lst[1])
				tx.run('MATCH (a:Domain) WHERE a.name = {name} SET a.ip = {ip}', name=lst[1], ip=lst[2])