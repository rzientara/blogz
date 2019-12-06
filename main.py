from flask import Flask, request, redirect, render_template, session
import re
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'ajliefjiasjefla'

####################################
#   Classes
####################################

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(300))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

####################################
#   Routes
####################################

#check if user is logged in
@app.before_request
def require_login():
    allow_routes = ['login', 'signup']
    if request.endpoint not in allow_routes and 'username' not in session:
        return redirect('/login')

#display all users
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

#display all blog posts
#render post page if a user or post is selected
@app.route('/blog', methods=['POST', 'GET'])
def blog():
    #check if a link is clicked
    if request.args:
        #get post id from args
        post_id = request.args.get('id')
        #if there is no post id, a username link was clicked
        if not post_id:
            #get username, filter to user, filter to that user's posts
            username = request.args.get('user')
            user = User.query.filter_by(username=username).first()
            posts = Blog.query.filter_by(owner_id=user.id).all()

            users = User.query.all()
            return render_template('post.html', posts=posts, users=users)
        #filter to post with id matching clicked link
        posts = Blog.query.filter_by(id=post_id).first()

        return render_template('post.html', posts=posts)
    
    posts = Blog.query.all()
    users = User.query.all()

    return render_template('blog.html', posts=posts, users=users)

#display page for new posts
#render the new post's page when it is successfully submitted
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        post_title = request.form['post-title']
        post_body = request.form['post-body']

        if not post_title or not post_body:
            error = "we need both a title and a body!"
            return render_template('newpost.html', error=error, post_title=post_title, post_body=post_body)

        owner = User.query.filter_by(username=session['username']).first()
        new_post = Blog(post_title, post_body, owner)
        db.session.add(new_post)
        db.session.commit()

        posts = Blog.query.order_by(Blog.id.desc()).first()

        return render_template('post.html',posts=posts)
    return render_template('newpost.html', post_title='', post_body='')

#display the login page
#redirect to newpost page when login is successful
@app.route('/login',  methods=['POST', 'GET'])
def login():
    #verifying login information
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if user.password == password:
                session['username'] = username
                return redirect('newpost')
            else:
                error = "Invalid password"
        else:
            error = "Invalid username"
        
        return render_template('login.html', error=error, username=username)

    return render_template('login.html')

#logout user
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

#display signup page
#render newpost page when signup is successful
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    #verify signup information
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        messages = ["That's not a valid username",
                    "That's not a valid password",
                    "Passwords don't match"]

        #reset error status
        error = False

        #list containing the valid status of user inputs.
        try:
            val_list
        except:
            val_list = ['', '', '']

        #validate username has proper length and no spaces.
        val_list[0] = re.search('^.{3,50}$', username)
        if re.search(' ', username):
            val_list[0] = None

        #validate password has proper length and no spaces.
        val_list[1] = re.search('^.{3,50}$', password)
        if re.search(' ', password):
            val_list[1] = None

        #validate password and repeated password match.
        if password != verify:
            val_list[2] = None
        else:
            val_list[2] = ""

        #if a user input is invalid, replace its value with the appropriate error message and set Error to True.
        #if the input is valid, replace its value with empty string.
        for item in val_list:
            if item == None:
                val_list[val_list.index(item)] = messages[val_list.index(item)]
                error = True
            else:
                val_list[val_list.index(item)] = ""

        #if Error is True, render login.html with the errors.
        #if Error is False, render blog.html.
        if error == True:
            return render_template('signup.html', user_error=val_list[0], pass_error=val_list[1], verify_error=val_list[2], username=username)
        else:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return render_template('newpost.html')
            else:
                #checks for duplicate username
                val_list[0] = 'A user with that username already exists'
                return render_template('signup.html', user_error=val_list[0], pass_error=val_list[1], verify_error=val_list[2], username=username)

    return render_template('signup.html')

if __name__ == '__main__':
    app.run()