##IMPORT LIBS
from bs4 import BeautifulSoup
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from time import time, sleep
import datetime

import pandas as pd

import csv
import os
import re

##DEFINE FUNCTIONS
# function to make beautiful soup object
def make_soup(link, headers):
    session = Session()
    session.headers.update(headers)

    try:
        page = session.get(link)
        html = page.content
        soup = BeautifulSoup(html,'lxml')
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

    return soup


# function that takes a bs4.element.ResultSet and returns list of the extracted text strings
def extract_text(result_set):
    new_list = []

    for tag in result_set:
        new_list.append(tag.get_text())

    return new_list


# function to extract each href link from lin_results
def extract_link(link_results, url):
    link_list = []

    for link in link_results:
        full_link = url + link["href"]
        link_list.append(full_link)
    return link_list


def extract_coverages(splits):
    # initialize empty lists for left, right, and center
    left = []
    center = []
    right = []
    # for each entry in coverage_splits
    for split in splits:
        # check if left, then enter left or 0
        if split.find(
            class_="text-light-primary bg-secondary-left text-light-primary leading-none flex items-center"
        ):
            left.append(
                split.find(
                    class_="text-light-primary bg-secondary-left text-light-primary leading-none flex items-center"
                )["style"][6:9]
            )
        else:
            left.append("0%")
        # check if center, then enter left or 0
        if split.find(
            class_="text-dark-primary bg-secondary-neutral leading-none flex items-center"
        ):
            center.append(
                split.find(
                    class_="text-dark-primary bg-secondary-neutral leading-none flex items-center"
                )["style"][6:9]
            )
        else:
            center.append("0%")
        # check if right, then enter left or 0
        if split.find(
            class_="text-light-primary bg-secondary-right text-light-primary leading-none flex items-center"
        ):
            right.append(
                split.find(
                    class_="text-light-primary bg-secondary-right text-light-primary leading-none flex items-center"
                )["style"][6:9]
            )
        else:
            right.append("0%")
    # return left, center, right
    return left, center, right


# function to get each story on the ground news home page, returning data as dataframe
def get_stories(url, headers):
    soup = make_soup(url, headers)

    # get story data
    stories = soup.select(
        "div.w-full.flex.justify-between.gap-1 > h4.text-22.leading-10.line-clamp-3"
    )
    topics = soup.select(
        "div.flex.flex-col.gap-8px.justify-center > span.text-12.leading-6"
    )
    locations = soup.select(
        "div.flex.flex-col.gap-8px.justify-center > span.text-12.leading-6 > span"
    )
    coverage_splits = soup.select("div.flex.items-center.gap-1.false > div > div")
    maj_cov_n_sources = soup.select(
        "div.flex.items-center.gap-1.false > div.text-12.leading-6 > span"
    )
    link_results = soup.select("a.absolute.left-0.right-0.top-0.bottom-0")

    # call extract_text on titles, topics, and locations
    stories_str = extract_text(stories)
    topics_str = extract_text(topics)
    locations_str = extract_text(locations)
    coverage_sources_str = extract_text(maj_cov_n_sources)

    # extract links for each article
    story_links = extract_link(link_results, url)

    # call function to extract coverage percentages from each political perspective
    left, center, right = extract_coverages(coverage_splits)

    # put data in dataframe
    df = pd.DataFrame()
    df["stories"] = stories_str
    df["topics"] = topics_str
    df["locations"] = locations_str
    df["left"] = left
    df["center"] = center
    df["right"] = right
    df["coverage_sources"] = coverage_sources_str
    df["story_links"] = story_links

    # START CLEANING DATA
    df["majority_coverage"] = (
        df["coverage_sources"].str.split(":").str[0].str.strip().str.split(" ").str[1]
    )
    df["n_sources"] = (
        df["coverage_sources"].str.split(":").str[1].str.strip().str.split(" ").str[0]
    )
    df = df.drop(columns="coverage_sources")
    df["locations"] = df["locations"].str.replace("· ", "")
    df["topics"] = df["topics"].str.split("·").str[0].str.strip()

    return df


#  function to iterate through all of the articles found for each story, returning dataframe containing all data
def get_articles(df, headers):
    # create new df to hold all new data
    new_df = pd.DataFrame()

    # iterate over each story
    for i, story in df.iterrows():

        # create new beautiful soup to scrape data
        soup = make_soup(story["story_links"], headers=headers)

        # # scrape the desired data
        article_titles = soup.select("h4.text-22.leading-11")
        article_sources = soup.select(
            "div.flex.gap-8px.items-center.text-14.flex-wrap > a > div > span"
        )
        text_samples = soup.select("p.font-normal.text-18.leading-9.break-words")
        article_lean_wrappers = soup.select(
            "div.flex.gap-8px.items-center.text-14.flex-wrap"
        )

        # clean soup into usable data
        article_titles_str = extract_text(article_titles)
        article_sources_str = extract_text(article_sources)
        text_samples_str = extract_text(text_samples)

        # extract article bias from article_leans
        # start with empty list of strings
        leans = []

        # iterate through article_leans, checking classes to determine lean and append to list
        for lean in article_lean_wrappers:
            if lean.find(
                class_=re.compile(
                    "secondary-left"
                )  # "py-1/2 rounded-4px text-12 justify-self-start leading-6 whitespace-nowrap flex flex-shrink items-center text-light-primary dark:text-light-primary  disabled:opacity-50 bg-secondary-left text-light-primary px-4px"
            ):
                leans.append("left")
            elif lean.find(
                class_=re.compile(
                    "secondary-neutral"
                )  # "py-1/2 rounded-4px text-12 justify-self-start leading-6 whitespace-nowrap flex flex-shrink items-center text-light-primary dark:text-light-primary  disabled:opacity-50 bg-secondary-neutral text-ground-black dark:bg-gray-100 dark:text-light-primary px-4px"
            ):
                leans.append("center")
            elif lean.find(
                class_=re.compile(
                    "secondary-right"
                )  # "py-1/2 rounded-4px text-12 justify-self-start leading-6 whitespace-nowrap flex flex-shrink items-center text-light-primary dark:text-light-primary  disabled:opacity-50 bg-secondary-right text-light-primary px-4px"
            ):
                leans.append("right")
            else:
                leans.append("None")

        # for each article, create a new row and append all relevant data to new_df
        for i, title in enumerate(article_titles_str):

            # getting duplicates, so skip half
            if i % 2 == 0:

                # create df row to hold article data and its associated story data
                article = pd.DataFrame(story).transpose()

                # add article data to the row
                article["title"] = title
                article["source"] = article_sources_str[i]
                article["sample"] = text_samples_str[i // 2]
                article["lean"] = leans[i]
                article["date"] = datetime.date.today()

                # append the row to new df
                new_df = pd.concat([new_df, article])

    # return new dataframe
    return new_df


# master function to fetch data once and write to csv
def run_news_scraper(filepath):
    # define url
    url = "http://ground.news"
    # Get user agent from 'https://httpbin.org/get'
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.5",
    }

    stories_df = get_stories(url, headers)

    articles = get_articles(stories_df, headers)

    now = datetime.datetime.now()

    # write to csv
    if not os.path.isfile(filepath):  # make new csv if not exists
        articles.to_csv(
            filepath,
            header="column_names",
        )
        print("Data initialized. ", now)  # success message
    else:  # update existing csv
        articles.to_csv(
            filepath,
            mode="a",
            header=False,
        )
        print("New articles gathered. ", now)  # success message


##RUN SCRIPT
csv_filepath = "news_articles.csv"

run_news_scraper(csv_filepath)

print(pd.read_csv(csv_filepath))

exit()
