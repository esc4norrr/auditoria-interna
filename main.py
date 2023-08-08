import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QPushButton, QTextEdit, QCheckBox
from PyQt5.QtCore import QProcess

config_path = os.path.join("config", "audt_config.json")
stage_path = os.path.join("controller", "Audt_stg_loader.py")
highlight_path = os.path.join("controller", "Audt_highlight_new.py")
selected_options_path = os.path.join("config", "audt_options_selected.json")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):        

        self.setWindowTitle("Auditoria Interna")
        self.setGeometry(100, 100, 400, 400)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QGridLayout()

        self.checkboxes = []
        self.create_checkboxes()

        self.button_run_highlight = QPushButton("Download && Highlight")
        self.button_run_stg_loader = QPushButton("Load to Internal Stage")
        self.button_save_selected = QPushButton("Save Audit Options")

        self.button_run_highlight.clicked.connect(self.run_highlight)
        self.button_run_stg_loader.clicked.connect(self.run_stg_loader)
        self.button_save_selected.clicked.connect(self.save_selected_options)

        self.output_widget = QTextEdit()
        self.output_widget.setReadOnly(True)
        row, col = 0, 0
        for checkbox in self.checkboxes:
            layout.addWidget(checkbox, row, col)
            col += 1
            if col == 2:
                col = 0
                row += 1

        layout.addWidget(self.button_save_selected, row + 1, 0, 1, 2)
        layout.addWidget(self.button_run_highlight, row + 3, 0, 1, 2)
        layout.addWidget(self.button_run_stg_loader, row + 2, 0, 1, 2)
        layout.addWidget(self.output_widget, row + 4, 0, 1, 2)

        central_widget.setLayout(layout)

        self.is_running = False


    def create_checkboxes(self):
        with open(config_path, "r") as file:
            options_data = json.load(file)

        for audit in options_data.get("Audits", []):
            audit_name = audit.get("Audit Name", "")
            checkbox = QCheckBox(audit_name)
            self.checkboxes.append(checkbox)


    def run_highlight(self):
        if not self.is_running:
            self.is_running = True
            self.button_run_highlight.setEnabled(False)
            self.run_python_script(highlight_path, self.button_run_highlight)

    def run_stg_loader(self):
        if not self.is_running:
            self.is_running = True
            self.button_run_stg_loader.setEnabled(False)
            print(stage_path)
            self.run_python_script(stage_path, self.button_run_stg_loader)

    def run_python_script(self, script_name, button):
        process = QProcess(self)
        process.readyReadStandardOutput.connect(lambda: self.update_output(process))
        process.readyReadStandardError.connect(lambda: self.update_output(process))
        process.finished.connect(lambda: self.on_script_finished(button))

        try:
            process.start("python", [script_name])
        except Exception as e:
            self.show_error_message(f"Error while running {script_name}: {str(e)}")
            self.on_script_finished(button)

    def update_output(self, process):
        output = process.readAllStandardOutput().data().decode()
        errors = process.readAllStandardError().data().decode()

        if output:
            self.output_widget.append(f"\n{output}")
        if errors:
            self.output_widget.append(f"\n{errors}")

    def on_script_finished(self, button):
        button.setEnabled(True)
        self.is_running = False
    
    def save_selected_options(self):
        selected_audits = [checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()]

        with open(config_path, "r") as file:
            options_data = json.load(file)

        selected_options = {"Audits": []}
        for audit in options_data.get("Audits", []):
            if audit.get("Audit Name") in selected_audits:
                selected_options["Audits"].append(audit)
        with open(selected_options_path, "w") as file:
            json.dump(selected_options, file)

        self.output_widget.append("Selected options saved to audt_options_selected.json")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
