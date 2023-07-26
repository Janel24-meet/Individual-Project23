from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'

config = {
  "apiKey": "AIzaSyBsYLYLSSc2i-sJNtC92PK_RS4RW4Wsulk",
  "authDomain": "draw-with-me-c5d15.firebaseapp.com",
  "projectId": "draw-with-me-c5d15",
  "storageBucket": "draw-with-me-c5d15.appspot.com",
  "messagingSenderId": "780339443720",
  "appId": "1:780339443720:web:cc3bb3033df05c27e8b9bd",
  'databaseURL': 'https://draw-with-me-c5d15-default-rtdb.europe-west1.firebasedatabase.app/'
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()


@app.route('/', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            login_session['user'] = auth.sign_in_with_email_and_password(email, password)
            return redirect(url_for('profile'))
        except:
            return render_template("index1.html")
    else:

        return render_template("index1.html")

@app.route('/profile2', methods=['GET', 'POST'])
def second_profile():
    if request.method == 'GET':
        name = request.form['search']
        try:
            UID = login_session['user']['localId']
            username = db.child("Users").get().val()
            twe = db.child("tweets").get().val()
            return render_template('secondprofile.html',ids=username, posts=twe, username=name, uid=UID)
        except:
            return render_template("secondprofile.html")
    else:
        name = request.form['search']
        try:
            UID = login_session['user']['localId']
            username = db.child("Users").get().val()
            twe = db.child("tweets").get().val()
            return render_template('secondprofile.html',ids=username, posts=twe, username=name, uid=UID)
        except:
            return render_template("secondprofile.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        fullna = request.form['fullname']
        us = request.form['username']
        bo = request.form['bio']
        try:
            login_session['user'] = auth.create_user_with_email_and_password(email, password)
            UID = login_session['user']['localId']
            user = {"fullname": fullna, "email": email, "username": us, "bio": bo, "followers":  [], "link": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Default_pfp.svg/1200px-Default_pfp.svg.png"}
            db.child("Users").child(UID).set(user)
            return redirect(url_for('profile'))
        except:
            return render_template("index1.html")
    else:

        return render_template("index1.html")



@app.route('/add_tweet', methods=['GET', 'POST'])
def add_tweet():
    if request.method == 'POST':
        tw = request.form['title']
        pic = request.form['pict']
        te = request.form['text']
        try:
            tweet = {"title": '', "text": '', "UID": '', "picture": ''}
            UID = login_session['user']['localId']
            tweet = {"title": tw, "text": te, "UID": UID, "picture": pic}
            db.child("tweets").push(tweet)
            return redirect(url_for('tweets'))
        except:
            return render_template("post.html")
    else:

        return render_template("post.html")

@app.route('/signout')
def signout():
    login_session['user'] = None
    auth.current_user = None
    return redirect(url_for('signin'))

@app.route('/all_tweets')
def tweets():
    UID = login_session['user']['localId']
    username = db.child("Users").get().val()
    twe = db.child("tweets").get().val()
    return render_template("allpost.html", twee=twe, uid=UID, su=username)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    
    UID = login_session['user']['localId']
    username = db.child("Users").child(UID).child("username").get().val()
    name = db.child("Users").child(UID).child("fullname").get().val()
    linkpic = db.child("Users").child(UID).child("link").get().val()
    p = db.child("Users").child(UID).child("bio").get().val()
    twe = db.child("tweets").get().val()

    return render_template("profile.html",uid=UID, user=username, fullname=name, piclink=linkpic, bio=p, twet=twe )

@app.route('/change', methods=['GET', 'POST'])
def change():
    if request.method == 'POST':
        k = request.form['pic']
        fullna = request.form['fullname']
        us = request.form['username']
        bo = request.form['bio']
        foll = []
        try:
            UID = login_session['user']['localId']
            if k!="":
                db.child("Users").child(UID).update({"link": k})
            if fullna!="":
                db.child("Users").child(UID).update({"fullname": fullna})
            if us!="":
                db.child("Users").child(UID).update({"username": us})
            if bo!="":
                db.child("Users").child(UID).update({"bio": bo})

            return redirect(url_for('profile'))
        except:
            return render_template("change.html")
    else:
        UID = login_session['user']['localId']
        username = db.child("Users").child(UID).child("username").get().val()
        name = db.child("Users").child(UID).child("fullname").get().val()
        linkpic = db.child("Users").child(UID).child("link").get().val()
        p = db.child("Users").child(UID).child("bio").get().val()

        return render_template("change.html",uid=UID, user=username, fullname=name, piclink=linkpic, bio=p)

@app.route('/follow/<string:uid>', methods=['GET', 'POST'])
def follow(uid):
    if not login_session['user']:
        return redirect(url_for('signin'))
    current_user_id = login_session['user']['localId']
    db.child('Users').child(current_user_id).child('following').child(uid).set(True)
    return redirect(url_for('profile'))


def get_feed():
    if 'user' not in login_session:
        return redirect(url_for('signin'))

    # Get the current UID from the session
    current_uid = login_session['user']['localId']

    following_ref = db.child('Users').child(current_uid).child('following')
    following_data = following_ref.get().val()

    following_users = []
    if following_data is not None:
        following_users = list(following_data.keys())
        print('<3', following_users)

    # Fetch posts from followed users
    posts_ref = db.child('Posts')
    all_posts = posts_ref.get()

    # Filter posts of followed users
    feed_posts = []
    if all_posts is not None:
        for post in all_posts.each():
            post_data = post.val()
            if 'uid' in post_data and post_data['UID'] in following_users:
                feed_posts.append(post_data)

    return feed_posts


@app.route('/feed')
def feed():
    UID = login_session['user']['localId']
    username = db.child("Users").get().val()
    twe = db.child("tweets").get().val()
    return render_template('allpost.html',twee = get_feed(), uid=UID, su=username)



if __name__ == '__main__':
    app.run(debug=True)