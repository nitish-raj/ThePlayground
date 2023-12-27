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
    res = re.sub("&nbsp;|&amp;", "", res)
    res = re.sub("&bull;", "", res)
    res = re.sub("\n", "", res)
    res = re.sub("  ", "", res)
    return res


def extract_value(paragraphs, index, part):
    """Extract value from paragraphs list or return 'NA' if IndexError"""
    try:
        return (
            re.sub(
                ": |:|\t",
                "",
                CleanHTML(
                    paragraphs[index].split("</b>")[part])),
        )
    except IndexError:
        return ("",)


def texttodf(feed) -> List[List[str]]:
    temp = []

    columns = [
        "Budget",
        "Posted On",
        "Category",
        "Country",
        "Hourly Range",
        "Skills",
    ]

    for entry in feed.entries:
        paragraphs = (entry.summary).split("<br />")
        try:
            col_idx = {}
            for i, x in enumerate(paragraphs):
                for col in columns:
                    if re.search(col, x):
                        col_idx[col] = i
                        break

            temp.append(
                [
                    CleanHTML(entry.title[:-9]),
                    entry.link,
                    entry.updated,
                    extract_value(
                        paragraphs, col_idx.get(columns[1]) or len(paragraphs), 1
                    )[0],
                    CleanHTML(entry.summary),
                    extract_value(
                        paragraphs,
                        col_idx.get(columns[0])
                        or col_idx.get(columns[4])
                        or len(paragraphs),
                        1,
                    )[0],
                    extract_value(
                        paragraphs,
                        col_idx.get(columns[0])
                        or col_idx.get(columns[4])
                        or len(paragraphs),
                        0,
                    )[0],
                    extract_value(
                        paragraphs, col_idx.get(columns[2]) or len(paragraphs), 1
                    )[0],
                    extract_value(
                        paragraphs, col_idx.get(columns[5]) or len(paragraphs), 1
                    )[0],
                    extract_value(
                        paragraphs, col_idx.get(columns[3]) or len(paragraphs), 1
                    )[0],
                ]
            )
        except Exception as e:
            logging.error(f"{e} error while processing entry: {entry.summary}")

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
    data_list = []

    for url in config_object["FEEDS"]["url"].split("\n"):
        try:
            feed = feedparser.parse(url)
            data_list.extend(texttodf(feed))
        except Exception as e:
            logging.error(f"Error parsing feed '{url}': {e}")

    data = pd.DataFrame(data_list, columns=columns)

    try:
        data["Publish_Date"] = pd.to_datetime(
            data.Publish_Date, format="mixed", dayfirst=True
        )
    except Exception as e:
        logging.error(
            f"Error converting 'Publish_Date' column to datetime: {e}")

    try:
        data["Update_Date"] = pd.to_datetime(
            data.Update_Date, format="mixed", dayfirst=True
        )
    except Exception as e:
        logging.error(
            f"Error converting 'Update_Date' column to datetime: {e}")

    data.to_csv(
        f'{root_folder}/{config_object["EXPORT"]["file_name"]}',
        index=False)
    logging.info("Data extraction and processing completed successfully.")


if __name__ == "__main__":
    main()
