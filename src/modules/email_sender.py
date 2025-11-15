"""
Email Sender Module - WITH PDF ATTACHMENT SUPPORT
Sends emails via Gmail SMTP (Port 465 SSL) with CV attachments
"""

import smtplib
import ssl
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from src.logger import logger


class EmailSender:
    """
    Enhanced Email sender with PDF attachment capability
    Uses Gmail SMTP with SSL (Port 465)
    """
    
    def __init__(self, sender_email: str, sender_password: str):
        """
        Initialize email sender
        
        Args:
            sender_email: Gmail address
            sender_password: Gmail app password
        """
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465  # ✅ CHANGED TO 465 (SSL)
        logger.info(f"✅ EmailSender initialized for: {sender_email}")
    
    def validate_email_setup(self) -> Tuple[bool, str]:
        """
        Validate email credentials using SSL connection
        
        Returns:
            (is_valid, message)
        """
        try:
            logger.info("🔐 Validating email credentials with SSL (Port 465)...")
            
            context = ssl.create_default_context()
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.sender_email, self.sender_password)
            
            logger.info("✅ Email credentials validated successfully")
            return True, "✅ Email configuration is valid!"
        
        except smtplib.SMTPAuthenticationError:
            logger.error("❌ Authentication failed - Invalid credentials")
            return False, "❌ Invalid email or password. Check your App Password."
        
        except Exception as e:
            logger.error(f"❌ Email validation failed: {str(e)}")
            return False, f"❌ Connection error: {str(e)}"
    
    def send_email(self, to_email: str, subject: str, body: str, 
                   attachments: Optional[List[str]] = None) -> bool:
        """
        Send a single email with optional attachments using SSL
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body
            attachments: List of file paths to attach
            
        Returns:
            Success status
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if Path(file_path).exists():
                        self._attach_file(msg, file_path)
                        logger.info(f"✅ Attached: {Path(file_path).name}")
                    else:
                        logger.warning(f"⚠️ Attachment not found: {file_path}")
            
            # Send email using SSL (Port 465)
            logger.info(f"📧 Sending email to: {to_email}")
            
            context = ssl.create_default_context()
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, to_email, msg.as_string())
            
            logger.info(f"✅ Email sent successfully to: {to_email}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_batch_emails(self, emails: List[Dict], 
                         cv_path: Optional[str] = None,
                         delay: int = 2) -> Dict:
        """
        Send multiple emails in batch with optional CV attachment
        
        Args:
            emails: List of email dictionaries with 'to', 'subject', 'body'
            cv_path: Path to CV file to attach to all emails
            delay: Delay between emails in seconds
            
        Returns:
            Results dictionary with sent/failed counts
        """
        results = {
            'sent': 0,
            'failed': 0,
            'details': []
        }
        
        logger.info(f"📧 Starting batch email sending: {len(emails)} emails")
        
        # Prepare attachments list
        attachments = [cv_path] if cv_path and Path(cv_path).exists() else None
        
        if cv_path and attachments:
            logger.info(f"📎 Attaching CV: {Path(cv_path).name}")
        
        for i, email_data in enumerate(emails, 1):
            try:
                to_email = email_data.get('to')
                subject = email_data.get('subject')
                body = email_data.get('body')
                
                if not to_email or not subject or not body:
                    logger.warning(f"⚠️ Skipping email {i}: Missing required fields")
                    results['failed'] += 1
                    continue
                
                logger.info(f"📧 [{i}/{len(emails)}] Sending to {to_email}...")
                
                success = self.send_email(to_email, subject, body, attachments)
                
                if success:
                    results['sent'] += 1
                    results['details'].append({
                        'to': to_email,
                        'status': 'sent',
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    logger.info(f"✅ Success: {to_email}")
                else:
                    results['failed'] += 1
                    results['details'].append({
                        'to': to_email,
                        'status': 'failed',
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    logger.warning(f"❌ Failed: {to_email}")
                
                # Delay to avoid rate limiting
                if i < len(emails):
                    logger.info(f"⏳ Waiting {delay}s before next email...")
                    time.sleep(delay)
            
            except Exception as e:
                logger.error(f"❌ Error processing email {i}: {str(e)}")
                results['failed'] += 1
        
        logger.info(f"✅ Batch sending complete: {results['sent']} sent, {results['failed']} failed")
        return results
    
    def _attach_file(self, msg: MIMEMultipart, file_path: str):
        """
        Attach a file to email message
        
        Args:
            msg: Email message object
            file_path: Path to file to attach
        """
        try:
            file_path = Path(file_path)
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Determine MIME type based on extension
            if file_path.suffix.lower() == '.pdf':
                attachment = MIMEApplication(file_data, _subtype='pdf')
            else:
                attachment = MIMEApplication(file_data)
            
            attachment.add_header(
                'Content-Disposition',
                'attachment',
                filename=file_path.name
            )
            
            msg.attach(attachment)
        
        except Exception as e:
            logger.error(f"❌ Error attaching file {file_path}: {str(e)}")
            raise
    
    def send_test_email(self, cv_path: Optional[str] = None) -> bool:
        """
        Send a test email to verify setup
        
        Args:
            cv_path: Optional CV to attach
            
        Returns:
            Success status
        """
        subject = "🎯 Test Email from JobFinder Pro"
        body = """
Hello!

This is a test email from JobFinder Pro to verify your email configuration.

If you're seeing this, your email setup is working correctly! ✅

You can now send personalized job applications automatically!

Best regards,
JobFinder Pro Team
        """
        
        attachments = [cv_path] if cv_path and Path(cv_path).exists() else None
        
        logger.info("📧 Sending test email...")
        success = self.send_email(self.sender_email, subject, body, attachments)
        
        if success:
            logger.info("✅ Test email sent successfully!")
        else:
            logger.error("❌ Test email failed")
        
        return success


# Demo function
def demo_email_sender():
    """Demo the email sender with attachment"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    
    if not sender_email or not sender_password:
        print("❌ Please set SENDER_EMAIL and SENDER_PASSWORD in .env file")
        return
    
    sender = EmailSender(sender_email, sender_password)
    
    # Validate setup
    is_valid, msg = sender.validate_email_setup()
    print(msg)
    
    if not is_valid:
        return
    
    # Send test email (to yourself)
    print("\n📧 Sending test email to yourself...")
    success = sender.send_test_email()
    
    if success:
        print("✅ Check your inbox!")
    else:
        print("❌ Test failed")


if __name__ == "__main__":
    demo_email_sender()