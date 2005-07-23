from wrapper import WindowWrapper


class WindowBidding(WindowWrapper):

	window_name = 'window_bidding'


	def new(self):
		self.call_tree_model = gtk.TreeStore(str, str, str, str)
		self.call_tree.set_model(self.call_tree_model)
		self.model_iter = self.call_tree_model.insert_after(parent = None, sibling = None)
		self.column = 0
		columnNames = ['North', 'East', 'South', 'West']
		i = 0
		for columnName in columnNames:
			renderer = gtk.CellRendererText()
			column = gtk.TreeViewColumn(columnName, renderer, text = i)
			self.call_tree.append_column(column)
			i+=1
		for x in range(23):
			self.insert_cell(x)


	def insert_cell(self, data):
		if self.column == 4:
			self.column = 0
			self.model_iter = self.call_tree_model.insert_after(parent = None, sibling = self.model_iter)
		self.call_tree_model.set_value(self.model_iter, self.column, value = data)
		self.column += 1
