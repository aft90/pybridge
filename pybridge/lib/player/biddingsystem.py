from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class BiddingSystem:
	"""
	The bidding system class provides an interface between the XML bidding
	system descriptions and higher-order classes.
	"""
	
	def __init__(self, filePath):
		""" Run the XML parser and load in bidding system data. """
		parser = make_parser()
		systemHandler = BiddingSystemHandler()
		parser.setContentHandler(systemHandler)
		parser.parse(filePath)
		self.title = systemHandler.title
		self.description = systemHandler.description
		self.definitions = systemHandler.definitions
	
	#def interpretCall(self, call, bidding, startScope = None):
	#	""" Returns implications of call. """
	#	if call in bidding:
	#		pass
	#	else: return False

class BiddingSystemHandler(ContentHandler):

	title = ''
	description = ''
	definitions = {}
	_elementStack = []  # Keeps track of current position in definitions.
	
	def startElement(self, name, attrs):
		# Determine the key to use in definitions and element stack.
		if name in ['context', 'rule']: key = attrs.getValue('name')
		else: key = name
		if 'definitions' in self._elementStack:
			# Build dictionary for attributes of the element.
			attributes = {}
			for attrName in attrs.getNames():
				attributes[attrName] = attrs.getValue(attrName)
			# Loop through definitions to find current block.
			block = self.definitions
			for chunk in self._elementStack[2:]:
				block = block[chunk]
			# Insert element in definitions, through block.
			if key in ['ownCalls', 'opponentCalls', 'implies', 'responses']:
				# These container elements take the attributes of their children.
				block[key] = []
			elif key in ['call', 'register', 'scope']:
				# The only useful data in these elements are the attributes.
				block.append(attributes)
			else:
				# Store the attributes as a dictionary.
				block[key] = attributes
		# Push element to the current position stack.
		self._elementStack.append(key)

	def endElement(self, name):
		# Pop this element from the stack.
		self._elementStack.pop()
	
	def characters(self, content):
		# Save character data for title and description.
		if self._elementStack[-1] == 'title':
			self.title = content
		elif self._elementStack[-1] == 'description':
			self.description = content
