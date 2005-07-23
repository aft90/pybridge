from wrapper import WindowWrapper


class WindowRooms(WindowWrapper):

	window_name = 'window_rooms'

	def new(self):
		self.room_tree_model = gtk.TreeStore(str, str, str)
		self.room_tree.set_model(self.room_tree_model)
		self.model_iter = self.room_tree_model.insert_after(parent = None, sibling = None)

