"""
email_sender.py
---------------
Sends the generated PDF investment memo to a user-supplied email address
via Gmail's SMTP server.  Uses only Python's stdlib — no extra packages.

Setup (one-time, takes 2 minutes)
----------------------------------
1. Enable 2-Step Verification on your Google account:
   https://myaccount.google.com/security

2. Create an App Password:
   https://myaccount.google.com/apppasswords
   → Select "Mail" + "Mac" (or any device) → Generate
   → Copy the 16-character password

3. Add to your .env file:
   EMAIL_SENDER=yourname@gmail.com
   EMAIL_PASSWORD=your_16_char_app_password

Why Gmail SMTP instead of SendGrid?
  - No external account signup required
  - Works on the free Gmail tier
  - smtplib is stdlib — zero extra dependencies
  - Straightforward to demo and explain in an interview
"""

import os
import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465          # SSL port (more reliable than STARTTLS 587 in demos)


def send_pdf_report(
    to_email: str,
    pdf_bytes: bytes,
    company: str,
    ticker: str,
) -> None:
    """
    Email a PDF investment memo as an attachment.

    Args:
        to_email:   Recipient email address (validated before calling this).
        pdf_bytes:  Raw PDF bytes from pdf_generator.generate_pdf().
        company:    Company name, e.g. 'JPMorgan Chase'
        ticker:     Stock ticker, e.g. 'JPM'

    Raises:
        EnvironmentError: If EMAIL_SENDER or EMAIL_PASSWORD are missing from .env.
        smtplib.SMTPException: On SMTP-level failures (auth error, timeout, etc.).
    """
    sender    = os.getenv("EMAIL_SENDER", "").strip()
    password  = os.getenv("EMAIL_PASSWORD", "").strip()

    if not sender or not password:
        raise EnvironmentError(
            "EMAIL_SENDER and EMAIL_PASSWORD must be set in your .env file. "
            "See src/utils/email_sender.py for setup instructions."
        )

    filename = f"{ticker.upper()}_research_memo.pdf"

    # Build the email 
    msg = EmailMessage()
    msg["Subject"] = f"📊 Investment Research Memo — {company} ({ticker.upper()})"
    msg["From"]    = f"Financial Research Assistant <{sender}>"
    msg["To"]      = to_email

    msg.set_content(
        f"Hi,\n\n"
        f"Please find attached the AI-generated investment research memo for "
        f"{company} ({ticker.upper()}).\n\n"
        f"This report was produced by the Financial Research Assistant using:\n"
        f"  • SEC EDGAR 10-K filings (most recent annual report)\n"
        f"  • Recent news articles\n"
        f"  • Multi-agent AI analysis (RAG + LangGraph + LLaMA 3)\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️  Disclaimer\n"
        f"This report is for informational and educational purposes only.\n"
        f"It does not constitute financial, investment, or legal advice.\n"
        f"Always consult a qualified financial advisor before making\n"
        f"investment decisions.\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Best regards,\n"
        f"Financial Research Assistant\n"
        f"Powered by RAG + LangGraph + SEC EDGAR\n"
    )

    # Attach the PDF
    msg.add_attachment(
        pdf_bytes,
        maintype="application",
        subtype="pdf",
        filename=filename,
    )

    # Send via Gmail SSL 
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
        server.login(sender, password)
        server.send_message(msg)
