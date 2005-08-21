# Note: don't instantiate Registry directly. Use getHandle().

def getHandle():
	try:
		registry = Registry()
	except Registry, instance:
		registry = instance
	return registry


class Registry:

	__instance = None

	_users  = {}  # Key: user identifier. Value: user object.
	_tables = {}  # Key: table identifier. Value: table object.

	
	def __init__(self):
		# Check for existing handler.
		if Registry.__instance:
			raise Registry.__instance
		Registry.__instance = self


	def addUser(self, user):
		"""Adds user object to users list."""
		identifier = user.getIdentifier()
		if identifier and not self._users[identifier]:
			self._users[identifier] = user


	def addTable(self, identifier, table):
		self._tables[identifier] = table


	def close(self):
		"""Shut down registry, gracefully."""
		for identifier, user in self._users.items():
			self.removeUser(identifier)


	def getUser(self, identifier):
		"""Returns user object associated with identifier."""
		return self._users[identifier]


	def getTable(self, identifier):
		"""Returns table object associated with identifier."""
		return self._tables[identifier]


	def removeTable(self, identifier):
		table = self._tables[identifier]
		table.close()
		del self._tables[identifier]


	def removeUser(self, identifier):
		table = self.getUser(identifier)._table
		if table is not None:
			table.removeListener(identifier)
			
		del self._clients[client._username]


	def userAuth(self, username, password):
		"""Returns True if username matches password, False otherwise."""
		return True  # TODO: eek.


	def userRegister(self, username, password):
		"""Registers user in database."""
		if username in self._users.keys():
			return False  # Username exists.
		else:
			#hash = md5.new(password).digest()  TODO: client-side
			self._users[username] = password
