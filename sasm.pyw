from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QCheckBox,
                             QRadioButton, QHeaderView, QMessageBox,
                             QButtonGroup, QMenu)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
import json
import time
import vdf
import sys
import os

# Application version
VERSION = "1.0"

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
VDF_PATH = os.path.join(os.getenv('ProgramFiles(x86)'), "Steam", "config", "loginusers.vdf")

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
    debug_print(f"Opening VDF file: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = vdf.load(f)
    
    debug_print(f"Successfully loaded VDF file")
    return data.get('users', {})

# Save data back to Steam's VDF configuration file
def save_vdf(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        vdf.dump({'users': data}, f, pretty=True)

# Main application class for Steam Account Manager
class SteamAccountManager(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.radio_button_group = QButtonGroup(self)  # Create a button group for radio buttons
        self.radio_button_group.setExclusive(True)    # Ensure only one can be selected
        self.load_data()  # Load data automatically on startup
    
    # Initialize the user interface
    def initUI(self):
        self.setWindowTitle(f"Steam Account Switcher Manager v{VERSION}")
        self.setGeometry(100, 100, 900, 500)
        
        layout = QVBoxLayout()
        
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
        
        # Create button layout
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
        
        # Add widgets to main layout
        layout.addWidget(self.table)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
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
        debug_print("Loading VDF data...")
        try:
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
    app = QApplication(sys.argv)
    window = SteamAccountManager()
    window.show()
    sys.exit(app.exec())