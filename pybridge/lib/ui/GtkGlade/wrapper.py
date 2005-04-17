import gtk, gtk.glade

glade_file = "lib/ui/GtkGlade/pybridge.glade"

class WindowWrapper(dict):
	def __init__(self):
		self.glade = gtk.glade.XML(glade_file, self.window_name, None)
		self.window = self.glade.get_widget(self.window_name)
		self.signal_autoconnect()
		self.new()
	
	def __getattr__(self, name):
		"""Allows referencing of Glade widgets as class attributes."""
		if name in self:
			return self[name]
		else:
			widget = self.glade.get_widget(name)
			if widget != None:
				self[name] = widget  # Saves time later.
				return widget
			else:
				raise AttributeError, name
	
	def __setattr__(self, name, value):
		self[name] = value
	
	def signal_autoconnect(self):
		"""Sets up class methods as named signal handlers."""
		signals = {}
		for attribute_name in dir(self):
			attribute = getattr(self, attribute_name)
			if callable(attribute):
				signals[attribute_name] = attribute
		self.glade.signal_autoconnect(signals)

	def new(self):
		pass

	def run(self):
		gtk.main()
