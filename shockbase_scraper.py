#!/usr/bin/python3

"""
Script to scrape watch data from the Shockbase website and save it to a CSV file.
"""

# Standard library imports.
import re

# Third-party imports.
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Base URLs for the website and image resources.
base_url = "https://shockbase.org/watches/"
series_url = base_url + "series_overview.php/"
image_base_url = "https://shockbase.org/pics2/"


def get_soup(session, url):
    """
    Send a GET request and return a BeautifulSoup object.
    """
    try:
        response = session.get(url)
        # Raise exception for HTTP errors.
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve URL: {url} with exception {e}")
        return None


def parse_main_page(soup):
    """
    Parse the main page to get the series and their links.
    """
    series_links = []

    # Find all <ul> elements with class "ul-clean".
    ul_elements = soup.find_all("ul", class_="ul-clean")

    for ul in ul_elements:
        # Find all <li> elements within each <ul>.
        li_elements = ul.find_all("li")

        for li in li_elements:
            # Find all <a> elements within each <li>.
            anchor_elements = li.find_all("a")

            for anchor in anchor_elements:
                # Extract the link text and strip whitespace.
                series_name = anchor.text.strip()
                # Construct the full URL for the series.
                series_url = base_url + anchor["href"]
                # Add a tuple (series name, URL) to the list.
                series_links.append((series_name, series_url))

    return series_links


def parse_series_page(soup):
    """
    Parse the series page to get the subseries and their links.
    """
    subseries_links = []

    # Find all <div> elements with the class "box".
    div_elements = soup.find_all("div", class_="box")

    for div in div_elements:
        # Find the <b> tag within each <div>
        b_tag = div.find("b")

        if b_tag:
            # Find the <a> tag within the <b> tag.
            subseries_link = b_tag.find('a')

            if subseries_link:
                # Extract the link text and strip whitespace.
                subseries_name = subseries_link.text.strip()
                # Construct the full URL for the subseries.
                subseries_url = base_url + subseries_link['href']
                # Add a tuple (subseries name, URL) to the list.
                subseries_links.append((subseries_name, subseries_url))

    return subseries_links


def extract_year_and_clean_name(watch_name):
    """
    Extract the year from the watch name and clean the name.
    """
    # Search for a year (4 digits) in parentheses.
    match = re.search(r"\((\d{4})\)", watch_name)

    if match:
        # Extract the year from the match.
        year = match.group(1)
        # Clean the name by removing the year and whitespace.
        cleaned_name = watch_name[:match.start()].strip()
    else:
        year = ""
        cleaned_name = watch_name.strip()

    return cleaned_name, year


def parse_subseries_page(soup, series, subseries):
    """
    Parse the subseries page to get the watches.
    """
    series_data = []

    for figure in soup.select("figure"):
        # Find the <img> element.
        img_tag = figure.find('img')
        # Find the <figcaption> element.
        figcaption_tag = figure.find("figcaption")

        if img_tag and figcaption_tag:
            # Extract and clean the watch name.
            watch_name = figcaption_tag.text.strip()
            # Extract year and clean name.
            cleaned_name, watch_year = extract_year_and_clean_name(watch_name)
            # Clean the image URL.
            img_src = img_tag["src"].replace("../pics2/", "")
            # Construct the full image URL.
            img_url = image_base_url + img_src.replace("_small.webp", ".png")
            # # Add data to the list.
            series_data.append([series, subseries, cleaned_name, watch_year, img_url])

    return series_data


def main():
    """
    Main function to scrape the watch data and save it to a CSV file.
    """
    # Create a requests session.
    with requests.Session() as session:
        # Get the main page soup.
        main_soup = get_soup(session, series_url)

        if main_soup:
            # Parse the main page to get series links.
            series_links = parse_main_page(main_soup)
            series_data = []

            for series, series_link in tqdm(series_links, desc="Processing series"):
                # Get the series page soup.
                series_soup = get_soup(session, series_link)

                if series_soup:
                    # Parse the series page to get subseries links.
                    subseries_links = parse_series_page(series_soup)

                    for subseries, subseries_link in subseries_links:
                        # Get the subseries page soup.
                        subseries_soup = get_soup(session, subseries_link)

                        if subseries_soup:
                            # Parse the subseries page to get watch data and extend the series data list.
                            series_data.extend(parse_subseries_page(subseries_soup, series, subseries))

            # Create a DataFrame and save it to a CSV file.
            df = pd.DataFrame(series_data, columns=["Series", "Subseries", "Watch Model", "Year", "Image URL"])
            csv_file_path = "shockbase.csv"
            df.to_csv(csv_file_path, index=False)

            print(f"Data successfully saved to {csv_file_path}.")
        else:
            print("Failed to retrieve the data.")


if __name__ == "__main__":
    main()
