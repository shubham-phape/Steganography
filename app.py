from flask import Flask, render_template, request, jsonify, make_response
from cryptography.fernet import Fernet
import pyrebase
import flask

#References: https://www.thepythoncode.com/article/encrypt-decrypt-files-symmetric-python

app = Flask(__name__)


firebaseConfig = {
  "apiKey": "AIzaSyByT3jioOwrU62L3AnxqPIqB-EFihwsRlI",
  "authDomain": "crypto-8f870.firebaseapp.com",
  "databaseURL": "https://crypto-8f870-default-rtdb.firebaseio.com",
  "projectId": "crypto-8f870",
  "storageBucket": "crypto-8f870.appspot.com",
  "messagingSenderId": "826758797675",
  "appId": "1:826758797675:web:75ac6146638f23a91cd42e",
  "measurementId": "G-DGDHH1DP16"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
storage = firebase.storage()
db = firebase.database()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/waytodashboard/<mail>', methods=['GET', 'POST'])
def waytodashboard(mail):
    
    return render_template('dashboard.html', useremail = mail)


@app.route('/hash/<mail>', methods = ['GET', 'POST'])
def hash(mail):

    return     render_template('hash.html', useremail = mail)


@app.route('/aes/<mail>', methods = ['GET', 'POST'])
def aes(mail):

    return render_template('aes.html', useremail = mail)


@app.route('/rsa/<mail>', methods = ['GET', 'POST'])
def rsa(mail):

    return     render_template('rsa.html', useremail = mail)


@app.route('/generateonekey', methods = ['GET', 'POST'])
def generateonekey():
    req = request.get_json()
    key = Fernet.generate_key()
    hex_str = key.hex()

    #converting hex key to bytes for encryption
    #new_rnd_bytes = bytes.fromhex(hex_str)
    
    res = make_response(jsonify({"message": hex_str}), 200)
    return res

@app.route('/onekeyencryptfile', methods = ['POST', 'GET'])
def onekeyencryptfile():
    if (request.method == 'POST'):
        file = request.files['file']
        curruser = request.form.get('cur_user')
        encryptionkey = request.form.get('aes_key')
        outputfilename = file.filename

        #converting hex key to bytes for encryption
        new_rnd_bytes = bytes.fromhex(encryptionkey)

        #encrypting file data
        fernet = Fernet(new_rnd_bytes)
        encrypted_data = fernet.encrypt(file.read())      
        
        #writing file to firebase cloud 
        storage.child(curruser+"/" + outputfilename).put(encrypted_data)

        #writing metadata to database
        data = {
                                "filename" : outputfilename,
                                "encryption": "aes",
                                "aeskey": encryptionkey
                                 }                
        db.child("users").child(encodeemail(curruser)).push(data)

    return render_template('aes.html', useremail = curruser)

@app.route('/test', methods = ['POST', 'GET'])
def test():
    rs= db.child("users").get()
    print(rs.val())
    data = {"filename": "Mortimer 'Morty' Smith"}
    db.child("users").child("Morty").set(data)
    return rs.val()

def decodeemail(email):
    dec_email = email.replace(",", ".")
    return dec_email

def encodeemail(email):
    enc_email = email.replace(".", ",")
    return enc_email

if __name__ == '__main__':
    app.run()
