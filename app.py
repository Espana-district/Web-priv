
from flask import Flask, render_template, request, redirect, session
import os
import shutil
import subprocess
import datetime

app = Flask(__name__)
app.secret_key = "CAMBIA_ESTO_POR_UNA_CLAVE_SEGURA"

PASSWORD = "CAMBIA_TU_PASSWORD"
BOT_FILE = "bot.py"
BACKUP_FOLDER = "backups"

os.makedirs(BACKUP_FOLDER, exist_ok=True)

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        password = request.form.get('password')

        if password == PASSWORD:
            session['logged'] = True
            return redirect('/')

    return render_template('login.html')

def check_login():
    return session.get('logged')

@app.route('/', methods=['GET', 'POST'])
def index():

    if not check_login():
        return redirect('/login')

    mensaje = ''

    if not os.path.exists(BOT_FILE):
        with open(BOT_FILE, 'w', encoding='utf-8') as f:
            f.write('# Archivo bot.py')

    with open(BOT_FILE, 'r', encoding='utf-8') as f:
        codigo = f.read()

    if request.method == 'POST':

        nuevo_codigo = request.form.get('codigo')

        fecha = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

        backup_name = f'backup_{fecha}.py'

        shutil.copy(
            BOT_FILE,
            os.path.join(BACKUP_FOLDER, backup_name)
        )

        temp_file = 'temp_bot.py'

        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(nuevo_codigo)

        result = subprocess.run(
            ['python', '-m', 'py_compile', temp_file],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:

            mensaje = f'''
            <div class="error-box">
            ❌ ERROR DE SINTAXIS
            <pre>{result.stderr}</pre>
            </div>
            '''

            os.remove(temp_file)

        else:

            shutil.move(temp_file, BOT_FILE)

            mensaje = '''
            <div class="success-box">
            ✅ Código actualizado correctamente
            </div>
            '''

            codigo = nuevo_codigo

    return render_template(
        'index.html',
        codigo=codigo,
        mensaje=mensaje
    )

@app.route('/restart')
def restart():

    if not check_login():
        return redirect('/login')

    return '''
    <h2>⚠️ Reinicia el bot manualmente desde el panel del hosting.</h2>
    <a href='/'>Volver</a>
    '''

@app.route('/backups')
def backups_page():

    if not check_login():
        return redirect('/login')

    archivos = os.listdir(BACKUP_FOLDER)

    return render_template(
        'backups.html',
        archivos=archivos
    )

@app.route('/restore/<archivo>')
def restore(archivo):

    if not check_login():
        return redirect('/login')

    ruta = os.path.join(BACKUP_FOLDER, archivo)

    if os.path.exists(ruta):

        shutil.copy(ruta, BOT_FILE)

        return '''
        <h2>✅ Backup restaurado correctamente</h2>
        <a href='/'>Volver</a>
        '''

    return '❌ Backup no encontrado'

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')

if __name__ == '__main__':

    port = int(os.environ.get('PORT', 5000))

    app.run(
        host='0.0.0.0',
        port=port
    )
