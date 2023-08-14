import click
import pandas as pd


@click.group()
def main():
    ...


@main.command()
@click.option("--title", "-t", required=True, help="Title of the markdown")
@click.option("--source", "-s", required=True, help="Path of the spreadsheet")
@click.option(
    "--links", "-l", multiple=True, help="Fields contain url link, multi-values."
)
@click.option("--drops", "-d", multiple=True, help="Fields to drop, multi-values.")
def csv2md(title, source, links, drops):
    """Generate paper list into markdown format from a given spreadsheet"""
    ...

    df = pd.read_csv(source).fillna("")
    if drops:
        df.drop(columns=drops, inplace=True)

    if links:
        for field in links:
            if field in df.columns:
                df[field] = [f"[link]({row})" if row else "" for row in df[field]]

    print(f"# {title}")
    print(df.to_markdown(index=False))


if __name__ == "__main__":
    main()
