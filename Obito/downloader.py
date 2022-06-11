from functools import partial
import os
import ssl
import sys
from typing import List
import typer
from time import sleep
from urllib.request import Request, urlopen
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from .get_filesize import get_filesize
# exceptions
from urllib.error import URLError


console = Console()

job_progress = Progress(
    "{task.description}",
    SpinnerColumn(),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
)

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
}

progress_table = Table.grid()
progress_table.add_row(
    Panel.fit(job_progress, title="[b]Downloads", border_style="magenta", padding=(1, 2)),
)

bins = {}

ssl._create_default_https_context = ssl._create_unverified_context


def getFilename(response, url):
    if not ".html" in url.split("/")[-1] and "text/html" in response.headers["Content-Type"]:
        url = url.rstrip("/"); url = url.replace(".", "_").replace("http://", "").replace("https://", "")
        return url.split("/")[-1] + ".html"
    

    elif not ".json" in url.split("/")[-1] and "application/json" in response.headers["Content-Type"]:
        url = url.rstrip("/"); url = url.replace(".", "_").replace("http://", "").replace("https://", "")
        return url.split("/")[-1] + ".json"

    
    else:
        return url.split("/")[-1]


def download(dest_path):
    with open(dest_path, "wb") as f:
        for data in iter(bins[dest_path], b""):
            f.write(data)

        while not job_progress.finished:
            for tasks in job_progress.tasks:
                if not tasks.finished:
                    sleep(0.1)
                    job_progress.update(tasks.id, advance=len(data))
                    

def process_url(
    urls: List[str] = typer.Option(..., "-u", "--url", help="URL(s) of files to be downloaded."),
    path: str = typer.Option("./", "-p", "--path", help="Path where files will be downloaded.")
    ):
    """Obito: URL file downloader which can download multiple files concurrently over internet."""
    if not os.path.exists(path):
        os.mkdir(path)
    with Live(progress_table, refresh_per_second=10):

        for url in urls:
            res = urlopen(Request(url, headers=headers))

            filesize = get_filesize(url)
            filename = getFilename(res, url)
            file_path = os.path.join(path, filename)

            bins.update(
                {
                    file_path: partial(res.read, filesize)
                }
            )

            job_progress.add_task(filename, total=filesize)
        print(list(map(download, bins.keys())))
        

def main():
    try:
        typer.run(process_url)
    except URLError:
        sys.exit(console.log("Please check your internet connection and URL(s)!", highlight=False))
    except OverflowError:
        sys.exit(console.log("File too large to download!"))
    except Exception as err:
        sys.exit(console.log(err))