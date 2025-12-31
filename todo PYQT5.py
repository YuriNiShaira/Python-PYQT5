import sys
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QListWidgetItem, QLineEdit, 
                             QPushButton, QLabel, QMessageBox, QComboBox, 
                             QDateEdit, QCheckBox, QSplitter, QFrame)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor


class TaskItemWidget(QWidget):
    """Custom widget for displaying individual tasks in the list"""
    
    taskEdited = pyqtSignal(str, str)  # task_id, new_text
    taskToggled = pyqtSignal(str, bool)  # task_id, completed
    
    def __init__(self, task_id, text, completed=False, category="Personal", due_date=None):
        super().__init__()
        self.task_id = task_id
        self.text = text
        self.completed = completed
        self.category = category
        
        self.setup_ui()
        self.update_appearance()
        
    def setup_ui(self):
        """Initialize the UI components for the task item"""
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Checkbox for completion status
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.completed)
        self.checkbox.stateChanged.connect(self.on_checkbox_changed)
        layout.addWidget(self.checkbox)
        
        # Task text display
        self.text_label = QLabel(self.text)
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("padding: 5px;")
        layout.addWidget(self.text_label, 1)  # 1 = stretch factor
        
        # Category badge
        self.category_label = QLabel(self.category)
        self.category_label.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                color: #1976d2;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 10px;
            }
        """)
        layout.addWidget(self.category_label)
        
        # Edit button
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        self.edit_btn.clicked.connect(self.start_editing)
        layout.addWidget(self.edit_btn)
        
        # Delete button
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        layout.addWidget(self.delete_btn)
        
        self.setLayout(layout)
        
    def update_appearance(self):
        """Update visual style based on completion status"""
        if self.completed:
            self.text_label.setStyleSheet("""
                QLabel {
                    color: #888;
                    text-decoration: line-through;
                    padding: 5px;
                    background-color: #e8f5e8;
                    border-radius: 3px;
                }
            """)
            self.category_label.setStyleSheet("""
                QLabel {
                    background-color: #c8e6c9;
                    color: #2e7d32;
                    padding: 2px 8px;
                    border-radius: 10px;
                    font-size: 10px;
                }
            """)
        else:
            self.text_label.setStyleSheet("""
                QLabel {
                    color: #333;
                    padding: 5px;
                    background-color: white;
                    border-radius: 3px;
                }
            """)
            self.category_label.setStyleSheet("""
                QLabel {
                    background-color: #e3f2fd;
                    color: #1976d2;
                    padding: 2px 8px;
                    border-radius: 10px;
                    font-size: 10px;
                }
            """)
    
    def on_checkbox_changed(self, state):
        """Handle checkbox state change"""
        self.completed = (state == Qt.Checked)
        self.update_appearance()
        self.taskToggled.emit(self.task_id, self.completed)
    
    def start_editing(self):
        """Switch to edit mode"""
        # Replace label with line edit
        old_text = self.text_label.text()
        self.text_label.deleteLater()
        
        self.edit_input = QLineEdit(old_text)
        self.edit_input.setStyleSheet("padding: 5px;")
        self.layout().insertWidget(1, self.edit_input, 1)
        
        # Change edit button to save button
        self.edit_btn.setText("Save")
        self.edit_btn.clicked.disconnect()
        self.edit_btn.clicked.connect(self.finish_editing)
        
        # Change delete button to cancel button
        self.delete_btn.setText("Cancel")
        self.delete_btn.clicked.disconnect()
        self.delete_btn.clicked.connect(self.cancel_editing)
        
        self.edit_input.setFocus()
    
    def finish_editing(self):
        """Save edited text"""
        new_text = self.edit_input.text().strip()
        if new_text:
            self.text = new_text
            self.taskEdited.emit(self.task_id, new_text)
        
        self.exit_edit_mode()
    
    def cancel_editing(self):
        """Cancel editing and restore original text"""
        self.exit_edit_mode()
    
    def exit_edit_mode(self):
        """Exit edit mode and restore normal view"""
        # Remove line edit and restore label
        self.edit_input.deleteLater()
        
        self.text_label = QLabel(self.text)
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("padding: 5px;")
        self.layout().insertWidget(1, self.text_label, 1)
        
        # Restore buttons
        self.edit_btn.setText("Edit")
        self.edit_btn.clicked.disconnect()
        self.edit_btn.clicked.connect(self.start_editing)
        
        self.delete_btn.setText("Delete")
        self.delete_btn.clicked.disconnect()
        
        self.update_appearance()


class TodoApp(QMainWindow):
    """Main To-Do List Application Window"""
    
    def __init__(self):
        super().__init__()
        self.tasks = []
        self.next_id = 1
        self.data_file = "todo_data.json"
        self.dark_mode = False
        
        self.setup_ui()
        self.load_tasks()
        self.apply_light_theme()  # Start with light theme
        
    def setup_ui(self):
        """Initialize the main UI components"""
        self.setWindowTitle("PyTodo - Your Smart Task Manager")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Header with title and theme toggle
        header_layout = QHBoxLayout()
        
        title_label = QLabel("PyTodo")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2196F3;
                padding: 10px;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Theme toggle button
        self.theme_btn = QPushButton("🌙 Dark Mode")
        self.theme_btn.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        self.theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_btn)
        
        main_layout.addLayout(header_layout)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search tasks...")
        self.search_input.textChanged.connect(self.filter_tasks)
        search_layout.addWidget(self.search_input)
        
        main_layout.addLayout(search_layout)
        
        # Task input section
        input_layout = QHBoxLayout()
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter a new task...")
        self.task_input.returnPressed.connect(self.add_task)
        input_layout.addWidget(self.task_input)
        
        # Category selection
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Personal", "Work", "Study", "Shopping", "Health"])
        input_layout.addWidget(self.category_combo)
        
        # Due date (optional)
        self.due_date = QDateEdit()
        self.due_date.setDate(QDate.currentDate())
        self.due_date.setCalendarPopup(True)
        input_layout.addWidget(QLabel("Due:"))
        input_layout.addWidget(self.due_date)
        
        # Add task button
        add_btn = QPushButton("Add Task")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_btn.clicked.connect(self.add_task)
        input_layout.addWidget(add_btn)
        
        main_layout.addLayout(input_layout)
        
        # Task list
        self.task_list = QListWidget()
        self.task_list.setAlternatingRowColors(True)
        main_layout.addWidget(self.task_list)
        
        # Statistics and controls
        footer_layout = QHBoxLayout()
        
        # Statistics
        self.stats_label = QLabel("Total: 0 | Completed: 0 | Pending: 0")
        footer_layout.addWidget(self.stats_label)
        
        footer_layout.addStretch()
        
        # Clear completed button
        clear_completed_btn = QPushButton("Clear Completed")
        clear_completed_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        clear_completed_btn.clicked.connect(self.clear_completed_tasks)
        footer_layout.addWidget(clear_completed_btn)
        
        main_layout.addLayout(footer_layout)
        
    def add_task(self):
        """Add a new task to the list"""
        text = self.task_input.text().strip()
        if not text:
            QMessageBox.warning(self, "Input Error", "Please enter a task description!")
            return
        
        task = {
            'id': str(self.next_id),
            'text': text,
            'completed': False,
            'category': self.category_combo.currentText(),
            'due_date': self.due_date.date().toString("yyyy-MM-dd"),
            'created_at': datetime.now().isoformat()
        }
        
        self.tasks.append(task)
        self.next_id += 1
        self.task_input.clear()
        self.refresh_task_list()
        self.save_tasks()
        
    def edit_task(self, task_id, new_text):
        """Edit an existing task"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['text'] = new_text
                break
        self.save_tasks()
        
    def toggle_task_completion(self, task_id, completed):
        """Toggle task completion status"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = completed
                break
        self.refresh_task_list()
        self.save_tasks()
        
    def delete_task(self, task_id):
        """Delete a task from the list"""
        for i, task in enumerate(self.tasks):
            if task['id'] == task_id:
                del self.tasks[i]
                break
        self.refresh_task_list()
        self.save_tasks()
        
    def clear_completed_tasks(self):
        """Remove all completed tasks"""
        if not any(task['completed'] for task in self.tasks):
            QMessageBox.information(self, "Info", "No completed tasks to clear!")
            return
            
        reply = QMessageBox.question(self, "Confirm Clear", 
                                   "Are you sure you want to clear all completed tasks?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.tasks = [task for task in self.tasks if not task['completed']]
            self.refresh_task_list()
            self.save_tasks()
        
    def refresh_task_list(self):
        """Refresh the task list display"""
        self.task_list.clear()
        
        # Filter tasks based on search
        search_text = self.search_input.text().lower()
        filtered_tasks = [task for task in self.tasks 
                         if search_text in task['text'].lower()]
        
        for task in filtered_tasks:
            item = QListWidgetItem(self.task_list)
            widget = TaskItemWidget(
                task['id'], 
                task['text'], 
                task['completed'],
                task['category'],
                task.get('due_date')
            )
            
            # Connect signals
            widget.taskEdited.connect(self.edit_task)
            widget.taskToggled.connect(self.toggle_task_completion)
            widget.delete_btn.clicked.connect(lambda checked=False, tid=task['id']: self.delete_task(tid))
            
            item.setSizeHint(widget.sizeHint())
            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, widget)
        
        self.update_statistics()
        
    def filter_tasks(self):
        """Filter tasks based on search text"""
        self.refresh_task_list()
        
    def update_statistics(self):
        """Update the statistics display"""
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task['completed'])
        pending = total - completed
        
        self.stats_label.setText(f"Total: {total} | Completed: {completed} | Pending: {pending}")
        
    def save_tasks(self):
        """Save tasks to JSON file"""
        try:
            data = {
                'tasks': self.tasks,
                'next_id': self.next_id
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")
            
    def load_tasks(self):
        """Load tasks from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = data.get('tasks', [])
                    self.next_id = data.get('next_id', 1)
                self.refresh_task_list()
        except Exception as e:
            print(f"Error loading tasks: {e}")
            
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            self.apply_dark_theme()
            self.theme_btn.setText("☀️ Light Mode")
        else:
            self.apply_light_theme()
            self.theme_btn.setText("🌙 Dark Mode")
            
    def apply_light_theme(self):
        """Apply light theme styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                background-color: #f5f5f5;
                color: #333333;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                border-bottom: 1px solid #eeeeee;
            }
            QListWidget::item:alternate {
                background-color: #f9f9f9;
            }
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
                background-color: white;
            }
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
                background-color: white;
            }
            QDateEdit {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
                background-color: white;
            }
        """)
        
    def apply_dark_theme(self):
        """Apply dark theme styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QListWidget {
                background-color: #3c3f41;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
                color: #ffffff;
            }
            QListWidget::item {
                border-bottom: 1px solid #555555;
            }
            QListWidget::item:alternate {
                background-color: #323232;
            }
            QLineEdit {
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                background-color: #3c3f41;
                color: #ffffff;
            }
            QComboBox {
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                background-color: #3c3f41;
                color: #ffffff;
            }
            QDateEdit {
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                background-color: #3c3f41;
                color: #ffffff;
            }
            QPushButton {
                background-color: #555555;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)


def main():
    """Main function to run the application"""
    app = QApplication(sys.argv)
    app.setApplicationName("PyTodo")
    
    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = TodoApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()