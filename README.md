# AES Encryption and Decryption Web App

## Resumen
Aplicación web (Flask) que permite encriptar y desencriptar texto usando AES en modos ECB, CBC y CFB. Soporta claves de 128 / 192 / 256 bits. El ciphertext se guarda en un fichero `.txt` (formato JSON con campos: mode, key_bits, salt, iv, ciphertext).

## Cómo ejecutar (local)
1. Crear entorno virtual (recomendado):
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

2. Ejecutar:
python app.py

3. Abrir http://127.0.0.1:5000 en el navegador.

