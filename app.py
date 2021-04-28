from flask import Flask, render_template, request, jsonify, make_response, send_from_directory
from cryptography.fernet import Fernet
import pyrebase
import flask
import urllib

# References: https://www.thepythoncode.com/article/encrypt-decrypt-files-symmetric-python

app = Flask(__name__)


firebaseConfig = {
    "apiKey": "AIzaSyByT3jioOwrU62L3AnxqPIqB-EFihwsRlI",
    "authDomain": "crypto-8f870.firebaseapp.com",
    "databaseURL": "https://crypto-8f870-default-rtdb.firebaseio.com",
    "projectId": "crypto-8f870",
    "storageBucket": "crypto-8f870.appspot.com",
    "messagingSenderId": "826758797675",
    "appId": "1:826758797675:web:75ac6146638f23a91cd42e",
    "measurementId": "G-DGDHH1DP16",
    "serviceAccount": "templates/crypto-8f870-firebase-adminsdk-g2hwp-c5cfe81a91.json"
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

    return render_template('dashboard.html', useremail=mail)


@app.route('/hash/<mail>', methods=['GET', 'POST'])
def hash(mail):

    return render_template('hash.html', useremail=mail)


@app.route('/aes/<mail>', methods=['GET', 'POST'])
def aes(mail):

    return render_template('aes.html', useremail=mail)


@app.route('/rsa/<mail>', methods=['GET', 'POST'])
def rsa(mail):

    return render_template('rsa.html', useremail=mail)


@app.route('/generateonekey', methods=['GET', 'POST'])
def generateonekey():
    req = request.get_json()
    key = Fernet.generate_key()
    hex_str = key.hex()

    # converting hex key to bytes for encryption
    #new_rnd_bytes = bytes.fromhex(hex_str)

    res = make_response(jsonify({"message": hex_str}), 200)
    return res


@app.route('/onekeyencryptfile', methods=['POST', 'GET'])
def onekeyencryptfile():
    if (request.method == 'POST'):
        file = request.files['file']
        curruser = request.form.get('cur_user')
        encryptionkey = request.form.get('aes_key')
        outputfilename = file.filename

        # converting hex key to bytes for encryption
        new_rnd_bytes = bytes.fromhex(encryptionkey)

        # encrypting file data
        fernet = Fernet(new_rnd_bytes)
        encrypted_data = fernet.encrypt(file.read())

        # writing file to firebase cloud
        storage.child(curruser+"/" + outputfilename).put(encrypted_data)

        # writing metadata to database
        data = {
            "filename": outputfilename,
            "encryption": "aes",
            "aeskey": encryptionkey
        }
        db.child("users").child(encodeemail(curruser)).push(data)

    return render_template('aes.html', useremail=curruser)


@app.route('/test', methods=['POST', 'GET'])
def test():
    #s= db.child("users").get()
    streferencefile = storage.child(
        "/shubham@gmail.com/corgi.png").get_url(None)
    filede = urllib.request.urlopen(streferencefile)

    return render_template('decryptedfile.html', filename="corgi.png")

# dECRYPT THE FILE


@app.route('/decryptthefile', methods=['POST', 'GET'])
def decryptthefile():
    if(request.method == 'POST'):
        filename = request.form.get('filename')
        username = request.form.get('username')

        # retrieving the file from strograge
        streferencefile = storage.child(
            "/"+username + "/" + filename).get_url(None)

        # retrieving the file meta data from data base
        targetkey = ""
        filedata = db.child("users").child(encodeemail(username)).get().val()
        for k in filedata.keys():
            if(filedata[k]['filename'] == filename):
                targetkey = k

        # doing the decryption here
        if(filedata[k]['encryption'] == 'aes'):
            # this is one key AES file
            new_rnd_bytes = bytes.fromhex(filedata[k]['aeskey'])
            filedecrypted = urllib.request.urlopen(streferencefile)
            fernet = Fernet(new_rnd_bytes)
            decrypted_data = fernet.decrypt(filedecrypted.read())
            file = open("decrypted/"+filename, "wb")
            file.write(decrypted_data)
            file.close()
            return render_template('decryptedfile.html', filename=filename)
        else:
            print("rsa")
            return "rsa"

    return "Page not ofund"

@app.route('/downloadfile/<filename>', methods=['POST', 'GET'])
def downloadfile(filename):
    print(filename)
    path = "decrypted"
    try:
        return send_from_directory(path, filename)
    except Exception as e:
        print(e)
    return send_from_directory(path, filename)



def decodeemail(email):
    dec_email = email.replace(",", ".")
    return dec_email


def encodeemail(email):
    enc_email = email.replace(".", ",")
    return enc_email


if __name__ == '__main__':
    app.run()
