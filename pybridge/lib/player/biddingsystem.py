from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class BiddingSystem:
	"""An interface between XML bidding system files and player classes."""
	
	def __init__(self, filePath):
		"""Run the XML parser and load in bidding system data."""
		parser = make_parser()
		systemHandler = BiddingSystemHandler()
		parser.setContentHandler(systemHandler)
		parser.parse(filePath)
		self.title = systemHandler.title
		self.description = systemHandler.description
		self.definitions = systemHandler.definitions
	
class BiddingSystemHandler(ContentHandler):
	"""XML Bidding System handler class.
	
	Note that this class does NOT validate the XML data as being conformant
	to the PyBridge bidding system specification; any error, therefore,
	will produce weird (and wonderful) results.
	"""

	title = ''
	description = ''
	_elementStack = []     # Names of current elements.

	definitions = {}       # Tree structure of nested dictionaries and lists.
	_definitionStack = []  # Pointers to track current position in definitions.
	
	def startElement(self, name, attrs):
		self._elementStack.append(name)  # Push name to stack.
		if self._definitionStack:
			element, key = None, None
			# Determine the content and key.
			if name in ['context', 'rule']:
				element, key = {}, attrs.getValue('name')
			elif name in ['own-calls', 'opponent-calls', 'implies', 'responses']:
				element, key = [], name
			elif name in ['call', 'register']:
				element = {}
				for attrName in attrs.getNames():
					value = attrs.getValue(attrName)
					if attrName in ['level', 'value', 'value-min', 'value-max']:
						value = int(value)
					element[attrName] = value
			elif name == 'scope':
				element = attrs.getValue('name')
			# Insert element in definitions by means of its parent...
			parent = self._definitionStack[-1]
			if key: parent[key] = element
			else: parent.append(element)
			# ... and add to the element stack.
			self._definitionStack.append(element)
		
		# Nasty "kickstart definitions" hack.
		if name == 'definitions':
			self._definitionStack.append(self.definitions)

	def endElement(self, name):
		# Pop definition pointer from the stack if necessary.
		if self._definitionStack:
			self._definitionStack.pop()
		self._elementStack.pop()
	
	def characters(self, content):
		# Save character data for title and description.
		if self._elementStack[-1] == 'title':
			self.title = content
		elif self._elementStack[-1] == 'description':
			self.description = content
