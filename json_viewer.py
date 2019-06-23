#!/usr/bin/python3

__author__ = "Ashwin Nanjappa, Abdul Arfan, Krayon";
__credits__ = ["Ashwin Nanjappa", "Abdul Arfan", "Krayon"];
__license__ = "Apache 2.0";
__version__ = "0.0.3";
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

# External
from PyQt5 import QtCore;
from PyQt5 import QtGui;
from PyQt5 import QtWidgets;

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

    def __init__(self, jdata, caption): #{
        super(JsonViewer, self).__init__();

        json_view = JsonView(jdata, caption);

        self.setCentralWidget(json_view);
        self.setWindowTitle("JSON Viewer");
        self.show();
    #}

    def keyPressEvent(self, e): #{
        if e.key() == QtCore.Qt.Key_Escape: #{
            self.close();
        #}
    #}

def main(): #{
    qt_app = QtWidgets.QApplication(sys.argv);

    # If no file specified, tell user gracefully
    if (len(sys.argv) <= 1): #{
        dialog = QtWidgets.QMessageBox();
        dialog.setIcon(QtWidgets.QMessageBox.Critical);
        dialog.setWindowTitle('JSON Viewer');
        dialog.setText('ERROR: No file specified');
        dialog.setStandardButtons(QtWidgets.QMessageBox.Close);
        dialog.setDefaultButton(QtWidgets.QMessageBox.Close);
        sys.exit(dialog.buttonRole(dialog.button(dialog.exec_())));
    #}

    fpath = sys.argv[1];

    # stdin?
    if (fpath == "-"): #{
        fpath = "stdin (Standard In)";
        all_line = "";
        for line in fileinput.input(): #{
            all_line = all_line + line;
        #}

        jdata = json.loads(all_line, object_pairs_hook=collections.OrderedDict);
    else: #}{
        jfile = open(fpath);
        jdata = json.load(jfile, object_pairs_hook=collections.OrderedDict);
    #}


    #    if len(sys.argv) == 2:
    #        fpath = sys.argv[1];
    #        jfile = open(fpath);
    #        jdata = json.load(jfile, object_pairs_hook=collections.OrderedDict);
    #    else:
    #
    #    json_view = JsonView(jdata);

    json_viewer = JsonViewer(jdata, fpath);
    sys.exit(qt_app.exec_());
#}

if "__main__" == __name__: #{
    main();
#}

# vim:ts=4:tw=80:sw=4:et:ai:si
