from flask import Flask, render_template, request, jsonify, make_response, send_from_directory
from cryptography.fernet import Fernet
import pyrebase, flask, base64, urllib, binascii,os, json, hashlib

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# References: https://www.thepythoncode.com/article/encrypt-decrypt-files-symmetric-python
# https://nitratine.net/blog/post/asymmetric-encryption-and-decryption-in-python/
#https://stackoverflow.com/questions/24570066/calculate-md5-from-werkzeug-datastructures-filestorage-without-saving-the-object
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
    tosend = {
            "message" : "",
            "useremail" : mail,
            "hash1": "",
            "hash2": "",
            "flag" : "0"
        }

    return render_template('hash.html', user= tosend)


@app.route('/aes/<mail>', methods=['GET', 'POST'])
def aes(mail):

    return render_template('aes.html', useremail=mail)


@app.route('/rsa/<mail>', methods=['GET', 'POST'])
def rsaweb(mail):

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


@app.route('/generatetwokey', methods=['GET', 'POST'])
def generatetwokey():
    req = request.get_json()
    
    #generating key
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    public_key = private_key.public_key()

    #saving the keys        
    privatekeybytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

    publickeybytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )


    if(request.method == 'POST'):
        #submitted the form
        file = request.files['file']
        curruser = request.form.get('cur_user')
        encryptionkey = request.form.get('aes_key')
        outputfilename = file.filename

        msg = file.read()

        #encrypting
        encrypted = public_key.encrypt(
        msg,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
            )
        )

        # writing file to firebase cloud
        filetosave = open("encrypted/"+outputfilename, "wb")
        filetosave.write(encrypted)
        filetosave.close()

        
        print(type(publickeybytes))
        # writing metadata to database
        data = {
            "filename": outputfilename,
            "encryption": "rsa",
            "rsaprivatekey": privatekeybytes.hex(),
            "rsapublickey" : publickeybytes.hex()
        }
        #print(data)
        db.child("users").child(encodeemail(curruser)).push(data)

        return render_template('rsa.html', useremail=curruser)

    else:
        print("get")

        # converting hex key to bytes for encryption
        #new_rnd_bytes = bytes.fromhex(hex_str)

        res = make_response(jsonify({"public": publickeybytes.hex(), "private":privatekeybytes.hex()}), 200)
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


@app.route('/getfilename', methods=['POST', 'GET'])
def getfilename():
    
    k =[]
    for file in os.listdir("encrypted"):
        if True:
            k.append(file)
    res = make_response(jsonify({"public": k}), 200)
    return res

    

@app.route('/decryptthefile', methods=['POST', 'GET'])
def decryptthefile():
    if(request.method == 'POST'):
        filename = request.form.get('filename')
        username = request.form.get('username')

        
        # retrieving the file meta data from data base
        targetkey = ""
        filedata = db.child("users").child(encodeemail(username)).get().val()
        for k in filedata.keys():
            if(filedata[k]['filename'] == filename):
                targetkey = k

        # doing the decryption here
        if(filedata[k]['encryption'] == 'aes'):
            # this is one key AES file

            # retrieving the file from strograge
            streferencefile = storage.child("/"+username + "/" + filename).get_url(None)

            new_rnd_bytes = bytes.fromhex(filedata[k]['aeskey'])
            filedecrypted = urllib.request.urlopen(streferencefile)
            fernet = Fernet(new_rnd_bytes)
            # decrypting the files
            decrypted_data = fernet.decrypt(filedecrypted.read())

            #saving the file
            file = open("decrypted/"+filename, "wb")
            file.write(decrypted_data)
            file.close()
            return render_template('decryptedfile.html', filename=filename)
        else:
            print("rsa")

            #retieving the encrypted file
            f = open("encrypted/"+ filename, 'rb')
            enc_message = f.read()
            f.close()   

            #retrievibg the keys in hex from database
            byprivatekey = bytes.fromhex(filedata[k]['rsaprivatekey'])
            bypublickey = bytes.fromhex(filedata[k]['rsapublickey'])

            #converting keys from  bytes  to desired types
            private_key = serialization.load_pem_private_key(
            byprivatekey,
            password=None,
            backend=default_backend()
            )
            # decrypting the files
            original_message = private_key.decrypt(
                enc_message,
                padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
                )
            )
            print(original_message)
            #saving the file in cloud directory
            file = open("decrypted/"+filename, "wb")
            file.write(original_message)
            file.close()

            #returning to open the file
            return render_template('decryptedfile.html', filename=filename)
            

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


@app.route('/comparehash', methods=['GET', 'POST'])
def comparehash():
    if (request.method == 'POST'):
        fileone = request.files['fileone']
        filetwo = request.files['filetwo']
        curruser = request.form.get('cur_user')
        
        #hashing both the files

        img_key1 = hashlib.md5(fileone.read()).hexdigest() 
        img_key2 = hashlib.md5(filetwo.read()).hexdigest() 

        #comparing hash of both files
        m=''
        if(img_key1 == img_key2):
            m= "Both the files are same so their hash is same too."
            print("same")
        else:
            m= "Different files so they have different hash"
            print("not same")

        tosend = {
            "message" : m,
            "useremail" : curruser,
            "hash1": img_key1,
            "hash2": img_key2,
            "flag" : "1",
            "name1" : fileone.filename,
            "name2" : filetwo.filename
        }
        
    return render_template('hash.html', user= tosend)


def decodeemail(email):
    dec_email = email.replace(",", ".")
    return dec_email


def encodeemail(email):
    enc_email = email.replace(".", ",")
    return enc_email


if __name__ == '__main__':
    app.run()
