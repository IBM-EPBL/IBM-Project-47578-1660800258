from flask import *
from connect import *
import datetime
from urllib.parse import urlparse
import smtplib
import random
from followback import *
app= Flask(__name__)
app.config['SECRET_KEY'] = 'df0331cefc6c2b9a5d0208a726a5d1c0fd37324feba25506'
app= Flask(__name__)
app.config['SECRET_KEY'] = 'df0331cefc6c2b9a5d0208a726a5d1c0fd37324feba25506'
app.config['MAIL_SERVER']='support.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'mith123@gmail.com'
app.config['MAIL_PASSWORD'] = 'nhmhbqmdeuxrhvwv'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

def mail_service(mailid,sub,body):
    try:
        msg = Message(sub,sender="mithfashions@gmail.com",recipients=[mailid])
        msg.body = body
        mail.send(msg)
        print("Sent")
    except Exception as e:
        print("error")
        
#cart
@app.route("/cart",methods=('GET','POST'))
def cart_page():
    userid=session.get('logged_in_userid', None)
    uname = session.get('logged_in_username', None)
    arr = fetch_cartarr(userid)

    amtarr=totamtcalculation(arr)
    if request.method == 'POST':
        prodid = request.form['prodid']
        print(prodid+"PRODID FROM CART")
        print(arr)
        flag = 0
        for cartitems in arr:
            if (cartitems[6] == prodid and cartitems[8] > 1):
                flag = 1
                updatequery = "UPDATE cart set quantity=quantity-1 where prodid='" + prodid + "'"
                ibm_db.exec_immediate(conn, updatequery)
        if (flag != 1):
            querycart = "DELETE from cart where prodid='" + prodid + "'"
            ibm_db.exec_immediate(conn, querycart)
    return  render_template("cart.html",cartarr=arr,totcost=amtarr[0],totdis=amtarr[1],netamt=amtarr[2],uname=uname,lencartarr=len(arr))

#home page
@app.route("/")
def home_page():
    logged_in_username = session.get('logged_in_username', None)
    logged_in_userid = session.get('logged_in_userid', None)
    return render_template("home.html",uname=logged_in_username,userid=logged_in_userid)

#logout page
@app.route("/logout")
def logout_pg():
    session.clear()
    return redirect(url_for('loginpage'))

@app.route('/redirect_to')
def redirect_to():
    link = request.args.get('link', '/')
    return redirect(link), 301

@app.route("/register",methods=('GET','POST'))
def regpage():
    if request.method == 'POST':
        sub="Verify your email for Sash Vogue"
        form_checkvals = request.form.getlist("checkval")
        userid=str(random.randint(16565565445345,96565565445345))
        email = request.form['mail']
        dob=request.form['DOB']
        username = request.form['username']
        password=request.form['password']
        contact=request.form['contact']
        address=request.form['address']
        query="insert into user values('"+userid+"','"+username+"','"+contact+"','"+password+"','"+email+"','"+dob+"','"+address+"')"
        stmt=ibm_db.exec_immediate(conn,query)
        rowcount=ibm_db.num_rows(stmt)
        subject="Verify email for Sash Vogue"
        body="You have been successfully registered with Sash Vogue Community."

        if(len(form_checkvals) !=0  and form_checkvals[0]=='yes'):
            mail_service(email,subject,body)
        return redirect(url_for('loginpage'))

    return render_template("registration.html")

@app.route("/login",methods=('GET','POST'))
def loginpage():
    type='user'
    if request.method == 'POST':
        uname = request.form['uname']
        password = request.form['password']
        query = "select COUNT(*)from user where username='"+uname+"' and password='"+password+"'"
        stmt5 = ibm_db.exec_immediate(conn,query)
        row = ibm_db.fetch_tuple(stmt5)
        query1="select * from user where username='"+uname+"' and password='"+password+"'"
        stmt2= ibm_db.exec_immediate(conn,query1)
        row2= ibm_db.fetch_tuple(stmt2)
        if(row[0] ==1 ):
            session['logged_in_username'] = uname
            session['logged_in_userid'] = row2[0]
            session['logged_in_usermail']=row2[4]
            print(row2[4])
            print(row2[1])
            return redirect(url_for('home_page'))
        else:
            flash("Invalid credentials! Please enter correct details")
    return render_template("login.html",type=type)



@app.route("/payment",methods=('GET','POST'))
def payment_pg():
    userid = session.get('logged_in_userid', None)
    uname = session.get('logged_in_username', None)
    arr = fetch_cartarr(userid)
    actualmon=datetime.date.today().month
    actualday=datetime.date.today().day
    amtarr = totamtcalculation(arr)
    print(amtarr)

    return render_template("payment.html",netamt=amtarr[2],birthdaycoupon=birthdaycoupon,userid=userid,res=res,uname=uname)

@app.route("/addstock")
def add_Stockpg():
    return render_template("addstock.html")
@app.route("/adminlogin",methods=('GET','POST'))
def adminloginpage():
    type='admin'
    if request.method == 'POST':
        actualuname='admin'
        actualpassword='123'
        uname = request.form['uname']
        password = request.form['password']
        if(actualpassword == password and actualuname == uname ):
             return redirect(url_for('home_page'))
        else:
            flash("Invalid credentials! Please enter correct details")
    return render_template("login.html",type=type)


@app.route('/admin')
def adminhomepage():
    arr=[]
    query="select prodid,prodname,category,type,brand,price from outfit ORDER BY prodid"
    stmt = ibm_db.exec_immediate(conn, query)
    row = ibm_db.fetch_tuple(stmt)
    while (row):
        arr.append(row)  # appending all dictionaries in arr
        row = ibm_db.fetch_tuple(stmt)  # incrementing that is to next row

    return render_template("adminhome.html",prodarr=arr)

@app.route("/productdetails/<category>/<type>/<prodid>",methods=('GET','POST'))
def product_detailspg(category,type,prodid):
    o = urlparse(request.base_url)
    userid = session.get('logged_in_userid', None)
    uname = session.get('logged_in_username', None)
    if (request.method=='POST'):
        if(uname !=None):
            arr = fetch_cartarr(userid)
            insert_intocart(arr,prodid,category,userid,type)
            return redirect(url_for('cart_page'))
        else:
            flash("Oops! Seems like you haven't registered with us. Sign Up")
    api=fetchapi(category)
    res18empty=False
    res19empty=False
    query="select  o.*,p.pic1,p.pic2,p.pic3,p.pic1 from outfit o inner join picture p on o.prodid=p.prodid where o.prodid='"+prodid+"'"
    stmt = ibm_db.exec_immediate(conn, query)
    res = ibm_db.fetch_tuple(stmt)
    pricedisplay= round(res[2] -(res[2]*res[6] / 100))
    if ((res[18] == None) or (res[18] == "nil")):
        res18empty = True
    if( (res[19]==None) or (res[19]=="nil") ):
        res19empty=True


    return render_template("productdetails.html",category=category,type=type,prodid=prodid,result=res,api=api,res18empty=res18empty,res19empty=res19empty,pricedisplay=pricedisplay,hostname=o.hostname,port=o.port,uname=uname)

@app.route("/sunglasses_/<category>/<type>/<prodid>",methods=('GET','POST'))
def sunglasses_detailspg(category,type,prodid):
    o = urlparse(request.base_url)
    api=fetchapi(category)
    uname = session.get('logged_in_username', None)
    userid = session.get('logged_in_userid', None)
    if (request.method=='POST'):
        if (uname != None):
            arr = fetch_cartarr(userid)
            insert_intocart(arr, prodid, category, userid, type)
        else:
            flash("Please login to add the products to cart")
    api=fetchapi(category)
    query="select  o.*,p.pic1,p.pic2,p.pic3,p.pic4,o.offer from sunglasses o inner join picture p on o.prodid=p.prodid where o.prodid='"+prodid+"'"
    stmt = ibm_db.exec_immediate(conn, query)
    res = ibm_db.fetch_tuple(stmt)
    pricedisplay = round(res[2] - (res[2] * res[17] / 100))
    return render_template("sunglasses_details.html",category=category,type=type,prodid=prodid,result=res,api=api,pricedisplay=pricedisplay,hostname=o.hostname,port=o.port,uname=uname)

@app.route('/wishlist')
def wishlist_pg():
    userid = session.get('logged_in_userid', None)
    uname = session.get('logged_in_username', None)
    arr=fetchwishlist(userid)
    return render_template("wishlist.html",wishlistarr=arr,uname=uname)

@app.route("/products/<category>/<type>",methods=('GET','POST'))
def products_page(category,type):
    arr=[]
    userid = session.get('logged_in_userid', None)
    uname = session.get('logged_in_username', None)
    api=""
    if(request.method=='POST'):
        prodid=request.form['prodid']
        if(uname != None):
            insertwishlist="insert into wishlist values ('"+userid+"','"+prodid+"')"
            ibm_db.exec_immediate(conn,insertwishlist)
        else:
            flash("Oops! Seems like you haven't registered with us. Sign Up")

    if(type != "Sunglasses"): #since sunglasses differ some characteristics with other products need to create separate page.

        api=fetchapi(category)
        query="select  o.prodid,o.prodname,o.brand,o.price,p.pic1,p.pic2,p.pic3,p.pic4,o.offer from outfit o inner join picture p on o.prodid=p.prodid where category='"+category+"' and type='"+type+"'"
        stmt = ibm_db.exec_immediate(conn, query)
        row = ibm_db.fetch_tuple(stmt)
        while (row):
            arr.append(row)  # appending all dictionaries in arr
            row = ibm_db.fetch_tuple(stmt)  # incrementing that is to next row
    else:
        api = fetchapi(category)
        query = "select  o.prodid,o.prodname,o.brand,o.price,p.pic1,p.pic2,p.pic3,p.pic4,o.offer from sunglasses o inner join picture p on o.prodid=p.prodid where category='"+category+"' and type='"+type+"'"
        stmt = ibm_db.exec_immediate(conn, query)
        row  = ibm_db.fetch_tuple(stmt)
        while (row):
            arr.append(row)  # appending all dictionaries in arr
            row = ibm_db.fetch_tuple(stmt)  # incrementing that is to next row
    return render_template("products.html",productsarr=arr,category=category,type=type,api=api,userid=userid,uname=uname)


if(__name__=='__main__'):
    app.run(host ='0.0.0.0', port = 5000)

