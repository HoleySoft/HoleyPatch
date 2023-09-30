# -*- coding: utf-8 -*-

# Import modules
from PySide2 import QtWidgets
from PySide2.QtWidgets import (QDialog, QDialogButtonBox)
# TODO: Remove

def _get_element(conf):
    if 0 == 0:
        if conf["FIELD_TYPE"] == 'label':
            return QtWidgets.QLabel(str(conf["FIELD_NAME"]))
        elif conf["FIELD_TYPE"] == 'TextField':
            return QtWidgets.QLineEdit()
        elif conf["FIELD_TYPE"] == 'TextBox':
            return QtWidgets.QTextEdit()
        elif conf["FIELD_TYPE"] == 'DropDownBox':
            drp_box = QtWidgets.QComboBox()
            for i in str(conf["FIELD_OPTIONS"]).split(';'):
                drp_box.addItem(i)
            return drp_box
        elif conf["FIELD_TYPE"] == 'SpinBox':
            return QtWidgets.QSpinBox()
        elif conf["FIELD_TYPE"] == 'DoubleSpinBox':
            return QtWidgets.QDoubleSpinBox()
        elif conf["FIELD_TYPE"] == 'FloatField':
            return QtWidgets.QLineEdit()
        else:
            print("Unknown element")
            return False


class FormDialog(QDialog):
    def __init__(self, parent):
        super(FormDialog, self).__init__()
        self.state = False
        self.parent = parent
        self.elements, self.results, self.config_options = None, None, None
        self.field_map = {
            "INT": "SpinBox",
            "VARCHAR": "TextField",
        }

    def make_database_config(self, database_fields):
        config = []
        for field_name, field_type in database_fields:
            try:
                field_type_map = self.field_map[field_type]
            except KeyError:
                print("Encountered untyped field")
                field_type_map = "Textfield"
            config.append(
                {
                    "FIELD_NAME": field_name,
                    "FIELD_TYPE":  field_type_map,
                    "FIELD_OPTIONS": "",
                    "FIELD_RETURN": "",
                }
            )
        return config

    def get_config(self, config_fname):
        dialog_config = configparser.ConfigParser()
        try:
            dialog_config.read(config_fname)
        except:
            print("Unable to read config: dialog_windows")
        widgets_config = []
        for conf in dialog_config.sections():
            widgets_config.append({"FIELD_NAME": dialog_config[conf]['FIELD_NAME'],
                                   "FIELD_TYPE": dialog_config[conf]['FIELD_TYPE'],
                                   "FIELD_OPTIONS": dialog_config[conf]['FIELD_OPTIONS'],
                                   "FIELD_RETURN": dialog_config[conf]['FIELD_RETURN'],
                                   })
        return widgets_config

    def load_dialog(self, dialog_title, config):
        if isinstance(config, list):
            self.config_options = config
        else:
            self.config_options = []
            for field_name in config:
                print(config[field_name])
                if len(config[field_name]) > 1:
                    self.config_options.append({k.upper(): v for k, v in dict(config[field_name]).items()})
        self.setWindowTitle(dialog_title)
        form_box = QtWidgets.QFormLayout()

        self.elements = []
        for conf in self.config_options:
            self.elements.append(_get_element(conf))
            try:
                if conf["FIELD_NAME"] != 'False' and conf["FIELD_TYPE"] != 'label' and self.elements[-1]:
                    form_box.addRow(conf["FIELD_NAME"], self.elements[-1])
                else:
                    form_box.addRow(self.elements[-1])
            except KeyError:
                self.elements.pop()

        button = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(button)
        self.buttonBox.accepted.connect(self.submit_function)
        self.buttonBox.rejected.connect(self.reject)
        form_box.addRow(self.buttonBox)

        self.setLayout(form_box)

    def get_results(self):
        self.results = []
        for c, element in enumerate(self.elements):
            # try:
            if 0 == 0:
                if self.config_options[c]["FIELD_TYPE"] == 'label':
                    pass
                elif self.config_options[c]["FIELD_TYPE"] == 'TextField':
                    self.results.append(str(element.text()))
                elif self.config_options[c]["FIELD_TYPE"] == 'TextBox':
                    self.results.append(str(element.toPlainText()))
                elif self.config_options[c]["FIELD_TYPE"] == 'DropdownBox':
                    self.results.append(str(self.config_options[c]["FIELD_RETURN"]).split(';')[element.currentIndex()])
                elif self.config_options[c]["FIELD_TYPE"] == 'SpinBox':
                    self.results.append(element.value())
                elif self.config_options[c]["FIELD_TYPE"] == 'DoubleSpinBox':
                    self.results.append(element.value())
                elif self.config_options[c]["FIELD_TYPE"] == 'FloatField':
                    self.results.append(str(element.text()))
                else:
                    print("Unknown element")

    def submit_function(self):
        self.state = True
        self.get_results()
        super(QDialog, self).close()
