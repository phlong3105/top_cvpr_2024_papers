import argparse
from typing import List

import pandas as pd

from pandas.core.series import Series

TOPIC_COLUMN_NAME = "topic"
TITLE_COLUMN_NAME = "title"
AUTHORS_COLUMN_NAME = "authors"
PAPER_COLUMN_NAME = "paper"
CODE_COLUMN_NAME = "code"

AUTOGENERATED_COURSES_TABLE_TOKEN = "<!--- AUTOGENERATED_COURSES_TABLE -->"

WARNING_HEADER = [
    "<!---",
    "   WARNING: DO NOT EDIT THIS TABLE MANUALLY. IT IS AUTOMATICALLY GENERATED.",
    "   HEAD OVER TO CONTRIBUTING.MD FOR MORE DETAILS ON HOW TO MAKE CHANGES PROPERLY.",
    "-->"
]

TABLE_HEADER = [
    "| **topic** | **title** | **authors** | **repository / paper** |",
    "|:---------:|:---------:|:-----------:|:----------------------:|"
]

GITHUB_CODE_PREFIX = "https://github.com/"
GITHUB_BADGE_PATTERN = "[![GitHub](https://img.shields.io/github/stars/{}?style=social)]({})"
ARXIV_BADGE_PATTERN = "[![arXiv](https://img.shields.io/badge/arXiv-{}-b31b1b.svg)](https://arxiv.org/abs/{})"


def read_lines_from_file(path: str) -> List[str]:
    with open(path) as file:
        return [line.rstrip() for line in file]


def save_lines_to_file(path: str, lines: List[str]) -> None:
    with open(path, "w") as f:
        for line in lines:
            f.write("%s\n" % line)


def format_entry(entry: Series) -> str:
    topic = entry.loc[TOPIC_COLUMN_NAME]
    title = entry.loc[TITLE_COLUMN_NAME]
    authors = entry.loc[AUTHORS_COLUMN_NAME]
    paper_url = entry.loc[PAPER_COLUMN_NAME]
    code_url = entry.loc[CODE_COLUMN_NAME]
    stripped_code_url = code_url.replace(GITHUB_CODE_PREFIX, "")
    github_badge = GITHUB_BADGE_PATTERN.format(stripped_code_url, code_url) if code_url else ""
    arxiv_badge = ARXIV_BADGE_PATTERN.format(paper_url, paper_url) if paper_url else ""
    return f"| {topic} | {title} | {authors} | {github_badge} {arxiv_badge}|"


def load_table_entries(path: str) -> List[str]:
    df = pd.read_csv(path, quotechar='"', dtype=str)
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df.columns = df.columns.str.strip()
    return [
        format_entry(row)
        for _, row
        in df.iterrows()
    ]


def search_lines_with_token(lines: List[str], token: str) -> List[int]:
    result = []
    for line_index, line in enumerate(lines):
        if token in line:
            result.append(line_index)
    return result


def inject_markdown_table_into_readme(readme_lines: List[str], table_lines: List[str]) -> List[str]:
    lines_with_token_indexes = search_lines_with_token(lines=readme_lines, token=AUTOGENERATED_COURSES_TABLE_TOKEN)
    if len(lines_with_token_indexes) != 2:
        raise Exception(f"Please inject two {AUTOGENERATED_COURSES_TABLE_TOKEN} "
                        f"tokens to signal start and end of autogenerated table.")

    [table_start_line_index, table_end_line_index] = lines_with_token_indexes
    return readme_lines[:table_start_line_index + 1] + table_lines + readme_lines[table_end_line_index:]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data_path', default='automation/data.csv')
    parser.add_argument('-r', '--readme_path', default='README.md')
    args = parser.parse_args()

    table_lines = load_table_entries(path=args.data_path)
    table_lines = WARNING_HEADER + TABLE_HEADER + table_lines
    readme_lines = read_lines_from_file(path=args.readme_path)
    readme_lines = inject_markdown_table_into_readme(readme_lines=readme_lines, table_lines=table_lines)
    save_lines_to_file(path=args.readme_path, lines=readme_lines)