import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import boto3
from boto3.exceptions import Boto3Error
import os
import toml

# Read AWS configuration from the toml file
# TODO Implement AWS S3 upload and uncomment
# config = toml.load('aws_config.toml')
# aws_access_key_id = config['aws']['access_key_id']
# aws_secret_access_key = config['aws']['secret_access_key']
# bucket_name = config['aws']['bucket_name']

def page_scrape(scrape_link):
    """
    Scrapes the pivot page for all links to grant pages.
    """

    # Create an S3 client #TODO Uncomment and fix S3 upload
    # s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    # Create a list to store the links
    links = []

    while True:
        try:
            # Fetch the webpage content
            response = requests.get(f"{scrape_link}")
            print(f"Fetching {scrape_link}" \
                  f"Status code: {response.status_code}")
            response.raise_for_status()  # Raise an exception if the request was unsuccessful
            soup = BeautifulSoup(response.text, 'html.parser')

            with open('pivot_page.html', 'w') as f:
                f.write(str(soup))

            # Find the select element and get the options
            select = soup.find('select', id='my-select')
            options = select.find_all('option')

            # Find the option with the value '63###264###rw'
            selected_option = None
            for option in options:
                if option['value'] == '63###264###rw':
                    selected_option = option
                    break

            # If the option is found, submit the form with the selected option
            if selected_option is not None:
                # Get the form data
                form = soup.find('form')
                if form is None:
                    print("Error: form not found")
                    break
                else:
                    action_url = form.get('action')
                    form_data = {}
                    for input in form.find_all('input'):
                        form_data[input['name']] = input.get('value', '')
                    form_data[select['name']] = selected_option['value']

                    # Submit the form
                    response = requests.post(action_url, data=form_data)
                    print(response.text)
            else:
                print("Option not found")

            # Extract the grant links
            grant_links = soup.find_all('a', class_=['pivot_track_link', 'results-title-link'])
            links.extend([link.get('href') for link in grant_links])

        except requests.exceptions.RequestException as e:
            print(f"An error occurred when fetching the webpage: {e}")
            break

        # Find the next page link
        next_page = soup.find('a', title='Next page')

        # If there's no next page, break the loop
        if next_page is None:
            break

        # Otherwise, get the link to the next page
        next_page = soup.find('a', title='Next page')
        if next_page is None:
            break
        if isinstance(next_page, Tag):
            scrape_link = next_page.get('href')
        else:
            print(f"Error: next_page is not a Tag object. Type: {type(next_page)}")
            break
    
    # Save links to text file
    with open('grant_links.txt', 'w') as f:
        for link in links:
            f.write(f"{link}\n")
