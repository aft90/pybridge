#!/usr/bin/env python

# simple-glade-codegen.py
# A code generator that uses pygtk, glade and SimpleGladeApp.py
# Copyright (C) 2004 Sandino Flores Moreno

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

import sys, os, re, codecs
import tokenize, shutil, time
import xml.sax
from xml.sax._exceptions import SAXParseException

header_format = """\
#!/usr/bin/env python
# -*- coding: UTF8 -*-

# Python module %(module)s.py
# Autogenerated from %(glade)s
# Generated on %(date)s

# Warning: Do not delete or modify comments related to context
# They are required to keep user's code

import os, gtk
from SimpleGladeApp import SimpleGladeApp

glade_dir = ""

# Put your modules and data here

# From here through main() codegen inserts/updates a class for
# every top-level widget in the .glade file.

"""

class_format = """\
class %(class)s(SimpleGladeApp):
%(t)sdef __init__(self, glade_path="%(glade)s", root="%(root)s", domain=None):
%(t)s%(t)sglade_path = os.path.join(glade_dir, glade_path)
%(t)s%(t)sSimpleGladeApp.__init__(self, glade_path, root, domain)

%(t)sdef new(self):
%(t)s%(t)s#context %(class)s.new {
%(t)s%(t)sprint "A new %(class)s has been created"
%(t)s%(t)s#context %(class)s.new }

%(t)s#context %(class)s custom methods {
%(t)s#--- Write your own methods here ---#
%(t)s#context %(class)s custom methods }

"""

callback_format = """\
%(t)sdef %(handler)s(self, widget, *args):
%(t)s%(t)s#context %(class)s.%(handler)s {
%(t)s%(t)sprint "%(handler)s called with self.%%s" %% widget.get_name()
%(t)s%(t)s#context %(class)s.%(handler)s }

"""

creation_format = """\
%(t)sdef %(handler)s(self, str1, str2, int1, int2):
%(t)s%(t)s#context %(class)s.%(handler)s {
%(t)s%(t)swidget = gtk.Label("%(handler)s")
%(t)s%(t)swidget.show_all()
%(t)s%(t)sreturn widget
%(t)s%(t)s#context %(class)s.%(handler)s }

"""

main_format = """\
def main():
"""

instance_format = """\
%(t)s%(root)s = %(class)s()
"""
run_format = """\

%(t)s%(root)s.run()

if __name__ == "__main__":
%(t)smain()
"""

class NotGladeDocumentException(SAXParseException):
	def __init__(self, glade_writer):
		strerror = "Not a glade-2 document"
		SAXParseException.__init__(self, strerror, None, glade_writer.sax_parser)

class SimpleGladeCodeWriter(xml.sax.handler.ContentHandler):
	def __init__(self, glade_file):
		self.indent = "\t"
		self.code = ""
		self.roots_list = []
		self.widgets_stack = []
		self.creation_functions = []
		self.callbacks = []
		self.parent_is_creation_function = False
		self.glade_file = glade_file
		self.data = {}
		self.input_dir, self.input_file = os.path.split(glade_file)
		base = os.path.splitext(self.input_file)[0]
		module = self.normalize_symbol(base)
		self.output_file = os.path.join(self.input_dir, module) + ".py"
		self.sax_parser = xml.sax.make_parser()
		self.sax_parser.setFeature(xml.sax.handler.feature_external_ges, False)
		self.sax_parser.setContentHandler(self)
		self.data["glade"] = self.input_file
		self.data["module"] = module
		self.data["date"] = time.asctime()

	def normalize_symbol(self, base):
		return "_".join( re.findall(tokenize.Name, base) )

	def capitalize_symbol(self, base):
		ClassName = "[a-zA-Z0-9]+"
		base = self.normalize_symbol(base)
		capitalize_map = lambda s : s[0].upper() + s[1:]
		return "".join( map(capitalize_map, re.findall(ClassName, base)) )

	def uncapitalize_symbol(self, base):
		InstanceName = "([a-z])([A-Z])"
		action = lambda m: "%s_%s" % ( m.groups()[0], m.groups()[1].lower() )
		base = self.normalize_symbol(base)
		base = base[0].lower() + base[1:]
		return re.sub(InstanceName, action, base)	

	def startElement(self, name, attrs):
		if name == "widget":
			widget_id = attrs.get("id")
			widget_class = attrs.get("class")
			if not widget_id or not widget_class:
				raise NotGladeDocumentException(self)
			if not self.widgets_stack:
				self.creation_functions = []
				self.callbacks = []
				class_name = self.capitalize_symbol(widget_id)
				self.data["class"] = class_name
				self.data["root"] = widget_id
				self.roots_list.append(widget_id)
				self.code += class_format % self.data
			self.widgets_stack.append(widget_id)
		elif name == "signal":
			if not self.widgets_stack:
				raise NotGladeDocumentException(self)
			widget = self.widgets_stack[-1]
			signal_object = attrs.get("object")
			if signal_object:
				return
			handler = attrs.get("handler")
			if not handler:
				raise NotGladeDocumentException(self)
			if handler.startswith("gtk_"):
				return
			signal = attrs.get("name")
			if not signal:
				raise NotGladeDocumentException(self)
			self.data["widget"] = widget
			self.data["signal"] = signal
			self.data["handler"]= handler
			if handler not in self.callbacks:
				self.code += callback_format % self.data
				self.callbacks.append(handler)
		elif name == "property":
			if not self.widgets_stack:
				raise NotGladeDocumentException(self)
			widget = self.widgets_stack[-1]
			prop_name = attrs.get("name")
			if not prop_name:
				raise NotGladeDocumentException(self)
			if prop_name == "creation_function":
				self.parent_is_creation_function = True
				
	def characters(self, content):
		if self.parent_is_creation_function:
			if not self.widgets_stack:
				raise NotGladeDocumentException(self)
			handler = content.strip()
			if handler not in self.creation_functions:
				self.data["handler"] = handler
				self.code += creation_format % self.data
				self.creation_functions.append(handler)
	
	def endElement(self, name):
		if name == "property":
			self.parent_is_creation_function = False
		elif name == "widget":
			if not self.widgets_stack:
				raise NotGladeDocumentException(self)
			self.widgets_stack.pop()
	
	def write(self):
		self.data["t"] = self.indent
		self.code += header_format % self.data
		try:
			glade = open(self.glade_file, "r")
			self.sax_parser.parse(glade)
		except xml.sax._exceptions.SAXParseException, e:
			sys.stderr.write("Error parsing document\n")
			return None
		except IOError, e:
			sys.stderr.write("%s\n" % e.strerror)
			return None

		self.code += main_format % self.data

		for root in self.roots_list:
			self.data["class"] = self.capitalize_symbol(root)
			self.data["root"] = self.uncapitalize_symbol(root)
			self.code += instance_format % self.data

		self.data["root"] = self.uncapitalize_symbol(self.roots_list[0])
		self.code += run_format % self.data
		
		try:
			self.output = codecs.open(self.output_file, "w", "utf-8")
			self.output.write(self.code)
			self.output.close()
		except IOError, e:
			sys.stderr.write("%s\n" % e.strerror)
			return None
		return self.output_file
		
def usage():
	program = sys.argv[0]
	print """\
Write a simple python file from a glade file.
Usage: %s <file.glade>
""" % program

def which(program):
	if sys.platform.startswith("win"):
		exe_ext = ".exe"
	else:
		exe_ext = ""
	path_list =  os.environ["PATH"].split(os.pathsep)
	for path in path_list:
		program_path = os.path.join(path, program) + exe_ext
		if os.path.isfile(program_path):
			return program_path
	return None

def check_for_programs():
	packages = {"diff" : "diffutils", "patch" : "patch"}
	for package in packages.keys():
		if not which(package):
			sys.stderr.write("Required program %s could not be found\n" % package)
			sys.stderr.write("Is the package %s installed?\n" % packages[package])
			if sys.platform.startswith("win"):
				sys.stderr.write("Download it from http://gnuwin32.sourceforge.net/packages.html\n")
			sys.stderr.write("Also, be sure it is in the PATH\n")
			return False
	return True
			
def main():
	if not check_for_programs():
		return -1
	if len(sys.argv) == 2:
		code_writer = SimpleGladeCodeWriter( sys.argv[1] )
		glade_file = code_writer.glade_file
		output_file = code_writer.output_file
		output_file_orig = output_file + ".orig"
		output_file_bak = output_file + ".bak"
		short_f = os.path.split(output_file)[1]
		short_f_orig = short_f + ".orig"
		short_f_bak = short_f + ".bak"
		helper_module = os.path.join(code_writer.input_dir,SimpleGladeApp_py)
		custom_diff = "custom.diff"
		
		exists_output_file = os.path.exists(output_file)
		exists_output_file_orig = os.path.exists(output_file_orig)
		if not exists_output_file_orig and exists_output_file:
			sys.stderr.write('File "%s" exists\n' % short_f)
			sys.stderr.write('but "%s" does not.\n' % short_f_orig)
			sys.stderr.write("That means your custom code would be overwritten.\n")
			sys.stderr.write('Please manually remove "%s"\n' % short_f)
			sys.stderr.write("from this directory.\n")
			sys.stderr.write("Anyway, I\'ll create a backup for you in\n")
			sys.stderr.write('"%s"\n' % short_f_bak)
			shutil.copy(output_file, output_file_bak)
			return -1
		if exists_output_file_orig and exists_output_file:
			os.system("diff -U1 %s %s > %s" % (output_file_orig, output_file, custom_diff) )
			if not code_writer.write():
				os.remove(custom_diff)
				return -1
			shutil.copy(output_file, output_file_orig)
			if os.system("patch -fp0 < %s" % custom_diff):
				os.remove(custom_diff)
				return -1
			os.remove(custom_diff)
		else:
			if not code_writer.write():
				return -1
			shutil.copy(output_file, output_file_orig)
		os.chmod(output_file, 0755)
		if not os.path.isfile(helper_module):
			open(helper_module, "w").write(SimpleGladeApp_content)
		print "Wrote", output_file
		return 0
	else:
		usage()
		return -1

SimpleGladeApp_py = "SimpleGladeApp.py"

SimpleGladeApp_content = """\
# SimpleGladeApp.py
# Module that provides an object oriented abstraction to pygtk and libglade.
# Copyright (C) 2004 Sandino Flores Moreno

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

try:
	import os
	import sys
	import gtk
	import gtk.glade
except ImportError:
	print "Error importing pygtk2 and pygtk2-libglade"
	sys.exit(1)

class SimpleGladeApp(dict):
	def __init__(self, glade_filename, main_widget_name=None, domain=None):
		gtk.glade.set_custom_handler(self.custom_handler)
		if os.path.isfile(glade_filename):
			self.glade_path = glade_filename
		else:
			glade_dir = os.path.split( sys.argv[0] )[0]
			self.glade_path = os.path.join(glade_dir, glade_filename)
		self.glade = gtk.glade.XML(self.glade_path, main_widget_name, domain)
		if main_widget_name:
			self.main_widget = self.glade.get_widget(main_widget_name)
		else:
			self.main_widget = None
		self.signal_autoconnect()
		self.new()

	def signal_autoconnect(self):
		signals = {}
		for attr_name in dir(self):
			attr = getattr(self, attr_name)
			if callable(attr):
				signals[attr_name] = attr
		self.glade.signal_autoconnect(signals)

	def custom_handler(self,
			glade, function_name, widget_name,
			str1, str2, int1, int2):
		if hasattr(self, function_name):
			handler = getattr(self, function_name)
			return handler(str1, str2, int1, int2)

	def __getattr__(self, data_name):
		if data_name in self:
			data = self[data_name]
			return data
		else:
			widget = self.glade.get_widget(data_name)
			if widget != None:
				self[data_name] = widget
				return widget
			else:
				raise AttributeError, data_name

	def __setattr__(self, name, value):
		self[name] = value

	def new(self):
		pass

	def on_keyboard_interrupt(self):
		pass

	def gtk_widget_show(self, widget, *args):
		widget.show()

	def gtk_widget_hide(self, widget, *args):
		widget.hide()

	def gtk_widget_grab_focus(self, widget, *args):
		widget.grab_focus()

	def gtk_widget_destroy(self, widget, *args):
		widget.destroy()

	def gtk_window_activate_default(self, widget, *args):
		widget.activate_default()

	def gtk_true(self, *args):
		return gtk.TRUE

	def gtk_false(self, *args):
		return gtk.FALSE

	def gtk_main_quit(self, *args):
		gtk.main_quit()

	def main(self):
		gtk.main()

	def quit(self):
		gtk.main_quit()

	def run(self):
		try:
			self.main()
		except KeyboardInterrupt:
			self.on_keyboard_interrupt()
"""

if __name__ == "__main__":
	exit_code = main()
	sys.exit(exit_code)
