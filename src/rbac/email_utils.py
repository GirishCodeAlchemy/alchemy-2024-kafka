import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SENDER_EMAIL = ""
RECIPIENT_EMAIL = ""


def send_email(sender_email, recipient_email,  subject, html_content):
    # SMTP server configuration
    smtp_server = ''
    smtp_port = 25

    # Create email message
    msg = MIMEMultipart("related")
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    html_part = MIMEText(html_content, "html")
    msg.attach(html_part)

    # Connect to SMTP server and send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.sendmail(sender_email, recipient_email, msg.as_string())


def generate_email(data, url):

    html_data = f"""
                <!DOCTYPE html>
                <html>
                <body>
                <h4>Hello,</h4>
                <h4>Please find the RBAC request submitted by. {data["requested_by"]}</h4>
                <h4>URL: {url}</h4>
                <h4>Details:</h4>
            """

    html_data += """
        <style>
        table {
            border-collapse: collapse;  }
        th, td {
            border: 1px solid black;  padding: 5px;  }
        th {
            background-color: #F0F0F0;  }
        </style>
        </br>
        <div>
        <table>
        <tr>
            <th>Requested Params</th>
            <th>Values</th>
        </tr>
        """

    for key, value in data.items():
        html_data += f"""<tr>
                    <td>{key.upper()}</td>
                    <td>{value}</td>
                </tr>"""

    html_data += """</table> </div></body>
                </html>"""
    subject = "RBAC Request"

    send_email(SENDER_EMAIL, RECIPIENT_EMAIL, subject, html_data)