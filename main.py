import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QGroupBox, QSpacerItem, QSizePolicy, QDialog, QDialogButtonBox, QMainWindow, QGridLayout)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi
import requests
from bs4 import BeautifulSoup
import json
import threading
import subprocess

def run_command_and_print(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    output = []

    for line in iter(process.stdout.readline, ''):
        print(line, end='')  # Print each line as it is output by the command
        output.append(line)  # Store each line in the output list

    process.stdout.close()
    process.wait()

    return ''.join(output)
def get_username_data(username):
    # user_input = input("Enter the input for Sherlock: ")
    command = f'sherlock "{username}"'
    # results = run_command(command)
    results = run_command_and_print(command)
    return results

def get_cnic_tel(cnic_tel):
    data = {
        'cnnum': str(cnic_tel),
    }
    try:
        response = requests.post('https://paksim.info/sim-database-online-2022-result.php', data=data)
    except:
        return "Try with a VPN connection...!"
    soup = BeautifulSoup(response.text, 'lxml')
    tables = soup.find_all("table", {'class': 'tg'})
    if len(tables) == 0:
        return f"No records found for: {cnic_tel}"
        
    result = []
    for index, table in enumerate(tables):
        table_data = []
        data_points = table.find("tbody").find_all("tr", recursive=False)
        for dp in data_points:
            key = dp.find("td").text.strip()
            value = dp.find_all("td")[1].text.strip()
            table_data.append(f"{key} : {value}")
        result.append("\n".join(table_data))
    return "\n\n".join(result)

def get_ip_info_2(ip):
    data = {
        'ip': str(ip),
        'source': 'ipgeolocation',
        'ipv': '4',
    }
    response = requests.post('https://www.iplocation.net/get-ipdata', data=data)
    json_data = response.json()
    
    if 'res' in json_data:
        ip_info = json_data['res']
        if 'data' in ip_info:
            data = ip_info['data']
            formatted_info = {
                'IP': "         " + data.get('ip', 'N/A'),
                'Continent': "  " + data.get('continent_name', 'N/A'),
                'Country': "    " + data.get('country_name', 'N/A'),
                'Region': "     " + data.get('state_prov', 'N/A'),
                'City': "       " + data.get('city', 'N/A'),
                'ISP': "        " + data.get('isp', 'N/A'),
                'Latitude': "   " + data.get('latitude', 'N/A'),
                'Longitude':"   " + data.get('longitude', 'N/A'),
                'Timezone': "   " + data.get('time_zone', {}).get('name', 'N/A'),
                'Currency': "   " + data.get('currency', {}).get('name', 'N/A'),
            }
            return formatted_info
    return "No valid data found."
def domain_to_ip(domain):
    data = {
        'domains': domain,
        'submit': 'Convert',
    }
    response = requests.post('https://domaintoipconverter.com/index.php',  data=data)
    soup = BeautifulSoup(response.text,'lxml')
    ip = soup.find("div",id="primary").find("p").find("span").text.strip()
    # print(ip)
    return ip

class OutputWindow(QDialog):
    def __init__(self, params):
        super().__init__()
        self.initUI(params)

    def initUI(self, params):
        self.setWindowTitle('Output Window')
        self.setGeometry(400, 400, 600, 400)
        layout = QVBoxLayout()
        
        outputText = ""
        for key, value in params.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    outputText += f"<b>{subkey.capitalize()}</b>: {subvalue}<br>"
            else:
                outputText += f"<b>{key.capitalize()}</b>: {value}<br>"
        
        outputLabel = QLabel(outputText)
        outputLabel.setWordWrap(True)
        outputLabel.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(outputLabel)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

        self.setLayout(layout)
        self.setStyleSheet(self.getStylesheet())
        self.show()

    def getStylesheet(self):
        return """
        QDialog {
            background-color: #2e2e2e;
        }
        QLabel {
            color: white;
            font-size: 14px;
            margin: 10px;
        }
        QDialogButtonBox {
            margin-top: 20px;
        }
        QDialogButtonBox QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
        }
        QDialogButtonBox QPushButton:hover {
            background-color: #45a049;
        }
        """

class InputForm(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('main.ui', self)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('ConnectFinder')
        
        self.mainLayout = QVBoxLayout(self.centralWidget())

        self.mainLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        self.groupBox = QGroupBox("Enter your details")
        self.groupBoxLayout = QGridLayout()

        self.cnicLabel = QLabel("CNIC")
        self.cnicInput = QLineEdit(self)
        self.cnicInput.setObjectName("cnicInput")
        self.groupBoxLayout.addWidget(self.cnicLabel, 0, 0)
        self.groupBoxLayout.addWidget(self.cnicInput, 0, 1)

        self.phoneLabel = QLabel("Phone Number")
        self.phoneInput = QLineEdit(self)
        self.phoneInput.setObjectName("phoneInput")
        self.groupBoxLayout.addWidget(self.phoneLabel, 1, 0)
        self.groupBoxLayout.addWidget(self.phoneInput, 1, 1)

        self.ipLabel = QLabel("IP Address")
        self.ipInput = QLineEdit(self)
        self.ipInput.setObjectName("ipInput")
        self.groupBoxLayout.addWidget(self.ipLabel, 2, 0)
        self.groupBoxLayout.addWidget(self.ipInput, 2, 1)
        
        self.domainLabel = QLabel("Domain")
        self.domainInput = QLineEdit(self)
        self.domainInput.setObjectName("DomainInput")
        self.groupBoxLayout.addWidget(self.domainLabel, 3, 0)
        self.groupBoxLayout.addWidget(self.domainInput, 3, 1)

        self.groupBox.setLayout(self.groupBoxLayout)
        self.mainLayout.addWidget(self.groupBox)

        self.mainLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.submitButton = QPushButton("Submit")
        self.submitButton.setObjectName("submitButton")
        self.submitButton.clicked.connect(self.onSubmit)
        self.mainLayout.addWidget(self.submitButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setStyleSheet(self.getStylesheet())
        self.show()
    
    def getStylesheet(self):
        return """
        QWidget {
            background-color: #2e2e2e;
            color: white;
        }
        QLabel {
            color: white;
            font-size: 14px;
        }
        QLineEdit {
            border: 1px solid #cccccc;
            border-radius: 10px;
            padding: 8px;
            font-size: 14px;
            background: rgba(255, 255, 255, 0.8);
            color: black;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QGroupBox {
            font-size: 16px;
            font-weight: bold;
        }
        """


    def onSubmit(self):
        phone = self.phoneInput.text().strip()
        ip = self.ipInput.text().strip()
        domain = self.domainInput.text().strip()
        cnic = self.cnicInput.text().strip()

        if ip != "":
            ip_params = {"IP" :get_ip_info_2(ip)}
            ip_window = OutputWindow(ip_params)
            ip_window.exec()

        if domain != "":
            ip = domain_to_ip(domain)
            domain_params = {"Domain : ":get_ip_info_2(ip)}
            domain_window = OutputWindow(domain_params)
            domain_window.exec()
            
        if phone != "":
            phone_params = {"Phone" : get_cnic_tel(phone)}
            phone_window = OutputWindow(phone_params)
            phone_window.exec()


        if cnic != "":
            cnic_params = {"Cnic Info : ":get_cnic_tel(cnic)}
            cnic_window = OutputWindow(cnic_params)
            cnic_window.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = InputForm()
    sys.exit(app.exec())

