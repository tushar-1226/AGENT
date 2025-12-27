"""
Google Calendar and Gmail integration using OAuth 2.0
Requires Google Cloud project with Calendar and Gmail APIs enabled
"""
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("Google libraries not installed. Run: pip install google-auth google-auth-oauthlib google-api-python-client")

class GoogleIntegration:
    def __init__(self):
        self.credentials = None
        self.calendar_service = None
        self.gmail_service = None
        
        # OAuth scopes
        self.SCOPES = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/gmail.readonly'
        ]
        
        # Credentials file path (user must provide)
        self.credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
        self.token_file = 'token.json'
    
    def get_authorization_url(self) -> str:
        """Get OAuth authorization URL for user to visit"""
        if not GOOGLE_AVAILABLE:
            return "Google libraries not installed"
        
        if not os.path.exists(self.credentials_file):
            return f"Credentials file not found: {self.credentials_file}"
        
        flow = Flow.from_client_secrets_file(
            self.credentials_file,
            scopes=self.SCOPES,
            redirect_uri='http://localhost:8000/api/google/callback'
        )
        
        auth_url, _ = flow.authorization_url(prompt='consent')
        return auth_url
    
    def authenticate(self, code: str = None) -> bool:
        """Authenticate with Google using OAuth code or saved token"""
        if not GOOGLE_AVAILABLE:
            return False
        
        # Try to load saved token
        if os.path.exists(self.token_file):
            self.credentials = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        
        # If no valid credentials, need to authenticate
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            elif code:
                # Exchange code for credentials
                flow = Flow.from_client_secrets_file(
                    self.credentials_file,
                    scopes=self.SCOPES,
                    redirect_uri='http://localhost:8000/api/google/callback'
                )
                flow.fetch_token(code=code)
                self.credentials = flow.credentials
            else:
                return False
            
            # Save credentials
            with open(self.token_file, 'w') as token:
                token.write(self.credentials.to_json())
        
        # Build services
        self.calendar_service = build('calendar', 'v3', credentials=self.credentials)
        self.gmail_service = build('gmail', 'v1', credentials=self.credentials)
        
        return True
    
    # ============= CALENDAR METHODS =============
    
    def get_calendar_events(self, max_results: int = 10) -> List[Dict]:
        """Get upcoming calendar events"""
        if not self.calendar_service:
            return []
        
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            return [{
                'id': event['id'],
                'summary': event.get('summary', 'No title'),
                'start': event['start'].get('dateTime', event['start'].get('date')),
                'end': event['end'].get('dateTime', event['end'].get('date')),
                'location': event.get('location', ''),
                'description': event.get('description', '')
            } for event in events]
        except Exception as e:
            print(f"Error getting calendar events: {e}")
            return []
    
    def create_calendar_event(self, summary: str, start_time: str, end_time: str, 
                             description: str = '', location: str = '') -> Optional[Dict]:
        """Create a calendar event"""
        if not self.calendar_service:
            return None
        
        try:
            event = {
                'summary': summary,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC',
                },
            }
            
            created_event = self.calendar_service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return {
                'id': created_event['id'],
                'link': created_event.get('htmlLink'),
                'summary': created_event.get('summary')
            }
        except Exception as e:
            print(f"Error creating calendar event: {e}")
            return None
    
    # ============= GMAIL METHODS =============
    
    def get_recent_emails(self, max_results: int = 10) -> List[Dict]:
        """Get recent emails"""
        if not self.gmail_service:
            return []
        
        try:
            results = self.gmail_service.users().messages().list(
                userId='me',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                msg = self.gmail_service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = {h['name']: h['value'] for h in msg['payload']['headers']}
                
                emails.append({
                    'id': msg['id'],
                    'from': headers.get('From', ''),
                    'subject': headers.get('Subject', ''),
                    'date': headers.get('Date', ''),
                    'snippet': msg.get('snippet', '')
                })
            
            return emails
        except Exception as e:
            print(f"Error getting emails: {e}")
            return []
    
    def create_email_draft(self, to: str, subject: str, body: str) -> Optional[Dict]:
        """Create an email draft"""
        if not self.gmail_service:
            return None
        
        try:
            import base64
            from email.mime.text import MIMEText
            
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            draft = self.gmail_service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw}}
            ).execute()
            
            return {
                'id': draft['id'],
                'message': 'Draft created successfully'
            }
        except Exception as e:
            print(f"Error creating email draft: {e}")
            return None
