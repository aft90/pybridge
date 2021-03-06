# PyBridge -- online contract bridge made easy.
# Copyright (C) 2004-2007 PyBridge Project.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


from gi.repository import Gtk

from pybridge.games.bridge.result import RubberResult
from pybridge.games.bridge.symbols import Direction

from pybridge.ui.eventhandler import SimpleEventHandler
import pybridge.ui.vocabulary as voc


class ScoreSheet(Gtk.TreeView):
    """A score sheet widget, which presents GameResult information."""

    def __init__(self):
        super().__init__()
        self.set_rules_hint(True)

        self.store = Gtk.ListStore(str, str, str, str, str)
        self.set_model(self.store)

        renderer = Gtk.CellRendererText()
        for index, title in enumerate([_('Board'), _('Contract'), _('Made'), _('N/S'), _('E/W')]):
            column = Gtk.TreeViewColumn(title, renderer, markup=index)
            self.append_column(column)

        self.totalsRow = self.store.append(('Total','','','0','0'))
        self.totalNS = 0
        self.totalEW = 0


    def add_result(self, result):
        if isinstance(result, RubberResult):
            # Rubber results are split into 'above' and 'below' scores.
            score = sum(result.score)
        else:
            score = result.score

        if result.contract is None:  # Bidding passed out.
            row = (str(result.board['num']), _('Passed out'), '-', '', '')

        else:
            absScore = abs(score)
            if result.contract.declarer in (Direction.North, Direction.South) and score > 0 \
            or result.contract.declarer in (Direction.East, Direction.West) and score < 0:
                scoreNS, scoreEW = str(absScore), ''
                self.totalNS += absScore
            else:
                scoreNS, scoreEW = '', str(absScore)
                self.totalEW += absScore

            row = (str(result.board['num']), voc.render_contract(result.contract),
                   str(result.tricksMade), scoreNS, scoreEW)

        self.store.remove(self.totalsRow)
        self.store.append(row)
        self.totalsRow = self.store.append(('Total','','',str(self.totalNS),str(self.totalEW)))


class RubberScoreSheet(Gtk.TreeView):
    """A score sheet widget, which presents a Rubber object."""


    def __init__(self):
        super().__init__()
        self.set_rules_hint(True)
        self.set_row_separator_func(self._row_separator)

        # Set bool field in a row to display as separator.
        self.store = Gtk.ListStore(str, str, bool)
        self.set_model(self.store)

        renderer = Gtk.CellRendererText()
        for index, title in enumerate([_('N/S'), _('E/W')]):
            column = Gtk.TreeViewColumn(title, renderer, markup=index)
            self.append_column(column)


    def set_rubber(self, rubber):
        self.store.clear()
        self.store.append(['', '', True])  # The initial dividing line.

        for _ in rubber.games:
            #aboveiters, belowiters = [], []
            for result in rubber:
                above, below = result.score
                if result.contract.declarer in (Direction.North, Direction.South) and below > 0 \
                or result.contract.declarer in (Direction.East, Direction.West) and above < 0:
                    self.store.prepend([str(above), '', False])
                    self.store.append([str(below), '', False])
                else:
                    self.store.prepend(['', str(above), False])
                    self.store.append(['', str(below), False])


    def _row_separator(self, model, iter):
        return model.get_value(iter, 2)




class WindowScoreSheet:
    """"""


    def __init__(self, parent=None):
        self.window = Gtk.Window()
        if parent:
            self.set_transient_for(parent.window)
        self.window.set_title(_('Score Sheet'))
        #self.window.connect('delete_event', self.on_delete_event)

        self.sw = Gtk.ScrolledWindow()
        self.sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        self.sw.set_size_request(-1, 150)
        self.window.add(self.sw)

        self.eventHandler = SimpleEventHandler(self)
        self.table = None

        self.window.show_all()


    def tearDown(self):
        self.table.game.detach(self.eventHandler)
        self.table = None  # Dereference table.


    def setTable(self, table):
        self.table = table
        self.table.game.attach(self.eventHandler)

        if hasattr(self.table.game, 'rubbers'):
            self.scoresheet = RubberScoreSheet()
            if self.table.game.rubbers:
                rubber = self.table.game.rubbers[-1]
                self.scoresheet.set_rubber(rubber)

        else:  # Duplicate-style list of results.
            self.scoresheet = ScoreSheet()
            for result in self.table.game.results:
                self.scoresheet.add_result(result)

        self.sw.add(self.scoresheet)
        self.scoresheet.show()


    def update(self):
        if self.table.game.results and not self.table.game.inProgress():
            if isinstance(self.scoresheet, RubberScoreSheet):
                rubber = self.table.game.rubbers[-1]
                self.scoresheet.set_rubber(rubber)
            else:
                result = self.table.game.results[-1]
                self.scoresheet.add_result(result)


    def event_makeCall(self, call, position):
        self.update()


    def event_playCard(self, card, position):
        self.update()

