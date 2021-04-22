from flask import Flask, render_template, request
from cryptography.fernet import Fernet


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/waytodashboard/<mail>', methods=['GET', 'POST'])
def waytodashboard(mail):
    
    print(mail)
    return render_template('dashboard.html', useremail = mail)


@app.route('/hash/<mail>', methods = ['GET', 'POST'])
def hash(mail):

    print(mail)
    return     render_template('hash.html', useremail = mail)


@app.route('/aes/<mail>', methods = ['GET', 'POST'])
def aes(mail):

    print(mail)
    return render_template('aes.html', useremail = mail)


@app.route('/rsa/<mail>', methods = ['GET', 'POST'])
def rsa(mail):

    print(mail)
    return     render_template('rsa.html', useremail = mail)


@app.route('/generateonekey')
def generateonekey():

    return Fernet.generate_key()



if __name__ == '__main__':
    app.run()
