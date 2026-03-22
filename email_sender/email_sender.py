#!/usr/bin/env python3
"""
Email Sender
A simple, extensible email sending utility using SMTP

Supports:
- Gmail (with app password)
- Outlook/Hotmail
- Any SMTP server

Usage:
    export SMTP_HOST="smtp.gmail.com"
    export SMTP_PORT="587"
    export SMTP_USER="your-email@gmail.com"
    export SMTP_PASS="your-app-password"
    export FROM_NAME="Your Name"
    
    python email_sender.py --to "recipient@example.com" --subject "Hello" --body "Message"
"""

import os
import sys
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


# --- Configuration ---

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_NAME = os.getenv("FROM_NAME", "Email Bot")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)


# --- Email Sending Functions ---

def create_message(from_email: str, from_name: str, to_email: str, 
                   subject: str, body: str, is_html: bool = False) -> MIMEMultipart:
    """Create an email message"""
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    
    # Attach body
    content_type = "html" if is_html else "plain"
    msg.attach(MIMEText(body, content_type))
    
    return msg


def send_email(to_email: str, subject: str, body: str, 
              is_html: bool = False, attachments: list = None) -> bool:
    """Send an email via SMTP"""
    
    if not SMTP_USER or not SMTP_PASS:
        print("ERROR: SMTP_USER and SMTP_PASS environment variables not set!")
        print("\nRequired environment variables:")
        print("  SMTP_HOST - SMTP server hostname")
        print("  SMTP_PORT - SMTP server port (587 for TLS)")
        print("  SMTP_USER - Your email address")
        print("  SMTP_PASS - Your password or app password")
        return False
    
    try:
        # Create message
        msg = create_message(FROM_EMAIL, FROM_NAME, to_email, subject, body, is_html)
        
        # Add attachments if provided
        if attachments:
            for filepath in attachments:
                with open(filepath, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                filename = os.path.basename(filepath)
                part.add_header("Content-Disposition", f"attachment; filename= {filename}")
                msg.attach(part)
        
        # Connect to SMTP server
        print(f"Connecting to {SMTP_HOST}:{SMTP_PORT}...")
        
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()  # Upgrade to TLS
        
        # Login
        server.login(SMTP_USER, SMTP_PASS)
        
        # Send
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        
        # Cleanup
        server.quit()
        
        print(f"✅ Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


# --- CLI Interface ---

def main():
    parser = argparse.ArgumentParser(
        description="Send emails via SMTP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple email
  email_sender.py --to "friend@example.com" --subject "Hi" --body "Hello friend!"
  
  # HTML email
  email_sender.py --to "friend@example.com" --subject "HTML" --body "<b>Bold!</b>" --html
  
  # With attachment
  email_sender.py --to "friend@example.com" --subject "File" --body "See attached" --attach file.txt
  
  # Read body from file
  email_sender.py --to "friend@example.com" --subject "Report" --body-file report.txt

Gmail Setup:
  1. Enable 2-Factor Authentication
  2. Go to App Passwords (https://myaccount.google.com/projectpasswords)
  3. Create an app password for "Mail"
  4. Use that password as SMTP_PASS
        """
    )
    
    parser.add_argument("--to", "-t", required=True, help="Recipient email address")
    parser.add_argument("--subject", "-s", required=True, help="Email subject")
    parser.add_argument("--body", "-b", help="Email body (text)")
    parser.add_argument("--body-file", "-f", help="Read body from file")
    parser.add_argument("--html", action="store_true", help="Body is HTML")
    parser.add_argument("--attach", "-a", action="append", help="Attachment file(s)")
    
    args = parser.parse_args()
    
    # Get body from file or argument
    if args.body_file:
        try:
            with open(args.body_file, "r") as f:
                body = f.read()
        except FileNotFoundError:
            print(f"ERROR: File not found: {args.body_file}")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Could not read file: {e}")
            sys.exit(1)
    elif args.body:
        body = args.body
    else:
        parser.error("Either --body or --body-file is required")
    
    # Send the email
    success = send_email(
        to_email=args.to,
        subject=args.subject,
        body=body,
        is_html=args.html,
        attachments=args.attach
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
