from __future__ import print_function

import os.path
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from collections import Counter
from bokeh.io import output_file, show, save
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.transform import factor_cmap
from bokeh.palettes import Plasma256, linear_palette, Turbo256

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

TOKEN_FILE = "token.json"


def plot_chart(spammers):
    spam_counts = Counter(spammers)

    # Convert the counts to a Bokeh ColumnDataSource object
    source = ColumnDataSource(
        data=dict(
            spammer=list(
                spam_counts.keys(),
            ),
            count=list(
                spam_counts.values(),
            ),
        )
    )

    # Create a Bokeh figure object
    p = figure(
        y_range=list(
            spam_counts.keys(),
        ),
        title="Distribution of Spammers in the inbox",
    )

    # Add horizontal bars to the figure
    p.hbar(
        y="spammer",
        right="count",
        height=0.8,
        source=source,
        line_color="white",
        fill_color=factor_cmap(
            "spammer",
            palette=linear_palette(Turbo256, len(spam_counts)),
            factors=list(
                spam_counts.keys(),
            ),
        ),
    )

    # # Define the tooltip behavior
    hover = HoverTool(
        tooltips=[
            ("Spammer", "@spammer"),
            ("Count", "@count"),
        ],
    )

    # # Add the tooltip to the chart
    p.add_tools(hover)

    # Set properties of the plot
    p.title.text_font_size = "16pt"
    p.xaxis.axis_label = "Count"
    p.yaxis.axis_label = "Spammers"
    p.sizing_mode = "scale_width"

    # Prepare the plot on browser
    output_file("spammer_distribution.html")

    # Display the plot
    show(p)

    return spam_counts


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing token")
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    spammers = []

    # Only from inbox, excluding gmail.com senders
    query = "in:inbox -from:gmail.com"

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        messages = (
            service.users()
            .messages()
            .list(userId="me", maxResults=500, q=query)
            .execute()
        )
        messages = messages["messages"]

        # Iterate over the retrieved messages and retrieve the sender's email address from the message headers
        for message in messages:
            message_id = message["id"]
            message = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=message_id,
                )
                .execute()
            )

            headers = message["payload"]["headers"]
            sender = [h["value"] for h in headers if h["name"] == "From"][0]
            print(f"Sender: {sender}")
            if "<" not in sender:
                spammers.append(sender)
                continue
            email_regex = r"<([^>]+)>"
            email_address = re.search(email_regex, sender).group(1)
            # if email_address not in spammers:
            spammers.append(email_address)

    except HttpError as error:
        print(f"An error occurred: {error}")

    plot_chart(spammers)


if __name__ == "__main__":
    main()
