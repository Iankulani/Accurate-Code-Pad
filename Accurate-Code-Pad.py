import sys
import os
import json
import subprocess
from PyQt5.QtCore import QRegExp
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QMenuBar, QMenu, QAction, QFileDialog, QMessageBox,
                             QLabel, QLineEdit, QPushButton, QTabWidget, QSplitter, QFrame,
                             QListWidget, QListWidgetItem, QToolBar, QStatusBar, QDialog,
                             QFormLayout, QGroupBox, QComboBox, QCheckBox, QSpinBox)
from PyQt5.QtCore import Qt, QSize, QSettings
from PyQt5.QtGui import QFont, QIcon, QColor, QTextCharFormat, QSyntaxHighlighter, QTextDocument
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter

# Syntax highlighter for Python code
class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.highlighting_rules = []
        
        # Keyword format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#FFD700"))  # Yellow
        keyword_format.setFontWeight(QFont.Bold)
        
        keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
            'elif', 'else', 'except', 'False', 'finally', 'for', 'from', 'global',
            'if', 'import', 'in', 'is', 'lambda', 'None', 'nonlocal', 'not', 'or',
            'pass', 'raise', 'return', 'True', 'try', 'while', 'with', 'yield'
        ]
        
        for word in keywords:
            pattern = r'\b' + word + r'\b'
            self.highlighting_rules.append((pattern, keyword_format))
        
        # String format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#FF6B6B"))  # Light red
        self.highlighting_rules.append((r'"[^"\\]*(\\.[^"\\]*)*"', string_format))
        self.highlighting_rules.append((r"'[^'\\]*(\\.[^'\\]*)*'", string_format))
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#AAAAAA"))  # Gray
        self.highlighting_rules.append((r'#.*', comment_format))
        
        # Function format
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#FFA500"))  # Orange
        function_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((r'\b[A-Za-z0-9_]+(?=\()', function_format))
        
        # Number format
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#FFD700"))  # Yellow
        self.highlighting_rules.append((r'\b[0-9]+\b', number_format))
    
    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)
        
        self.setCurrentBlockState(0)

# Settings dialog
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(500, 400)
        
        self.settings = QSettings("Codepad", "Settings")
        
        layout = QVBoxLayout()
        
        # API Configuration
        api_group = QGroupBox("API Configuration")
        api_layout = QFormLayout()
        
        self.api_combo = QComboBox()
        self.api_combo.addItems(["OpenAI", "Custom API"])
        api_layout.addRow("API Provider:", self.api_combo)
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        api_layout.addRow("API Key:", self.api_key_edit)
        
        self.api_url_edit = QLineEdit()
        api_layout.addRow("API URL:", self.api_url_edit)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # Telegram Configuration
        telegram_group = QGroupBox("Telegram Configuration")
        telegram_layout = QFormLayout()
        
        self.telegram_token_edit = QLineEdit()
        self.telegram_token_edit.setEchoMode(QLineEdit.Password)
        telegram_layout.addRow("Telegram Token:", self.telegram_token_edit)
        
        self.telegram_chat_id_edit = QLineEdit()
        telegram_layout.addRow("Chat ID:", self.telegram_chat_id_edit)
        
        telegram_group.setLayout(telegram_layout)
        layout.addWidget(telegram_group)
        
        # Editor Settings
        editor_group = QGroupBox("Editor Settings")
        editor_layout = QFormLayout()
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        editor_layout.addRow("Font Size:", self.font_size_spin)
        
        self.tab_width_spin = QSpinBox()
        self.tab_width_spin.setRange(2, 8)
        self.tab_width_spin.setValue(4)
        editor_layout.addRow("Tab Width:", self.tab_width_spin)
        
        self.line_numbers_check = QCheckBox("Show Line Numbers")
        self.line_numbers_check.setChecked(True)
        editor_layout.addRow("", self.line_numbers_check)
        
        editor_group.setLayout(editor_layout)
        layout.addWidget(editor_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Load saved settings
        self.load_settings()
        
        # Connect signals
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.reject)
    
    def load_settings(self):
        self.api_combo.setCurrentText(self.settings.value("api_provider", "OpenAI"))
        self.api_key_edit.setText(self.settings.value("api_key", ""))
        self.api_url_edit.setText(self.settings.value("api_url", ""))
        self.telegram_token_edit.setText(self.settings.value("telegram_token", ""))
        self.telegram_chat_id_edit.setText(self.settings.value("telegram_chat_id", ""))
        self.font_size_spin.setValue(int(self.settings.value("font_size", 12)))
        self.tab_width_spin.setValue(int(self.settings.value("tab_width", 4)))
        self.line_numbers_check.setChecked(self.settings.value("line_numbers", True, type=bool))
    
    def save_settings(self):
        self.settings.setValue("api_provider", self.api_combo.currentText())
        self.settings.setValue("api_key", self.api_key_edit.text())
        self.settings.setValue("api_url", self.api_url_edit.text())
        self.settings.setValue("telegram_token", self.telegram_token_edit.text())
        self.settings.setValue("telegram_chat_id", self.telegram_chat_id_edit.text())
        self.settings.setValue("font_size", self.font_size_spin.value())
        self.settings.setValue("tab_width", self.tab_width_spin.value())
        self.settings.setValue("line_numbers", self.line_numbers_check.isChecked())
        
        self.accept()

# Main application window
class CodeNotepad(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Accurate Code Pad")
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply red and yellow theme
        self.apply_theme()
        
        # Initialize variables
        self.current_file = None
        self.file_list = []
        
        # Setup UI
        self.setup_ui()
        
        # Load settings
        self.settings = QSettings("CodeNotepad", "Settings")
        
        # Create syntax highlighter
        self.highlighter = PythonHighlighter(self.editor.document())
        
        # Update editor settings
        self.update_editor_settings()
    
    def apply_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2B2B2B;
            }
            QMenuBar {
                background-color: #8B0000;
                color: #FFD700;
            }
            QMenuBar::item:selected {
                background-color: #FF0000;
            }
            QMenu {
                background-color: #8B0000;
                color: #FFD700;
                border: 1px solid #FF0000;
            }
            QMenu::item:selected {
                background-color: #FF0000;
            }
            QToolBar {
                background-color: #8B0000;
                border: none;
            }
            QToolButton {
                background-color: #8B0000;
                color: #FFD700;
                border: none;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #FF0000;
            }
            QStatusBar {
                background-color: #8B0000;
                color: #FFD700;
            }
            QTextEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                selection-background-color: #FF6B6B;
            }
            QListWidget {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: none;
            }
            QListWidget::item:selected {
                background-color: #FF6B6B;
                color: #000000;
            }
            QSplitter::handle {
                background-color: #8B0000;
            }
            QDialog {
                background-color: #2B2B2B;
            }
            QGroupBox {
                color: #FFD700;
                font-weight: bold;
                border: 1px solid #FF6B6B;
                border-radius: 5px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
            QLabel {
                color: #FFD700;
            }
            QLineEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #FF6B6B;
                padding: 5px;
            }
            QPushButton {
                background-color: #8B0000;
                color: #FFD700;
                border: none;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #FF0000;
            }
            QComboBox {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #FF6B6B;
                padding: 5px;
            }
            QSpinBox {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #FF6B6B;
                padding: 5px;
            }
            QCheckBox {
                color: #FFD700;
            }
            QTabWidget::pane {
                border: 1px solid #FF6B6B;
                background-color: #2B2B2B;
            }
            QTabBar::tab {
                background-color: #8B0000;
                color: #FFD700;
                padding: 8px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #FF0000;
            }
        """)
    
    def setup_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Splitter for sidebar and editor
        splitter = QSplitter(Qt.Horizontal)
        
        # Sidebar for file list
        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(250)
        self.sidebar.itemDoubleClicked.connect(self.open_file_from_list)
        splitter.addWidget(self.sidebar)
        
        # Editor area
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        
        # Text editor
        self.editor = QTextEdit()
        editor_layout.addWidget(self.editor)
        
        splitter.addWidget(editor_widget)
        splitter.setSizes([200, 1000])
        
        main_layout.addWidget(splitter)
        
        # Setup menu bar
        self.setup_menu_bar()
        
        # Setup toolbar
        self.setup_toolbar()
        
        # Setup status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def setup_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        print_action = QAction("Print", self)
        print_action.setShortcut("Ctrl+P")
        print_action.triggered.connect(self.print_file)
        file_menu.addAction(print_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cut", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        
        preferences_action = QAction("Preferences", self)
        preferences_action.setShortcut("Ctrl+,")
        preferences_action.triggered.connect(self.open_settings)
        settings_menu.addAction(preferences_action)
    
    def setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        new_action = QAction(QIcon.fromTheme("document-new"), "New", self)
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
        
        open_action = QAction(QIcon.fromTheme("document-open"), "Open", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction(QIcon.fromTheme("document-save"), "Save", self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        undo_action = QAction(QIcon.fromTheme("edit-undo"), "Undo", self)
        undo_action.triggered.connect(self.editor.undo)
        toolbar.addAction(undo_action)
        
        redo_action = QAction(QIcon.fromTheme("edit-redo"), "Redo", self)
        redo_action.triggered.connect(self.editor.redo)
        toolbar.addAction(redo_action)
        
        toolbar.addSeparator()
        
        cut_action = QAction(QIcon.fromTheme("edit-cut"), "Cut", self)
        cut_action.triggered.connect(self.editor.cut)
        toolbar.addAction(cut_action)
        
        copy_action = QAction(QIcon.fromTheme("edit-copy"), "Copy", self)
        copy_action.triggered.connect(self.editor.copy)
        toolbar.addAction(copy_action)
        
        paste_action = QAction(QIcon.fromTheme("edit-paste"), "Paste", self)
        paste_action.triggered.connect(self.editor.paste)
        toolbar.addAction(paste_action)
    
    def update_editor_settings(self):
        # Set font
        font_size = self.settings.value("font_size", 12, type=int)
        font = QFont("Monospace", font_size)
        self.editor.setFont(font)
        
        # Set tab width
        tab_width = self.settings.value("tab_width", 4, type=int)
        self.editor.setTabStopDistance(tab_width * self.editor.fontMetrics().width(' '))
    
    def new_file(self):
        self.editor.clear()
        self.current_file = None
        self.setWindowTitle("Code Notepad - New File")
        self.status_bar.showMessage("New file created")
    
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "All Files (*);;Python Files (*.py);;Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    self.editor.setPlainText(content)
                    self.current_file = file_path
                    self.setWindowTitle(f"Code Notepad - {file_path}")
                    
                    # Add to file list if not already there
                    if file_path not in self.file_list:
                        self.file_list.append(file_path)
                        self.sidebar.addItem(file_path)
                    
                    self.status_bar.showMessage(f"Opened {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
    
    def open_file_from_list(self, item):
        file_path = item.text()
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                self.editor.setPlainText(content)
                self.current_file = file_path
                self.setWindowTitle(f"Code Notepad - {file_path}")
                self.status_bar.showMessage(f"Opened {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
    
    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, 'w') as file:
                    file.write(self.editor.toPlainText())
                self.status_bar.showMessage(f"Saved {self.current_file}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
        else:
            self.save_as_file()
    
    def save_as_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "All Files (*);;Python Files (*.py);;Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(self.editor.toPlainText())
                self.current_file = file_path
                self.setWindowTitle(f"Code Notepad - {file_path}")
                
                # Add to file list if not already there
                if file_path not in self.file_list:
                    self.file_list.append(file_path)
                    self.sidebar.addItem(file_path)
                
                self.status_bar.showMessage(f"Saved {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
    
    def print_file(self):
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec_() == QPrintDialog.Accepted:
            self.editor.print_(printer)
    
    def zoom_in(self):
        current_font = self.editor.font()
        current_font.setPointSize(current_font.pointSize() + 1)
        self.editor.setFont(current_font)
    
    def zoom_out(self):
        current_font = self.editor.font()
        if current_font.pointSize() > 8:
            current_font.setPointSize(current_font.pointSize() - 1)
            self.editor.setFont(current_font)
    
    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.update_editor_settings()
            self.status_bar.showMessage("Settings saved")

# Main function
def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    notepad = CodeNotepad()
    notepad.show()
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()