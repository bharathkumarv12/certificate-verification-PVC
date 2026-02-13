from flask import Flask, render_template, request, send_file
import qrcode
import os
import uuid
import sqlite3

app = Flask(__name__)

# Create folders if not exist
os.makedirs("static/qrcodes", exist_ok=True)
os.makedirs("static/pdfs", exist_ok=True)

# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS certificates (
            id TEXT PRIMARY KEY,
            name TEXT,
            father TEXT,
            gsc TEXT,
            address TEXT,
            verification TEXT,
            validity TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- HOME / FORM ----------------

@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":

        unique_id = str(uuid.uuid4())[:8]

        name = request.form["name"]
        father = request.form["father"]
        gsc = request.form["gsc"]
        address = request.form["address"]
        verification = request.form["verification"]
        validity = request.form["validity"]

        pdf_file = request.files["pdf"]

        # Save PDF
        pdf_path = os.path.join("static/pdfs", f"{unique_id}.pdf")
        pdf_file.save(pdf_path)

        # Save to database
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO certificates
            (id, name, father, gsc, address, verification, validity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (unique_id, name, father, gsc, address, verification, validity))
        conn.commit()
        conn.close()

        # Generate QR
        certificate_url = request.host_url + "certificate/" + unique_id
        qr = qrcode.make(certificate_url)

        qr_path = os.path.join("static/qrcodes", f"{unique_id}.png")
        qr.save(qr_path)

        return render_template("form.html", qr_image=qr_path)

    return render_template("form.html", qr_image=None)


# ---------------- CERTIFICATE PAGE ----------------

@app.route("/certificate/<cert_id>")
def certificate(cert_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM certificates WHERE id=?", (cert_id,))
    record = cursor.fetchone()
    conn.close()

    if not record:
        return "Invalid Certificate"

    data = {
        "id": record[0],
        "name": record[1],
        "father": record[2],
        "gsc": record[3],
        "address": record[4],
        "verification": record[5],
        "validity": record[6]
    }

    return render_template("certificate.html", record=data)


# ---------------- DOWNLOAD PDF ----------------

@app.route("/download/<cert_id>")
def download_pdf(cert_id):
    file_path = os.path.join("static/pdfs", f"{cert_id}.pdf")
    return send_file(file_path, as_attachment=True)



