#!/usr/bin/env python3
"""
PyQt5 GUI Network Scanner
A desktop application for network scanning with port detection.
Combines PyQt5 GUI programming with network automation concepts.
"""

import sys
import socket
import threading
import ipaddress
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QProgressBar, QComboBox, QGroupBox, QStatusBar, QMessageBox,
    QHeaderView, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette


# Common ports and their services
COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
    445: "SMB", 993: "IMAPS", 995: "POP3S", 3306: "MySQL",
    3389: "RDP", 5432: "PostgreSQL", 5900: "VNC", 8080: "HTTP-Alt",
    8443: "HTTPS-Alt", 27017: "MongoDB"
}

SCAN_TIMEOUT = 1.0


class ScanWorker(QThread):
    """Worker thread for scanning hosts and ports."""
    progress_updated = pyqtSignal(int, str)  # percentage, current target
    host_found = pyqtSignal(str, str)  # IP, hostname
    port_found = pyqtSignal(str, int, str)  # IP, port, service
    scan_complete = pyqtSignal(int, int)  # hosts scanned, hosts up
    
    def __init__(self, ip_range, ports_to_scan, scan_type="ping"):
        super().__init__()
        self.ip_range = ip_range
        self.ports_to_scan = ports_to_scan
        self.scan_type = scan_type
        self.running = True
        self.hosts_up = 0
        self.hosts_scanned = 0
        
    def run(self):
        try:
            network = ipaddress.ip_network(self.ip_range, strict=False)
            total_hosts = sum(1 for _ in network.hosts())
            scanned = 0
            
            for host in network.hosts():
                if not self.running:
                    break
                    
                host_str = str(host)
                self.progress_updated.emit(
                    int((scanned / total_hosts) * 100), 
                    host_str
                )
                
                if self._is_host_up(host_str):
                    self.hosts_up += 1
                    hostname = self._get_hostname(host_str)
                    self.host_found.emit(host_str, hostname)
                    
                    # Scan ports if requested
                    if self.ports_to_scan:
                        for port in self.ports_to_scan:
                            if not self.running:
                                break
                            if self._scan_port(host_str, port):
                                service = COMMON_PORTS.get(port, "Unknown")
                                self.port_found.emit(host_str, port, service)
                
                scanned += 1
                self.hosts_scanned = scanned
                
        except ValueError as e:
            print(f"Invalid IP range: {e}")
            
        self.scan_complete.emit(self.hosts_scanned, self.hosts_up)
    
    def _is_host_up(self, ip):
        """Check if host is up using TCP connect."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(SCAN_TIMEOUT)
            result = sock.connect_ex((ip, 80))
            sock.close()
            return result == 0
        except:
            return False
    
    def _get_hostname(self, ip):
        """Get hostname via reverse DNS."""
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return "Unknown"
    
    def _scan_port(self, ip, port):
        """Scan a single port on an IP."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(SCAN_TIMEOUT)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def stop(self):
        self.running = False


class NetworkScannerGUI(QMainWindow):
    """Main GUI window for the network scanner."""
    
    def __init__(self):
        super().__init__()
        self.scan_worker = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("PyQt5 Network Scanner")
        self.setGeometry(100, 100, 900, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title = QLabel("🔍 Network Scanner")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Input group
        input_group = QGroupBox("Scan Configuration")
        input_layout = QVBoxLayout()
        
        # IP Range row
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel("IP Range (CIDR):"))
        self.ip_input = QLineEdit("192.168.1.0/24")
        self.ip_input.setPlaceholderText("e.g., 192.168.1.0/24")
        ip_layout.addWidget(self.ip_input)
        input_layout.addLayout(ip_layout)
        
        # Port selection row
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Scan Type:"))
        self.scan_type = QComboBox()
        self.scan_type.addItems([
            "Quick Scan (Ping only)", 
            "Common Ports",
            "Top 20 Ports",
            "Custom Ports"
        ])
        port_layout.addWidget(self.scan_type)
        
        self.custom_ports = QLineEdit("22,80,443,3389")
        self.custom_ports.setPlaceholderText("e.g., 22,80,443,3389")
        self.custom_ports.setEnabled(False)
        port_layout.addWidget(self.custom_ports)
        
        input_layout.addLayout(port_layout)
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Connect scan type to custom ports enable
        self.scan_type.currentTextChanged.connect(self._on_scan_type_changed)
        
        # Buttons row
        button_layout = QHBoxLayout()
        self.scan_btn = QPushButton("▶ Start Scan")
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        self.scan_btn.clicked.connect(self.start_scan)
        button_layout.addWidget(self.scan_btn)
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #da190b; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_scan)
        button_layout.addWidget(self.stop_btn)
        
        self.clear_btn = QPushButton("🗑 Clear")
        self.clear_btn.clicked.connect(self.clear_results)
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        main_layout.addWidget(self.progress)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "IP Address", "Hostname", "Status", "Open Ports", "Services"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: white;
            }
            QTableWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
        """)
        main_layout.addWidget(self.results_table)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to scan")
        
        # Results storage
        self.scan_results = {}  # IP -> {hostname, ports, services}
    
    def _on_scan_type_changed(self, text):
        """Enable/disable custom ports input based on selection."""
        self.custom_ports.setEnabled("Custom" in text)
    
    def start_scan(self):
        """Start the network scan."""
        ip_range = self.ip_input.text().strip()
        
        if not ip_range:
            QMessageBox.warning(self, "Invalid Input", "Please enter an IP range")
            return
        
        # Get ports based on scan type
        scan_text = self.scan_type.currentText()
        if "Quick" in scan_text:
            ports = []
        elif "Common" in scan_text:
            ports = list(COMMON_PORTS.keys())
        elif "Top 20" in scan_text:
            ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 
                     143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080]
        else:
            try:
                ports = [int(p.strip()) for p in self.custom_ports.text().split(",") if p.strip()]
            except ValueError:
                QMessageBox.warning(self, "Invalid Ports", "Please enter valid port numbers")
                return
        
        # Clear previous results
        self.clear_results()
        
        # Update UI state
        self.scan_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.ip_input.setEnabled(False)
        self.scan_type.setEnabled(False)
        self.custom_ports.setEnabled(False)
        
        # Start scan worker
        self.scan_worker = ScanWorker(ip_range, ports)
        self.scan_worker.progress_updated.connect(self.update_progress)
        self.scan_worker.host_found.connect(self.add_host)
        self.scan_worker.port_found.connect(self.add_port)
        self.scan_worker.scan_complete.connect(self.scan_finished)
        self.scan_worker.start()
        
        self.status_bar.showMessage("Scanning in progress...")
    
    def stop_scan(self):
        """Stop the current scan."""
        if self.scan_worker:
            self.scan_worker.stop()
            self.scan_worker.wait()
        self._reset_ui()
        self.status_bar.showMessage("Scan stopped by user")
    
    def update_progress(self, value, target):
        """Update progress bar and status."""
        self.progress.setValue(value)
        self.status_bar.showMessage(f"Scanning: {target}")
    
    def add_host(self, ip, hostname):
        """Add a discovered host to the results."""
        self.scan_results[ip] = {
            "hostname": hostname,
            "ports": [],
            "services": []
        }
        
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        self.results_table.setItem(row, 0, QTableWidgetItem(ip))
        self.results_table.setItem(row, 1, QTableWidgetItem(hostname))
        self.results_table.setItem(row, 2, QTableWidgetItem("🟢 Online"))
        
        # Style the status cell
        status_item = self.results_table.item(row, 2)
        status_item.setBackground(QColor(200, 255, 200))
        status_item.setForeground(QColor(0, 128, 0))
        
        self.results_table.setItem(row, 3, QTableWidgetItem("-"))
        self.results_table.setItem(row, 4, QTableWidgetItem("-"))
    
    def add_port(self, ip, port, service):
        """Add an open port to a host."""
        if ip in self.scan_results:
            self.scan_results[ip]["ports"].append(port)
            self.scan_results[ip]["services"].append(service)
            
            # Update table
            for row in range(self.results_table.rowCount()):
                item = self.results_table.item(row, 0)
                if item and item.text() == ip:
                    ports_str = ", ".join(map(str, self.scan_results[ip]["ports"]))
                    services_str = ", ".join(self.scan_results[ip]["services"])
                    self.results_table.setItem(row, 3, QTableWidgetItem(ports_str))
                    self.results_table.setItem(row, 4, QTableWidgetItem(services_str))
                    break
    
    def scan_finished(self, scanned, up):
        """Handle scan completion."""
        self._reset_ui()
        self.status_bar.showMessage(
            f"Scan complete! Found {up} active hosts out of {scanned} scanned"
        )
        
        if up == 0:
            QMessageBox.information(
                self, "Scan Complete", 
                "No active hosts found in the specified range."
            )
        else:
            QMessageBox.information(
                self, "Scan Complete",
                f"Found {up} active host(s). Check the results table for details."
            )
    
    def _reset_ui(self):
        """Reset UI to ready state."""
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.ip_input.setEnabled(True)
        self.scan_type.setEnabled(True)
        self._on_scan_type_changed(self.scan_type.currentText())
        self.progress.setValue(0)
    
    def clear_results(self):
        """Clear all scan results."""
        self.results_table.setRowCount(0)
        self.scan_results = {}
        self.status_bar.showMessage("Results cleared")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set application-wide palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.WindowText, Qt.black)
    app.setPalette(palette)
    
    window = NetworkScannerGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
