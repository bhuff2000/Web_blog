from flask import Flask, render_template, request, session, make_response, jsonify, json, redirect, url_for, flash
from flask_socketio import SocketIO, emit, send, join_room, leave_room, rooms
from flask_login import LoginManager, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from datetime import datetime
import logging
from logging import StreamHandler
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, email, Regexp

from bson.json_util import dumps, loads, ObjectId
from src.common.database import Database
from src.common.utils import Utils
from src.forms.create_pool import CreatePool, SelectRace
from src.forms.view_pool import SelectDriver, DriverList
from src.models import user
from src.models.blog import Blog
from src.models.draft_picks import Draft_Picks
from src.models.entrants import Entrants
from src.models.results import Results
from src.models.post import Post
from src.models.races import Sched_Event
from src.models.rooms import Room
from src.models.members import Room_Member
from src.models.messages import Message
from src.models.test import Test
from src.models.user import User
from src.forms.login import LoginForm
from src.forms.register import RegistrationForm



app = Flask(__name__)
app.config.from_object('src.config')
app.secret_key = "jose"
CORS(app, resources={r"/behoughton.com/*": {"origins": "*"}} ,supports_credentials=True)

file_handler = StreamHandler()
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
socketio =SocketIO(app, logger=True, engineio_logger=True, cors_allowed_origins="*")
login_manager = LoginManager()
login_manager.login_view = '/login'
login_manager.init_app(app)
Bootstrap(app)
csrf = CSRFProtect()
csrf.init_app(app)





@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response

room_lst =[]

@app.route('/')
def home_template():
    return render_template('home.html')

# +++++++++++++++ Socket Code ++++++++++++++++++++++++++++++++++++++++++++++++++
@app.route('/draft')
def load_draft():
    return render_template('draft.html', email=current_user.email )


@socketio.on('send_messages')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {}".format(data['username'], data['room'], data['message']))
    data['created_at'] = datetime.now()
    new_message = Message(data['room'], data['message'], data['username'])
    new_message.save_message()
    print(new_message.json())
    socketio.emit('receive message', {'username': data['username'], 'message': data['message']}, room=data['room'],
                  broadcast=True, include_self=True)

@socketio.on('start_draft')
def handle_start_draft(data):
    print(data)
    room_id = data["room_id"]
    print('in socket for pick list creation ' + str(room_id))
    members = Draft_Picks.create_and_save_pick_list(room_id)
    print(members)
    socketio.emit('start_draft_annc', {'pick_list': members}, broadcast=True, include_self=True)


@socketio.on('load_driver_pick')
def handle_load_driver_pick(data):
    driver_id = data["driver_id"]
    room_id = data["room_id"]
    race_id = Room.get_race_id(room_id)
    print(str(race_id))
    #race_id = room_data.race_id
    username = data["username"]
    pick_num = data["pick_num"]
    print("pick number " +str(pick_num))
    print('in socket for load driver pick ' + str(driver_id))
    drv_data = Entrants.find_by_driver_id(race_id, driver_id)
    print('drv_data '+ str(drv_data))
    Draft_Picks.update_pick(room_id, username, pick_num ,drv_data["car_num"], drv_data["drv_full"])
    next_pick = Draft_Picks.get_next_pick_data(room_id)
    pick_data = {"car_num": drv_data["car_num"], "drv_full": drv_data["drv_full"], "driver_id": drv_data["driver_id"],
                 "username": username, "pick_data":next_pick}
    print("pick_data" + str(pick_data))
    socketio.emit('driver_pick', {'driver_pick': pick_data}, broadcast=True, include_self=True)

@socketio.on('join_room')
def handle_join_room_event(data):
    #app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', {'username': current_user.username}, broadcast=True, include_self=True)


@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['username'], data['room']))
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data, room=data['room'], broadcast=True)

@socketio.on('join')
def new_draft(newDraft):
    user_rm = request.sid
    user = current_user.email
    print(user)
    room = newDraft['draft_name']
    print(room)
    found = False
    rms = rooms(namespace='/draft2')
    print(rms)
    for rm in room_lst:
        rm1 = rm['draft_name']
        if rm1 == room:
            found = True
    print(found)
    if found:
        print('iam in if')
        emit('user join room', {'draft_name': room, 'user': user}, room=room, broadcast=True, include_self=True)
    else:
        print('iam in else')
        room_lst.append(newDraft)
        print(room)
        join_room(room)
        emit('new draft', {'draft_name': room, 'user': user}, room=room, broadcast=True, include_self=True)


@socketio.on('get_room_list')
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
@app.route('/login', methods=['POST', 'GET'])
def login_template():
    form = LoginForm()
    email = form.email.data
    password = form.password.data

    if form.validate_on_submit():
        email = request.form["email"]
        password = request.form["password"]
        find_user = Database.find_one("users", {"email": email})
        if User.login_valid(email, password):
            loguser = User(find_user["email"], find_user["password"], find_user["username"], find_user["_id"])
            loguser.user_login()
            flash('You have been logged in!', 'success')
            return redirect(url_for('nascar_template'))
        else:
            flash('Login Unsuccessful.  Please check email and password', 'danger')
    return render_template('log_in.html', title='Login', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login_template'))

@login_manager.user_loader
def load_user(user_id):
    user = User.get_by_id(user_id)
    if user_id is not None:
        return User.get_by_id(user_id)
    else:
        return None



@app.route('/register', methods=['GET', 'POST'])
def register_template():
    form = RegistrationForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            username = request.form["username"]
            email = request.form["email"]
            password = Utils.hash_password(request.form["password"])
            find_user = User.get_by_email(email)
            if find_user is None:
                User.register(email, password, username)
                flash(f'Account created for {form.username.data}!', 'success')
                return render_template('profile.html', email=session['email'])
            else:
                flash(f'Account already exists for {form.username.data}!', 'success')
    return render_template('register.html', title='Register', form=form)

@app.before_first_request
def initialize_database():
    Database.initialize()

@app.route('/auth/login', methods=['POST'])
def login_user():


    #if current_user.is_authenticated():
    #    return redirect(url_for('profile'))

    email = request.form['email']
    password = request.form['password']

    if User.login_valid(email, password):
        User.login(email)
    else:
        session['email'] = None
    #return render_template("profile.html", email=session['email'])
    return redirect(url_for('nascar_template'))

@app.route('/auth/register', methods=['GET', 'POST'])
def register_user():

    email = request.form['email']
    password = request.form['password']
    username = request.form['username']

    User.register(email, password, username)

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
@login_required
def nascar_template():
    #fuck_sakes = Sched_Event.find_by_year(2020)
    #print(str(fuck_sakes))
    username = current_user.username
    print('user fing name ' + str(username))
    drafts = list(Room.get_by_username(username))
    #print(drafts[0])
    draft_list=[]
    for draft in drafts:
        room_data = Room.get_room_by_name(draft['room_name'])
        print(draft['room_name'])
        race_name = room_data.race_name
        draft_list.append({'race_name': race_name, 'room_name': draft['room_name'], 'room_id': draft['room_id']})
    return render_template('nascar_home.html', drafts=draft_list)



@app.route('/nascar/pool', methods=['GET', 'POST'])
@login_required
def nascar_pool():
    #form = CreatePool(meta={'csrf': False})
    form = CreatePool()

    if form.validate_on_submit():
        pool_name = form.pool_name.data
        race_id = form.race.data
        race_data = Sched_Event.find_one_race(race_id['races'])
        race_name = race_data['race_name']
        print(race_name)
     #   print(pool_name, ' ', race_id)

        members = [member.strip() for member in request.form.get('members').split(',')]
        if len(pool_name) and len(members):
            username = current_user.username
            new_pool = Room(pool_name, username, race_id, race_name)
            #print(new_pool.json())
            new_pool.save_room()
            room_data = Room.get_room_by_name(pool_name)
            if current_user.username in members:
                members.remove(current_user.username)
            for member in members:
                load_member = Room_Member(room_data._id, room_data.room_name, member,
                                      current_user.username, is_room_admin=False)
                load_member.add_room_member()

            return redirect(url_for('view_room', race_id=race_id, room_id=room_data._id))
        else:
            message = "Failed to create room"
            return render_template('create_pool.html', form= form, message=message)
    else:
        print('shit not working')
        print(form.race.errors)
    return render_template('create_pool.html', methods='POST',  form = form)

@app.route('/view-pool/<string:room_id>', methods=['GET', 'POST'])
@login_required
def view_room(room_id):
    form = SelectDriver()

    room_data = Room.get_room_by_id(room_id)
    room_name = room_data.room_name
    message=''
    #if request.method =='POST':
    room_members = Room.get_room_members(room_id)
    print("room Members " + str(room_members[0]["_id"]["username"]))
    race_id = room_data.race_id['races']
    print(race_id)
    drivers = Entrants.find_drivers_by_race_id(race_id)
    print(drivers)
    pick_list = Draft_Picks.pick_order(room_members,room_id)
    print('pick list: ' + str(pick_list))
    messages = Message.get_messages(room_id)
    return render_template('view_pool.html', username=current_user.username, messages=messages, pick_list = pick_list,
                           room_members=room_members.rewind(), room_data=room_data, drivers=drivers, form=form)


@app.route('/nascar/results/<string:room_id>', methods=['GET', 'POST'])
@login_required
def nascar_pool_results(room_id):
    race_id = Room.get_race_id(room_id)
    update_pick_list = Draft_Picks.get_pool_picks(room_id)
    for update_pick in update_pick_list:
        drv_full = update_pick.drv_full
        position = Results.get_position_by_race_id_driver_name(race_id, drv_full)
        Database.update_one("picks", {"$and": [{"room_id": room_id}, {"drv_full": drv_full}]},
                            {"$set": {"position": position["position"]}})

    pool_picks = Draft_Picks.get_pool_picks(room_id)
    json_list = []
    for pick in pool_picks:
        json_list.append(pick.json())
        print(str(pick.drv_full) + " : " + str(pick.position))
    print(type(pool_picks))
    sorted_pool_picks = sorted(json_list, key = lambda i: i["pool_pick_num"])
    print(sorted_pool_picks)
    users = []
    for pick in sorted_pool_picks:
        if not pick["username"]["username"] in users:
            users.append(pick["username"]["username"])
            print(users)
    round_num=1
    round_picks = []
    sum_pick_list = []
    for sorted_pick in sorted_pool_picks:
        if sorted_pick["user_pick_num"] == round_num:
            pick_data = {"username": sorted_pick["username"]["username"], "car_num": sorted_pick["car_num"],
                         "drv_full": sorted_pick["drv_full"], "position": sorted_pick["position"]}
            round_picks.append(pick_data)
            #rev_round_picks = round_picks.reverse()
            print("round pick rev 425 " + str(round_picks))
        else:
            if round_num % 2 == 0:
                #rev_round_picks = round_picks.reverse()
                sum_pick_list.append(round_picks[::-1])
                print("sum pick list 429 " + str(sum_pick_list) )
            else:
                sum_pick_list.append(round_picks)
                print("sum pick list 432 " + str(sum_pick_list))
            round_num = round_num + 1
            pick_data = {"username": sorted_pick["username"]["username"], "car_num": sorted_pick["car_num"],
                         "drv_full": sorted_pick["drv_full"], "position": sorted_pick["position"]}
            round_picks = [pick_data]
            print("round pick 437 " + str(round_picks))
    round_num = round_num-1

    if round_num % 2 == 0:
        #rev_round_picks = round_picks.reverse()
        sum_pick_list.append(round_picks[::-1])
        print("sum pick list 442 " + str(sum_pick_list))
    else:
        sum_pick_list.append(round_picks)
        print("sum pick list 445 " + str(sum_pick_list))

    return render_template("pool_results.html", users=users, pool_picks=sum_pick_list)




@app.route('/nascar/admin')
@login_required
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
    year = int(datetime.now().year)
    #mongo_list = Sched_Event.find_by_race_series_and_year(series, year)
    #SelectRace.add_choices(mongo_list)
    if series == "sc":
        series1 = "CUP"
    elif series == "xf":
        series1 = "XFINITY"
    elif series == "go":
        series1 = "TRUCK"
    else:
        series1 = "na"
    mongo_list = Sched_Event.find_by_race_series_and_year(series, year)
    SelectRace.add_choices(mongo_list)
    cursor = Sched_Event.find_by_race_series_and_year(series1, year)
    ser_to_json = dumps(cursor)
    #print(type(ser_to_json))
    return ser_to_json

@app.route('/ajax_get_drivers', methods=['POST', 'GET'])
def ajax_get_drivers():
    room_id = request.args.get('room_id', 0, type=str)
    print(room_id)
    room_data = Room.get_room_by_id(room_id)
    room_name = room_data.room_name
    message = ''
    # if request.method =='POST':
    room_members = Room.get_room_members(room_id)
    race_id = room_data.race_id['races']
    print(race_id)
    drivers = Entrants.find_drivers_by_race_id(race_id)
    print(drivers)

    #mongo_list = Sched_Event.find_by_race_series_and_year(series, year)
    DriverList.add_choices(drivers)
    cursor = Entrants.find_drivers_by_race_id(race_id)
    ser_to_json = dumps(cursor)
    #print(type(ser_to_json))
    return ser_to_json


@app.route('/load/entrants', methods=['POST', 'GET'])
@login_required
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

@app.route('/nascar/race_results', methods=['POST', 'GET'])
@login_required
def load_race_results():
    type1 = 'races'
    #race_id ='4daedbcd-f1c6-4bc1-9690-f85d1fd1af4a'
    race_id = request.form['race_drop_down_abc_rr']
    series = request.form['series_drop_down_rr']
    file = 'results.json'
    data = Utils.get_from_sportradar(series, type1, race_id, file)
    #json_object = json.loads(data)
    print_str = json.dumps(data,indent=2)
    print(print_str)

    if data is not None:
        results_list = Results.extract_sportradar_data(data)
    else:
        text = "No data returned from SportRadar"
        return render_template('results_load.html', text=text)

    load_list = []
    ignore_list = []
    for result in results_list:
        test_race_id = result.get_race_id()
        test_drv_id = result.get_drv_id()
        test = Results.find_by_race_and_drv_id(test_race_id, test_drv_id)
        if test is True:
            result.save_to_mongo()
            load_list.append(result)
        else:
            record = Results.get_by_race_and_drv_id(test_race_id, test_drv_id)
            record_json = record.json()
            rec_json =result.json()
            obj_id_to_replace = str('"'+str(record_json["_id"])+'"')
            #obj_id_to_replace = "5ec5f4b93acf8b000bfe6ec3"
            print(str(obj_id_to_replace))
            print(type(obj_id_to_replace))
            query = {"_id": ObjectId(obj_id_to_replace)}
            print(str(result.position)+ " - "+ str(result.drv_full))
            print(str(rec_json["position"]) + " - " + str(rec_json["drv_full"]))
            # stage_2_points, laps_led, laps_completed}
            query_update_data = {"$set": {"race_status": str(rec_json["race_status"]), "start_pos": int(rec_json["start_pos"]), "position": int(rec_json["position"]),
                                  "drv_status": str(rec_json["drv_status"]), "points": int(rec_json["points"]), "bonus_points": int(rec_json["bonus_points"]),
                                  "penalty_points": int(rec_json["penalty_points"]), "stage_1_points": int(rec_json["stage_1_points"]),
                                  "stage_2_points": int(rec_json["stage_2_points"]), "laps_led": int(rec_json["laps_led"]), "laps_completed": int(rec_json["laps_completed"])}}

            replace_dir = Database.update_one("results", query, query_update_data)
            print(str(dir(replace_dir.modified_count)))
            print(replace_dir.raw_result)
            ignore_list.append(result)

    races = Database.find(collection="results", query={"race_id": race_id})
    text = "load successful"
    return render_template('results_load.html', text=text, results=load_list, ignore_list=ignore_list)
    #return render_template('drivers_load.html', text=race_id)
    #return render_template('nascar_admin.html')


@app.route('/nascar/load', methods=['POST', 'GET'])
@login_required
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
    result_id = "5ec5f4b93acf8b000bfe6ec3"
    obj_id_to_replace = (ObjectId(result_id))
    query = {"_id": obj_id_to_replace}
    # stage_2_points, laps_led, laps_completed}
    query_replace_data = {"$set": {"race_status": "pretty good", "laps_led": 25, "start_pos": 30,
                          "position": 23, "drv_status": "hard on", "points": 25, "bonus_points": 1,
                          "penalty_points": 1, "stage_1_points": 35, "stage_2_points": 22, "laps_completed": 45}}
    replace_dir = Database.update_one("results", query, query_replace_data)
    print(str(dir(replace_dir.modified_count)))
    print(str(dir(replace_dir)))
    print(replace_dir.raw_result)

    return render_template('test.html', test=test)

if __name__ == '__main__':
    socketio.run(app, DEBUG=True)
   #app.run(debug=app.config['DEBUG'], port=4990)

