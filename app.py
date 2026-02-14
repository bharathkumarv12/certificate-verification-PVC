from flask import Flask, render_template, request
import qrcode
import os
import uuid
import urllib.parse

app = Flask(__name__)

os.makedirs("static/qrcodes", exist_ok=True)

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

        # 🔥 Sevasindhu-style link
        seva_link = f"https://sevasindhuservices.karnataka.gov.in/t/{unique_id}"

        # 🔥 Proper formatted certificate text
        certificate_text = f"""Name of Applicant : {name}
Father Name/Husband’s Name:{father}
GSC Number:{gsc}
Present Address:{address}
Verification type: {verification}
This Certificate is valid for one year from{validity}
https://sevasindhuservices.karnataka.gov.in/t/XwL4bD99FD88A"""


        # Encode text for Google search
        encoded_text = urllib.parse.quote_plus(certificate_text)
        google_link = f"https://www.google.com/search?q={encoded_text}"

        # Generate QR
        qr = qrcode.make(google_link)
        qr_path = os.path.join("static/qrcodes", f"{unique_id}.png")
        qr.save(qr_path)

        return render_template(
            "form.html",
            qr_image=qr_path,
            certificate_text=certificate_text,
            google_link=google_link
        )

    return render_template(
        "form.html",
        qr_image=None,
        certificate_text=None,
        google_link=None
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
