from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QCheckBox,
                             QRadioButton, QHeaderView, QMessageBox,
                             QButtonGroup, QMenu, QFrame)
from PySide6.QtGui import QAction, QPainter, QPixmap, QIcon
from PySide6.QtCore import Qt, QSize, QPoint, QTimer
from PySide6.QtSvg import QSvgRenderer
import json
import time
import vdf
import sys
import os
import winreg

# Application version
VERSION = "1.1.1"

# Enable verbose logging if -v or --verbose flag is present
VERBOSE = "-v" in sys.argv or "--verbose" in sys.argv

# Debug print function that only prints when verbose mode is enabled
def debug_print(*args, **kwargs):
    if VERBOSE:
        print("[DEBUG]", *args, **kwargs)

# Define paths for application data and Steam configuration
APPDATA_PATH = os.path.join(os.getenv('APPDATA'), "KRWCLASSIC", "steamaccountswitchermanager")
os.makedirs(APPDATA_PATH, exist_ok=True)
DISABLED_ACCOUNTS_FILE = os.path.join(APPDATA_PATH, "disabled_accounts.json")
SETTINGS_FILE = os.path.join(APPDATA_PATH, "settings.json")  # New settings file
BACKUP_PATH = os.path.join(APPDATA_PATH, "backups")
os.makedirs(BACKUP_PATH, exist_ok=True)  # Create backups directory

def find_steam_path():
    """Try to locate Steam installation path by finding the Steam binary"""
    try:
        # Try to find Steam path from registry
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
                steam_path = winreg.QueryValueEx(key, "SteamPath")[0]
                debug_print(f"Found Steam path in registry: {steam_path}")
                vdf_path = os.path.join(steam_path, "config", "loginusers.vdf")
                if os.path.exists(vdf_path):
                    return vdf_path
        except FileNotFoundError:
            pass
        
        # Try to find Steam binary through Steam protocol handler
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"steam\Shell\Open\Command") as key:
                command = winreg.QueryValueEx(key, "")[0]
                # Extract path from command (usually something like "C:\Program Files (x86)\Steam\steam.exe" "%1")
                steam_exe_path = command.split('"')[1]
                steam_path = os.path.dirname(steam_exe_path)
                debug_print(f"Found Steam path through protocol handler: {steam_path}")
                vdf_path = os.path.join(steam_path, "config", "loginusers.vdf")
                if os.path.exists(vdf_path):
                    return vdf_path
        except FileNotFoundError:
            pass
        
        # Try to find Steam through Windows App Paths
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\steam.exe") as key:
                steam_exe_path = winreg.QueryValueEx(key, "")[0]
                steam_path = os.path.dirname(steam_exe_path)
                debug_print(f"Found Steam path through App Paths: {steam_path}")
                vdf_path = os.path.join(steam_path, "config", "loginusers.vdf")
                if os.path.exists(vdf_path):
                    return vdf_path
        except FileNotFoundError:
            pass
        
        # If all else fails, try the default location
        default_path = os.path.join(os.getenv('ProgramFiles(x86)'), "Steam", "config", "loginusers.vdf")
        if os.path.exists(default_path):
            return default_path
        
        return None
        
    except Exception as e:
        debug_print(f"Error finding Steam path: {str(e)}")
        return None

# Update VDF_PATH to use the find_steam_path function
VDF_PATH = find_steam_path()

# Function to create an icon from SVG string
def svg_to_icon(svg_string, size=24, color=None):
    """Convert SVG string to QIcon with optional color override"""
    # If color is specified, try to replace the fill color in the SVG
    if color:
        svg_string = svg_string.replace('fill="currentColor"', f'fill="{color}"')
    
    # Convert the SVG string to a byte array
    svg_bytes = svg_string.encode('utf-8')
    
    # Create an SVG renderer
    renderer = QSvgRenderer(svg_bytes)
    
    # Create a pixmap to render to
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)  # Make the background transparent
    
    # Create a painter to paint onto the pixmap
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    
    # Create and return an icon from the pixmap
    return QIcon(pixmap)

# Custom floating action button class
class FloatingActionButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(56, 56)  # Standard FAB size
        
        # Increase icon size by 140% (24 * 1.4 = 33.6, rounded to 34)
        self.setIconSize(QSize(34, 34))  # Increased icon size
        
        # Set the icon using the new SVG with white color
        self.setIcon(svg_to_icon('''
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" id="data-backup">
                <path fill="#FFFFFF" d="M17.58 32.7H10a.73.73 0 0 1-.69-.7v-6a.73.73 0 0 1 .73-.73h10.3a1 1 0 0 0 1-1 1 1 0 0 0-1-1H10a.73.73 0 0 1-.73-.73V16.6a.73.73 0 0 1 .73-.73h21.67a.73.73 0 0 1 .73.73v3a1 1 0 0 0 2 0v-3a2.73 2.73 0 0 0-.64-1.73 2.68 2.68 0 0 0 .64-1.72v-6a2.72 2.72 0 0 0-2.72-2.72H10a2.72 2.72 0 0 0-2.69 2.75v6a2.67 2.67 0 0 0 .63 1.72 2.72 2.72 0 0 0-.63 1.73v5.95a2.65 2.65 0 0 0 .69 1.7A2.7 2.7 0 0 0 7.31 26v6A2.73 2.73 0 0 0 10 34.7h7.54a1 1 0 0 0 0-2ZM9.31 7.18a.72.72 0 0 1 .69-.72h21.68a.72.72 0 0 1 .72.72v6a.72.72 0 0 1-.72.72H10a.72.72 0 0 1-.72-.72Z"></path>
                <circle fill="#FFFFFF" cx="12.18" cy="10.33" r="1.5"></circle>
                <circle fill="#FFFFFF" cx="12.18" cy="19.52" r="1.5"></circle>
                <circle fill="#FFFFFF" cx="12.18" cy="28.68" r="1.5"></circle>
                <path fill="#FFFFFF" d="M29.1 21.19a8 8 0 0 0-8 8 9.07 9.07 0 0 0 .06.91l-1.48-1.4a1 1 0 0 0-1.41 0 1 1 0 0 0 0 1.42l3.27 3.11a1 1 0 0 0 .69.27 1 1 0 0 0 .71-.29l3.12-3.11a1 1 0 0 0 0-1.42 1 1 0 0 0-1.41 0l-1.47 1.52a6.64 6.64 0 0 1-.09-1 6 6 0 1 1 6 6 6.21 6.21 0 0 1-1.81-.28 1 1 0 1 0-.6 1.9 7.88 7.88 0 0 0 2.41.38 8 8 0 1 0 0-16Z"></path>
            </svg>
        ''', 34, "#FFFFFF"))  # Increased size to 34 and set color to white
        
        # Style the button to be square with a dark theme
        self.setStyleSheet("""
            QPushButton {
                background-color: #424242;  /* Dark background */
                border-radius: 8px;  /* Rounded corners */
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #616161;  /* Lighter on hover */
            }
            QPushButton:pressed {
                background-color: #757575;  /* Even lighter on press */
            }
        """)
        
        # Set the cursor to a pointing hand
        self.setCursor(Qt.CursorShape.PointingHandCursor)

# Load disabled accounts from JSON file
def load_disabled_accounts():
    if os.path.exists(DISABLED_ACCOUNTS_FILE):
        try:
            with open(DISABLED_ACCOUNTS_FILE, 'r') as f:
                data = json.load(f)
                # Convert list to dict if needed (for backward compatibility)
                if isinstance(data, list):
                    debug_print("Converting disabled accounts from list to dictionary format")
                    # Try to load the VDF file to get actual account data for disabled accounts
                    try:
                        vdf_data = parse_vdf(VDF_PATH)
                        new_data = {}
                        for steam_id in data:
                            # If the account exists in the VDF file, use that data
                            if steam_id in vdf_data:
                                new_data[steam_id] = vdf_data[steam_id]
                            else:
                                # Otherwise use placeholder data
                                new_data[steam_id] = {
                                    "AccountName": f"Account_{steam_id[-4:]}",
                                    "PersonaName": f"User_{steam_id[-4:]}",
                                    "RememberPassword": "1",
                                    "WantsOfflineMode": "0",
                                    "SkipOfflineModeWarning": "0",
                                    "AllowAutoLogin": "1",
                                    "MostRecent": "0",
                                    "Timestamp": "0"
                                }
                        return new_data
                    except Exception as e:
                        debug_print(f"Error loading VDF data for disabled accounts: {str(e)}")
                        # Fallback to basic conversion
                        new_data = {}
                        for steam_id in data:
                            new_data[steam_id] = {
                                "AccountName": f"Account_{steam_id[-4:]}",
                                "PersonaName": f"User_{steam_id[-4:]}",
                                "RememberPassword": "1",
                                "WantsOfflineMode": "0",
                                "SkipOfflineModeWarning": "0",
                                "AllowAutoLogin": "1",
                                "MostRecent": "0",
                                "Timestamp": "0"
                            }
                        return new_data
                return data
        except Exception as e:
            debug_print(f"Error loading disabled accounts: {str(e)}")
            return {}
    return {}  # Return empty dict if no disabled accounts file exists

# Save disabled accounts to JSON file
def save_disabled_accounts(accounts):
    with open(DISABLED_ACCOUNTS_FILE, 'w') as f:
        json.dump(accounts, f, indent=4)

# Parse Steam's VDF configuration file
def parse_vdf(filepath):
    if not filepath or not os.path.exists(filepath):
        raise FileNotFoundError("Steam installation not found. Please make sure Steam is installed.")
    
    debug_print(f"Opening VDF file: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = vdf.load(f)
    
    debug_print(f"Successfully loaded VDF file")
    return data.get('users', {})

# Save data back to Steam's VDF configuration file
def save_vdf(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        vdf.dump({'users': data}, f, pretty=True)

# Load settings from JSON file
def load_settings():
    default_settings = {
        "auto_backup": True
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                user_settings = json.load(f)
                # Merge with default settings
                return {**default_settings, **user_settings}
        except Exception as e:
            debug_print(f"Error loading settings: {str(e)}")
            return default_settings
    return default_settings

# Save settings to JSON file
def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

# Main application class for Steam Account Manager
class SteamAccountManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()  # Load settings
        self.auto_backup = self.settings.get("auto_backup", True)  # Get auto_backup setting
        self.radio_button_group = QButtonGroup(self)  # Create a button group for radio buttons
        self.radio_button_group.setExclusive(True)    # Ensure only one can be selected
        self.initUI()
        self.load_data()  # Load data automatically on startup
    
    # Initialize the user interface
    def initUI(self):
        self.setWindowTitle(f"Steam Account Switcher Manager v{VERSION}")
        
        # Set default window size
        default_width = 915
        default_height = 450
        
        # Set minimum window size (default size - 50px on both sides)
        min_width = default_width - 50
        min_height = default_height - 50
        
        # Set window size and minimum size
        self.setGeometry(100, 100, default_width, default_height)
        self.setMinimumSize(min_width, min_height)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create a frame to hold the table and FAB
        self.table_frame = QFrame(self)
        self.table_frame.setObjectName("tableFrame")
        table_layout = QVBoxLayout(self.table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to ensure FAB is properly positioned
        
        # Create table for displaying accounts
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Order", "Account Name", "Persona Name", "Most Recent", "Enabled", "Steam ID"])
        
        # Connect signals for table interactions
        self.table.cellChanged.connect(self.handle_cell_edit)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Configure table column behavior
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        
        # Set column widths
        self.table.setColumnWidth(0, 60)    # Order column
        self.table.setColumnWidth(1, 200)   # Account Name
        self.table.setColumnWidth(2, 200)   # Persona Name
        self.table.setColumnWidth(3, 100)   # Most Recent column
        self.table.setColumnWidth(4, 70)    # Enabled column
        self.table.setColumnWidth(5, 200)   # Steam ID column
        
        # Add the table to the table layout
        table_layout.addWidget(self.table)
        
        # Create floating action button
        self.fab = FloatingActionButton(self.table_frame)  # Make the FAB a child of the table frame
        self.fab.clicked.connect(self.show_fab_menu)
        
        # Add the table frame to the main layout
        main_layout.addWidget(self.table_frame)
        
        # Create button layout for other buttons
        button_layout = QHBoxLayout()
        
        # Create and configure buttons
        self.load_button = QPushButton("Reload")
        self.load_button.clicked.connect(self.load_data)
        
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_data)
        
        self.move_up_button = QPushButton("Move Up")
        self.move_up_button.clicked.connect(self.move_up)
        
        self.move_down_button = QPushButton("Move Down")
        self.move_down_button.clicked.connect(self.move_down)
        
        # Add buttons to layout
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.move_up_button)
        button_layout.addWidget(self.move_down_button)
        
        # Add button layout to main layout
        main_layout.addLayout(button_layout)
    
    # Show the window and position the FAB after the layout is complete
    def showEvent(self, event):
        super().showEvent(event)
        # Use a single-shot timer to position the FAB after the window is shown
        QTimer.singleShot(0, self.position_fab)
    
    # Position the FAB in the bottom right corner of the table frame
    def position_fab(self):
        if self.table_frame and self.fab:
            self.fab.move(
                self.table_frame.width() - self.fab.width() - 16,  # 16px margin from the right
                self.table_frame.height() - self.fab.height() - 16  # 16px margin from the bottom
            )
    
    # Reposition the FAB when the window is resized
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.position_fab()
    
    # Show the menu when the FAB is clicked
    def show_fab_menu(self):
        menu = QMenu(self)
        
        # Add auto backup option with checkbox (no icon)
        auto_backup_action = QAction("Auto Backup", self)
        auto_backup_action.setCheckable(True)
        auto_backup_action.setChecked(self.auto_backup)
        auto_backup_action.triggered.connect(self.toggle_auto_backup)
        menu.addAction(auto_backup_action)
        
        # Add manual backup option (no icon)
        manual_backup_action = QAction("Create Manual Backup", self)
        manual_backup_action.triggered.connect(self.create_manual_backup)
        menu.addAction(manual_backup_action)
        
        # Position the menu above the FAB
        pos = self.fab.mapToGlobal(QPoint(0, -menu.sizeHint().height()))
        menu.exec(pos)
    
    # Toggle auto backup setting
    def toggle_auto_backup(self, state):
        self.auto_backup = state
        self.settings["auto_backup"] = state
        save_settings(self.settings)  # Save updated settings
        debug_print(f"Auto backup {'enabled' if state else 'disabled'}")
    
    # Create a backup of the VDF file
    def create_backup(self, manual=False):
        try:
            # Skip if auto backup is disabled and this is not a manual backup
            if not self.auto_backup and not manual:
                debug_print("Auto backup is disabled, skipping backup")
                return None
                
            # Generate timestamp for the backup filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_type = "manual" if manual else "auto"
            backup_filename = f"loginusers_{backup_type}_{timestamp}.vdf"
            backup_filepath = os.path.join(BACKUP_PATH, backup_filename)
            
            # Copy the VDF file to the backup location
            import shutil
            shutil.copy2(VDF_PATH, backup_filepath)
            
            debug_print(f"Created backup at {backup_filepath}")
            return backup_filepath
        except Exception as e:
            debug_print(f"Error creating backup: {str(e)}")
            if manual:
                QMessageBox.warning(self, "Backup Error", f"Failed to create backup: {str(e)}")
            return None
    
    # Create a manual backup and show confirmation
    def create_manual_backup(self):
        backup_path = self.create_backup(manual=True)
        if backup_path:
            # Create a simplified path for display
            simplified_path = backup_path.replace(os.getenv('APPDATA'), "%APPDATA%")
            QMessageBox.information(
                self, 
                "Backup Created", 
                f"Manual backup created successfully at:\n{simplified_path}"
            )
    
    # Move selected account up in the list
    def move_up(self):
        try:
            current_row = self.table.currentRow()
            if current_row <= 0:
                return
            
            # Swap rows in data model and update UI
            self.swap_rows_in_data(current_row, current_row - 1)
            self.table.setCurrentCell(current_row - 1, self.table.currentColumn())
        except Exception as e:
            debug_print(f"Error moving row up: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to move row up: {str(e)}")
    
    # Move selected account down in the list
    def move_down(self):
        try:
            current_row = self.table.currentRow()
            if current_row >= self.table.rowCount() - 1 or current_row < 0:
                return
            
            # Swap rows in data model and update UI
            self.swap_rows_in_data(current_row, current_row + 1)
            self.table.setCurrentCell(current_row + 1, self.table.currentColumn())
        except Exception as e:
            debug_print(f"Error moving row down: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to move row down: {str(e)}")
    
    # Swap two rows in the table and update the data model
    def swap_rows_in_data(self, row1, row2):
        try:
            # Get Steam IDs for both rows
            steam_id1 = self.table.item(row1, 5).text() if self.table.item(row1, 5) else None
            steam_id2 = self.table.item(row2, 5).text() if self.table.item(row2, 5) else None
            
            if not steam_id1 or not steam_id2:
                debug_print(f"Missing Steam IDs for rows {row1} and/or {row2}")
                return
            
            debug_print(f"Swapping rows: {row1} ({steam_id1}) and {row2} ({steam_id2})")
            
            # Swap table items
            for col in range(self.table.columnCount()):
                if col == 0 or col == 3 or col == 4:  # Skip order numbers, radio buttons and checkboxes
                    continue
                
                # Swap the items
                item1 = self.table.takeItem(row1, col)
                item2 = self.table.takeItem(row2, col)
                
                if item1:
                    self.table.setItem(row2, col, item1)
                if item2:
                    self.table.setItem(row1, col, item2)
            
            # Get widgets for radio buttons and checkboxes
            radio_container1 = self.table.cellWidget(row1, 3)
            radio_container2 = self.table.cellWidget(row2, 3)
            
            checkbox_container1 = self.table.cellWidget(row1, 4)
            checkbox_container2 = self.table.cellWidget(row2, 4)
            
            # Get the state of radio buttons and checkboxes
            radio_btn1 = radio_container1.findChild(QRadioButton) if radio_container1 else None
            radio_btn2 = radio_container2.findChild(QRadioButton) if radio_container2 else None
            
            checkbox1 = checkbox_container1.findChild(QCheckBox) if checkbox_container1 else None
            checkbox2 = checkbox_container2.findChild(QCheckBox) if checkbox_container2 else None
            
            # Default values if widgets are not found
            is_active1 = False
            is_active2 = False
            is_enabled1 = True
            is_enabled2 = True
            
            # Get actual values if widgets exist
            if radio_btn1:
                is_active1 = radio_btn1.isChecked()
            if radio_btn2:
                is_active2 = radio_btn2.isChecked()
            if checkbox1:
                is_enabled1 = checkbox1.isChecked()
            if checkbox2:
                is_enabled2 = checkbox2.isChecked()
            
            # Remove old radio buttons from the button group
            if radio_btn1:
                self.radio_button_group.removeButton(radio_btn1)
            if radio_btn2:
                self.radio_button_group.removeButton(radio_btn2)
            
            # Create new centered radio buttons
            radio_container1 = QWidget()
            radio_layout1 = QHBoxLayout(radio_container1)
            radio_layout1.setContentsMargins(0, 0, 0, 0)
            radio_layout1.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            new_radio1 = QRadioButton()
            new_radio1.setChecked(is_active2)
            new_radio1.setEnabled(is_enabled2)  # Only enable if account is enabled
            new_radio1.clicked.connect(lambda checked, r=row1: self.set_active_account(r))
            self.radio_button_group.addButton(new_radio1)  # Add to button group
            radio_layout1.addWidget(new_radio1)
            
            radio_container2 = QWidget()
            radio_layout2 = QHBoxLayout(radio_container2)
            radio_layout2.setContentsMargins(0, 0, 0, 0)
            radio_layout2.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            new_radio2 = QRadioButton()
            new_radio2.setChecked(is_active1)
            new_radio2.setEnabled(is_enabled1)  # Only enable if account is enabled
            new_radio2.clicked.connect(lambda checked, r=row2: self.set_active_account(r))
            self.radio_button_group.addButton(new_radio2)  # Add to button group
            radio_layout2.addWidget(new_radio2)
            
            # Create new centered checkboxes
            checkbox_container1 = QWidget()
            checkbox_layout1 = QHBoxLayout(checkbox_container1)
            checkbox_layout1.setContentsMargins(0, 0, 0, 0)
            checkbox_layout1.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            new_checkbox1 = QCheckBox()
            new_checkbox1.setChecked(is_enabled2)
            new_checkbox1.stateChanged.connect(lambda state, sid=steam_id2: self.toggle_account(sid, state))
            checkbox_layout1.addWidget(new_checkbox1)
            
            checkbox_container2 = QWidget()
            checkbox_layout2 = QHBoxLayout(checkbox_container2)
            checkbox_layout2.setContentsMargins(0, 0, 0, 0)
            checkbox_layout2.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            new_checkbox2 = QCheckBox()
            new_checkbox2.setChecked(is_enabled1)
            new_checkbox2.stateChanged.connect(lambda state, sid=steam_id1: self.toggle_account(sid, state))
            checkbox_layout2.addWidget(new_checkbox2)
            
            # Set the new widgets
            self.table.setCellWidget(row1, 3, radio_container1)
            self.table.setCellWidget(row2, 3, radio_container2)
            self.table.setCellWidget(row1, 4, checkbox_container1)
            self.table.setCellWidget(row2, 4, checkbox_container2)
            
            # Update the data model based on the new table order
            self.update_data_from_table()
            
            # Update order numbers for all rows
            self.update_order_numbers()
            
        except Exception as e:
            debug_print(f"Error swapping rows in data: {str(e)}")
            raise
    
    # Update order numbers in the table
    def update_order_numbers(self):
        for row in range(self.table.rowCount()):
            order_item = QTableWidgetItem(str(row + 1))
            order_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # Make order number non-editable
            order_item.setFlags(order_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, order_item)
    
    # Update the data model based on current table order
    def update_data_from_table(self):
        try:
            # Get current order from table
            current_order = []
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 5)  # Steam ID column
                if item and item.text():
                    current_order.append(item.text())
            
            debug_print(f"Current order from table: {current_order}")
            
            # Get all account data (both enabled and disabled)
            combined_data = {}
            # First add enabled accounts
            for steam_id, account_data in self.data.items():
                combined_data[steam_id] = account_data.copy()
            
            # Then add disabled accounts
            for steam_id, account_data in self.disabled_accounts.items():
                if steam_id not in combined_data:
                    combined_data[steam_id] = account_data.copy()
            
            # Create new ordered dictionaries
            new_data = {}
            new_disabled = {}
            
            # Rebuild the data models in the new order
            for steam_id in current_order:
                if steam_id not in combined_data:
                    continue
                    
                # Check if the account is enabled or disabled based on the checkbox
                is_enabled = False
                for row in range(self.table.rowCount()):
                    if self.table.item(row, 5) and self.table.item(row, 5).text() == steam_id:
                        checkbox_container = self.table.cellWidget(row, 4)
                        if checkbox_container:
                            # Try to find the checkbox within the container
                            checkbox = checkbox_container.findChild(QCheckBox)
                            if checkbox:
                                is_enabled = checkbox.isChecked()
                            else:
                                # Fallback: check if the account is in self.data (enabled accounts)
                                is_enabled = steam_id in self.data
                        else:
                            # Fallback: check if the account is in self.data (enabled accounts)
                            is_enabled = steam_id in self.data
                        break
                
                if is_enabled:
                    new_data[steam_id] = combined_data[steam_id]
                else:
                    new_disabled[steam_id] = combined_data[steam_id]
            
            # Update the data models
            self.data = new_data
            self.disabled_accounts = new_disabled
            
            debug_print(f"Updated data model with new order: {list(new_data.keys())}")
            debug_print(f"Updated disabled accounts: {list(new_disabled.keys())}")
            
        except Exception as e:
            debug_print(f"Error updating data from table: {str(e)}")
            raise
    
    # Reload table UI without reloading data from disk
    def reload_table_without_data_reload(self):
        try:
            # Remember current selection
            current_row = self.table.currentRow()
            current_col = self.table.currentColumn()
            
            # Get current order from the table before clearing
            current_order = []
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 5)  # Steam ID column
                if item and item.text():
                    current_order.append(item.text())
            
            debug_print(f"Preserving current order: {current_order}")
            
            # Clear the table
            self.table.clearContents()
            
            # Clear the radio button group
            for button in self.radio_button_group.buttons():
                self.radio_button_group.removeButton(button)
            
            # Ensure disabled_accounts is a dictionary
            if not hasattr(self, 'disabled_accounts') or not isinstance(self.disabled_accounts, dict):
                debug_print("Initializing disabled_accounts as empty dict")
                self.disabled_accounts = {}
            
            # Get all account data (both enabled and disabled)
            combined_data = {}
            # First add enabled accounts
            for steam_id, account_data in self.data.items():
                combined_data[steam_id] = account_data
            
            # Then add disabled accounts
            for steam_id, account_data in self.disabled_accounts.items():
                if steam_id not in combined_data:
                    combined_data[steam_id] = account_data
            
            # If we have a current order, use it
            if current_order:
                # Create ordered data based on current order
                ordered_data = {}
                for steam_id in current_order:
                    if steam_id in combined_data:
                        ordered_data[steam_id] = combined_data[steam_id]
                
                # Add any accounts that weren't in the current order
                for steam_id, account_data in combined_data.items():
                    if steam_id not in ordered_data:
                        ordered_data[steam_id] = account_data
            else:
                # If no current order, sort by timestamp (newest first)
                debug_print("No current order, sorting by timestamp")
                # Sort enabled accounts by timestamp (newest first)
                enabled_accounts = sorted(
                    self.data.items(),
                    key=lambda x: int(x[1].get("Timestamp", "0")),
                    reverse=True  # Newest first
                )
                
                # Create an ordered dictionary with enabled accounts first
                ordered_data = {}
                for steam_id, account_data in enabled_accounts:
                    ordered_data[steam_id] = account_data
                
                # Add disabled accounts at the end
                for steam_id, account_data in self.disabled_accounts.items():
                    if steam_id not in ordered_data:
                        ordered_data[steam_id] = account_data
            
            self.table.setRowCount(len(ordered_data))
            debug_print(f"Setting table row count to {len(ordered_data)}")
            
            # Reload the table with current data
            for row, (steam_id, info) in enumerate(ordered_data.items()):
                account_name = info.get("AccountName", "Unknown")
                persona_name = info.get("PersonaName", "Unknown")
                is_most_recent = info.get("MostRecent", "0") == "1"
                # An account is enabled if it exists in the VDF file (self.data)
                is_enabled = steam_id in self.data
                
                debug_print(f"Adding row {row}: {account_name} ({persona_name}) - Most Recent: {is_most_recent}, Enabled: {is_enabled}")
                
                # Order number
                order_item = QTableWidgetItem(str(row + 1))
                order_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                # Make order number non-editable
                order_item.setFlags(order_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 0, order_item)
                
                # Account Name
                self.table.setItem(row, 1, QTableWidgetItem(account_name))
                
                # Persona Name
                self.table.setItem(row, 2, QTableWidgetItem(persona_name))
                
                # Most Recent Radio Button in centered container
                radio_container = QWidget()
                radio_layout = QHBoxLayout(radio_container)
                radio_layout.setContentsMargins(0, 0, 0, 0)
                radio_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                radio_btn = QRadioButton()
                radio_btn.setChecked(is_most_recent)
                radio_btn.setEnabled(is_enabled)  # Disable the radio button for disabled accounts
                radio_btn.clicked.connect(lambda checked, r=row: self.set_active_account(r))
                self.radio_button_group.addButton(radio_btn)  # Add to button group
                
                radio_layout.addWidget(radio_btn)
                self.table.setCellWidget(row, 3, radio_container)
                
                # Enabled Checkbox in centered container
                checkbox_container = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_container)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                checkbox = QCheckBox()
                checkbox.setChecked(is_enabled)
                checkbox.stateChanged.connect(lambda state, sid=steam_id: self.toggle_account(sid, state))
                
                checkbox_layout.addWidget(checkbox)
                self.table.setCellWidget(row, 4, checkbox_container)
                
                # Steam ID
                id_item = QTableWidgetItem(steam_id)
                id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 5, id_item)
            
            # Restore selection if possible
            if 0 <= current_row < self.table.rowCount() and 0 <= current_col < self.table.columnCount():
                self.table.setCurrentCell(current_row, current_col)
                
        except Exception as e:
            debug_print(f"Error reloading table: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to reload table: {str(e)}")
    
    # Load account data from VDF and JSON files
    def load_data(self):
        try:
            if not VDF_PATH:
                QMessageBox.critical(self, "Error", 
                    "Steam installation not found. Please make sure Steam is installed.")
                return
            
            debug_print("Loading VDF data...")
            # First load the VDF file (enabled accounts)
            self.data = parse_vdf(VDF_PATH)
            debug_print(f"Successfully parsed VDF data, found {len(self.data)} accounts")
            
            # Then load disabled accounts
            try:
                self.disabled_accounts = load_disabled_accounts()
                if not isinstance(self.disabled_accounts, dict):
                    debug_print("Disabled accounts is not a dictionary, resetting to empty dict")
                    self.disabled_accounts = {}
                debug_print(f"Loaded {len(self.disabled_accounts)} disabled accounts: {self.disabled_accounts}")
            except Exception as e:
                debug_print(f"Error loading disabled accounts, resetting: {str(e)}")
                self.disabled_accounts = {}
            
            # Sort enabled accounts by timestamp (newest first to match Steam's display order)
            enabled_accounts = sorted(
                self.data.items(),
                key=lambda x: int(x[1].get("Timestamp", "0")),
                reverse=True  # Newest first (highest timestamp at the top)
            )
            debug_print(f"Sorted enabled accounts by timestamp (newest first): {[id for id, _ in enabled_accounts]}")
            
            # Create an ordered dictionary with enabled accounts first
            ordered_data = {}
            for steam_id, account_data in enabled_accounts:
                ordered_data[steam_id] = account_data
            
            # Add disabled accounts at the end
            for steam_id, account_data in self.disabled_accounts.items():
                if steam_id not in ordered_data:
                    ordered_data[steam_id] = account_data
            
            # Update self.data to maintain the order
            self.data = {k: v for k, v in ordered_data.items() if k not in self.disabled_accounts}
            
            # Set up the table
            self.table.setRowCount(len(ordered_data))
            debug_print("Set table row count to", len(ordered_data))
            
            # Clear the radio button group
            for button in self.radio_button_group.buttons():
                self.radio_button_group.removeButton(button)
            
            # Fill the table with data in the correct order
            for row, (steam_id, info) in enumerate(ordered_data.items()):
                account_name = info.get("AccountName", "Unknown")
                persona_name = info.get("PersonaName", "Unknown")
                is_most_recent = info.get("MostRecent", "0") == "1"
                # An account is enabled if it exists in the VDF file (self.data)
                is_enabled = steam_id in self.data
                
                debug_print(f"Adding row {row}: {account_name} ({persona_name}) - Most Recent: {is_most_recent}, Enabled: {is_enabled}")
                
                # Order number
                order_item = QTableWidgetItem(str(row + 1))
                order_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                # Make order number non-editable
                order_item.setFlags(order_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 0, order_item)
                
                # Account Name
                self.table.setItem(row, 1, QTableWidgetItem(account_name))
                
                # Persona Name
                self.table.setItem(row, 2, QTableWidgetItem(persona_name))
                
                # Most Recent Radio Button in centered container
                radio_container = QWidget()
                radio_layout = QHBoxLayout(radio_container)
                radio_layout.setContentsMargins(0, 0, 0, 0)
                radio_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                radio_btn = QRadioButton()
                radio_btn.setChecked(is_most_recent)
                radio_btn.setEnabled(is_enabled)  # Disable the radio button for disabled accounts
                radio_btn.clicked.connect(lambda checked, r=row: self.set_active_account(r))
                self.radio_button_group.addButton(radio_btn)  # Add to button group
                
                radio_layout.addWidget(radio_btn)
                self.table.setCellWidget(row, 3, radio_container)
                
                # Enabled Checkbox in centered container
                checkbox_container = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_container)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                checkbox = QCheckBox()
                checkbox.setChecked(is_enabled)
                checkbox.stateChanged.connect(lambda state, sid=steam_id: self.toggle_account(sid, state))
                
                checkbox_layout.addWidget(checkbox)
                self.table.setCellWidget(row, 4, checkbox_container)
                
                # Steam ID
                id_item = QTableWidgetItem(steam_id)
                id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 5, id_item)
            
            debug_print("Finished loading data into table")
            
        except FileNotFoundError as e:
            QMessageBox.critical(self, "Error", 
                f"Steam installation not found. Please make sure Steam is installed.\n\nDetails: {str(e)}")
        except Exception as e:
            debug_print(f"Error loading data: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")
    
    # Set the active (most recent) account
    def set_active_account(self, active_row):
        try:
            debug_print(f"Setting active account to row {active_row}")
            
            # First check if the account at active_row is enabled
            steam_id_item = self.table.item(active_row, 5)
            if not steam_id_item:
                return
                
            steam_id = steam_id_item.text()
            if not steam_id:
                return
                
            # Check if the account is disabled
            if steam_id not in self.data or steam_id in self.disabled_accounts:
                debug_print(f"Cannot set disabled account {steam_id} as most recent")
                # Reset the radio button
                radio_container = self.table.cellWidget(active_row, 3)
                if radio_container:
                    radio_btn = radio_container.findChild(QRadioButton)
                    if radio_btn:
                        radio_btn.setChecked(False)
                QMessageBox.warning(self, "Warning", "Cannot set a disabled account as most recent.")
                return
            
            # Update all radio buttons
            for row in range(self.table.rowCount()):
                try:
                    radio_container = self.table.cellWidget(row, 3)
                    if not radio_container:
                        continue
                        
                    steam_id_item = self.table.item(row, 5)
                    if not steam_id_item:
                        continue
                        
                    steam_id = steam_id_item.text()
                    if not steam_id or steam_id not in self.data:
                        continue
                    
                    if row == active_row:
                        self.data[steam_id]["MostRecent"] = "1"
                        debug_print(f"Set account {steam_id} as most recent (not saved yet)")
                    else:
                        self.data[steam_id]["MostRecent"] = "0"
                except Exception as e:
                    debug_print(f"Error updating active state for row {row}: {str(e)}")
            
            # Changes will be saved when the user clicks the Save button
            
        except Exception as e:
            debug_print(f"Error setting active account: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to set active account: {str(e)}")
    
    # Toggle account enabled/disabled state
    def toggle_account(self, steam_id, state):
        debug_print(f"Toggling account {steam_id} {'enabled' if state else 'disabled'}")
        try:
            if state == Qt.CheckState.Checked.value:
                if steam_id in self.disabled_accounts:
                    # Re-enable account by restoring its data
                    account_data = self.disabled_accounts[steam_id]
                    self.data[steam_id] = account_data
                    del self.disabled_accounts[steam_id]
                    debug_print(f"Re-enabled account {steam_id} with data: {account_data} (not saved yet)")
            else:
                if steam_id not in self.disabled_accounts and steam_id in self.data:
                    # Disable account by moving its data to disabled_accounts
                    account_data = self.data[steam_id].copy()  # Make a copy to prevent reference issues
                    self.disabled_accounts[steam_id] = account_data
                    del self.data[steam_id]
                    debug_print(f"Disabled account {steam_id}, backed up data: {account_data} (not saved yet)")
                    
                    # If this account was set as most recent, unset it
                    if account_data.get("MostRecent", "0") == "1":
                        debug_print(f"Unsetting most recent flag for disabled account {steam_id}")
                        self.disabled_accounts[steam_id]["MostRecent"] = "0"
                        
                        # Find the row for this account and update the radio button
                        for row in range(self.table.rowCount()):
                            if self.table.item(row, 5) and self.table.item(row, 5).text() == steam_id:
                                radio_container = self.table.cellWidget(row, 3)
                                if radio_container:
                                    radio_btn = radio_container.findChild(QRadioButton)
                                    if radio_btn:
                                        radio_btn.setChecked(False)
                                break
            
            # Changes will be saved when the user clicks the Save button
            
            # Reload the table to reflect changes
            self.reload_table_without_data_reload()
        except Exception as e:
            debug_print(f"Error toggling account: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to toggle account: {str(e)}")
    
    # Save changes to VDF and JSON files
    def save_data(self, show_message=True):
        try:
            debug_print("Saving changes...")
            
            # Create backup before saving
            self.create_backup()
            
            base_timestamp = int(time.time())
            
            # First update any edited Account Name or Persona Name values from the table
            self.update_account_names_from_table()
            
            # Get the current order of Steam IDs from the table
            current_order = []
            for row in range(self.table.rowCount()):
                steam_id_item = self.table.item(row, 5)
                if steam_id_item and steam_id_item.text():
                    current_order.append(steam_id_item.text())
            
            debug_print(f"Current order before saving: {current_order}")
            
            # Create new ordered data dictionary
            ordered_data = {}
            
            # Set timestamps based on position in the table
            # Higher position in table = higher timestamp = higher in Steam's list
            for idx, steam_id in enumerate(current_order):
                # Only include enabled accounts in the VDF file
                if steam_id in self.data and steam_id not in self.disabled_accounts:
                    ordered_data[steam_id] = self.data[steam_id].copy()
                    
                    # First row gets highest timestamp, last row gets lowest
                    # This ensures the order in Steam matches the order in our table
                    timestamp_offset = (len(current_order) - idx - 1) * 60
                    ordered_data[steam_id]["Timestamp"] = str(base_timestamp + timestamp_offset)
                    debug_print(f"Setting timestamp for {steam_id} (position {idx+1}) to {base_timestamp + timestamp_offset}")
                else:
                    debug_print(f"Skipping disabled account {steam_id} from VDF file")
            
            # Save the ordered data to VDF file
            debug_print(f"Saving {len(ordered_data)} accounts to VDF file")
            self.data = {k: v for k, v in self.data.items() if k not in self.disabled_accounts}
            save_vdf(VDF_PATH, ordered_data)
            
            # Save disabled accounts to JSON file
            debug_print(f"Saving {len(self.disabled_accounts)} disabled accounts to JSON file")
            save_disabled_accounts(self.disabled_accounts)
            
            debug_print("Changes saved successfully")
            
            # Always show success message (ignoring show_message parameter for now)
            debug_print(f"Showing success message (show_message={show_message})")
            QMessageBox.information(self, "Success", "Changes saved successfully!")
            
        except Exception as e:
            debug_print(f"Error saving data: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to save changes: {str(e)}")

    # Show context menu with additional account options
    def show_context_menu(self, position):
        try:
            # Get the row at the position
            row = self.table.rowAt(position.y())
            if row < 0:
                return
            
            # Get the Steam ID for this row
            steam_id_item = self.table.item(row, 5)
            if not steam_id_item:
                return
                
            steam_id = steam_id_item.text()
            if not steam_id:
                return
            
            # Check if the account is enabled
            is_enabled = steam_id in self.data
            if not is_enabled:
                return  # Don't show context menu for disabled accounts
            
            # Get the account data
            account_data = self.data[steam_id]
            
            # Create context menu
            context_menu = QMenu(self)
            
            # Add checkboxes for binary values
            remember_password_action = QAction("Remember Password", self)
            remember_password_action.setCheckable(True)
            remember_password_action.setChecked(account_data.get("RememberPassword", "1") == "1")
            remember_password_action.triggered.connect(
                lambda checked, sid=steam_id, key="RememberPassword": self.toggle_account_setting(sid, key, checked)
            )
            
            wants_offline_mode_action = QAction("Wants Offline Mode", self)
            wants_offline_mode_action.setCheckable(True)
            wants_offline_mode_action.setChecked(account_data.get("WantsOfflineMode", "0") == "1")
            wants_offline_mode_action.triggered.connect(
                lambda checked, sid=steam_id, key="WantsOfflineMode": self.toggle_account_setting(sid, key, checked)
            )
            
            skip_offline_warning_action = QAction("Skip Offline Warning", self)
            skip_offline_warning_action.setCheckable(True)
            skip_offline_warning_action.setChecked(account_data.get("SkipOfflineModeWarning", "0") == "1")
            skip_offline_warning_action.triggered.connect(
                lambda checked, sid=steam_id, key="SkipOfflineModeWarning": self.toggle_account_setting(sid, key, checked)
            )
            
            allow_auto_login_action = QAction("Allow Auto Login", self)
            allow_auto_login_action.setCheckable(True)
            allow_auto_login_action.setChecked(account_data.get("AllowAutoLogin", "1") == "1")
            allow_auto_login_action.triggered.connect(
                lambda checked, sid=steam_id, key="AllowAutoLogin": self.toggle_account_setting(sid, key, checked)
            )
            
            # Add actions to menu
            context_menu.addAction(remember_password_action)
            context_menu.addAction(wants_offline_mode_action)
            context_menu.addAction(skip_offline_warning_action)
            context_menu.addAction(allow_auto_login_action)
            
            # Show the menu
            context_menu.exec(self.table.mapToGlobal(position))
            
        except Exception as e:
            debug_print(f"Error showing context menu: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to show context menu: {str(e)}")
    
    # Toggle a binary setting for an account
    def toggle_account_setting(self, steam_id, key, checked):
        try:
            if steam_id not in self.data:
                return
                
            # Update the setting in memory only
            self.data[steam_id][key] = "1" if checked else "0"
            debug_print(f"Updated {key} for {steam_id} to {self.data[steam_id][key]} (not saved yet)")
            
            # Changes will be saved when the user clicks the Save button
            
        except Exception as e:
            debug_print(f"Error toggling account setting: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to toggle account setting: {str(e)}")

    # Handle edits to cells, particularly Account Name and Persona Name
    def handle_cell_edit(self, row, column):
        try:
            # Only process edits to Account Name (column 1) or Persona Name (column 2)
            if column not in [1, 2]:
                return
                
            # Get the Steam ID for this row
            steam_id_item = self.table.item(row, 5)
            if not steam_id_item:
                return
                
            steam_id = steam_id_item.text()
            if not steam_id:
                return
                
            # Check if the account is enabled
            is_enabled = steam_id in self.data
            if not is_enabled:
                return  # Don't process edits for disabled accounts
                
            # Get the new value
            item = self.table.item(row, column)
            if not item:
                return
                
            new_value = item.text()
            
            # Update the appropriate field in the data
            if column == 1:  # Account Name
                debug_print(f"Updating Account Name for {steam_id} to: {new_value}")
                self.data[steam_id]["AccountName"] = new_value
            elif column == 2:  # Persona Name
                debug_print(f"Updating Persona Name for {steam_id} to: {new_value}")
                self.data[steam_id]["PersonaName"] = new_value
                
            # Note: Changes will be saved when the user clicks the Save button
                
        except Exception as e:
            debug_print(f"Error handling cell edit: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to update account information: {str(e)}")
            
    # Update Account Name and Persona Name from the table to the data model
    def update_account_names_from_table(self):
        try:
            for row in range(self.table.rowCount()):
                # Get the Steam ID for this row
                steam_id_item = self.table.item(row, 5)
                if not steam_id_item or not steam_id_item.text():
                    continue
                    
                steam_id = steam_id_item.text()
                
                # Check if the account is enabled
                is_enabled = steam_id in self.data
                if not is_enabled:
                    continue  # Skip disabled accounts
                
                # Get Account Name and Persona Name from the table
                account_name_item = self.table.item(row, 1)
                persona_name_item = self.table.item(row, 2)
                
                if account_name_item and account_name_item.text():
                    self.data[steam_id]["AccountName"] = account_name_item.text()
                    
                if persona_name_item and persona_name_item.text():
                    self.data[steam_id]["PersonaName"] = persona_name_item.text()
                    
            debug_print("Updated account names from table")
            
        except Exception as e:
            debug_print(f"Error updating account names from table: {str(e)}")
            raise

# Main entry point
if __name__ == '__main__':
    sys.argv += ['-platform', 'windows:darkmode=2'] # Force Windows Dark Mode
    
    app = QApplication(sys.argv)
    window = SteamAccountManager()
    window.show()
    sys.exit(app.exec())