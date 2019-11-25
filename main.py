from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(300))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def index():
    return redirect('http://127.0.0.1:5000/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.method == 'POST':
        post_title = request.form['post-title']
        post_body = request.form['post-body']
        title_error = 'hidden'
        body_error = 'hidden'

        if not post_title or not post_body:
            if not post_title:
                title_error = 'visible'
            if not post_body:
                body_error = 'visible'

            return render_template('newpost.html', title_error=title_error, body_error=body_error, post_title=post_title, post_body=post_body)

        new_post = Blog(post_title, post_body)
        db.session.add(new_post)
        db.session.commit()

        posts = Blog.query.order_by(Blog.id.desc()).first()

        return render_template('post.html',posts=posts)
            

    if request.args:
        post_id = request.args.get('id')
        posts = Blog.query.filter_by(id=post_id).all()
        return render_template('post.html', posts=posts)

    
    posts = Blog.query.all()

    return render_template('blog.html',posts=posts)

@app.route('/newpost')
def newpost():

    return render_template('newpost.html', post_title='', post_body='')

if __name__ == '__main__':
    app.run()