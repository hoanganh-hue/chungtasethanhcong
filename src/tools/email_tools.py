"""
Email Operations Tools for OpenManus-Youtu Integrated Framework
Advanced email sending, receiving, and processing capabilities
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, BinaryIO
from pathlib import Path
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email import encoders
from datetime import datetime, timedelta
import json
import base64

logger = logging.getLogger(__name__)

class EmailSender:
    """Email sending capabilities."""
    
    def __init__(self, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.connection = None
    
    async def send_email(self, sender_email: str, sender_password: str, 
                        recipient_emails: List[str], subject: str, 
                        body: str, html_body: str = None, 
                        attachments: List[Dict[str, Any]] = None,
                        cc_emails: List[str] = None, 
                        bcc_emails: List[str] = None) -> Dict[str, Any]:
        """Send email with attachments."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = sender_email
            msg['To'] = ', '.join(recipient_emails)
            msg['Subject'] = subject
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # Add text body
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Add HTML body if provided
            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    await self._add_attachment(msg, attachment)
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            
            # Send email
            all_recipients = recipient_emails.copy()
            if cc_emails:
                all_recipients.extend(cc_emails)
            if bcc_emails:
                all_recipients.extend(bcc_emails)
            
            text = msg.as_string()
            server.sendmail(sender_email, all_recipients, text)
            server.quit()
            
            return {
                "success": True,
                "message": "Email sent successfully",
                "recipients": all_recipients,
                "subject": subject,
                "sent_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return {"error": str(e)}
    
    async def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]) -> None:
        """Add attachment to email message."""
        try:
            file_path = attachment.get('file_path')
            file_name = attachment.get('file_name', Path(file_path).name if file_path else 'attachment')
            file_data = attachment.get('file_data')
            mime_type = attachment.get('mime_type', 'application/octet-stream')
            
            if file_path:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
            
            if file_data:
                # Determine MIME type based on file extension
                if file_name.endswith(('.jpg', '.jpeg')):
                    mime_type = 'image/jpeg'
                elif file_name.endswith('.png'):
                    mime_type = 'image/png'
                elif file_name.endswith('.pdf'):
                    mime_type = 'application/pdf'
                elif file_name.endswith(('.doc', '.docx')):
                    mime_type = 'application/msword'
                elif file_name.endswith(('.xls', '.xlsx')):
                    mime_type = 'application/vnd.ms-excel'
                
                # Create attachment
                if mime_type.startswith('image/'):
                    attachment_part = MIMEImage(file_data)
                elif mime_type == 'application/pdf':
                    attachment_part = MIMEApplication(file_data, _subtype='pdf')
                else:
                    attachment_part = MIMEBase('application', 'octet-stream')
                    attachment_part.set_payload(file_data)
                    encoders.encode_base64(attachment_part)
                
                attachment_part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {file_name}'
                )
                msg.attach(attachment_part)
                
        except Exception as e:
            logger.error(f"Failed to add attachment: {e}")

class EmailReceiver:
    """Email receiving capabilities."""
    
    def __init__(self, imap_server: str = "imap.gmail.com", imap_port: int = 993):
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.connection = None
    
    async def connect(self, email_address: str, password: str) -> bool:
        """Connect to IMAP server."""
        try:
            self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.connection.login(email_address, password)
            return True
        except Exception as e:
            logger.error(f"IMAP connection failed: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from IMAP server."""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
            except:
                pass
            self.connection = None
    
    async def get_emails(self, folder: str = "INBOX", limit: int = 10, 
                        unread_only: bool = False, since_date: datetime = None) -> Dict[str, Any]:
        """Get emails from specified folder."""
        try:
            if not self.connection:
                return {"error": "Not connected to IMAP server"}
            
            # Select folder
            self.connection.select(folder)
            
            # Build search criteria
            search_criteria = []
            if unread_only:
                search_criteria.append('UNSEEN')
            if since_date:
                search_criteria.append(f'SINCE {since_date.strftime("%d-%b-%Y")}')
            
            search_string = ' '.join(search_criteria) if search_criteria else 'ALL'
            
            # Search for emails
            status, messages = self.connection.search(None, search_string)
            if status != 'OK':
                return {"error": "Failed to search emails"}
            
            email_ids = messages[0].split()
            
            # Limit results
            if limit > 0:
                email_ids = email_ids[-limit:]  # Get most recent emails
            
            emails = []
            
            for email_id in email_ids:
                try:
                    # Fetch email
                    status, msg_data = self.connection.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        continue
                    
                    # Parse email
                    email_message = email.message_from_bytes(msg_data[0][1])
                    email_info = await self._parse_email(email_message)
                    emails.append(email_info)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse email {email_id}: {e}")
                    continue
            
            return {
                "success": True,
                "emails": emails,
                "total_found": len(emails),
                "folder": folder
            }
            
        except Exception as e:
            logger.error(f"Failed to get emails: {e}")
            return {"error": str(e)}
    
    async def _parse_email(self, email_message) -> Dict[str, Any]:
        """Parse email message."""
        try:
            email_info = {
                "message_id": email_message.get('Message-ID', ''),
                "from": email_message.get('From', ''),
                "to": email_message.get('To', ''),
                "cc": email_message.get('Cc', ''),
                "bcc": email_message.get('Bcc', ''),
                "subject": email_message.get('Subject', ''),
                "date": email_message.get('Date', ''),
                "body": "",
                "html_body": "",
                "attachments": [],
                "headers": dict(email_message.items())
            }
            
            # Extract body content
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get('Content-Disposition', ''))
                    
                    if content_type == 'text/plain' and 'attachment' not in content_disposition:
                        email_info["body"] = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif content_type == 'text/html' and 'attachment' not in content_disposition:
                        email_info["html_body"] = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif 'attachment' in content_disposition:
                        # Handle attachment
                        filename = part.get_filename()
                        if filename:
                            attachment_data = part.get_payload(decode=True)
                            email_info["attachments"].append({
                                "filename": filename,
                                "content_type": content_type,
                                "size": len(attachment_data) if attachment_data else 0
                            })
            else:
                # Single part message
                content_type = email_message.get_content_type()
                if content_type == 'text/plain':
                    email_info["body"] = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                elif content_type == 'text/html':
                    email_info["html_body"] = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            return email_info
            
        except Exception as e:
            logger.error(f"Failed to parse email: {e}")
            return {"error": str(e)}
    
    async def mark_as_read(self, email_id: str) -> bool:
        """Mark email as read."""
        try:
            if not self.connection:
                return False
            
            self.connection.store(email_id, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            logger.error(f"Failed to mark email as read: {e}")
            return False
    
    async def delete_email(self, email_id: str) -> bool:
        """Delete email."""
        try:
            if not self.connection:
                return False
            
            self.connection.store(email_id, '+FLAGS', '\\Deleted')
            self.connection.expunge()
            return True
        except Exception as e:
            logger.error(f"Failed to delete email: {e}")
            return False

class EmailProcessor:
    """Email processing and analysis capabilities."""
    
    def __init__(self):
        self.sender = EmailSender()
        self.receiver = EmailReceiver()
    
    async def send_notification_email(self, sender_email: str, sender_password: str,
                                    recipient_email: str, subject: str, 
                                    message: str, priority: str = "normal") -> Dict[str, Any]:
        """Send notification email."""
        try:
            # Create HTML body with priority styling
            priority_colors = {
                "low": "#28a745",
                "normal": "#007bff", 
                "high": "#ffc107",
                "urgent": "#dc3545"
            }
            
            color = priority_colors.get(priority.lower(), "#007bff")
            
            html_body = f"""
            <html>
            <body>
                <div style="border-left: 4px solid {color}; padding: 10px; margin: 10px 0;">
                    <h3 style="color: {color}; margin: 0;">{subject}</h3>
                    <p style="margin: 10px 0;">{message}</p>
                    <small style="color: #666;">Priority: {priority.upper()}</small>
                </div>
            </body>
            </html>
            """
            
            result = await self.sender.send_email(
                sender_email=sender_email,
                sender_password=sender_password,
                recipient_emails=[recipient_email],
                subject=f"[{priority.upper()}] {subject}",
                body=message,
                html_body=html_body
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Notification email failed: {e}")
            return {"error": str(e)}
    
    async def send_report_email(self, sender_email: str, sender_password: str,
                              recipient_emails: List[str], report_data: Dict[str, Any],
                              report_type: str = "General Report") -> Dict[str, Any]:
        """Send report email with data."""
        try:
            # Generate HTML report
            html_body = self._generate_html_report(report_data, report_type)
            
            # Create text version
            text_body = self._generate_text_report(report_data, report_type)
            
            result = await self.sender.send_email(
                sender_email=sender_email,
                sender_password=sender_password,
                recipient_emails=recipient_emails,
                subject=f"Report: {report_type} - {datetime.now().strftime('%Y-%m-%d')}",
                body=text_body,
                html_body=html_body
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Report email failed: {e}")
            return {"error": str(e)}
    
    def _generate_html_report(self, report_data: Dict[str, Any], report_type: str) -> str:
        """Generate HTML report."""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e9ecef; border-radius: 3px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report_type}</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        """
        
        # Add metrics
        if 'metrics' in report_data:
            html += '<div class="section"><h2>Metrics</h2>'
            for key, value in report_data['metrics'].items():
                html += f'<div class="metric"><strong>{key}:</strong> {value}</div>'
            html += '</div>'
        
        # Add tables
        if 'tables' in report_data:
            for table_name, table_data in report_data['tables'].items():
                html += f'<div class="section"><h2>{table_name}</h2>'
                if table_data and len(table_data) > 0:
                    html += '<table>'
                    # Header
                    html += '<tr>'
                    for key in table_data[0].keys():
                        html += f'<th>{key}</th>'
                    html += '</tr>'
                    # Rows
                    for row in table_data:
                        html += '<tr>'
                        for value in row.values():
                            html += f'<td>{value}</td>'
                        html += '</tr>'
                    html += '</table>'
                html += '</div>'
        
        html += '</body></html>'
        return html
    
    def _generate_text_report(self, report_data: Dict[str, Any], report_type: str) -> str:
        """Generate text report."""
        text = f"{report_type}\n"
        text += "=" * len(report_type) + "\n"
        text += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Add metrics
        if 'metrics' in report_data:
            text += "METRICS:\n"
            for key, value in report_data['metrics'].items():
                text += f"  {key}: {value}\n"
            text += "\n"
        
        # Add tables
        if 'tables' in report_data:
            for table_name, table_data in report_data['tables'].items():
                text += f"{table_name.upper()}:\n"
                if table_data and len(table_data) > 0:
                    # Header
                    headers = list(table_data[0].keys())
                    text += "  " + " | ".join(headers) + "\n"
                    text += "  " + "-" * (len(" | ".join(headers))) + "\n"
                    # Rows
                    for row in table_data:
                        values = [str(row.get(h, "")) for h in headers]
                        text += "  " + " | ".join(values) + "\n"
                text += "\n"
        
        return text
    
    async def analyze_email_content(self, email_content: str) -> Dict[str, Any]:
        """Analyze email content for sentiment and keywords."""
        try:
            # Simple analysis (can be enhanced with NLP libraries)
            words = email_content.lower().split()
            word_count = len(words)
            char_count = len(email_content)
            
            # Sentiment indicators (simple approach)
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like']
            negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'horrible', 'worst', 'angry']
            
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            
            sentiment = "neutral"
            if positive_count > negative_count:
                sentiment = "positive"
            elif negative_count > positive_count:
                sentiment = "negative"
            
            # Extract potential keywords (words that appear frequently)
            word_freq = {}
            for word in words:
                if len(word) > 3:  # Ignore short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "success": True,
                "analysis": {
                    "word_count": word_count,
                    "character_count": char_count,
                    "sentiment": sentiment,
                    "positive_words": positive_count,
                    "negative_words": negative_count,
                    "keywords": [{"word": word, "frequency": freq} for word, freq in keywords]
                }
            }
            
        except Exception as e:
            logger.error(f"Email content analysis failed: {e}")
            return {"error": str(e)}

# Global email processor instance
email_processor = EmailProcessor()

# Convenience functions
async def send_email_notification(sender_email: str, sender_password: str,
                                recipient_email: str, subject: str, message: str) -> Dict[str, Any]:
    """Send notification email."""
    return await email_processor.send_notification_email(
        sender_email, sender_password, recipient_email, subject, message
    )

async def send_email_report(sender_email: str, sender_password: str,
                          recipient_emails: List[str], report_data: Dict[str, Any],
                          report_type: str = "General Report") -> Dict[str, Any]:
    """Send report email."""
    return await email_processor.send_report_email(
        sender_email, sender_password, recipient_emails, report_data, report_type
    )

async def get_emails_from_inbox(email_address: str, password: str, 
                               limit: int = 10, unread_only: bool = False) -> Dict[str, Any]:
    """Get emails from inbox."""
    receiver = EmailReceiver()
    if await receiver.connect(email_address, password):
        result = await receiver.get_emails(limit=limit, unread_only=unread_only)
        await receiver.disconnect()
        return result
    else:
        return {"error": "Failed to connect to email server"}

async def analyze_email_sentiment(email_content: str) -> Dict[str, Any]:
    """Analyze email sentiment."""
    return await email_processor.analyze_email_content(email_content)