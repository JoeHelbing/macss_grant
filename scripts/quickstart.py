from __future__ import print_function

import os.path

import pivot_page_scrape

from bs4 import BeautifulSoup
from bs4.element import Tag
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

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
                    parts = payload.get('parts')
                    for part in parts:
                        if part['mimeType'] == 'text/html':
                            data = part['body']['data']
                            data = data.replace("-","+").replace("_","/")
                            decoded_data = base64.b64decode(data)
                            soup = BeautifulSoup(decoded_data , "html.parser")
                            body = soup.body
                            if body is not None:
                                link = see_all_results_link(body)
                                print("Link: ", link if link is not None else "(No link)")
                                pivot_page_scrape.page_scrape(link)

                    print("Subject: ", subject if subject is not None else "(No subject)")
                    print("From: ", from_name if from_name is not None else "(No from name)")
                except BaseException as error:
                    print("An exception occurred: {}".format(error))

                # Mark the message as read #TODO: Uncomment this line to mark the message as read
                # service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()

                message_count += 1
        print(f"Processed {message_count} messages.")

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


def see_all_results_link(contents):
    """
    This function takes the HTML soup and pulls out the link to the see all results button at the bottom of the email.
    """
    # Find the <a> tag and get the href attribute
    a_tag = contents.find('a', style="color:#4F5764; font-weight:bold; text-decoration:none")
    link = a_tag.get('href') if isinstance(a_tag, Tag) and 'href' in a_tag.attrs else None
    return link


if __name__ == '__main__':
    main()