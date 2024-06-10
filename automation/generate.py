import argparse
from typing import List

import pandas as pd

from pandas.core.series import Series

TITLE_COLUMN_NAME = "title"
AUTHORS_COLUMN_NAME = "authors"
TOPIC_COLUMN_NAME = "topic"
SESSION_COLUMN_NAME = "session"
POSTER_COLUMN_NAME = "poster"
PAPER_COLUMN_NAME = "paper"
CODE_COLUMN_NAME = "code"
HUGGINGFACE_SPACE_COLUMN_NAME = "huggingface"
YOUTUBE_COLUMN_NAME = "youtube"
COLAB_COLUMN_NAME = "colab"

AUTOGENERATED_PAPERS_LIST_TOKEN = "<!--- AUTOGENERATED_PAPERS_LIST -->"

WARNING_HEADER = [
    "<!---",
    "   WARNING: DO NOT EDIT THIS LIST MANUALLY. IT IS AUTOMATICALLY GENERATED.",
    "   HEAD OVER TO https://github.com/SkalskiP/top-cvpr-2024-papers/blob/master/CONTRIBUTING.md FOR MORE DETAILS ON HOW TO MAKE CHANGES PROPERLY.",
    "-->"
]

ARXIV_BADGE_PATTERN = '[<a href="https://arxiv.org/abs/{}">paper</a>]'
GITHUB_BADGE_PATTERN = '[<a href="{}">code</a>]'
HUGGINGFACE_SPACE_BADGE_PATTERN = '[<a href="{}">demo</a>]'
COLAB_BADGE_PATTERN = '[<a href="{}">colab</a>]'
YOUTUBE_BADGE_PATTERN = '[<a href="{}">video</a>]'

def read_lines_from_file(path: str) -> List[str]:
    """
    Reads lines from file and strips trailing whitespaces.
    """
    with open(path) as file:
        return [line.rstrip() for line in file]


def save_lines_to_file(path: str, lines: List[str]) -> None:
    """
    Saves lines to file.
    """
    with open(path, "w") as f:
        for line in lines:
            f.write("%s\n" % line)


def format_entry(entry: Series) -> str:
    """
    Formats entry into Markdown table row, ensuring dates are formatted correctly.
    """
    title = entry.loc[TITLE_COLUMN_NAME]
    authors = entry.loc[AUTHORS_COLUMN_NAME]
    topics = entry.loc[TOPIC_COLUMN_NAME]
    session = entry.loc[SESSION_COLUMN_NAME]
    poster = entry.loc[POSTER_COLUMN_NAME]
    paper_url = entry.loc[PAPER_COLUMN_NAME]
    code_url = entry.loc[CODE_COLUMN_NAME]
    huggingface_url = entry.loc[HUGGINGFACE_SPACE_COLUMN_NAME]
    youtube_url = entry.loc[YOUTUBE_COLUMN_NAME]
    colab_url = entry.loc[COLAB_COLUMN_NAME]
    arxiv_badge = ARXIV_BADGE_PATTERN.format(paper_url) if paper_url else ""
    code_badge = GITHUB_BADGE_PATTERN.format(code_url) if code_url else ""
    youtube_badge = YOUTUBE_BADGE_PATTERN.format(youtube_url) if youtube_url else ""
    huggingface_badge = HUGGINGFACE_SPACE_BADGE_PATTERN.format(huggingface_url) if huggingface_url else ""
    colab_badge = COLAB_BADGE_PATTERN.format(colab_url) if colab_url else ""
    badges = " ".join([arxiv_badge, code_badge, youtube_badge, huggingface_badge, colab_badge])

    if not poster:
        return ""

    return f"""
<p align="left">
<img src="{poster}" alt="{title}" width="300px" align="left" />
<a href="{paper_url}" title="{title}"><strong>{title}</strong></a>
<br/>
{authors}
<br/>
{badges}
<br/>
<ul>
<li><strong>Topic:</strong> {topics}</li>
<li><strong>Session:</strong> {session}</li>
</ul>

</p>

<br/>
    """


def load_table_entries(path: str) -> List[str]:
    """
    Loads table entries from csv file, sorted by date in descending order and formats dates.
    """
    df = pd.read_csv(path, quotechar='"', dtype=str)
    df.columns = df.columns.str.strip()
    df = df.fillna("")
    return [
        format_entry(row)
        for _, row
        in df.iterrows()
    ]


def search_lines_with_token(lines: List[str], token: str) -> List[int]:
    """
    Searches for lines with token.
    """
    result = []
    for line_index, line in enumerate(lines):
        if token in line:
            result.append(line_index)
    return result


def inject_papers_list_into_readme(
    readme_lines: List[str],
    papers_list_lines: List[str]
) -> List[str]:
    """
    Injects papers list into README.md.
    """
    lines_with_token_indexes = search_lines_with_token(
        lines=readme_lines, token=AUTOGENERATED_PAPERS_LIST_TOKEN)

    if len(lines_with_token_indexes) != 2:
        raise Exception(f"Please inject two {AUTOGENERATED_PAPERS_LIST_TOKEN} "
                        f"tokens to signal start and end of autogenerated table.")

    [start_index, end_index] = lines_with_token_indexes
    return readme_lines[:start_index + 1] + papers_list_lines + readme_lines[end_index:]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data_path', default='automation/data.csv')
    parser.add_argument('-r', '--readme_path', default='README.md')
    args = parser.parse_args()

    table_lines = load_table_entries(path=args.data_path)
    table_lines = WARNING_HEADER + table_lines
    readme_lines = read_lines_from_file(path=args.readme_path)
    readme_lines = inject_papers_list_into_readme(readme_lines=readme_lines,
                                                  papers_list_lines=table_lines)
    save_lines_to_file(path=args.readme_path, lines=readme_lines)