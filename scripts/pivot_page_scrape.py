import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import boto3
from boto3.exceptions import Boto3Error
import os
import toml


# Base URL for the website
base_url = 'https://pivot.proquest.com'

# Start page
page_url = '/funding/results'

# Temp file to store the links
file_name = 'links.txt'

# Read AWS configuration from the toml file
config = toml.load('aws_config.toml')
aws_access_key_id = config['aws']['access_key_id']
aws_secret_access_key = config['aws']['secret_access_key']
bucket_name = config['aws']['bucket_name']

# Create an S3 client
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

while True:
    try:
        # Fetch the webpage content
        response = requests.get(f"{base_url}{page_url}")
        response.raise_for_status()  # Raise an exception if the request was unsuccessful
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the grant links
        grant_links = soup.find_all('a', class_=['pivot_track_link', 'results-title-link'])
        links = [base_url + link.get('href') for link in grant_links]

        # Append the links to the file
        with open(file_name, 'a') as f:
            for link in links:
                f.write(link + '\n')

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
        page_url = next_page.get('href')
    else:
        print(f"Error: next_page is not a Tag object. Type: {type(next_page)}")
        break

# Try to upload the file to the S3 bucket
try:
    s3.upload_file(file_name, bucket_name, file_name)
except Boto3Error as e:
    print(f"An error occurred when uploading the file to S3: {e}")
    
# Delete the local file if it exists
if os.path.isfile(file_name):
    os.remove(file_name)