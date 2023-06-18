from flask import render_template, redirect, request, abort, url_for, send_from_directory, session
from werkzeug.security import generate_password_hash, check_password_hash
from   werkzeug.utils import secure_filename
from app.models import *
from app import app
import os
import secrets
import string
import fitz
from PIL import Image
import io

app.config['APP_ROOT'] = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(app.config['APP_ROOT'], 'static', 'uploads')


def get_current_user():
    user = None
    
    if 'user' in session:
        user = session['user']
        user = Users.query.filter(Users.username==user).first()
        return user
    
    
@app.route('/')
def home(page=1):
    user = get_current_user()
    path = app.config['UPLOAD_FOLDER']

    files_extensions=current_file_type=current_file_extension=None
    
    if request.args:
        file_type = request.args.get('file_type', '').upper()
        file_extension = request.args.get('file_extension', '').upper()
        
        if (file_type != '') and (file_type in app.config['ALLOWED_FILES_AND_EXTENSIONS'].keys()) and file_extension == 'ALL':
            files_extensions = app.config['ALLOWED_FILES_AND_EXTENSIONS'][file_type]
            current_file_type = file_type
            current_file_extension = file_extension
            files = Files.query.filter(Files.file_type==file_type)
            
        elif (file_type != '') and (file_type in app.config['ALLOWED_FILES_AND_EXTENSIONS'].keys()) and (file_extension != 'ALL') and (file_extension in app.config['ALLOWED_FILES_AND_EXTENSIONS'][file_type]):
                files_extensions = app.config['ALLOWED_FILES_AND_EXTENSIONS'][file_type]
                current_file_type = file_type
                current_file_extension = file_extension
                files = Files.query.filter(Files.extension==file_extension.upper())

        else:
            files = Files.query
            
    else:
        files = Files.query
        
    files = db.paginate(files, per_page=10)
    
    return render_template('home.html', path=path, files=files, user=user, files_types=app.config['ALLOWED_FILES_AND_EXTENSIONS'], files_extensions=files_extensions, current_file_type=current_file_type, current_file_extension=current_file_extension)



@app.route('/singup', methods=['GET', 'POST'])
def singup():
    user = get_current_user()
    error = None
    
    if request.method == 'POST':
        first_name = request.form['FirstName']
        last_name = request.form['LastName']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        check_user = Users.query.filter(Users.username==username).first()
        check_email = Users.query.filter(Users.email==email).first()
        
        if check_user and check_email:
            error = 'There was an issue on your register ): username alryead exists'
            return render_template('singup.html')
        
        hash_password = generate_password_hash(password, method='sha256') 
        
        new_user = Users(first_name=first_name, last_name=last_name, username=username, email=email, password=hash_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            session['user'] = username
            return redirect(url_for('home'))
        
        except:
            return "There was an issue on your register ):"
    
    return render_template('singup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    user = error = None
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
                
        user = Users.query.filter(Users.username==username, email==email).first()
        
        if user:
            
            check_password = check_password_hash(user.password, password)
            if check_password:
                session['user'] = user.username
                return redirect(url_for('home'))
            
            else:
                error =  "There was an issue on your login ): password the incorrect"
                user = None
                
        else:
            error = "There was an issue on your login ): username or email the incorrect"
                 
    data = {
    'user': user,
    'error': error
    }
    return  render_template('login.html', data=data)


@app.route('/logout')
def logout():
    user = get_current_user()
    
    if not user:
        return redirect(url_for('login'))
    
    session.pop('user', None)
    return redirect(url_for('home'))


def allowed_file(filename, file_type):
    
    if not '.' in filename and not filename == '':
        return False
    
    extension = filename.rsplit('.')[1].upper()
    
    if extension.upper() in app.config['ALLOWED_FILES_EXTENSIONS']:
        if (file_type in app.config['ALLOWED_FILES_AND_EXTENSIONS'].keys()) and (extension in app.config['ALLOWED_FILES_AND_EXTENSIONS'][file_type]):
            return True
        return False
    else:
        return False    

def get_cover_image(filepath, filename):
    doc = fitz.Document(filepath)
    page = doc.load_page(0)
    xref = page.get_images()[0][0]
    baseImage = doc.extract_image(xref)
    image = Image.open(io.BytesIO(baseImage['image']))    
    image.save(f'{filename}')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    user = get_current_user()
    
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        file = request.files['file']
        bio = request.form['bio']
        file_type = request.form['type'].upper()
        
        if not allowed_file(file.filename, file_type):
            return redirect(request.url)
        
        else:
            filename = secure_filename(file.filename)
            filename = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(5)) + '_' + filename
            extension = filename.rsplit('.')[1].upper()
            file_path = file_type + '\\' + filename
            image_name = filename
            
            try:    
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],  file_path))
                
                if extension == 'PDF':
                    img_name = 'Image' + '\\' + filename[: -4] + '.jpg'
                    image_name = filename[: -4] + '.jpg'
                    get_cover_image(os.path.join(app.config['UPLOAD_FOLDER'], file_path), os.path.join(app.config['UPLOAD_FOLDER'], img_name))
                    
                new_file = Files(name=filename, cover_image=image_name, user_id=user.id, bio=bio, file_type=file_type, extension=extension)
                db.session.add(new_file)
                db.session.commit()
                return redirect(url_for('home'))
            
            except:
                return "There was an issue on your register ):"
            
    return render_template('upload.html', user=user)



@app.route('/files/<int:file_id>')
def file_view(file_id):
    do = False
    current_user = get_current_user()
    file = Files.query.get_or_404(file_id)
    user = Users.query.filter(Users.id==file.user_id).first()
    
    if current_user:
        if current_user.id == user.id:
            do = True
    
    return render_template('file_view.html', file=file, user=user, current_user=current_user, do=do)



@app.route('/files/<int:file_id>/download')
def download(file_id):
    current_user = get_current_user()
    
    if not current_user:
        return redirect(url_for('login'))
    
    file = Files.query.get_or_404(file_id)
    filename = file.file_type + '/' + file.name
    
    try:
        return send_from_directory(directory=app.config['UPLOAD_FOLDER'], path=filename, as_attachment=True, current_user=current_user)
    
    except FileNotFoundError:
        abort(404)



@app.route('/user/<string:username>')
def user_view(username):
    current_user = get_current_user()
    try:
        user = Users.query.filter(Users.username==username).first()
        files = Files.query.filter(Files.user_id==user.id).all()
        
    except:
        return "User note foind"
    
    return render_template('user_view.html', files=files, user=user, current_user=current_user)


@app.route('/profile/<int:id>', methods=['GET', 'POST'])
def profile(id):
    current_user = get_current_user()
    
    if not current_user:
        return redirect(url_for('login'))
    
    user = Users.query.get_or_404(id)
    if not current_user.id == user.id:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        password = request.form['password']
        profile_pic = request.files['file']

        hash_password = generate_password_hash(password, method='sha256') 
        if not allowed_file(profile_pic.filename, 'IMAGE'):
            return redirect(request.url)
        
        else:
            filename = secure_filename(profile_pic.filename)
        
            user.first_name = request.form['FirstName']
            user.last_name = request.form['LastName']
            user.username = request.form['username']
            user.email = request.form['email']
            user.bio = request.form['bio']
            user.password = hash_password
            user.profile_pic = filename
            
            try:    
                profile_pic.save(os.path.join(os.path.join(app.config['APP_ROOT'], 'static', 'img'),  filename))
                db.session.commit()
                return redirect(url_for('user_view', username=request.form['username']))
            except:
                return "oh noooooooooo"
        
    
    return render_template('profile_edit.html', user=user, current_user=current_user)


@app.route('/delete/<int:id>')
def delete(id):
    file_to_delete = Files.query.get_or_404(id)
    
    try:
        db.session.delete(file_to_delete)
        db.session.commit()
        return redirect(url_for('home'))
    except:
        return "There was an problem delteting that file ):"
    