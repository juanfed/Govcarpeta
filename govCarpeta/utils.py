import requests
import json
import urllib.parse
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import subprocess
import os


""" ------------------SMTP Email Send------------------ """
def sendEmail(sender, receiver, subject, HTMLBodyPath):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'st0261.topicos@gmail.com'
    #sender_email = sender
    receiver_email = 'dmadridr@eafit.edu.co'
    #receiver_email = receiver
    password = 'cicanudnyterpilq'
    #password = 'Topicos2023**'

    message = MIMEMultipart('alternative')
    message['Subject'] = '[GovCarpetaSystem]: Mensaje desde Operador'
    #message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = receiver_email

    with open('html/index2.html', 'r') as file:
        html = file.read()

    """with open(HTMLBodyPath, 'r') as file:
        html = file.read()"""

    part = MIMEText(html, 'html')
    message.attach(part)

    context = ssl.create_default_context()

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

""" ------------------PDF Compression------------------ """
# Compress a PDF using ghostscript
def compress_pdf(input_path, output_path):
    gs_command = ['gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4', '-dPDFSETTINGS=/screen', '-dNOPAUSE', '-dQUIET', '-dBATCH', f'-sOutputFile={output_path}', input_path]
    subprocess.run(gs_command)

""" ------------------PDF Conversion------------------ """
# Convert PDF to Binary string
def pdf_to_binary(file_path):
    with open(file_path, 'rb') as file:
        binary_data = file.read()
        encoded_data = base64.b64encode(binary_data)
        return encoded_data

# Convert Binary string to PDF
def binary_to_pdf(binary_data, output_path):
    decoded_data = base64.b64decode(binary_data)
    with open(output_path, 'wb') as file:
        file.write(decoded_data)

""" ------------------EndPoints------------------ """
def postRegisterCitizen(id, name, address, email, operatorId, operatorName):
    base_url = 'http://169.51.195.62:30174'
    register_endpoint = '/apis/registerCitizen'
    url = f'{base_url}{register_endpoint}'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    payload = {
        "id": id,
        "name": name,
        "address": address,
        "email": email,
        "operatorId": operatorId,
        "operatorName": operatorName
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    statusCode = response.status_code
    if statusCode == 200:
        response_data = response.json()
        return f'{statusCode}, {response_data}'
    elif statusCode == 201:
        return f'{statusCode}, Created'
    elif statusCode == 501:
        return f'{statusCode}, Error: Not Implemented'
    else:
        return 'Error:', statusCode

def authenticateDocument(id, path, title):
    base_url = 'http://169.51.195.62:30174'
    documentId = id
    documentPath = urllib.parse.quote_plus(path)
    documentTitle = title
    
    authenticate_endpoint = f'/apis/authenticateDocument/{documentId}/{documentPath}/{documentTitle}'
    url = f'{base_url}{authenticate_endpoint}'
    headers = {
        'accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    statusCode = response.status_code
    if statusCode == 200:
        response_data = response.json()
        return f'{statusCode}, {response_data}'
    elif statusCode == 204:
        return f'{statusCode}, Not Content'
    elif statusCode == 500:
        return f'{statusCode}, failed: Application Error...'
    elif statusCode == 501:
        return f'{statusCode}, failed: Wrong Parameters...'
    else:
        return 'Error:', statusCode

#print(authenticateDocument(1234567896, '/data/folder1/cedula.pdf', 'Cedula'))
def validateCitizen(id):
    base_url = 'http://169.51.195.62:30174'
    citizen_id = id
    validate_endpoint = f'/apis/validateCitizen/{citizen_id}'
    url = f'{base_url}{validate_endpoint}'
    headers = {
        'accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    statusCode = response.status_code
    if statusCode == 200:
        response_data = response.json()
        return f'{statusCode}, {response_data}'
    elif statusCode == 204:
        return f'{statusCode}, Not Content'
    elif statusCode == 500:
        return f'{statusCode}, failed: Application Error...'
    elif statusCode == 501:
        return f'{statusCode}, failed: Wrong Parameters...'
    else:
        return 'Error:', statusCode
    

""" ------------------PathHandling------------------ """
def add_folder_structure(folder_structure, path):
    folders = path.split('/')
    current_folder = folder_structure
    for i, folder in enumerate(folders):
        if folder not in current_folder:
            current_folder[folder] = {}
        current_folder = current_folder[folder]
        if i == len(folders) - 1:  # Last folder in the path
            if '.' in folder:  # Check if the folder contains a file format
                file_name, file_extension = folder.split('.')
                current_folder['docContent'] = 'null'
                current_folder['docTitle'] = folder
                current_folder['isVerified'] = False
    return folder_structure

folder_structure = {}
path5 = 'COMFAMA/Salud/RUT/RUT.pdf'
folder_structure = add_folder_structure(folder_structure, path5)

path6 = 'COMFAMA/Pension/Cedula/cedula1.pdf'
folder_structure = add_folder_structure(folder_structure, path6)
path7 = 'COMFAMA/Pension/Cedula/cedula2.pdf'
folder_structure = add_folder_structure(folder_structure, path7)

cedula_field = folder_structure['COMFAMA']['Pension']['Cedula']['cedula1.pdf']
print(cedula_field)
jsonOutput = json.dumps(folder_structure, indent=4)
print(jsonOutput)
