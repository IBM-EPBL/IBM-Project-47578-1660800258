from flask import Flask, request, render_template, url_for,redirect
app = Flask(__name__)
@app.route('/success/<name>')
def success(name):
    return 'welcome %s' %name
@app.route('/login', methods =['GET', 'POST'])
def login():
    if request.method=="POST":
       first_name = request.form.get("username")
       email_id = request.form.get("email")
       phone_num = request.form.get("number")
       return "Your name is" +first_name + "Your email is" +email_id + "Your Phone number is" +phone_num
       return redirect(url_for('success',name = first_name))
 
if __name__=='__main__':
   app.run(debug=True)