import sqlite3
from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def login():
    login_form = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login</title>
        <link rel="stylesheet" href="/static/styles.css">
    </head>
    <body>
        <h2>Login Form</h2>
        <form method="post">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
            <br>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
            <br><br>
            <input type="submit" value="Login">
        </form>
        <br>
        <form action="/view-data" method="get">
            <button type="submit">View Data</button>
        </form>
    </body>
    </html>
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()

        return f"""<link rel="stylesheet" href="/static/styles.css">
        <h3>Selamat datang, {username}!</h3>
        <br>
        <form action="/" method="get">
            <button type="submit">Kembali ke Login</button>
        </form>
        <br>
        <form action="/view-data" method="get">
            <button type="submit">View Data</button>
        </form>
        """
    
    return render_template_string(login_form)


@app.route('/view-data', methods=['GET', 'POST'])
def view_data():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password FROM users')
    users = cursor.fetchall()
    conn.close()

    user_list = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>View Data</title>
        <link rel="stylesheet" href="/static/datapengguna.css">
    </head>
    <body>
        <h2>Data Pengguna:</h2>
        <table border="1">
            <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Password</th>
                <th>Aksi</th>
            </tr>
    """
    for user in users:
        user_list += f"""
            <tr>
                <td>{user[0]}</td>
                <td>{user[1]}</td>
                <td>{user[2]}</td>
                <td>
                    <form action="/delete/{user[0]}" method="post" style="display:inline;">
                        <button type="submit">Hapus</button>
                    </form>
                    <form action="/update/{user[0]}" method="get" style="display:inline;">
                        <button type="submit">Update</button>
                    </form>
                </td>
            </tr>
        """
    user_list += """
        </table>
        <br>
        <form action="/" method="get" class="centered-form">
            <button type="submit">Kembali ke Login</button>
        </form>
    </body>
    </html>
    """
    return user_list

@app.route('/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()

    cursor.execute('DELETE FROM sqlite_sequence WHERE name="users"')
    conn.commit()

    conn.close()
    return redirect('/view-data')

def get_next_available_id():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users ORDER BY id')
    used_ids = [user[0] for user in cursor.fetchall()]

    next_id = 1
    while next_id in used_ids:
        next_id += 1
    
    conn.close()
    return next_id


@app.route('/update/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET username = ?, password = ? WHERE id = ?', (username, password, user_id))
        conn.commit()
        conn.close()
        return redirect('/view-data')

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, password FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    update_form = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Update Data</title>
        <link rel="stylesheet" href="/static/styles.css">
    </head>
    <body>
        <h2>Update Data</h2>
        <form method="post">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" value="{user[0]}" required>
            <br>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" value="{user[1]}" required>
            <br><br>
            <input type="submit" value="Update">
        </form>
        <br>
        <form action="/view-data" method="get">
            <button type="submit">Kembali</button>
        </form>
    </body>
    </html>
    """
    return render_template_string(update_form)

if __name__ == '__main__':
    app.run(debug=True)
