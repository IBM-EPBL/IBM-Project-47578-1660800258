from flask import Flask,redirect,url_for,request,render_template
app=Flask(_name_)

@app.route('/admin')
def hello_admin():
    return "hello admin"

@app.route('/guest/<guest>')
def hello_guest(guest):
    return "hello %s guest" %guest

@app.route('/user/<name>')
def hello_user(name):
    if(name=='admin'):
        return redirect(url_for("hello_admin"))
    else:
        return redirect(url_for("hello_guest",guest=name))
app.run(debug=True
