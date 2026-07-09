import qrcode
from io import BytesIO
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

def generate_qr_png(data: str) -> BytesIO:
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def send_ticket_email(to_email: str, context: dict, qr_bytes: BytesIO, filename: str):
    subject = f"Успешно купен билет – {context.get('event_title','Настан')}"
    html_body = render_to_string("tickets_addons/email_ticket.html", context)
    email = EmailMessage(subject=subject, body=html_body, to=[to_email])
    email.content_subtype = "html"
    email.attach(filename=filename, content=qr_bytes.read(), mimetype="image/png")
    email.send(fail_silently=False)

def send_contact_email_to_admin(context: dict, admin_to: str):
    subject = "НОВА порака од контакт форма"
    html = render_to_string("tickets_addons/email_contact_to_admin.html", context)
    EmailMessage(subject, html, to=[admin_to]).send(fail_silently=False)
