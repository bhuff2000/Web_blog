from flask import Flask, render_template, request, session, make_response, jsonify, json
from flask_socketio import SocketIO, emit, send, join_room, leave_room, rooms

from bson.json_util import dumps, loads
from src.common.database import Database
from src.common.utils import Utils
from src.models import user
from src.models.blog import Blog
from src.models.entrants import Entrants
from src.models.post import Post
from src.models.races import Sched_Event
from src.models.test import Test
from src.models.user import User



app = Flask(__name__)
app.config.from_object('src.config')
app.secret_key = "jose"
socketio =SocketIO(app)
room_lst =[]

@app.route('/')
def home_template():
    return render_template('home.html')

# +++++++++++++++ Socket Code ++++++++++++++++++++++++++++++++++++++++++++++++++
@app.route('/draft')
def load_draft():
    return render_template('draft.html', email=session['email'] )

@socketio.on('join', namespace='/draft2')
def new_draft(newDraft):
    user_rm = request.sid
    user = session['email']
    print(user)
    room = newDraft['draft_name']
    print(room)
    found = False
    rms = rooms()
    print(rms)
    for rm in room_lst:
        rm1 = rm['draft_name']
        if rm1 == room:
            found = True
    print(found)
    if found:
        print('iam in if')
        emit('user join room', {'draft_name': room, 'user': user}, room=room, broadcast=True)
    else:
        print('iam in else')
        room_lst.append(newDraft)
        print(room)
        join_room(room)

        emit('new draft', {'draft_name': room, 'user': user}, room=room, broadcast=True)





@socketio.on('get_room_list', namespace='/draft2')
def get_room_list():
    room_list = room_lst
    print(room_list)
    emit('rec_room_list', room_list)

#@socketio.on('my event')
#def my_custom_event(json):
#    print('my event: ' + str(json))
#    send(json, broadcast=True)

#@app.route('/originate')
#def originate():
#    socketio.emit('server originated', 'Something happened on server')
#    return '<h1>Sent!</h1>'

#@socketio.on('message from user', namespace='/draft2')
#def receive_message_from_user(message):
#    print(request.sid)
#    print('USER MESSAGE: {}'.format(message))
#    emit('from flask', message.upper(), broadcast=True)

#@socketio.on('username', namespace='/draft2' )
#def receive_username(username):
#    users.update({username :  request.sid})
#    print('Username: '+ username + ' added!')

#**@socketio.on('private_message', namespace='/draft2')
#**def private_message(payload):
#**    user = payload['username']
#**    recipient_session_id = users[user]
#**    message = payload['message']
#**    print(message + ' : ' + recipient_session_id)
#**    emit('new_private_message', message, room=recipient_session_id)



#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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


@app.route('/backgroundProcess')
def background_process():

    #lang = request.args.get('proglang', 0, type=str)    #code used for successful race_id
    #cursor = Sched_Event.find_one_race(lang)            #code used for successful race_id
    #cur_dump = dumps(cursor)                            #code used for successful race_id
    #return cur_dump                                    #code used for successful race_id
    series = request.args.get('proglang', 0, type=str)
    cursor = Sched_Event.find_by_series(series)
    ser_to_json = dumps(cursor)
    ser_to_json1 = ser_to_json[10]
    return ser_to_json


@app.route('/ajax_get_races')
def ajax_get_races():
    series = request.args.get('series', 0, type=str)
    if series == "sc":
        series1 = "CUP"
    elif series == "xf":
        series1 = "XFINITY"
    elif series == "go":
        series1 = "TRUCK"
    else:
        series1 = "na"
    cursor = Sched_Event.find_by_series(series1)
    ser_to_json = dumps(cursor)
    return ser_to_json


@app.route('/load/entrants', methods=['POST', 'GET'])
def load_entrants():
    type1 = 'races'
    race_id = request.form['race_drop_down_abc']
    series = request.form['series_drop_down']
    file = 'entry_list.json'
    data = Utils.get_from_sportradar(series, type1, race_id, file)
    if data is not None:
        entrant_list = Entrants.extract_sportradar_data(data)
    else:
        text = "No data returned from SportRadar"
        return render_template('drivers_load.html', text=text)

    load_list = []
    ignore_list = []
    for entrant in entrant_list:
        test_race_id = entrant.get_race_id()
        test_drv_id = entrant.get_drv_id()
        test = Entrants.find_by_race_and_drv_id(test_race_id, test_drv_id)
        if test is True:
            entrant.save_to_mongo()
            load_list.append(entrant)
        else:
            ignore_list.append(entrant)

    #races = Database.find(collection="entrants", query={"race_id": race_id})
    text = "load successful"
    return render_template('drivers_load.html', text=text, entrants=load_list, ignore_list=ignore_list)
    #return render_template('drivers_load.html', text=race_id)

#  return render_template('races_list.html', data=data)

@app.route('/nascar/load', methods=['POST', 'GET'])
def nascar_load_template():
    type1 = request.form['type']
    year = request.form['year']
    series = request.form['series']
    file = request.form['file']
    data = Utils.get_from_sportradar(series, year, type1, file)
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


@app.route('/interactive', methods=['POST', 'GET'] )
def interactive():
    #race_id = "91259bd6-010c-4e48-b69e-e22ea1cda9ec"   #code used for successful race_id
    #race_name=Sched_Event.find_one_race(race_id)       #code used for successful race_id
    #rn_dump = dumps(race_name)                         #code used for successful race_id
    #return render_template('interactive.html', race_name=rn_dump)  #code used for cuccessful race_id
    series = "CUP"
    cursor = Sched_Event.find_by_series(series)
    ser_list1 = loads(dumps(cursor))    #internal server error when loads is not included - need to understand why as it works above with single item
    #ser_list = loads(ser_list1)
    ser_list3 = ser_list1[15]["race_name"]
    return render_template('interactive.html', ser_list=ser_list1)


@app.route('/test', methods=['POST', 'GET'])
def test():
    test = "this working?"
    return render_template('test.html', test=test)

if __name__ == '__main__':
    socketio.run(app, DEBUG=True)
   #app.run(debug=app.config['DEBUG'], port=4990)

