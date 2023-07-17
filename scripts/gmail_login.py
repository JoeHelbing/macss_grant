import os
import pickle
import base64
import re
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def lambda_handler(event, context):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API to fetch unread emails
    results = service.users().messages().list(userId='me',labelIds=['INBOX'], q='is:unread').execute()
    messages = results.get('messages', [])

    message_count = 0

    if not messages:
        print('No new messages.')
    else:
        subject = None
        from_name = None
        body = None
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            email_data = msg['payload']['headers']
            for values in email_data:
                name = values['name']
                if name == 'From':
                    from_name = values['value']
                if name == 'Subject':
                    subject = values['value']
            try:
                payload = msg['payload']
                body = payload.get('body', {})
                data = body.get('data')
                soup = None # initalize soup to None
                print("Data: ", data)
                if data is not None:
                    # data = data.replace("-","+").replace("_","/")
                    decoded_data = base64.b64decode(data)
                    soup = BeautifulSoup(decoded_data , "html.parser")
                    print("Soup: ", soup)
                if soup is not None:
                    for script in soup:
                        print("Script: ", script)
                        # do something with the body object
                    else: #TODO
                        pass
                        # handle the case where body is None
                else: #TODO
                    pass
                    # handle the case where soup is None
                print("Subject: ", subject if subject is not None else "(No subject)")
                print("From: ", from_name if from_name is not None else "(No from name)")
                print("Message: ", body if body is not None else "(No message)")
            except BaseException as error:
                print("An exception occurred: {}".format(error))

            # Mark the message as read
            service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()

            message_count += 1
    print(f"Processed {message_count} messages.")

if __name__ == '__main__':
    lambda_handler(None, None)