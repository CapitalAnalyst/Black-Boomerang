#!/usr/bin/python

"""
Function:
    1. Download HTML content from multiple URLs (Cyber.gov.au, AFP, Hacker News).
    2. Parse the HTML content and extract specific details (date, title, URL, label).
    3. Save the extracted details into a single CSV file, appending data if the file already exists.

I/O:
    1. Input:
        1.1 URLs of the webpages to download (list of str)
    2. Output:
        2.1 A CSV file ('final_new.csv') containing the extracted details (date, title, URL, label) for all webpages.
"""

import datetime
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from transformers import pipeline


def get_writable_path(filename):
    """ Determine a writable directory for storing the updated CSV file """
    user_data_dir = os.path.expanduser("~")  # Store in the user's home directory
    writable_path = os.path.join(user_data_dir, "BlackBoomerang", filename)
    os.makedirs(os.path.dirname(writable_path), exist_ok=True)  # Create the directory if it doesn't exist
    return writable_path


def download_html(url):
    """
    Downloads the HTML content from the given URL.

    Args:
        url (str): The URL to download the HTML content from.

    Returns:
        str: The downloaded HTML content.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp}: Executing download_html for {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()  # Check that the request was successful
        html_content = response.text

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp}: Success - HTML content downloaded successfully.")

        return html_content

    except Exception as ex:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp}: Error - download_html encountered an error. Details: {ex}")
        return None


def get_url_list(url_list, position_div_list, site):
    """
    Extracts the date, title, and URL from a list of news item divs
    and adds them to the url_list dictionary.

    Args:
        url_list (list): A list to store the extracted details (date, title, content, URL).
        position_div_list (list): A list of div elements containing the news item details.
        site (str): The site identifier to adapt the parsing logic for each site.
    """
    for div in position_div_list:
        instance = dict()

        if site == 'hackernews':
            title = div.find('h2').text.strip()
            link_tag = div.find('a', href=True)
            if link_tag:
                url = link_tag['href']
            else:
                url = None
            label_date_div = div.find('div', class_='item-label')
            date = label_date_div.find('span', class_='h-datetime').text.strip()
            label = label_date_div.find('span', class_='h-tags').text.strip()

        elif site == 'cyber':
            title = div.find('p').text.strip()

            url = div['href']

            date = div.find('header').text.strip()
            label = 'n'

        elif site == 'afp':
            title_div = div.find('div', class_='field--name-node-title')
            if title_div:
                title = title_div.text.strip()
            else:
                title = None
            link_tag = div.find('a', href=True)
            if link_tag:
                url = "https://afp.gov.au" + link_tag['href']
            else:
                url = None
            date_div = div.find('div', class_='card--date')
            if date_div:
                date = date_div.text.strip()
            else:
                date = None
            label = "cyber"

        instance['Summary'] = title
        instance['URL'] = url
        instance['Date'] = date
        instance['Final Label'] = label

        url_list.append(instance)
def run_summarization_and_classification(df):
    """
    Perform summarization and classification on Cyber.gov.au content.

    Args:
        df (pandas.DataFrame): DataFrame containing the Cyber.gov.au data.

    Returns:
        pandas.DataFrame: DataFrame with added summarization and classification results.
    """
    # Initialize the summarization and classification pipelines
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    # Prepare lists to store the summary and classification results
    summaries = []
    final_labels = []

    # Specify candidate labels for classification
    candidate_labels = ["cyber security", "business", "finance", "technology"]

    # Iterate over each row in the DataFrame
    for _, row in df.iterrows():
        content = row['Summary']

        # Perform summarization
        summary_result = summarizer(content, max_length=30, min_length=10, do_sample=False)
        summary_text = summary_result[0]['summary_text']
        summaries.append(summary_text)

        # Perform classification
        classification_result = classifier(content, candidate_labels)
        max_score_index = classification_result['scores'].index(max(classification_result['scores']))
        final_label = classification_result['labels'][max_score_index]
        final_labels.append(final_label)

    # Add the summary and classification results as new columns in the DataFrame
    df['Summary'] = summaries
    df['Final Label'] = final_labels
    # Retain only the necessary columns
    df = df[['Summary', 'URL', 'Date', 'Final Label']]

    return df


def parse_and_save_news(html_content, site):
    """
    Parses the HTML content, extracts details of news items, and saves them into a CSV file.

    Args:
        html_content (str): The HTML content to parse.
        site (str): The site identifier to adapt the parsing logic for each site.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp}: Executing parse_and_save_news for {site}...")

    try:
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        if site == 'hackernews':
            position_div_list = soup.find_all("div", class_="body-post clear")
        elif site == 'cyber':
            position_div_list = soup.find_all("a", class_="card--alert flex flex-col w-full h-full px-6 pt-6 pb-[56] border relative rounded-sm size--small rating-- color--white")
        elif site == 'afp':
            position_div_list = soup.find_all("div", class_="node--type-article")

        # Extract and save the news details
        url_list = []
        get_url_list(url_list, position_div_list, site)
        df = pd.DataFrame(url_list)
        if site == 'cyber':
            # Perform summarization and classification for Cyber.gov.au data
            df = run_summarization_and_classification(df)
        # Check if final_new.csv exists; if it does, append data, else create new file
        csv_path = get_writable_path('final_new.csv')
        if os.path.exists(csv_path):
            df.to_csv(csv_path, mode='a', index=False, header=False)
        else:
            df.to_csv(csv_path, mode='w', index=False)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp}: Success - News details saved to {csv_path} for {site}.")

    except Exception as ex:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp}: Error - parse_and_save_news encountered an error for {site}. Details: {ex}")


if __name__ == "__main__":
    start_time = datetime.datetime.now()
    self_name = os.path.basename(__file__)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("----------" * 10)
    print(f"{timestamp}: {self_name} started to run.")

    # Define URLs and corresponding site identifiers
    urls_and_sites = {
        "https://thehackernews.com/": "hackernews",
        "https://www.cyber.gov.au/about-us/view-all-content/news-and-media": "cyber",
        "https://www.afp.gov.au/news-centre": "afp"
    }

    for url, site in urls_and_sites.items():
        html_content = download_html(url)
        if html_content:
            parse_and_save_news(html_content, site)

    end_time = datetime.datetime.now()
    duration = end_time - start_time
    print(f"{self_name} took time: {duration}")
    print("----------" * 10)
