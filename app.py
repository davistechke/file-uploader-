import os, json
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, send_from_directory)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'cracked-secret-2024-xK9mP')

ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'mack')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'ajega')
UPLOAD_FOLDER  = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
META_FILE      = os.path.join(UPLOAD_FOLDER, '_meta.json')
ALLOWED_EXTENSIONS = {
    'exe','apk','zip','rar','7z','dmg','pkg','deb',
    'pdf','txt','py','js','mp4','mp3','iso','tar','gz'
}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

def load_meta():
    if os.path.exists(META_FILE):
        try:
            with open(META_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_meta(meta):
    with open(META_FILE, 'w') as f:
        json.dump(meta, f, indent=2)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_files():
    meta  = load_meta()
    files = []
    for fname in os.listdir(UPLOAD_FOLDER):
        if fname == '_meta.json':
            continue
        fpath = os.path.join(UPLOAD_FOLDER, fname)
        if os.path.isfile(fpath):
            size = os.path.getsize(fpath)
            desc = meta.get(fname, {}).get('description', '')
            files.append({
                'name':        fname,
                'size':        size,
                'size_str':    fmt_size(size),
                'ext':         fname.rsplit('.', 1)[-1].lower() if '.' in fname else 'bin',
                'description': desc,
            })
    return sorted(files, key=lambda x: x['name'].lower())

def fmt_size(b):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if b < 1024:
            return f'{b:.1f} {unit}'
        b /= 1024
    return f'{b:.1f} TB'

@app.route('/')
def index():
    return render_template('index.html', files=get_files())

@app.route('/download/<filename>')
def download(filename):
    safe = secure_filename(filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], safe, as_attachment=True)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST' and 'login' in request.form:
        if (request.form.get('username') == ADMIN_USERNAME and
                request.form.get('password') == ADMIN_PASSWORD):
            session['admin'] = True
            flash('Welcome back, Mack!', 'success')
            return redirect(url_for('admin'))
        flash('Wrong credentials.', 'error')
    if not session.get('admin'):
        return render_template('admin.html', logged_in=False, files=[])
    return render_template('admin.html', logged_in=True, files=get_files())

@app.route('/admin/upload', methods=['POST'])
def upload():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    uploaded    = request.files.getlist('files')
    description = request.form.get('description', '').strip()
    meta        = load_meta()
    count       = 0
    for f in uploaded:
        if f and f.filename and allowed_file(f.filename):
            fname = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
            meta[fname] = {'description': description}
            count += 1
    if count:
        save_meta(meta)
        flash(f'{count} file(s) uploaded successfully.', 'success')
    else:
        flash('No valid files uploaded.', 'error')
    return redirect(url_for('admin'))

@app.route('/admin/update_desc', methods=['POST'])
def update_desc():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    fname = request.form.get('filename', '').strip()
    desc  = request.form.get('description', '').strip()
    if fname:
        meta = load_meta()
        if fname not in meta:
            meta[fname] = {}
        meta[fname]['description'] = desc
        save_meta(meta)
        flash(f'Description updated for {fname}.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/delete/<filename>', methods=['POST'])
def delete_file(filename):
    if not session.get('admin'):
        return redirect(url_for('admin'))
    safe  = secure_filename(filename)
    fpath = os.path.join(app.config['UPLOAD_FOLDER'], safe)
    if os.path.exists(fpath):
        os.remove(fpath)
        meta = load_meta()
        meta.pop(safe, None)
        save_meta(meta)
        flash(f'{filename} deleted.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin'))

@app.route('/health')
def health():
    from flask import jsonify
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
