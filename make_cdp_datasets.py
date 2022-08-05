"""
This script processes the raw CDP cities, states, and corporations datasets,
and outputs 3 new CSV files for each dataset:
- filtered_comments.csv
- filtered_responses.csv
- combined.csv
"""
from __future__ import annotations

from collections.abc import Sequence
import os
import re

from langdetect import DetectorFactory, detect
import pandas as pd
from tqdm import tqdm


DetectorFactory.seed = 0  # by default, langdetect is non-deterministic
tqdm.pandas()


def lang(x: str) -> str:
    """Returns the 2-letter language code for a given string.

    See the list of supported language codes here:
    https://github.com/Mimino666/langdetect
    """
    try:
        return detect(x)
    except:
        tqdm.write(x)
        return "na"


def clean(x: str) -> str:
    """Replace sequences of digits with empty string."""
    try:
        return re.sub(r'\d+. ', '', x)
    except:
        return x


def make_cdp_dataset(data_folder: str,
                     filename_template: str,
                     years: Sequence[str],
                     columns: Sequence[str],
                     comm_col: str,
                     resp_col: str,
                     clean_cols: Sequence[str] = (),
                     ) -> None:
    """
    Args
    - data_folder: path to folder where raw CSVs are located, and where
        processed CSVs will be saved
    - filename_template: filename of raw CSV, with `{y}` for year
    - years: list of years
    - columns: names of columns to read from raw CSV
    - comm_col: name of "comments" column
    - resp_col: name of "responses" column
    - clean_cols: name of columns to clean in the combined output CSV
    """
    comment_dfs = []
    response_dfs = []

    for y in years:
        csv_path = os.path.join(data_folder, filename_template.format(y=y))
        print(f"Reading CSV: {csv_path}")
        df = pd.read_csv(csv_path, usecols=columns, low_memory=False)
        comment_df = df[~df[comm_col].isna()]
        response_df = df[df[comm_col].isna() & df[resp_col].notna()]
        comment_dfs.append(comment_df)
        response_dfs.append(response_df)

    comments = pd.concat(comment_dfs)
    comments.drop_duplicates(subset=[comm_col], keep="first", inplace=True)
    comments = comments[comments[comm_col].str.split().apply(len) > 10]
    comments = comments[comments[comm_col].progress_apply(lang) == "en"]
    comments_csv_path = os.path.join(data_folder, "filtered_comments.csv")
    comments.to_csv(comments_csv_path)
    print("Finished filtering comments")

    responses = pd.concat(response_dfs)
    responses.drop_duplicates(subset=[resp_col], keep="first", inplace=True)
    responses = responses[responses[resp_col].str.split().apply(len) > 10]
    responses = responses[responses[resp_col].progress_apply(lang) == "en"]
    responses_csv_path = os.path.join(data_folder, "filtered_responses.csv")
    responses.to_csv(responses_csv_path)
    print("Finished filtering responses")

    combined = pd.concat([responses, comments])
    combined["Text"] = combined[comm_col].where(
        ~combined[comm_col].isna(), combined[resp_col]
    )
    for col in clean_cols:
        combined[col] = combined[col].apply(clean)
    combined = (
        combined
        .reset_index(drop=True)
        .reset_index()
        .rename(columns={"index": "id"})
    )
    combined_csv_path = os.path.join(data_folder, "combined.csv")
    combined.to_csv(combined_csv_path, index=False)
    print("Finished combining")


def make_cdp_cities_dataset() -> None:
    data_folder = "./CDP/Cities/Cities Responses/"
    years = ["2018", "2019", "2020", "2021"]
    filename_template = "{y}_Full_Cities_Dataset.csv"
    columns = [
        "Year Reported to CDP",
        "Organization",
        "Parent Section",
        "Section",
        "Question Name",
        "Row Name",
        "Response Answer",
        "Comments",
    ]
    comm_col = "Comments"
    resp_col = "Response Answer"
    clean_cols = ["Parent Section", "Section"]
    make_cdp_dataset(
        data_folder=data_folder, filename_template=filename_template,
        years=years, columns=columns, comm_col=comm_col, resp_col=resp_col,
        clean_cols=clean_cols)


def make_cdp_states_dataset() -> None:
    data_folder = "./CDP/States/"
    years = ["2018-2019", "2020", "2021"]
    filename_template = "{y}_Full_States_Dataset.csv"
    columns = [
        "Year Reported to CDP",
        "Organization",
        "Parent Section",
        "Section",
        "Question Name",
        "Row Name",
        "Response Answer",
        "Comments",
    ]
    comm_col = "Comments"
    resp_col = "Response Answer"
    clean_cols = ["Parent Section", "Section"]
    make_cdp_dataset(
        data_folder=data_folder, filename_template=filename_template,
        years=years, columns=columns, comm_col=comm_col, resp_col=resp_col,
        clean_cols=clean_cols)


def make_cdp_corp_dataset() -> None:
    data_folder = "./CDP/Corporations/Corporations Responses/Climate Change/"
    years = ["2018", "2019", "2020"]
    filename_template = "{y}_Full_Climate_Change_Dataset.csv"
    columns = [
        "survey_year",
        "organization",
        "module_name",
        "column_name",
        "question_unique_reference",
        "response_value",
        "comments",
    ]
    comm_col = "comments"
    resp_col = "response_value"
    clean_cols = ["module_name", "column_name"]
    make_cdp_dataset(
        data_folder=data_folder, filename_template=filename_template,
        years=years, columns=columns, comm_col=comm_col, resp_col=resp_col,
        clean_cols=clean_cols)


if __name__ == '__main__':
    make_cdp_cities_dataset()
    make_cdp_corp_dataset()
    # make_cdp_states_dataset()
