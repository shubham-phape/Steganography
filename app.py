from flask import Flask, render_template, request, jsonify, make_response
from cryptography.fernet import Fernet


#References: https://www.thepythoncode.com/article/encrypt-decrypt-files-symmetric-python

app = Flask(__name__)


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
    new_rnd_bytes = bytes.fromhex(hex_str)
    
    res = make_response(jsonify({"message": hex_str}), 200)
    return res

@app.route('/onekeyhashfile', methods = ['POST', 'GET'])
def onekeyhashfile():
    if (request.method == 'POST'):
        file = request.files['file']
        encryptionkey = request.form.get('aes_key')
        
        new_rnd_bytes = bytes.fromhex(encryptionkey)
        
        output_filename = "/encrypted/"+file.filename
        fernet = Fernet(new_rnd_bytes)
        encrypted_data = fernet.encrypt(file.read())
        print(new_rnd_bytes)
    
        f = open(output_filename,"wb")
        f.write(encrypted_data)
        f.close()
    return output_filename

if __name__ == '__main__':
    app.run()
