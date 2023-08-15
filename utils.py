import click
import pandas as pd
import os
from slugify import slugify
import fitz
import requests
import time
import random


@click.group()
def main():
    ...


@main.command()
@click.option("--title", "-t", required=True, help="Title of the markdown")
@click.option("--csv", "-s", required=True, help="Path of the spreadsheet")
@click.option(
    "--links",
    "-l",
    multiple=True,
    help="Fields are expected to be url link, multi-values.",
)
@click.option("--drops", "-d", multiple=True, help="Fields to drop, multi-values.")
def csv2md(title, csv, links, drops):
    """Generate paper list into markdown format from a spreadsheet"""

    df = pd.read_csv(csv).fillna("")
    if drops:
        df.drop(columns=drops, inplace=True)

    if links:
        for field in links:
            if field in df.columns:
                df[field] = [f"[link]({row})" if row else "" for row in df[field]]

    print(f"# {title}")
    print(df.to_markdown(index=False))


@main.command()
@click.option("--csv", "-s", required=True, help="Path of the input spreadsheet")
@click.option(
    "--output", "-o", required=True, help="Output folder for downloaded papers"
)
@click.option("--link", "-l", required=True, help="Paper link field in the spreadsheet")
@click.option("--title", "-t", required=True, help="Title field in the spreadsheet")
def download(csv, output, link, title):
    """Download papers from a given spreadsheet"""

    df = pd.read_csv(csv).fillna("")

    for i, row in df.iterrows():
        tt = row[title]
        slug = slugify(tt)
        out = os.path.join(output, f"{slug}.pdf")
        if os.path.isfile(out):
            print(f"SKIP[{i}] file already exists: {out}")
            continue

        url = row[link]
        if url:
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code != 200:
                    raise RuntimeError("Response status != 200")
            except Exception as err:
                print(f"[WARN[{i}] {url}, {err}")
                continue

            with open(out, "wb") as f:
                f.write(resp.content)

            print(f"Save[{i}] {url} to {out}")
            time.sleep(1 + random.random() * 2)  # sleep for a while between api calls


@main.command()
def pdf2xml():
    """Convert PDF to XML format"""
    # TODO: pdf2xml
    ...


if __name__ == "__main__":
    main()
