#%%
import pandas as pd
import feedparser
import re
from configparser import ConfigParser
import logging
from typing import List
from pathlib import Path

# import boto3

# Read config.ini file
root_folder = Path(__file__).parents[1]
config_object = ConfigParser()
config_object.read(f"{root_folder}/config.ini")

# Configure logging
logging.basicConfig(
    filename=f'{root_folder}/{config_object["EXPORT"]["logname"]}',
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def CleanHTML(results):
    """Clean HTML tags"""
    res = results
    res = re.sub("<em>", "", res)
    res = re.sub("<b>", "", res)
    res = re.sub("</b>", "", res)
    res = re.sub("</em>", "", res)
    res = re.sub("%2f", " ", res)
    res = re.sub("%3a", " ", res)
    res = re.sub("<strong>", "", res)
    res = re.sub("</strong>", "", res)
    res = re.sub("<wbr>", "", res)
    res = re.sub("</wbr>", "", res)
    res = re.sub("&lt;", "", res)
    res = re.sub("<.*?>", "", res)
    res = re.sub("&nbsp;", "", res)
    res = re.sub("&bull;", "", res)
    res = re.sub("\n", "", res)
    res = re.sub("  ", "", res)
    return res


def extract_value(paragraphs, index, part):
    """Extract value from paragraphs list or return 'NA' if IndexError"""
    try:
        if index == -3:
            return re.sub(
                ": |:|\t", "", CleanHTML(paragraphs[index].split("</b>")[part])
            )
        return (re.sub(": |:", "", CleanHTML(paragraphs[index].split("</b>")[part])),)
    except IndexError:
        return "NA"

#%%
def texttodf(feed) -> List[List[str]]:
    temp = []
    try:
        for entry in feed.entries:
            paragraphs = (entry.summary).split("<br />")
            temp.append(
                [
                    CleanHTML(entry.title),
                    entry.link,
                    entry.updated,
                    extract_value(paragraphs, -5, 1)[0],
                    CleanHTML(entry.summary),
                    extract_value(paragraphs, -6, 1)[0],
                    extract_value(paragraphs, -6, 0)[0],
                    extract_value(paragraphs, -4, 1)[0],
                    extract_value(paragraphs, -3, 1),
                    extract_value(paragraphs, -2, 1)[0],
                ]
            )
    except Exception as e:
        logging.error(f"{e} error while processing entry: {paragraphs}")

    return temp


def main():
    columns = [
        "Title",
        "Link",
        "Update_Date",
        "Publish_Date",
        "Summary",
        "Rate",
        "Rate_type",
        "Category",
        "Skills",
        "Country",
    ]
    data = pd.DataFrame(columns=columns)

    for url in config_object["FEEDS"]["url"].split("\n"):
        try:
            feed = feedparser.parse(url)
            data = pd.concat(
                [data, pd.DataFrame(texttodf(feed), columns=columns)], ignore_index=True
            )
        except Exception as e:
            logging.error(f"Error parsing feed '{url}': {e}")

    try:
        data["Publish_Date"] = pd.to_datetime(
            data.Publish_Date, format="mixed", dayfirst=True
        )
    except Exception as e:
        logging.error(f"Error converting 'Publish_Date' column to datetime: {e}")

    try:
        data["Update_Date"] = pd.to_datetime(
            data.Update_Date, format="mixed", dayfirst=True
        )
    except Exception as e:
        logging.error(f"Error converting 'Update_Date' column to datetime: {e}")

    data.to_csv(f'{root_folder}/{config_object["EXPORT"]["file_name"]}', index=False)
    logging.info("Data extraction and processing completed successfully.")


if __name__ == "__main__":
    main()
