import base64
from email.message import EmailMessage
import mimetypes
import os
import os.path

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


class GmailClient:
    def get_creds(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return creds


    def send_message(self, *, to, year, pdf):
        creds = self.get_creds()

        try:
            # create gmail api client
            service = build("gmail", "v1", credentials=creds)
            mime_message = EmailMessage()

            # headers
            mime_message["To"] = to
            mime_message["From"] = "Fox Hollow First Addition HOA <hoa@foxhollow.community>"
            mime_message["Subject"] = f"Fox Hollow First Addition HOA {year} Membership Invoice"

            # text
            mime_message.set_content(
                f"Hello,\n\nPlease find your invoice for the {year} membership dues for Fox Hollow HOA.\n\nThank you for your support of our neighborhood!\n\nBest regards,\nEmily Brodersen, President"
            )

            # attachment
            attachment_filename = f"fox_hollow_{year}_invoice.pdf"
            # guessing the MIME type
            type_subtype, _ = mimetypes.guess_type(attachment_filename)
            maintype, subtype = type_subtype.split("/")

            mime_message.add_attachment(pdf, maintype=maintype, subtype=subtype, filename=attachment_filename)
            encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()

            create_message = {"raw": encoded_message}
            # pylint: disable=E1101
            send_message = (
                service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )
            print(f'Message id: {send_message["id"]}')
        except HttpError as error:
            print(f"An error occurred: {error}")
            draft = None
        return send_message
