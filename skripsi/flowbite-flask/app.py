# app.py
from flask import Flask, render_template, request, session, redirect, url_for, abort, jsonify, flash
from flaskext.mysql import MySQL
from model import *
from datetime import timedelta, datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "watermelon"
app.permanent_session_lifetime = timedelta(days=1) 

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'enkripsi'

mysql = MySQL(app)
key = "Kunci12345"

def before_request():
    if 'username' in session and 'role' in session:
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        last_active = session.get('last_active', now)
        
        allowed_inactive_time = timedelta(minutes=10)

        if now - last_active > allowed_inactive_time:
            session.clear()
            return redirect(url_for('index'))

    session['last_active'] = datetime.utcnow().replace(tzinfo=timezone.utc)
    
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        nama = request.form['username']
        sandi = request.form['password']

        conn = mysql.connect()
        cursor = conn.cursor()

        
        playfair_matrix = generate_playfair_matrix(key)

        playfair_nama = encrypt(nama, playfair_matrix)
        playfair_sandi = encrypt(sandi, playfair_matrix)

        username = encrypt_ecb(playfair_nama, key, 1)
        password = encrypt_ecb(playfair_sandi, key, 1)

        query = "SELECT * FROM users WHERE username=%s AND password=%s"

        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            ecb_name = decrypt_ecb(user[3], key, 1)
            role = decrypt(ecb_name, playfair_matrix)

            session['logged_in'] = True
            session['username'] = nama
            session['role'] = role
            session.permanent = True
            session.modified = True
            role = session.get('role', '')
            username = session.get('username', '')
            if role == 'admin ' and session.get('role') == 'admin ':
                return render_template("admin.html", username=username, role=role)
            elif role == 'dokter' and session.get('role') == 'dokter':
                return render_template("dokter.html", username=username, role=role)
            elif role == 'resepsionis ' and session.get('role') == 'resepsionis ':
                return render_template("resepsionis.html", username=username, role=role)
            elif role == 'apoteker' and session.get('role') == 'apoteker':
                return render_template("apoteker.html", username=username, role=role)
            else:
                flash('Akses ditolak. Peran tidak sesuai.', 'error')
                return redirect(url_for('index'))
        else:
            flash('Username atau password salah', 'error')
    if 'logged_in' in session and session['logged_in']:
        role = session.get('role', '')
        username = session.get('username', '')
        if role == 'admin ' and session.get('role') == 'admin ':
            return render_template("admin.html", username=username, role=role)
        elif role == 'dokter' and session.get('role') == 'dokter':
            return render_template("dokter.html", username=username, role=role)
        elif role == 'resepsionis ' and session.get('role') == 'resepsionis ':
            return render_template("resepsionis.html", username=username, role=role)
        elif role == 'apoteker' and session.get('role') == 'apoteker':
            return render_template("apoteker.html", username=username, role=role)
        else:
            flash('Akses ditolak. Peran tidak sesuai.', 'error')
            return redirect(url_for('index'))
    else:
        flash('Username atau password salah', 'error')
    
    return render_template("index.html")


@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")

# ADMIN
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if 'logged_in' in session and session['logged_in'] and session.get('role') == 'admin ':
        if request.method == "POST":
            role = session.get('role', '')
            username = session.get('username', '')
            username = request.form["username"]
            password = request.form["password"]
            role = request.form["role"]

            conn = mysql.connect()
            cursor = conn.cursor()

            
            playfair_matrix = generate_playfair_matrix(key)
            playfair_name = encrypt(username, playfair_matrix)
            playfair_lahir = encrypt(password, playfair_matrix)
            playfair_alamat = encrypt(role, playfair_matrix)

            encrypted_name = encrypt_ecb(playfair_name, key,1)
            encrypted_lahir = encrypt_ecb(playfair_lahir, key,1)
            encrypted_alamat = encrypt_ecb(playfair_alamat, key,1)
            
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (encrypted_name,encrypted_lahir, encrypted_alamat))
            conn.commit()

            cursor.close()
            conn.close()

            return render_template("admin.html", username=session.get('username', ''), role=session.get('role', ''), encrypted_name=encrypted_name, encrypted_lahir=encrypted_lahir, encrypted_alamat=encrypted_alamat)

    else:
        flash('Akses ditolak. Anda harus masuk sebagai dokter.', 'error')
        return redirect(url_for('index'))

    return render_template("admin.html")

@app.route("/view_user")
def view_user():
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    hasil = cursor.fetchall()

    
    playfair_matrix = generate_playfair_matrix(key)

    decrypted_data = []
    for row in hasil:
        ecb_username = decrypt_ecb(row[1], key, 1)
        ecb_password = decrypt_ecb(row[2], key, 1)
        ecb_role = decrypt_ecb(row[3], key, 1)
        
        decrypt_username = decrypt(ecb_username, playfair_matrix)
        decrypt_password = decrypt(ecb_password, playfair_matrix)
        decrypt_role = decrypt(ecb_role, playfair_matrix)
        if 'role' in session:
            role = session['role']
            if role == 'admin ':
                decrypted_data.append((row[0], decrypt_username, decrypt_password, decrypt_role))
            else:
                decrypted_data.append((row[0], row[1], row[2], row[3]))
    cursor.close()
    conn.close()

    return render_template("view_user.html", data=decrypted_data, role=role)

@app.route('/get_user/<int:id_user>')
def get_user(id_user):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE users.id_user = %s", (id_user,))
    hasil = cursor.fetchall()

    
    playfair_matrix = generate_playfair_matrix(key)

    decrypted_data = []
    for row in hasil:
        ecb_username = decrypt_ecb(row[1], key, 1)
        ecb_password = decrypt_ecb(row[2], key, 1)
        ecb_role = decrypt_ecb(row[3], key, 1)
        
        decrypt_username = decrypt(ecb_username, playfair_matrix)
        decrypt_password = decrypt(ecb_password, playfair_matrix)
        decrypt_role = decrypt(ecb_role, playfair_matrix)
        
        if 'role' in session:
            role = session['role']
            if role == 'admin':
                decrypted_data.append((row[0], row[1], row[2], row[3]))
            else:
                decrypted_data.append((row[0], row[1], row[2], row[3]))
                
    dummy_data = {
        'id': id_user,
        'username': decrypt_username,
        'password': decrypt_password,
        'role': decrypt_role,
    }
    cursor.close()
    conn.close()
    
    return jsonify(dummy_data)

def update_user_in_database(id_user, username, password, role):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        
        playfair_matrix = generate_playfair_matrix(key)
        playfair_username = encrypt(username, playfair_matrix)
        playfair_password = encrypt(password, playfair_matrix)
        playfair_role = encrypt(role, playfair_matrix)
        
        encrypted_username = encrypt_ecb(playfair_username, key,1)
        encrypted_password = encrypt_ecb(playfair_password, key,1)
        encrypted_role = encrypt_ecb(playfair_role, key,1)
        
        update_query = "UPDATE users SET username = %s, password = %s, role = %s WHERE id_user = %s"
        cursor.execute(update_query, (encrypted_username, encrypted_password, encrypted_role, id_user))

        conn.commit()

        cursor.close()
        conn.close()

        return True
    except Exception as e:
        print(f"Error updating data: {str(e)}")
        return False


@app.route('/update_user', methods=['POST'])
def update_user():
    try:
        id_user = request.form.get('id')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        success = update_user_in_database(id_user, username, password, role)

        if success:
            return jsonify({'message': 'Data updated successfully'})
        else:
            return jsonify({'error': 'Failed to update data'}), 500
    except Exception as e:
        print(f"Error updating data: {str(e)}")
        return jsonify({'error': 'Failed to update data'}), 500


@app.route('/delete_user/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM users WHERE id_user=%s', (id,))
        connection.commit()
        connection.close()
        return jsonify({"message": "Data deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)})


# RESEPSIONIS
@app.route("/resepsionis", methods=["GET", "POST"])
def resepsionis():
    if 'logged_in' in session and session['logged_in'] and session.get('role') == 'resepsionis ':
        if request.method == "POST":
            role = session.get('role', '')
            username = session.get('username', '')
            nama = request.form["nama"]
            lahir = request.form["lahir"]
            alamat = request.form["alamat"]
            kontak = request.form["kontak"]

            conn = mysql.connect()
            cursor = conn.cursor()

            
            playfair_matrix = generate_playfair_matrix(key)
            playfair_nama = encrypt(nama, playfair_matrix)
            playfair_lahir = encrypt(lahir, playfair_matrix)
            playfair_alamat = encrypt(alamat, playfair_matrix)
            playfair_kontak = encrypt(kontak, playfair_matrix)


            encrypted_nama = encrypt_ecb(playfair_nama, key, 1)
            encrypted_lahir = encrypt_ecb(playfair_lahir, key, 1)
            encrypted_alamat = encrypt_ecb(playfair_alamat, key, 1)
            encrypted_kontak = encrypt_ecb(playfair_kontak, key, 1)

            cursor.execute("INSERT INTO data_pasien (nama, lahir, alamat, kontak) VALUES (%s, %s, %s, %s)", (encrypted_nama,encrypted_lahir, encrypted_alamat, encrypted_kontak))
            conn.commit()
            cursor.close()
            conn.close()

            return render_template("resepsionis.html",  username=session.get('username', ''), role=session.get('role', ''), encrypted_name=encrypted_nama, encrypted_lahir=encrypted_lahir, encrypted_alamat=encrypted_alamat, encrypted_kontak=encrypted_kontak)
        return render_template("resepsionis.html", username=session.get('username', ''), role=session.get('role', ''))
    else:
        flash('Akses ditolak. Anda harus masuk sebagai dokter.', 'error')
        return redirect(url_for('index'))


@app.route("/view_pasien")
def view_pasien():
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM data_pasien")
    hasil = cursor.fetchall()

    
    playfair_matrix = generate_playfair_matrix(key)

    decrypted_data = []
    for row in hasil:
        ecb_nama = decrypt_ecb(row[1], key, 1)
        ecb_umur = decrypt_ecb(row[2], key, 1)
        ecb_alamat = decrypt_ecb(row[3], key, 1)
        ecb_kontak = decrypt_ecb(row[4], key, 1)
        
        decrypt_nama = decrypt(ecb_nama, playfair_matrix)
        decrypt_umur = decrypt(ecb_umur, playfair_matrix)
        decrypt_alamat = decrypt(ecb_alamat, playfair_matrix)
        decrypt_kontak = decrypt(ecb_kontak, playfair_matrix)
        if 'role' in session:
            role = session['role']
            if role == 'resepsionis ' or role == 'dokter' or role == 'admin ':
                decrypted_data.append((row[0], decrypt_nama, decrypt_umur, decrypt_alamat, decrypt_kontak ))
            else:
                decrypted_data.append((row[0], row[1], row[2], row[3], row[4]))
    cursor.close()
    conn.close()

    return render_template("view_pasien.html", data=decrypted_data, role=role)

@app.route('/get_pasien/<int:id_pasien>')
def get_pasien(id_pasien):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM data_pasien WHERE data_pasien.id_pasien = %s", (id_pasien,))
    hasil = cursor.fetchall()

    
    playfair_matrix = generate_playfair_matrix(key)

    decrypted_data = []
    for row in hasil:
        ecb_nama = decrypt_ecb(row[1], key, 1)
        ecb_umur = decrypt_ecb(row[2], key, 1)
        ecb_alamat = decrypt_ecb(row[3], key, 1)
        ecb_kontak = decrypt_ecb(row[4], key, 1)
        
        decrypt_nama = decrypt(ecb_nama, playfair_matrix)
        decrypt_umur = decrypt(ecb_umur, playfair_matrix)
        decrypt_alamat = decrypt(ecb_alamat, playfair_matrix)
        decrypt_kontak = decrypt(ecb_kontak, playfair_matrix)
        if 'role' in session:
            role = session['role']
            if role == 'resepsionis':
                decrypted_data.append((row[0], decrypt_nama, decrypt_umur, decrypt_alamat, decrypt_kontak))
            else:
                decrypted_data.append((row[0], row[1], row[2], row[3], row[4]))
                
    dummy_data = {
        'id': id_pasien,
        'nama': decrypt_nama,
        'umur': decrypt_umur,
        'alamat': decrypt_alamat,
        'kontak': decrypt_kontak,
        # Add other dummy data fields
    }
    cursor.close()
    conn.close()
    
    return jsonify(dummy_data)

def update_pasien_in_database(id, nama, umur, alamat, kontak):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        
        playfair_matrix = generate_playfair_matrix(key)
        playfair_nama = encrypt(nama, playfair_matrix)
        playfair_umur = encrypt(umur, playfair_matrix)
        playfair_alamat = encrypt(alamat, playfair_matrix)
        playfair_kontak = encrypt(kontak, playfair_matrix)
        
        encrypted_nama = encrypt_ecb(playfair_nama, key,1)
        encrypted_umur = encrypt_ecb(playfair_umur, key,1)
        encrypted_alamat = encrypt_ecb(playfair_alamat, key,1)
        encrypted_kontak = encrypt_ecb(playfair_kontak, key,1)
        
        update_query = "UPDATE data_pasien SET nama = %s, lahir = %s, alamat = %s, kontak = %s WHERE id_pasien = %s"
        cursor.execute(update_query, (encrypted_nama, encrypted_umur, encrypted_alamat, encrypted_kontak, id))

        conn.commit()
        cursor.close()
        conn.close()

        return True
    except Exception as e:
        print(f"Error updating data: {str(e)}")
        return False

@app.route('/update_pasien', methods=['POST'])
def update_pasien():
    try:
        id_pasien = request.form.get('id')
        nama = request.form.get('nama')
        umur = request.form.get('umur')
        alamat = request.form.get('alamat')
        kontak = request.form.get('kontak')
        
        success = update_pasien_in_database(id_pasien, nama, umur, alamat, kontak)
        if success:
            return jsonify({'message': 'Data updated successfully'})
        else:
            return jsonify({'error': 'Failed to update data'}), 500
    except Exception as e:
        print(f"Error updating data: {str(e)}")
        return jsonify({'error': 'Failed to update data'}), 500

@app.route('/delete_pasien/<int:id>', methods=['DELETE'])
def delete_pasien(id):
    try:
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM data_pasien WHERE id_pasien=%s', (id,))
        connection.commit()
        connection.close()
        return jsonify({"message": "Data deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/antri", methods=["GET", "POST"])
def antri():
    if 'logged_in' in session and session['logged_in'] and session.get('role') == 'resepsionis ':
        conn = mysql.connect()
        cursor = conn.cursor()
        if request.method == "POST":
            id = request.form['id']
            status = 1
            evaluasi_options = request.form.getlist('evaluasi[]')

            if not evaluasi_options:
                conn = mysql.connect()
                cursor = conn.cursor()

                
                playfair_matrix = generate_playfair_matrix(key)
                cursor.execute("SELECT nama, lahir, alamat, kontak FROM data_pasien WHERE id_pasien = %s", (id,))
                hasil_program2 = cursor.fetchone()

                decrypted_data_program = []
                if hasil_program2:
                        ecb_name = decrypt_ecb(hasil_program2[0], key, 1)
                        ecb_lahir = decrypt_ecb(hasil_program2[1], key, 1)
                        ecb_address = decrypt_ecb(hasil_program2[2], key, 1)
                        ecb_kontak = decrypt_ecb(hasil_program2[3], key, 1)
                        decrypted_name = decrypt(ecb_name, playfair_matrix)
                        decrypted_lahir = decrypt(ecb_lahir, playfair_matrix)
                        decrypted_address = decrypt(ecb_address, playfair_matrix)
                        decrypted_kontak = decrypt(ecb_kontak, playfair_matrix)
                        decrypted_data_program.append((decrypted_name, decrypted_lahir, decrypted_address, decrypted_kontak))
                        
                        cursor.close()
                        conn.close()
                return render_template("antri.html",  data=decrypted_data_program, username=session.get('username',''), role=session.get('role',''))

            else:
                tanggal = request.form["tanggal"]
                rencana = request.form["rencana"]
                evaluasi = request.form["evaluasi"]
                riwayat = request.form["riwayat"]
                tes = request.form["tes"]
                pencitraan = request.form["pencitraan"]
                selectedId = request.form["selectedId"]
                role = session['role']
                
                conn = mysql.connect()
                cursor = conn.cursor()
                id = int(id)
                status = int(status)
                
                playfair_matrix = generate_playfair_matrix(key)
                playfair_tanggal = encrypt(tanggal, playfair_matrix)
                playfair_rencana = encrypt(rencana, playfair_matrix)
                playfair_evaluasi = encrypt(evaluasi, playfair_matrix)
                playfair_riwayat = encrypt(riwayat, playfair_matrix)
                playfair_tes = encrypt(tes, playfair_matrix)
                playfair_pencitraan = encrypt(pencitraan, playfair_matrix)

                encrypted_tanggal = encrypt_ecb(playfair_tanggal, key, 1)
                encrypted_rencana = encrypt_ecb(playfair_rencana, key, 1)
                encrypted_evaluasi = encrypt_ecb(playfair_evaluasi, key, 1)
                encrypted_riwayat = encrypt_ecb(playfair_riwayat, key, 1)
                encrypted_tes = encrypt_ecb(playfair_tes, key, 1)
                encrypted_pencitraan = encrypt_ecb(playfair_pencitraan, key, 1)

                cursor.execute("INSERT INTO pemeriksaan (pasien_id, tanggal, rencana, evaluasi, riwayat,  tes, pencitraan, status, obat_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                               (id, encrypted_tanggal, encrypted_rencana, encrypted_evaluasi,encrypted_riwayat, encrypted_tes, encrypted_pencitraan, status, selectedId ))
                conn.commit()
                cursor.close()
                conn.close()
                return render_template("antri.html", id=id)
        return render_template("antri.html", username=session.get('username', ''), role=session.get('role', ''))
    else:
        flash('Akses ditolak. Anda harus masuk sebagai dokter.', 'error')
        return redirect(url_for('index'))

@app.route("/view_antri")
def view_antri():
    conn = mysql.connect()
    cursor = conn.cursor()
    if 'role' in session:
        role = session['role']
        if role == 'resepsionis ' or role == 'dokter':
            cursor.execute("SELECT * FROM pemeriksaan INNER JOIN data_pasien ON pemeriksaan.pasien_id = data_pasien.id_pasien  WHERE pemeriksaan.status = 1 ORDER BY pemeriksaan.id_pemeriksaan")
            hasil = cursor.fetchall()

            
            playfair_matrix = generate_playfair_matrix(key)

            decrypted_data = []
            for row in hasil:
                ecb_nama = decrypt_ecb(row[11], key, 1)
                ecb_umur = decrypt_ecb(row[12], key, 1)
                ecb_alamat = decrypt_ecb(row[13], key, 1)
                ecb_kontak = decrypt_ecb(row[14], key, 1)
                        
                decrypt_nama = decrypt(ecb_nama, playfair_matrix)
                decrypt_umur = decrypt(ecb_umur, playfair_matrix)
                decrypt_alamat = decrypt(ecb_alamat, playfair_matrix)
                decrypt_kontak = decrypt(ecb_kontak, playfair_matrix)
                decrypted_data.append((row[0], row[1], decrypt_nama, decrypt_umur, decrypt_alamat, decrypt_kontak, row[1]))
        
        elif role == 'apoteker':
            cursor.execute("SELECT * FROM pemeriksaan INNER JOIN data_pasien ON pemeriksaan.pasien_id = data_pasien.id_pasien INNER JOIN obat ON pemeriksaan.obat_id = obat.id_obat WHERE pemeriksaan.status = 2 ORDER BY pemeriksaan.id_pemeriksaan")
            hasil = cursor.fetchall()

            
            playfair_matrix = generate_playfair_matrix(key)

            decrypted_data = []
            for row in hasil:
                ecb_nama = decrypt_ecb(row[11], key, 1)
                ecb_obat = decrypt_ecb(row[16], key,1 )
                ecb_kategori = decrypt_ecb(row[17], key,1 )
                ecb_bentuk = decrypt_ecb(row[18], key,1 )
                ecb_dosis = decrypt_ecb(row[19], key,1 )
                ecb_penggunaan = decrypt_ecb(row[20], key,1 )
                                
                decrypt_nama = decrypt(ecb_nama, playfair_matrix)
                decrypt_obat = decrypt(ecb_obat, playfair_matrix)
                decrypt_kategori = decrypt(ecb_kategori, playfair_matrix)
                decrypt_bentuk = decrypt(ecb_bentuk, playfair_matrix)
                decrypt_dosis = decrypt(ecb_dosis, playfair_matrix)
                decrypt_penggunaan = decrypt(ecb_penggunaan, playfair_matrix)
                
                decrypted_data.append((row[0], decrypt_nama, decrypt_obat, decrypt_kategori, decrypt_bentuk, decrypt_dosis, decrypt_penggunaan, row[1]))
        
        else:
            decrypted_data.append((row[0], row[11], row[12], row[13], row[14], row[1]))
    cursor.close()
    conn.close()

    return render_template("view_antri.html", data=decrypted_data, role=role)

@app.route('/ubah_nama', methods=['POST'])
def ubah_nama():
    conn = mysql.connect()
    cursor = conn.cursor()

    data = request.get_json()
    id_selected = data['id']
    nama_baru = data['nama_baru']

    cursor.execute("UPDATE pemeriksaan SET status = %s WHERE id_pemeriksaan = %s", (nama_baru, id_selected))
    conn.commit()

    return jsonify({'status': 'success'})


# DOKTER
@app.route("/dokter", methods=["GET", "POST"])
def dokter():
    if 'logged_in' in session and session['logged_in'] and session.get('role') == 'dokter':
        return render_template("dokter.html", username=session.get('username', ''), role=session.get('role', ''))
    else:
        flash('Akses ditolak. Anda harus masuk sebagai dokter.', 'error')
        return redirect(url_for('index'))

@app.route("/pasien", methods=["GET", "POST"])
def pasien():
    if 'logged_in' in session and session['logged_in'] and session.get('role') == 'dokter':
        conn = mysql.connect()
        cursor = conn.cursor()
        id_pasien = request.form.get('pasien')
        id = request.args.get('id')
        nama = request.args.get('nama')
        umur = request.args.get('umur')
        alamat = request.args.get('alamat')
        kontak = request.args.get('kontak')
        idpasien = request.args.get('pasien')
        if request.method == "POST":
            tanggal = request.form["tanggal"]
            rencana = request.form["rencana"]
            evaluasi = request.form["evaluasi"]
            riwayat = request.form["riwayat"]
            tes = request.form["tes"]
            pencitraan = request.form["pencitraan"]
            pasien = request.form["id"]
            selectedId = request.form["selectedId"]
            role = session['role']

            if rencana:
                conn = mysql.connect()
                cursor = conn.cursor()
                id = int(id_pasien)
                status = 2
                
                playfair_matrix = generate_playfair_matrix(key)
                playfair_tanggal = encrypt(tanggal, playfair_matrix)
                playfair_rencana = encrypt(rencana, playfair_matrix)
                playfair_evaluasi = encrypt(evaluasi, playfair_matrix)
                playfair_riwayat = encrypt(riwayat, playfair_matrix)
                playfair_tes = encrypt(tes, playfair_matrix)
                playfair_pencitraan = encrypt(pencitraan, playfair_matrix)

                encrypted_tanggal = encrypt_ecb(playfair_tanggal, key, 1)
                encrypted_rencana = encrypt_ecb(playfair_rencana, key, 1)
                encrypted_evaluasi = encrypt_ecb(playfair_evaluasi, key, 1)
                encrypted_riwayat = encrypt_ecb(playfair_riwayat, key, 1)
                encrypted_tes = encrypt_ecb(playfair_tes, key, 1)
                encrypted_pencitraan = encrypt_ecb(playfair_pencitraan, key, 1)

                cursor.execute("UPDATE pemeriksaan SET tanggal = %s, rencana = %s, evaluasi = %s, riwayat = %s, tes = %s, pencitraan = %s, status = %s, obat_id = %s WHERE  id_pemeriksaan= %s",
                               (encrypted_tanggal, encrypted_rencana, encrypted_evaluasi, encrypted_riwayat, encrypted_tes, encrypted_pencitraan, status, selectedId, pasien))
                conn.commit()
                cursor.close()
                conn.close()
                return render_template("pasien.html", id=id, encrypted_tanggal=encrypted_tanggal, encrypted_rencana=encrypted_rencana, encrypted_evaluasi=encrypted_evaluasi, encrypted_riwayat=encrypted_riwayat, encrypted_tes=encrypted_tes, encrypted_pencitraan=encrypted_pencitraan, show_popup=True)
            
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT id_obat, nama_obat FROM obat")
        hasil_program1 = cursor.fetchall()

        
        playfair_matrix = generate_playfair_matrix(key)

        decrypted_data_program1 = []
        for row in hasil_program1:

            ecb_name = decrypt_ecb(row[1], key, 1)
            decrypted_id = row[0]
            decrypted_name = decrypt(ecb_name, playfair_matrix)
            decrypted_data_program1.append((decrypted_id,decrypted_name))

            cursor.execute("SELECT * FROM pemeriksaan INNER JOIN data_pasien ON pemeriksaan.pasien_id = data_pasien.id_pasien WHERE id_pemeriksaan = %s", (id,))
            hasil_program2 = cursor.fetchone()

        decrypted_data_program2 = []
        if hasil_program2:
                ecb_name = decrypt_ecb(hasil_program2[11], key, 1)
                ecb_lahir = decrypt_ecb(hasil_program2[12], key, 1)
                ecb_address = decrypt_ecb(hasil_program2[13], key, 1)
                ecb_kontak = decrypt_ecb(hasil_program2[14], key, 1)
                decrypted_name = decrypt(ecb_name, playfair_matrix)
                decrypted_lahir = decrypt(ecb_lahir, playfair_matrix)
                decrypted_address = decrypt(ecb_address, playfair_matrix)
                decrypted_kontak = decrypt(ecb_kontak, playfair_matrix)
                decrypted_data_program2.append((decrypted_name, decrypted_lahir, decrypted_address, decrypted_kontak))

                cursor.close()
                conn.close()
        return render_template("pasien.html", obat=decrypted_data_program1, id=id, nama=nama, umur=umur, alamat=alamat, kontak=kontak, pasien=idpasien, username=session.get('username', ''), role=session.get('role', ''))
    else:
        flash('Akses ditolak. Anda harus masuk sebagai dokter.', 'error')
        return redirect(url_for('index'))
    return render_template("pasien.html")


@app.route("/view_pemeriksaan")
def view_pemeriksaan():
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM data_pasien")
    hasil = cursor.fetchall()

    
    playfair_matrix = generate_playfair_matrix(key)

    decrypted_data = []
    for row in hasil:
        ecb_nama = decrypt_ecb(row[1], key, 1)
        
        decrypt_nama = decrypt(ecb_nama, playfair_matrix)
        if 'role' in session:
            role = session['role']
            if role == 'resepsionis ' or role == 'dokter' or role == 'apoteker' or role == 'admin ':
                decrypted_data.append((row[0], decrypt_nama))
            else:
                decrypted_data.append((row[0], row[1]))
    cursor.close()
    conn.close()

    return render_template("view_pemeriksaan.html", data=decrypted_data, role=role)


@app.route("/view_data/<int:id>")
def view_data(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute(("SELECT * FROM pemeriksaan INNER JOIN data_pasien ON pemeriksaan.pasien_id = data_pasien.id_pasien INNER JOIN obat ON pemeriksaan.obat_id = obat.id_obat WHERE data_pasien.id_pasien =%s AND pemeriksaan.status = 3 ORDER BY pemeriksaan.id_pemeriksaan;"),(id))
    hasil = cursor.fetchall()

    
    playfair_matrix = generate_playfair_matrix(key)

    decrypted_data = []
    for row in hasil:
        ecb_nama = decrypt_ecb(row[11], key,1 )
        ecb_lahir = decrypt_ecb(row[12], key,1 )
        ecb_alamat = decrypt_ecb(row[13], key,1 )
        ecb_kontak = decrypt_ecb(row[14], key,1 )
        ecb_tanggal = decrypt_ecb(row[2], key,1 )
        ecb_rencana = decrypt_ecb(row[3], key,1 )
        ecb_evaluasi = decrypt_ecb(row[4], key,1 )
        ecb_riwayat = decrypt_ecb(row[5], key,1 )
        ecb_tes = decrypt_ecb(row[6], key,1 )
        ecb_pencitraan = decrypt_ecb(row[7], key,1 )
        ecb_obat = decrypt_ecb(row[16], key,1 )
        ecb_kategori = decrypt_ecb(row[17], key,1 )
        ecb_bentuk = decrypt_ecb(row[18], key,1 )
        ecb_dosis = decrypt_ecb(row[19], key,1 )
        ecb_penggunaan = decrypt_ecb(row[20], key,1 )

        decrypted_name = decrypt(ecb_nama, playfair_matrix)
        decrypted_lahir = decrypt(ecb_lahir, playfair_matrix)
        decrypt_alamat = decrypt(ecb_alamat, playfair_matrix)
        decrypt_kontak = decrypt(ecb_kontak, playfair_matrix)
        decrypt_tanggal = decrypt(ecb_tanggal, playfair_matrix)
        decrypt_rencana = decrypt(ecb_rencana, playfair_matrix)
        decrypt_evaluasi = decrypt(ecb_evaluasi, playfair_matrix)
        decrypt_riwayat = decrypt(ecb_riwayat, playfair_matrix)
        decrypt_tes = decrypt(ecb_tes, playfair_matrix)
        decrypt_pencitraan = decrypt(ecb_pencitraan, playfair_matrix)
        decrypt_obat = decrypt(ecb_obat, playfair_matrix)
        decrypt_kategori = decrypt(ecb_kategori, playfair_matrix)
        decrypt_bentuk = decrypt(ecb_bentuk, playfair_matrix)
        decrypt_dosis = decrypt(ecb_dosis, playfair_matrix)
        decrypt_penggunaan = decrypt(ecb_penggunaan, playfair_matrix)
        if 'role' in session:
            role = session['role']
            if role == 'dokter' or role == 'admin ':
                decrypted_data.append((row[0], row[1], decrypted_name, decrypted_lahir, decrypt_alamat,
                                       decrypt_kontak, decrypt_tanggal, decrypt_rencana, decrypt_evaluasi, decrypt_riwayat,
                                       decrypt_tes, decrypt_pencitraan, decrypt_obat, decrypt_kategori, decrypt_bentuk,
                                       decrypt_dosis, decrypt_penggunaan))
            elif role == 'apoteker':
                decrypted_data.append((row[0], row[1], decrypted_name, decrypted_lahir, decrypt_alamat,
                                       decrypt_kontak,
                                       decrypt_tanggal, row[3], row[4], row[5], row[6], row[7],
                                       decrypt_obat, decrypt_kategori, decrypt_bentuk, decrypt_dosis,
                                       decrypt_penggunaan))
            elif role == 'resepsionis ':
                decrypted_data.append((row[0], row[1], decrypted_name, decrypted_lahir, decrypt_alamat, decrypt_kontak,
                                       decrypt_tanggal, row[3], row[4], row[5], row[6], row[7], row[16], row[17], row[18],
                                       row[19], row[20]))
            else:
                decrypted_data.append((row[0], row[1], row[11], row[12], row[13], row[14], row[2], row[3],
                                       row[4], row[5], row[6], row[7], row[16], row[17], row[18],
                                       row[19], row [20]))
    cursor.close()
    conn.close()
    
    if not decrypted_data:
        return render_template("no_data.html")  # Create a template for displaying a message when there's no data

    return render_template("view_data.html", data=decrypted_data, role=role)

@app.route('/get_data/<int:id_pemeriksaan>')
def get_data(id_pemeriksaan):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pemeriksaan LEFT JOIN data_pasien ON pemeriksaan.pasien_id = data_pasien.id_pasien LEFT JOIN obat ON pemeriksaan.obat_id = obat.id_obat WHERE pemeriksaan.id_pemeriksaan = %s", (id_pemeriksaan,))
    hasil = cursor.fetchall()

    
    playfair_matrix = generate_playfair_matrix(key)

    decrypted_data = []
    for row in hasil:
        id_pasien = row[1]
        ecb_nama = decrypt_ecb(row[11], key,1 )
        ecb_lahir = decrypt_ecb(row[12], key,1 )
        ecb_alamat = decrypt_ecb(row[13], key,1 )
        ecb_kontak = decrypt_ecb(row[14], key,1 )
        ecb_tanggal = decrypt_ecb(row[2], key,1 )
        ecb_rencana = decrypt_ecb(row[3], key,1 )
        ecb_evaluasi = decrypt_ecb(row[4], key,1 )
        ecb_riwayat = decrypt_ecb(row[5], key,1 )
        ecb_tes = decrypt_ecb(row[6], key,1 )
        ecb_pencitraan = decrypt_ecb(row[7], key,1 )
        ecb_obat = decrypt_ecb(row[16], key,1 )
        ecb_kategori = decrypt_ecb(row[17], key,1 )
        ecb_bentuk = decrypt_ecb(row[18], key,1 )
        ecb_dosis = decrypt_ecb(row[19], key,1 )
        ecb_penggunaan = decrypt_ecb(row[20], key,1 )

        decrypted_name = decrypt(ecb_nama, playfair_matrix)
        decrypted_lahir = decrypt(ecb_lahir, playfair_matrix)
        decrypt_alamat = decrypt(ecb_alamat, playfair_matrix)
        decrypt_kontak = decrypt(ecb_kontak, playfair_matrix)
        decrypt_tanggal = decrypt(ecb_tanggal, playfair_matrix)
        decrypt_rencana = decrypt(ecb_rencana, playfair_matrix)
        decrypt_evaluasi = decrypt(ecb_evaluasi, playfair_matrix)
        decrypt_riwayat = decrypt(ecb_riwayat, playfair_matrix)
        decrypt_tes = decrypt(ecb_tes, playfair_matrix)
        decrypt_pencitraan = decrypt(ecb_pencitraan, playfair_matrix)
        decrypt_obat = decrypt(ecb_obat, playfair_matrix)
        decrypt_kategori = decrypt(ecb_kategori, playfair_matrix)
        decrypt_bentuk = decrypt(ecb_bentuk, playfair_matrix)
        decrypt_dosis = decrypt(ecb_dosis, playfair_matrix)
        decrypt_penggunaan = decrypt(ecb_penggunaan, playfair_matrix)
        if 'role' in session:
            role = session['role']
            if role == 'dokter':
                decrypted_data.append((row[0], row[1], decrypted_name, decrypted_lahir, decrypt_alamat, decrypt_kontak,
                                       decrypt_tanggal, decrypt_rencana, decrypt_evaluasi,
                                       decrypt_riwayat, decrypt_tes, decrypt_pencitraan,
                                       decrypt_obat, decrypt_kategori, decrypt_bentuk, decrypt_dosis,
                                       decrypt_penggunaan))
            elif role == 'apoteker':
                decrypted_data.append((row[0], row[1], decrypted_name, decrypted_lahir, decrypt_alamat, decrypt_kontak,
                                       decrypt_tanggal, row[3], row[4], row[5], row[6], row[7],
                                       decrypt_obat, decrypt_kategori, decrypt_bentuk, decrypt_dosis,
                                       decrypt_penggunaan))
            elif role == 'resepsionis ':
                decrypted_data.append((row[0], row[1], decrypted_name, decrypted_lahir, decrypt_alamat, decrypt_kontak,
                                       decrypt_tanggal, row[3], row[4], row[5], row[6], row[7], row[16], row[17], 
                                       row[18], row[19], row[20]))
            else:
                decrypted_data.append((row[0], row[1], row[11], row[12], row[13], row[14], row[2], row[3],
                                       row[4], row[5], row[6], row[7], row[16], row[17], row[18], row[19],
                                       row[20]))
                            
    dummy_data = {
        'id': id_pemeriksaan,
        'id_pasien': id_pasien,
        'nama': decrypted_name,
        'umur': decrypted_lahir,
        'alamat': decrypt_alamat,
        'kontak': decrypt_kontak,
        'tanggal': decrypt_tanggal,
        'rencana': decrypt_rencana,
        'evaluasi': decrypt_evaluasi,
        'riwayat': decrypt_riwayat,
        'tes': decrypt_tes,
        'pencitraan': decrypt_pencitraan,
        'namaobat': decrypt_obat,
        'kategoriobat': decrypt_kategori,
        'bentukobat': decrypt_bentuk,
        'dosisobat': decrypt_dosis,
        'carapenggunaan': decrypt_penggunaan,
    }
    cursor.close()
    conn.close()
    
    return jsonify(dummy_data)

def update_data_in_database(id_pemeriksaan, id_pasien, rencana, evaluasi, riwayat, tes, pencitraan):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        
        id_pasien = int(id_pasien)
        playfair_matrix = generate_playfair_matrix(key)
        playfair_rencana = encrypt(rencana, playfair_matrix)
        playfair_evaluasi = encrypt(evaluasi, playfair_matrix)
        playfair_riwayat = encrypt(riwayat, playfair_matrix)
        playfair_tes = encrypt(tes, playfair_matrix)
        playfair_pencitraan = encrypt(pencitraan, playfair_matrix)

        encrypted_rencana = encrypt_ecb(playfair_rencana, key,1)
        encrypted_evaluasi = encrypt_ecb(playfair_evaluasi, key,1)
        encrypted_riwayat = encrypt_ecb(playfair_riwayat, key,1)
        encrypted_tes = encrypt_ecb(playfair_tes, key,1)
        encrypted_pencitraan = encrypt_ecb(playfair_pencitraan, key,1)


        update_query = "UPDATE pemeriksaan SET pasien_id = %s, rencana = %s, evaluasi = %s, riwayat = %s, tes = %s, pencitraan = %s WHERE id_pemeriksaan = %s"
        cursor.execute(update_query, (id_pasien, encrypted_rencana, encrypted_evaluasi, encrypted_riwayat, encrypted_tes, encrypted_pencitraan, id_pemeriksaan))

        conn.commit()

        cursor.close()
        conn.close()

        return True
    except Exception as e:
        print(f"Error updating data: {str(e)}")
        return False


@app.route('/update_data', methods=['POST'])
def update_data():
    try:
        id_pemeriksaan = request.form.get('id')
        id_pasien = request.form.get('id_pasien')
        rencana = request.form.get('rencana')
        evaluasi = request.form.get('evaluasi')
        riwayat = request.form.get('riwayat')
        tes = request.form.get('tes')
        pencitraan = request.form.get('pencitraan')

        success = update_data_in_database(id_pemeriksaan, id_pasien, rencana, evaluasi, riwayat, tes, pencitraan)
        if success:
            return jsonify({'message': 'Data updated successfully'})
        else:
            return jsonify({'error': 'Failed to update data'}), 500
    except Exception as e:
        print(f"Error updating data: {str(e)}")
        return jsonify({'error': 'Failed to update data'}), 500


@app.route('/delete_data/<int:id>', methods=['DELETE'])
def delete_data(id):
    try:
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM pemeriksaan WHERE id_pemeriksaan=%s', (id,))
        connection.commit()
        connection.close()
        return jsonify({"message": "Data deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)})


#APOTEKER
@app.route("/apoteker", methods=["GET", "POST"])
def apoteker():
    if 'role' in session and session['role'] == 'apoteker':
        if request.method == "POST":
            nama = request.form["nama"]
            kategori = request.form["kategori"]
            bentuk = request.form["bentuk"]
            dosis = request.form["dosis"]
            cara = request.form["cara"]

            conn = mysql.connect()
            cursor = conn.cursor()

            
            playfair_matrix = generate_playfair_matrix(key)
            playfair_nama = encrypt(nama, playfair_matrix)
            playfair_kategori = encrypt(kategori, playfair_matrix)
            playfair_bentuk = encrypt(bentuk, playfair_matrix)
            playfair_dosis = encrypt(dosis, playfair_matrix)
            playfair_cara = encrypt(cara, playfair_matrix)

            encrypted_nama = encrypt_ecb(playfair_nama, key,1)
            encrypted_kategori = encrypt_ecb(playfair_kategori, key,1)
            encrypted_bentuk = encrypt_ecb(playfair_bentuk, key,1)
            encrypted_dosis = encrypt_ecb(playfair_dosis, key,1)
            encrypted_cara = encrypt_ecb(playfair_cara, key,1)

            cursor.execute("INSERT INTO obat (nama_obat, kategori, bentuk, dosis, cara_penggunaan) VALUES (%s,%s,%s,%s,%s)",
                           (encrypted_nama, encrypted_kategori, encrypted_bentuk, encrypted_dosis, encrypted_cara))
            conn.commit()

            cursor.close()
            conn.close()

            return render_template("apoteker.html", encrypted_name=encrypted_nama, encrypted_kategori=encrypted_kategori, encrypted_bentuk=encrypted_bentuk, encrypted_dosis=encrypted_dosis, encrypted_cara=encrypted_cara)

        return render_template("apoteker.html")

    abort(403)
        
@app.route("/view_obat")
def view_obat():
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM obat")
    hasil = cursor.fetchall()

    
    playfair_matrix = generate_playfair_matrix(key)

    decrypted_data = []
    for row in hasil:
        ecb_obat = decrypt_ecb(row[1], key, 1)
        ecb_kategori = decrypt_ecb(row[2], key, 1)
        ecb_bentuk = decrypt_ecb(row[3], key, 1)
        ecb_dosis = decrypt_ecb(row[4], key, 1)
        ecb_penggunaan = decrypt_ecb(row[5], key, 1)

        decrypt_obat = decrypt(ecb_obat, playfair_matrix)
        decrypt_kategori = decrypt(ecb_kategori, playfair_matrix)
        decrypt_bentuk = decrypt(ecb_bentuk, playfair_matrix)
        decrypt_dosis = decrypt(ecb_dosis, playfair_matrix)
        decrypt_penggunaan = decrypt(ecb_penggunaan, playfair_matrix)
        if 'role' in session:
            role = session['role']
            if role == 'apoteker' or role == 'admin ':
                decrypted_data.append((row[0], decrypt_obat, decrypt_kategori, decrypt_bentuk, decrypt_dosis,
                                       decrypt_penggunaan))
            else:
                decrypted_data.append((row[0], row[1], row[2], row[3], row[4], row[5]))
    cursor.close()
    conn.close()
    return render_template("view_obat.html", data=decrypted_data, role=role)

@app.route('/get_obat/<int:id_obat>')
def get_obat(id_obat):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM obat WHERE obat.id_obat = %s", (id_obat,))
    hasil = cursor.fetchall()

    
    playfair_matrix = generate_playfair_matrix(key)

    decrypted_data = []
    for row in hasil:
        ecb_obat = decrypt_ecb(row[1], key, 1)
        ecb_kategori = decrypt_ecb(row[2], key, 1)
        ecb_bentuk = decrypt_ecb(row[3], key, 1)
        ecb_dosis = decrypt_ecb(row[4], key, 1)
        ecb_penggunaan = decrypt_ecb(row[5], key, 1)

        decrypt_obat = decrypt(ecb_obat, playfair_matrix)
        decrypt_kategori = decrypt(ecb_kategori, playfair_matrix)
        decrypt_bentuk = decrypt(ecb_bentuk, playfair_matrix)
        decrypt_dosis = decrypt(ecb_dosis, playfair_matrix)
        decrypt_penggunaan = decrypt(ecb_penggunaan, playfair_matrix)
        if 'role' in session:
            role = session['role']
            if role == 'apoteker':
                decrypted_data.append((row[0], row[1], row[2], row[3], row[4], row[5]))
            else:
                decrypted_data.append((row[0], row[1], row[2], row[3], row[4], row[5]))
                
    dummy_data = {
        'id': id_obat,
        'namaobat': decrypt_obat,
        'kategoriobat': decrypt_kategori,
        'bentukobat': decrypt_bentuk,
        'dosisobat': decrypt_dosis,
        'carapenggunaan': decrypt_penggunaan,
    }
    cursor.close()
    conn.close()    
    return jsonify(dummy_data)

def update_obat_in_database(id_obat, nama, kategori, bentuk, dosis, cara_penggunaan):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        
        playfair_matrix = generate_playfair_matrix(key)
        playfair_nama = encrypt(nama, playfair_matrix)
        playfair_kategori = encrypt(kategori, playfair_matrix)
        playfair_bentuk = encrypt(bentuk, playfair_matrix)
        playfair_dosis = encrypt(dosis, playfair_matrix)
        playfair_cara = encrypt(cara_penggunaan, playfair_matrix)
        
        encrypted_nama = encrypt_ecb(playfair_nama, key,1)
        encrypted_kategori = encrypt_ecb(playfair_kategori, key,1)
        encrypted_bentuk = encrypt_ecb(playfair_bentuk, key,1)
        encrypted_dosis = encrypt_ecb(playfair_dosis, key,1)
        encrypted_cara = encrypt_ecb(playfair_cara, key,1)
        
        update_query = "UPDATE obat SET nama_obat = %s, kategori = %s, bentuk = %s, dosis = %s, cara_penggunaan = %s WHERE id_obat = %s"
        cursor.execute(update_query, (encrypted_nama, encrypted_kategori, encrypted_bentuk, encrypted_dosis, encrypted_cara, id_obat))

        conn.commit()

        cursor.close()
        conn.close()

        return True
    except Exception as e:
        print(f"Error updating data: {str(e)}")
        return False


@app.route('/update_obat', methods=['POST'])
def update_obat():
    try:
        id_obat = request.form.get('id')
        nama = request.form.get('namaobat')
        kategori = request.form.get('kategoriobat')
        bentuk = request.form.get('bentukobat')
        dosis = request.form.get('dosisobat')
        cara = request.form.get('carapenggunaan')
        
        success = update_obat_in_database(id_obat, nama, kategori, bentuk, dosis, cara)
        if success:
            return jsonify({'message': 'Data updated successfully'})
        else:
            return jsonify({'error': 'Failed to update data'}), 500
    except Exception as e:
        print(f"Error updating data: {str(e)}")
        return jsonify({'error': 'Failed to update data'}), 500


@app.route('/delete_obat/<int:id>', methods=['DELETE'])
def delete_obat(id):
    try:
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM obat WHERE id_obat=%s', (id,))
        connection.commit()
        connection.close()
        return jsonify({"message": "Data deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)})




    



if __name__ == "__main__":
    app.run(debug=True)
