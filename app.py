from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps

# Kullanıcı Giriş Decorator'ı  BUNU 1 KERE YAZABİLİRİZ KULLANICILARIN GÖRMESİNİ İSTEMEDİĞİMİZ ŞEYLERİ BÖYLECE HALLEDERİZ
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):  
        if "logged_in" in session:    # yani sessionda loggedin varmı ona bakıo demekki giriş yapılmış 
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için lütfen giriş yapın.","danger")
            return redirect(url_for("login"))

    return decorated_function

#Kullanıcı kayıt formu
class RegisterForm(Form):
    name = StringField("İsim Soyisim:",validators=[validators.length(min=4,max=35)])
    username = StringField("Kullancıcı Adı:",validators=[validators.length(min=3,max=25)])
    email = StringField("Eposta:",validators=[validators.email(message="Lütfen Geçerli Bir E-mail Adreis Giriniz")])
    password = PasswordField("Parolanız:",validators=[
        validators.DataRequired(message="Lütfen Bir Parola Belirleyiniz"),
        validators.EqualTo(fieldname="confirm",message="Parolanız Uyuşmuyor...")
    ])
    confirm = PasswordField("Parola Doğrula")

#Kullanıcı Login Form
class LoginForm(Form):
    username = StringField("Kullanıcı Adı:")
    password = PasswordField("Parola:")
app = Flask(__name__)
app.secret_key="unlemtab"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "unlemtab"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


@app.route("/about")
def about():
    return render_template("about.html")



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/article")
def article():
    return render_template("article.html")

#kayıt olma
@app.route("/register",methods =["GET","POST"])
def register():
    form = RegisterForm(request.form)
    return render_template("register.html")

    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)

        cursor = mysql.connection.cursor()

        sorgu = "Insert Into users(name,email,username,password) VALUES(%s,%s,%s,%s)"
        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()
        cursor.close()

        flash("Başarıyla Kayıt Oldunuz","succes")
        return redirect(url_for("login"))
    else:
        return render_template("register.html",form=form)



#giriş yapma
@app.route("/login")
def login():
    form = LoginForm(request.form)
    if request.method =="POST":
        username = form.username.data
        password_entered = form.password.data
        sorgu = "Select * From users where username = %s"
        cursor = mysql.connection.cursor()
        rusult = cursor.execute(sorgu,(username,))

        if result >0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered,real_password):
               flash("Başarıyla Giriş Yaptınız...","success")

               session["logged_in"] = True
               session["username"] = username

               return redirect(url_for("index"))
            else:
                flash("Parolanızı Yanlış Girdiniz...","danger")
                return redirect(url_for("login")) 

        else:
           flash("Böyle bir kullanıcı bulunmuyor...","danger")
           return redirect(url_for("login"))

    
    return render_template("login.html",form = form)


    return render_template("login.html")

#çıkış yapma işlemi
@app.route("/logout")
def logout():
    session.clear()
    return(url_for("index"))








if __name__ == "__main__":
    app.run(debug=True)

#bu değişiklik pull içindir


