#!/usr/bin/python3

__author__ = "Ashwin Nanjappa, Abdul Arfan, Zhangxiao, Krayon";
__credits__ = ["Ashwin Nanjappa", "Abdul Arfan", "Zhangxiao", "Krayon"];
__license__ = "Apache 2.0";
__version__ = "0.0.5";
__maintainer__ = "Krayon";
__email__ = "krayon.git@qdnx.org";

# GUI viewer to view JSON data as tree.
# Ubuntu packages needed:
# python3-pyqt5

# Std
import argparse;
import collections;
import json;
import sys;
import fileinput;
import os;

# External
from PyQt5           import QtCore;
from PyQt5           import QtGui;
from PyQt5           import QtWidgets;
from PyQt5.QtWidgets import QFileDialog, QAction;

win_title = "JSONGV (JSON GUI Viewer) v%s" % (__version__);

class TextToTreeItem: #{

    def __init__(self): #{
        self.text_list = [];
        self.titem_list = [];
    #}

    def append(self, text_list, titem): #{
        for text in text_list: #{
            self.text_list.append(text);
            self.titem_list.append(titem);
        #}
    #}

    # Return model indices that match string
    def find(self, find_str): #{
        titem_list = [];
        for i, s in enumerate(self.text_list): #{
            if find_str in s: #{
                titem_list.append(self.titem_list[i]);
            #}
        #}

        return titem_list;
    #}
#}

class JsonView(QtWidgets.QWidget): #{

    def __init__(self, jdata, caption=''): #{
        super(JsonView, self).__init__();

        self.find_box = None;
        self.find_result = None;
        self.tree_widget = None;
        self.text_to_titem = TextToTreeItem();
        self.find_str = "";
        self.found_titem_list = [];
        self.found_idx = 0;


        # Find UI
        find_layout = self.make_find_ui();

        # Tree
        self.tree_widget = QtWidgets.QTreeWidget();
        self.tree_widget.setHeaderLabels(["Key", "Value"]);
        #KRAYON:Allow Resize#self.tree_widget.header().setSectionResizeMode(QtWidgets.QHeaderView.Stretch);

        self.tree_widget.itemDoubleClicked.connect(self.double_clicked);

        root_item = QtWidgets.QTreeWidgetItem(["Root"]);
        self.recurse_jdata(jdata, root_item);
        self.tree_widget.addTopLevelItem(root_item);

        # Add table to layout
        layout = QtWidgets.QHBoxLayout();
        layout.addWidget(self.tree_widget);

        # Group box
        gbox = QtWidgets.QGroupBox(caption);
        gbox.setLayout(layout);

        layout2 = QtWidgets.QVBoxLayout();
        layout2.addLayout(find_layout);
        layout2.addWidget(gbox);

        self.setLayout(layout2);
    #}

    def make_find_ui(self): #{
        # Text box
        self.find_box = QtWidgets.QLineEdit();
        self.find_box.returnPressed.connect(self.find_button_clicked);

        # Find result
        self.find_result = QtWidgets.QLabel('');
        self.find_result.setStyleSheet('color: default; font-style: italic;');

        # Find Button
        find_button = QtWidgets.QPushButton("Find");
        find_button.clicked.connect(self.find_button_clicked);

        layout = QtWidgets.QHBoxLayout();
        layout.addWidget(self.find_box);
        layout.addWidget(find_button);

        layout2 = QtWidgets.QVBoxLayout();
        layout2.addLayout(layout);
        layout2.addWidget(self.find_result);

        return layout2;
    #}

    def find_button_clicked(self): #{
        find_str = self.find_box.text();

        # Very common for user to click Find on empty string
        if find_str == "": #{
            self.find_result.setText('');
            return;
        #}

        self.find_result.setStyleSheet('color: green; font-style: italic;');

        # New search string
        if find_str != self.find_str: #{
            self.found_idx = -1;
            self.find_str = find_str;
            self.found_titem_list = self.text_to_titem.find(self.find_str);
            self.find_result.setStyleSheet('color: green; font-style: italic; font-weight: bold;');
        #}

        if len(self.found_titem_list) <= 0: #{
            # Not found
            self.find_result.setText('No results found');
            self.find_result.setStyleSheet('color: red; font-style: italic; font-weight: bold;');
            return;
        #}

        # String is found
        matches = len(self.found_titem_list);
        self.found_idx += 1;
        if (self.found_idx >= matches): #{
            # Wrap around
            self.found_idx = 0;
            self.find_result.setStyleSheet('color: orange; font-style: italic;');
        #}

        self.find_result.setText("%d results found, result: %d" % ( matches, self.found_idx+1 ));

        if (self.found_idx >= 0): #{
            self.tree_widget.setCurrentItem(self.found_titem_list[self.found_idx]);
        #}
    #}

    def double_clicked(self, item, col): #{
        global qt_app;

        if (not item): return;

        # If not shifted, and item is a container, do nothing
        if (
            not (qt_app.keyboardModifiers() & QtCore.Qt.ShiftModifier)
            and item.childCount() > 0
        ): #{
            return;
        #}

        self.find_box.setText(item.text(col));
        self.find_button_clicked();
    #}

    def recurse_jdata(self, jdata, tree_widget): #{
        if isinstance(jdata, dict): #{
            for key, val in jdata.items(): #{
                self.tree_add_row(key, val, tree_widget);
            #}
        elif isinstance(jdata, list): #}{
            for i, val in enumerate(jdata): #{
                key = str(i);
                self.tree_add_row(key, val, tree_widget);
            #}
        else: #}{
            print("This should never be reached!");
        #}
    #}

    def tree_add_row(self, key, val, tree_widget): #{
        text_list = [];

        if isinstance(val, dict) or isinstance(val, list): #{
            text_list.append(key);
            row_item = QtWidgets.QTreeWidgetItem([key]);
            self.recurse_jdata(val, row_item);
        else: #}{
            text_list.append(key);
            text_list.append(str(val));
            row_item = QtWidgets.QTreeWidgetItem([key, str(val)]);
        #}

        tree_widget.addChild(row_item);
        self.text_to_titem.append(text_list, row_item);
    #}
#}

class JsonViewer(QtWidgets.QMainWindow): #{
    json_view = None;
    cwd = os.getcwd();
    ftype = "JSON Files (*.json)";

    def __init__(self, fpath, fdata): #{
        super(JsonViewer, self).__init__();

        if (fpath == ''): #{
            if (fdata == ''): #{
                # No file loaded
                fpath='';
                fdata='{}';
            else: #}{
                # Data from stdin
                fpath='stdin (Standard In)';
            #}

            jdata = json.loads(fdata, object_pairs_hook=collections.OrderedDict);
            self.json_view = JsonView(jdata, fpath);
        else: #}{
            self.loadFile(fpath);
        #}

        openaction = QAction(QtGui.QIcon.fromTheme('document-open'), '&Open...', self);
        openaction.triggered.connect(self.menuFileOpen)
        openaction.setShortcut(QtGui.QKeySequence.Open);

        exitaction = QAction(QtGui.QIcon.fromTheme('application-exit'), 'E&xit', self);
        exitaction.triggered.connect(self.menuFileExit)
        exitaction.setShortcuts([QtGui.QKeySequence.Quit, QtCore.Qt.Key_Escape]);

        menubar = self.menuBar();

        filemenu = menubar.addMenu('&File');
        filemenu.addAction(openaction);
        filemenu.addSeparator();
        filemenu.addAction(exitaction);

        self.setCentralWidget(self.json_view);
        self.setWindowTitle(win_title);
        self.show();
    #}

    def menuFileExit(self): #{
        self.close();
    #}

    def menuFileOpen(self): #{
        fpath, ftype = QFileDialog.getOpenFileName(
            self,
            "Open new JSON file...",
            self.cwd,
            "All Files (*);;JSON Files (*.json)",
            self.ftype
        );
        if (fpath != ''): #{
            self.cwd = os.path.dirname(fpath);
            self.loadFile(fpath);
        #}
        if (ftype != ''): #{
            self.ftype = ftype;
        #}
    #}

    def loadFile(self, fpath): #{
        print("fpath: %s" % (fpath));
        jfile = open(fpath);
        jdata = json.load(jfile, object_pairs_hook=collections.OrderedDict);
        print("jdata: %s" % (jdata));

        self.json_view = JsonView(jdata, fpath);
        self.setCentralWidget(self.json_view);
    #}

qt_app = None;
def main(): #{
    global qt_app;

    fpath = '';
    fdata = '';

    qt_app = QtWidgets.QApplication(sys.argv);

    if (
        (
            len(sys.argv) > 1 and
            sys.argv[1] == '--' and
            len(sys.argv) > 3
        )
        or len(sys.argv) > 2
    ): #{
        # Too many parameters
        dialog = QtWidgets.QMessageBox();
        dialog.setIcon(QtWidgets.QMessageBox.Critical);
        dialog.setWindowTitle(win_title);
        dialog.setText('ERROR: Too many parameters specified');
        dialog.setStandardButtons(QtWidgets.QMessageBox.Close);
        dialog.setDefaultButton(QtWidgets.QMessageBox.Close);
        sys.exit(dialog.buttonRole(dialog.button(dialog.exec_())));
    #}

    if (len(sys.argv) > 1): #{
        fpath = sys.argv[1];
        if (fpath == '-'): fpath = '';
        if (fpath == '--'): fpath = sys.argv[2];

        # stdin?
        if (fpath == ''): #{
            for line in fileinput.input(): #{
                fdata = fdata + line;
            #}
        #}
    #}

    json_viewer = JsonViewer(fpath, fdata);
    sys.exit(qt_app.exec_());
#}

if "__main__" == __name__: #{
    main();
#}

# vim:ts=4:tw=80:sw=4:et:ai:si
