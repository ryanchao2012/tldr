import click
import pandas as pd
import os
from slugify import slugify
import fitz
import requests
import time
import random
import json


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
    "--outdir", "-o", required=True, help="Output folder for downloaded papers"
)
@click.option("--link", "-l", required=True, help="Paper link field in the spreadsheet")
@click.option("--title", "-t", required=True, help="Title field in the spreadsheet")
def download(csv, outdir, link, title):
    """Batch download papers from a given spreadsheet"""

    df = pd.read_csv(csv).fillna("")

    os.makedirs(outdir, exist_ok=True)

    for i, row in df.iterrows():
        tt = row[title]
        slug = slugify(tt)
        out = os.path.join(outdir, f"{slug}.pdf")
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
@click.option("--csv", "-s", required=True, help="Path of the input spreadsheet")
@click.option("--title", "-t", required=True, help="Title field in the spreadsheet")
@click.option("--indir", "-i", required=True, help="Input folder to search PDF files")
@click.option(
    "--outdir", "-o", required=True, help="Output folder to output JSON files"
)
@click.option(
    "--overwrite",
    "-w",
    default=False,
    help="If False, Skip conversion when output JSON exists already",
)
def pdf2json(csv, title, indir, outdir, overwrite):
    """Batch convert PDF to JSON from a given spreadsheet"""
    df = pd.read_csv(csv).fillna("")

    os.makedirs(outdir, exist_ok=True)

    for i, row in df.iterrows():
        tt = row[title]
        slug = slugify(tt)
        in_ = os.path.join(indir, f"{slug}.pdf")
        out = os.path.join(outdir, f"{slug}.json")
        if (not overwrite) and os.path.isfile(out):
            print(f"SKIP[{i}] output JSON already exists: {out}")
            continue
        elif not os.path.isfile(in_):
            print(f"SKIP[{i}] input PDF doesn't exist: {in_}")
            continue

        _file2json(in_, outdir, True)


@main.command()
@click.option("--pdf", "-p", required=True, help="Input PDF path")
@click.option("--outdir", "-o", required=True, help="Output folder to output JSON file")
@click.option(
    "--overwrite",
    "-w",
    default=False,
    help="If False, Skip conversion when output JSON exists already",
)
def file2json(pdf: str, outdir: str, overwrite: bool):
    _file2json(pdf, outdir, overwrite)


def _file2json(pdf: str, outdir: str, overwrite: bool):
    """Convert single PDF to JSON"""

    os.makedirs(outdir, exist_ok=True)
    fname = pdf.rsplit("/")[-1].split(".")[0]
    out = os.path.join(outdir, f"{fname}.json")
    if (not overwrite) and os.path.isfile(out):
        print(f"[SKIP] {out}")
        return

    doc = fitz.Document(pdf)
    with open(out, "w") as f:
        for p, page in enumerate(doc):
            data = json.loads(page.get_text("json"))
            data["page_no"] = p

            f.write(
                json.dumps(
                    data,
                    ensure_ascii=False,
                )
                .encode("utf-8", "ignore")
                .decode()
                + "\n"
            )

    print(f"[Save] {out}")


if __name__ == "__main__":
    main()
