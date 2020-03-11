from flask import Flask, render_template, request, session, make_response, jsonify

from src.common.database import Database
from src.common.utils import Utils
from src.models import user
from src.models.blog import Blog
from src.models.post import Post
from src.models.races import Sched_Event

from src.models.user import User



app = Flask(__name__)
app.config.from_object('src.config')
app.secret_key = "jose"

@app.route('/')
def home_template():
    return render_template('home.html')


@app.route('/login')
def login_template():
    return render_template('login.html')

@app.route('/register')
def register_template():
    return render_template('register.html')

@app.before_first_request
def initialize_database():
    Database.initialize()

@app.route('/auth/login', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']

    if User.login_valid(email, password):
        User.login(email)
    else:
        session['email'] = None

    return render_template("profile.html", email=session['email'])

@app.route('/auth/register', methods=['POST'])
def register_user():
    email = request.form['email']
    password = request.form['password']

    User.register(email, password)

    return render_template("profile.html", email=session['email'])

@app.route('/blogs/<string:user_id>')
@app.route('/blogs')
def user_blogs(user_id=None):
    if user_id is not None:
        user = User.get_by_id(user_id)
    else:
        user = User.get_by_email(session['email'])

    blogs = user.get_blogs()

    return render_template("user_blogs.html", blogs=blogs, email=user.email)

@app.route('/blogs/new', methods=['POST', 'GET'])
def create_new_blog():
    if request.method == 'GET':
        return render_template('new_blog.html')
    else:
        title = request.form['title']
        description = request.form['description']
        user = User.get_by_email(session['email'])

        new_blog = Blog(user.email, title, description, user._id)
        new_blog.save_to_mongo()

        return make_response(user_blogs(user._id))

@app.route('/posts/<string:blog_id>')
def blog_posts(blog_id):
    blog = Blog.from_mongo(blog_id)
    posts = blog.get_posts()

    return render_template('posts.html', posts=posts, blog_title=blog.title, blog_id=blog._id)

@app.route('/posts/new/<string:blog_id>', methods=['POST', 'GET'])
def create_new_post(blog_id):
    if request.method == 'GET':
        return render_template('new_post.html', blog_id=blog_id)
    else:
        title = request.form['title']
        content = request.form['content']
        user = User.get_by_email(session['email'])

        new_post = Post(blog_id, title, content, user.email)
        new_post.save_to_mongo()

        return make_response(blog_posts(blog_id))

@app.route('/nascar')
def nascar_template():
    return render_template('nascar_home.html')


@app.route('/nascar/admin')
def nascar_admin_template():
    races = Sched_Event.find_by_year('2020')
    return render_template('nascar_admin.html', races=races)


@app.route('/background_process')
def background_process():
    try:
        lang = request.args.get('proglang', 0, type=str)
        if lang.lower() == 'python':
            return jsonify(result="you are correct")
        else:
            return jsonify(result="try again")
    except Exception as e:
        return str(e)



@app.route('/nascar/load', methods=['POST', 'GET'])
def nascar_load_template():
    type1 = request.form['type']
    year = request.form['year']
    series = request.form['series']
    file = request.form['file']
    data = Utils.get_from_sportradar(type1, year, series, file)
    race_list = Sched_Event.extract_sportradar_data(data)
    #load_list = Sched_Event.define_load_list(race_list)
    #if len(load_list) == 0:
    #    load_list = "none"
    load_list = []
    ignore_list = []
    for race in race_list:
        test = race.get_race_id()
        test1 = Sched_Event.find_by_race_id(test)
        if test1 is True:
            race.save_to_mongo()
            load_list.append(race)
        else:
            ignore_list.append(race)

    #races_loaded = load_list[0]
    races = Database.find(collection="races", query={"year": int(year)})
    #races_ignored = load_list[1]
    text = "load successful"
    return render_template('races_list.html', text=text, races=load_list, ignore_list = ignore_list)
  #  return render_template('races_list.html', data=data)


@app.route('/interactive')
def interactive():
    return render_template('interactive.html')



if __name__ == '__main__':
   app.run(debug=app.config['DEBUG'], port=4990)

