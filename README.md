# JSON Viewer #

![JSON Viewer](./json_viewer.png)

Python3 script to view a JSON file as a tree in GUI.

## Usage ##

Can be invoked with the file as a command line parameter:
```bash
./json_viewer.py sample.json
```

Or, JSON data can be read in from stdin:
```bash
cat sample.json|./json_viewer.py -
```

## Key and Mouse Mapping ##

You can _double-click_ on any field to do a find on that field's content. If
the field is a parent, you need to also hold `SHIFT`.

## History ##

Fork of [ashwin/json-viewer](https://github.com/ashwin/json-viewer) with
some enhancements and cherry-picks from
[arfan/json-viewer](https://github.com/arfan/json-viewer/) and
[zhangxiao/json-viewer-windows](https://github.com/zhangxiao/json-viewer-windows/) .

