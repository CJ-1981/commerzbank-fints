#!/usr/bin/env python3
"""
Commerzbank Local FinTS Payout Automator (Qt Desktop Application)
Combines an interactive batch table manager, real-time IBAN validation,
and native background FinTS threads that prompt for photoTAN challenges inline.

Requirements:
    pip install PyQt6 fints
"""

import sys
import threading
from decimal import Decimal, InvalidOperation
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QRadioButton, QButtonGroup, 
    QPlainTextEdit, QInputDialog, QMessageBox, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor

# Import open-source FinTS client libraries
try:
    from fints.client import FinTS3PinTanClient
    from fints.models import SEPATransferOrder
    from fints.exceptions import FinTSClientPINError
    from fints.dialog import NeedTANResponse
    FINTS_AVAILABLE = True
except ImportError:
    FINTS_AVAILABLE = False


class FinTSWorker(QThread):
    """
    Background worker thread to handle network-blocking banking operations
    without freezing the main Qt GUI thread.
    """
    log_signal = pyqtSignal(str, str)             # (message, color)
    request_tan_signal = pyqtSignal(str, bool)    # (challenge_text, is_decoupled)
    finished_signal = pyqtSignal(bool, str)       # (success, status_message)

    def __init__(self, blz, user_id, pin, debtor_iban, payouts, method):
        super().__init__()
        self.blz = blz
        self.user_id = user_id
        self.pin = pin
        self.debtor_iban = debtor_iban
        self.payouts = payouts
        self.method = method  # "collective" or "individual"
        
        # Thread-safe event coordination to wait for user TAN input
        self.tan_event = threading.Event()
        self.submitted_tan = ""
        self.is_cancelled = False

    def log(self, message, level="info"):
        color = "#e2e8f0"  # default slate-200
        if level == "error":
            color = "#f87171"  # red-400
        elif level == "success":
            color = "#34d399"  # emerald-400
        elif level == "warning":
            color = "#fbbf24"  # amber-400
        self.log_signal.emit(message, color)

    def set_tan(self, tan_code):
        """Called by the main GUI thread when the user submits their photoTAN."""
        self.submitted_tan = tan_code
        self.tan_event.set()

    def cancel_tan(self):
        """Called by the main GUI thread if the user aborts the photoTAN prompt."""
        self.is_cancelled = True
        self.tan_event.set()

    def run(self):
        if not FINTS_AVAILABLE:
            self.log("[-] Python library 'fints' is not installed. Run 'pip install fints'", "error")
            self.finished_signal.emit(False, "Missing dependencies")
            return

        self.log("[*] Initializing secure FinTS connection client...", "warning")
        
        client = FinTS3PinTanClient(
            bank_identifier=self.blz,
            user_id=self.user_id,
            pin=self.pin,
            server="https://fints.commerzbank.de/fints",
            product_id="9A5B7C218E1D5FA0B0"
        )

        try:
            with client:
                self.log("[*] Establishing secure SSL/TLS connection socket with Commerzbank...", "warning")
                accounts = client.get_sepa_accounts()
                self.log("[+] Authentication validated. Account list fetched.", "success")

                # Match debtor IBAN
                debtor_acc = next((a for a in accounts if a.iban.replace(" ", "").upper() == self.debtor_iban.replace(" ", "").upper()), None)
                if not debtor_acc:
                    self.log(f"[-] Target debtor IBAN {self.debtor_iban} not found in authorized accounts list.", "error")
                    self.finished_signal.emit(False, "Debtor IBAN matching failed")
                    return

                if self.method == "collective":
                    self.process_collective_transfer(client, debtor_acc)
                else:
                    self.process_individual_transfers(client, debtor_acc)

        except FinTSClientPINError:
            self.log("[-] Authentication Refused: Invalid Commerzbank login PIN.", "error")
            self.finished_signal.emit(False, "Invalid PIN")
        except Exception as e:
            self.log(f"[-] FinTS Exception: {str(e)}", "error")
            self.finished_signal.emit(False, str(e))

    def process_collective_transfer(self, client, debtor_acc):
        self.log(f"[*] Bundling {len(self.payouts)} payouts into a single Collective SEPA order (Sammelüberweisung)...")
        orders = []
        for p in self.payouts:
            orders.append(
                SEPATransferOrder(
                    recipient_name=p["name"],
                    recipient_iban=p["iban"],
                    amount=Decimal(p["amount"]),
                    reason=p["reference"]
                )
            )

        self.log("[*] Transmission started. Submitting batch request to Commerzbank...", "warning")
        res = client.sepa_transfer_multiple(account=debtor_acc, orders=orders)
        
        # Handle verification dialog loop
        res = self.handle_tan_challenge_loop(client, res)
        
        if self.is_cancelled:
            self.log("[-] Transfer aborted by user.", "error")
            self.finished_signal.emit(False, "Aborted")
        else:
            self.log("[+] SUCCESS! Commerzbank has authorized and booked the collective transfer.", "success")
            self.finished_signal.emit(True, "Collective batch processed successfully")

    def process_individual_transfers(self, client, debtor_acc):
        total = len(self.payouts)
        self.log(f"[*] Processing {total} individual payments sequentially...")

        for idx, p in enumerate(self.payouts, 1):
            if self.is_cancelled:
                self.log("[-] Processing cancelled by user.", "error")
                break

            self.log(f"\n[{idx}/{total}] Preparing individual payout to {p['name']} for {p['amount']} EUR...")
            res = client.simple_sepa_transfer(
                account=debtor_acc,
                iban=p["iban"],
                amount=Decimal(p["amount"]),
                recipient_name=p["name"],
                reason=p["reference"]
            )

            res = self.handle_tan_challenge_loop(client, res)

            if self.is_cancelled:
                self.log(f"[-] Execution aborted at payment #{idx}.", "error")
                break
            
            self.log(f"[+] Payout of {p['amount']} EUR to {p['name']} authorized successfully.", "success")

        self.finished_signal.emit(not self.is_cancelled, "Individual payouts processing finished")

    def handle_tan_challenge_loop(self, client, response):
        """Interactively halts the background thread to poll the user for photoTAN approval."""
        res = response
        while isinstance(res, NeedTANResponse) and not self.is_cancelled:
            self.log("-" * 65, "warning")
            self.log("[!] ACTION REQUIRED: photoTAN confirmation pending...", "warning")
            self.log(f"Challenge text from Commerzbank: {res.challenge}", "warning")
            
            # Reset event and request main thread to pop open standard input dialog
            self.tan_event.clear()
            self.request_tan_signal.emit(res.challenge, getattr(res, 'decoupled', False))
            
            # Suspend background worker until user provides input or closes the window
            self.tan_event.wait()

            if self.is_cancelled:
                break

            if getattr(res, 'decoupled', False):
                self.log("[*] Sending decoupled mobile confirmation approval update...", "warning")
                res = client.send_tan(res, "decoupled")
            else:
                self.log(f"[*] Forwarding submitted 6-digit photoTAN code: {self.submitted_tan}...", "warning")
                res = client.send_tan(res, self.submitted_tan)
        
        return res


class CommerzbankFinTSApp(QMainWindow):
    """
    Main application window built using responsive stylesheet layers (QSS)
    mimicking high-fidelity modern dashboard architectures.
    """
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Commerzbank FinTS Payout Automator")
        self.resize(1100, 750)
        self.setup_dark_palette()

        # Core Layout Splitter
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # ----------------- Left Panel (Control Panel) -----------------
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

        # Config Panel Frame
        config_frame = QFrame()
        config_frame.setObjectName("PanelFrame")
        config_layout = QGridLayout(config_frame)
        config_layout.setSpacing(10)

        config_title = QLabel("FinTS Connection & Configuration")
        config_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #10b981; padding-bottom: 5px;")
        config_layout.addWidget(config_title, 0, 0, 1, 2)

        config_layout.addWidget(QLabel("Bank Code (BLZ):"), 1, 0)
        self.blz_input = QLineEdit("37040044")
        config_layout.addWidget(self.blz_input, 1, 1)

        config_layout.addWidget(QLabel("Online Banking Login ID:"), 2, 0)
        self.user_id_input = QLineEdit("1234567890")
        config_layout.addWidget(self.user_id_input, 2, 1)

        config_layout.addWidget(QLabel("Online Banking PIN:"), 3, 0)
        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setPlaceholderText("Enter PIN (never stored)")
        config_layout.addWidget(self.pin_input, 3, 1)

        config_layout.addWidget(QLabel("Debtor Account IBAN:"), 4, 0)
        self.debtor_iban_input = QLineEdit("DE89370400440001234567")
        config_layout.addWidget(self.debtor_iban_input, 4, 1)

        left_layout.addWidget(config_frame)

        # Strategy Switcher Frame
        strategy_frame = QFrame()
        strategy_frame.setObjectName("PanelFrame")
        strategy_layout = QVBoxLayout(strategy_frame)
        
        strat_title = QLabel("SCA Authorization Strategy")
        strat_title.setStyleSheet("font-weight: bold; font-size: 12px; color: #10b981;")
        strategy_layout.addWidget(strat_title)

        self.method_group = QButtonGroup(self)
        self.radio_collective = QRadioButton("Collective Batch (Sammelüberweisung)")
        self.radio_collective.setChecked(True)
        self.radio_individual = QRadioButton("Individual Transfers (Separate photoTAN per payment)")
        
        self.method_group.addButton(self.radio_collective)
        self.method_group.addButton(self.radio_individual)
        strategy_layout.addWidget(self.radio_collective)
        strategy_layout.addWidget(self.radio_individual)

        strategy_desc = QLabel("Collective mode bundles payments to trigger only ONE single photoTAN push challenge.")
        strategy_desc.setStyleSheet("color: #94a3b8; font-size: 11px; padding-left: 18px;")
        strategy_layout.addWidget(strategy_desc)

        left_layout.addWidget(strategy_frame)

        # Table Control Frame
        table_frame = QFrame()
        table_frame.setObjectName("PanelFrame")
        table_layout = QVBoxLayout(table_frame)

        table_header = QHBoxLayout()
        table_title = QLabel("Payout Batch List")
        table_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #10b981;")
        table_header.addWidget(table_title)
        
        table_actions = QHBoxLayout()
        self.btn_add_payout = QPushButton("+ Add")
        self.btn_add_payout.setObjectName("BtnSecondary")
        self.btn_add_payout.clicked.connect(self.add_table_row)
        table_actions.addWidget(self.btn_add_payout)

        self.btn_paste = QPushButton("Paste Clipboard")
        self.btn_paste.setObjectName("BtnSecondary")
        self.btn_paste.setToolTip("Paste tab-separated spreadsheet columns")
        self.btn_paste.clicked.connect(self.paste_from_clipboard)
        table_actions.addWidget(self.btn_paste)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setObjectName("BtnDanger")
        self.btn_delete.clicked.connect(self.delete_selected_row)
        table_actions.addWidget(self.btn_delete)

        table_header.addLayout(table_actions)
        table_layout.addLayout(table_header)

        # Table Widget Creation
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Recipient Name", "IBAN", "Amount (€)", "Reference"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.itemChanged.connect(self.on_table_changed)
        table_layout.addWidget(self.table)

        # Batch Totals Panel
        totals_layout = QHBoxLayout()
        self.lbl_batch_count = QLabel("Size: 0 Payouts")
        self.lbl_batch_count.setStyleSheet("font-weight: bold; font-size: 12px; color: #cbd5e1;")
        self.lbl_batch_total = QLabel("Total Sum: €0.00")
        self.lbl_batch_total.setStyleSheet("font-weight: bold; font-size: 13px; color: #10b981;")
        totals_layout.addWidget(self.lbl_batch_count)
        totals_layout.addStretch()
        totals_layout.addWidget(self.lbl_batch_total)
        table_layout.addLayout(totals_layout)

        left_layout.addWidget(table_frame)
        splitter.addWidget(left_widget)

        # ----------------- Right Panel (Execution Terminal Log) -----------------
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)

        terminal_frame = QFrame()
        terminal_frame.setObjectName("PanelFrame")
        terminal_layout = QVBoxLayout(terminal_frame)

        terminal_title = QLabel("System Terminal Logs")
        terminal_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #10b981; padding-bottom: 5px;")
        terminal_layout.addWidget(terminal_title)

        self.log_terminal = QPlainTextEdit()
        self.log_terminal.setReadOnly(True)
        self.log_terminal.setStyleSheet("""
            background-color: #020617; 
            border: 1px solid #1e293b; 
            border-radius: 5px; 
            font-family: 'JetBrains Mono', 'Courier New', monospace; 
            font-size: 11px;
        """)
        terminal_layout.addWidget(self.log_terminal)

        self.btn_execute = QPushButton("⚡ Execute Payout Batch")
        self.btn_execute.setObjectName("BtnPrimary")
        self.btn_execute.setFixedHeight(45)
        self.btn_execute.clicked.connect(self.start_batch_execution)
        terminal_layout.addWidget(self.btn_execute)

        right_layout.addWidget(terminal_frame)
        splitter.addWidget(right_widget)

        # Distribute Splitter ratio
        splitter.setSizes([600, 500])

        # Setup standard mock items to match layout
        self.load_mock_data()
        self.update_batch_calculations()

    def setup_dark_palette(self):
        """Applies highly refined stylesheet definitions targeting modern web aesthetics."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0b0f19;
            }
            QWidget {
                color: #e2e8f0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
            QLabel {
                color: #94a3b8;
            }
            QFrame#PanelFrame {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 12px;
                padding: 10px;
            }
            QLineEdit {
                background-color: #090d16;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px 10px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 1px solid #10b981;
            }
            QTableWidget {
                background-color: #090d16;
                border: 1px solid #1e293b;
                gridline-color: #1e293b;
                border-radius: 8px;
                color: #f1f5f9;
            }
            QTableWidget::item:selected {
                background-color: #10b981;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #1e293b;
                color: #94a3b8;
                border: none;
                padding: 6px;
                font-weight: bold;
            }
            QRadioButton {
                color: #cbd5e1;
                spacing: 8px;
                padding-top: 5px;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
                border-radius: 8px;
                border: 2px solid #475569;
            }
            QRadioButton::indicator:checked {
                background-color: #10b981;
                border: 2px solid #10b981;
            }
            QPushButton#BtnPrimary {
                background-color: #10b981;
                color: #042f1a;
                font-weight: bold;
                border-radius: 8px;
                font-size: 14px;
                border: none;
            }
            QPushButton#BtnPrimary:hover {
                background-color: #34d399;
            }
            QPushButton#BtnPrimary:disabled {
                background-color: #334155;
                color: #64748b;
            }
            QPushButton#BtnSecondary {
                background-color: #1e293b;
                color: #e2e8f0;
                font-weight: 500;
                border-radius: 6px;
                padding: 5px 12px;
                border: 1px solid #334155;
            }
            QPushButton#BtnSecondary:hover {
                background-color: #334155;
            }
            QPushButton#BtnDanger {
                background-color: #7f1d1d;
                color: #fca5a5;
                font-weight: 500;
                border-radius: 6px;
                padding: 5px 12px;
                border: 1px solid #991b1b;
            }
            QPushButton#BtnDanger:hover {
                background-color: #991b1b;
            }
        """)

    def load_mock_data(self):
        mock_payouts = [
            ("Max Mustermann", "DE12370400440001111111", "350.00", "Refund Invoice 10934"),
            ("Acme Components GmbH", "DE56370400440002222222", "1280.50", "Supplies Batch 81A"),
            ("Web Hosting Services Ltd", "DE78370400440003333333", "49.99", "SaaS Cloud Base")
        ]
        for name, iban, amount, ref in mock_payouts:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(iban))
            self.table.setItem(row, 2, QTableWidgetItem(amount))
            self.table.setItem(row, 3, QTableWidgetItem(ref))

    def add_table_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem("New Recipient"))
        self.table.setItem(row, 1, QTableWidgetItem("DE"))
        self.table.setItem(row, 2, QTableWidgetItem("0.00"))
        self.table.setItem(row, 3, QTableWidgetItem("Invoice Ref"))
        self.update_batch_calculations()

    def delete_selected_row(self):
        selected = self.table.selectedRanges()
        if not selected:
            QMessageBox.warning(self, "No Row Selected", "Please click a cell in the row you wish to delete.")
            return
        
        # Remove selected rows in reverse order
        rows_to_remove = set()
        for r in selected:
            for row_idx in range(r.topRow(), r.bottomRow() + 1):
                rows_to_remove.add(row_idx)
                
        for row_idx in sorted(list(rows_to_remove), reverse=True):
            self.table.removeRow(row_idx)
            
        self.update_batch_calculations()

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if not text:
            return

        lines = text.split('\n')
        added_count = 0

        for line in lines:
            parts = line.split('\t')
            if len(parts) >= 3:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(parts[0].strip()))
                self.table.setItem(row, 1, QTableWidgetItem(parts[1].strip().replace(" ", "").upper()))
                self.table.setItem(row, 2, QTableWidgetItem(parts[2].strip().replace(",", ".")))
                self.table.setItem(row, 3, QTableWidgetItem(parts[3].strip() if len(parts) > 3 else "Invoice Reference"))
                added_count += 1

        if added_count > 0:
            self.update_batch_calculations()
            self.append_terminal_message(f"[+] Clipboard parsed: Imported {added_count} rows.", "#34d399")

    def on_table_changed(self, item):
        self.update_batch_calculations()

    def validate_iban_mod97(self, iban):
        iban = iban.replace(" ", "").upper()
        if len(iban) < 15:
            return False
        rearranged = iban[4:] + iban[:4]
        numeric = ""
        for char in rearranged:
            if char.isdigit():
                numeric += char
            elif char.isalpha():
                numeric += str(ord(char) - 55)
            else:
                return False
        try:
            return int(numeric) % 97 == 1
        except ValueError:
            return False

    def update_batch_calculations(self):
        row_count = self.table.rowCount()
        self.lbl_batch_count.setText(f"Size: {row_count} Payout{'s' if row_count != 1 else ''}")

        total_sum = Decimal("0.00")
        for row in range(row_count):
            amount_item = self.table.item(row, 2)
            iban_item = self.table.item(row, 1)

            if amount_item:
                try:
                    val = Decimal(amount_item.text().strip() or "0")
                    total_sum += val
                except (InvalidOperation, ValueError):
                    pass

            if iban_item:
                raw_iban = iban_item.text().strip()
                if self.validate_iban_mod97(raw_iban):
                    iban_item.setForeground(QColor("#f1f5f9"))
                else:
                    iban_item.setForeground(QColor("#f87171"))  # Red-400 hint for bad checksum

        self.lbl_batch_total.setText(f"Total Sum: €{total_sum:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    @pyqtSlot(str, str)
    def append_terminal_message(self, text, color="#cbd5e1"):
        """Displays custom formatted text chunks inside the logging box."""
        self.log_terminal.appendHtml(f'<span style="color: {color};">{text}</span>')
        self.log_terminal.moveCursor(self.log_terminal.textCursor().MoveOperation.End)

    def start_batch_execution(self):
        if self.worker and self.worker.isRunning():
            self.append_terminal_message("[-] Cannot run: Background worker thread is already executing.", "#f87171")
            return

        blz = self.blz_input.text().strip()
        user_id = self.user_id_input.text().strip()
        pin = self.pin_input.text().strip()
        debtor_iban = self.debtor_iban_input.text().strip()
        
        if not pin:
            QMessageBox.critical(self, "PIN Required", "Please enter your Commerzbank online banking PIN to authenticate.")
            return

        # Build list of active payouts from editable UI elements
        payouts = []
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text().strip()
            iban = self.table.item(row, 1).text().strip()
            amount = self.table.item(row, 2).text().strip()
            ref = self.table.item(row, 3).text().strip()

            if not name or not iban or not amount:
                QMessageBox.critical(self, "Incomplete Data", f"Row {row+1} has empty cells. Please verify.")
                return
            
            payouts.append({
                "name": name,
                "iban": iban,
                "amount": amount,
                "reference": ref
            })

        if not payouts:
            QMessageBox.critical(self, "No Payouts Set", "Your payout list is empty. Add or paste rows first.")
            return

        method = "collective" if self.radio_collective.isChecked() else "individual"

        # Initialize background worker
        self.worker = FinTSWorker(blz, user_id, pin, debtor_iban, payouts, method)
        
        # Connect signals
        self.worker.log_signal.connect(self.append_terminal_message)
        self.worker.request_tan_signal.connect(self.prompt_user_for_tan)
        self.worker.finished_signal.connect(self.on_worker_finished)

        # Disable execute buttons while network task is in motion
        self.btn_execute.setEnabled(False)
        self.log_terminal.clear()
        
        self.worker.start()

    @pyqtSlot(str, bool)
    def prompt_user_for_tan(self, challenge, is_decoupled):
        """Displays dialog prompting the user for photoTAN authentication."""
        if is_decoupled:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("photoTAN App Confirmation")
            msg_box.setText(f"<b>Decoupled photoTAN Push Activated!</b><br/><br/>{challenge}<br/><br/>Please unlock your smartphone, approve the transfer batch inside the photoTAN App, and press OK below.")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.addButton(QMessageBox.StandardButton.Ok)
            msg_box.addButton(QMessageBox.StandardButton.Cancel)
            
            ret = msg_box.exec()
            if ret == QMessageBox.StandardButton.Ok:
                self.worker.set_tan("decoupled")
            else:
                self.worker.cancel_tan()
        else:
            tan, ok = QInputDialog.getText(
                self, 
                "photoTAN Challenge Required", 
                f"{challenge}\n\nPlease enter the 6-digit photoTAN code:"
            )
            if ok and tan.strip():
                self.worker.set_tan(tan.strip())
            else:
                self.worker.cancel_tan()

    @pyqtSlot(bool, str)
    def on_worker_finished(self, success, message):
        self.btn_execute.setEnabled(True)
        if success:
            QMessageBox.information(self, "Payout Complete", f"Success:\n{message}")
        else:
            QMessageBox.critical(self, "Payout Failed", f"Operation terminated with errors:\n{message}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CommerzbankFinTSApp()
    window.show()
    sys.exit(app.exec())