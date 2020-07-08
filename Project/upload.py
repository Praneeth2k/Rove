from flask import Flask,render_template, redirect,url_for
from flask_wtf import FlaskForm
from wtforms import FileField
from flask_uploads import UploadSet,configure_uploads,IMAGES
from werkzeug.utils import secure_filename

app=Flask(__name__)

app.config['SECRET_KEY']="THISISTOPSECRET"

app.config['UPLOADS_DEFAULT_DEST']='static/images/uploads'

pics = UploadSet('pics',IMAGES)

configure_uploads(app,pics)

class PicForm(FlaskForm):
    pic=FileField('Profile Pic')

@app.route('/')
def index():
    return redirect(url_for('profile'))
    
@app.route('/profile' , methods=['GET','POST'])
def profile():
    form = PicForm()

    if form.validate_on_submit():
        print(form.pic.data)
        
        filename=secure_filename(pics.save(form.pic.data))
        return f"filename = {filename}"

    return render_template('imageupload.html',form = form)

