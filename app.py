from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import os
from utils.crypto_utils import encrypt, decrypt
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)
app.secret_key = 'cambia_esto_por_una_clave_secreta_en_el_repo'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        operation = request.form.get('operation')
        mode = request.form.get('mode')
        key_bits = int(request.form.get('key_bits'))
        password = request.form.get('password', '')
        plaintext = request.form.get('plaintext', '')

        if not password:
            flash('La clave no puede estar vacía.', 'error')
            return redirect(url_for('index'))

        if operation == 'encrypt':
            if not plaintext:
                flash('Introduce texto para encriptar.', 'error')
                return redirect(url_for('index'))
            payload = encrypt(plaintext, password, mode, key_bits)
            filename = secure_filename(f'cipher_{mode}_{key_bits}.txt')
            return send_file(
                io.BytesIO(payload.encode('utf-8')),
                as_attachment=True,
                download_name=filename,
                mimetype='text/plain'
            )
        else:
            file = request.files.get('cipherfile')
            input_text = request.form.get('ciphertextarea', '').strip()
            payload = None
            if file and file.filename:
                payload = file.read().decode('utf-8')
            elif input_text:
                payload = input_text
            else:
                flash('Sube un fichero .txt con el ciphertext o pega el contenido.', 'error')
                return redirect(url_for('index'))
            try:
                plaintext = decrypt(payload, password)
                result = plaintext
            except Exception as e:
                flash(f'Error al desencriptar: {str(e)}', 'error')
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
