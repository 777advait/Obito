from urllib.request import Request, urlopen
import ssl

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
}

def get_filesize(url):
    ssl._create_default_https_context = ssl._create_unverified_context
    return len(urlopen(Request(url, headers=headers)).read())

# print(get_filesize("https://google.com"))