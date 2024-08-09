import requests
from termcolor import colored
from bs4 import BeautifulSoup
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
import argparse
import tkinter as tk
from tkinter import messagebox

class WebCrawler:
    def __init__(self, url, max_depth):
        self.url = url
        self.max_depth = max_depth
        self.subdomains = set()
        self.links = set()
        self.jsfiles = set()
        self.visited = set()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    def start_crawling(self):
        self.crawl(self.url, depth=1)

    def crawl(self, url, depth):
        if depth > self.max_depth or url in self.visited:
            return
        self.visited.add(url)

        try:
            response = requests.get(url, headers=self.headers, timeout=5, allow_redirects=True)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as err:
            print(f"[-] An error occurred: {err}")
            return

        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        subdomain_query = fr"https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"

        for link in soup.find_all('a', href=True):
            link_text = link.get('href')
            full_link = urljoin(base_url, link_text)

            if re.match(subdomain_query, full_link) and full_link not in self.subdomains:
                self.subdomains.add(full_link)
            elif full_link.startswith(base_url) and full_link not in self.links:
                self.links.add(full_link)
                self.crawl(full_link, depth + 1)

        for file in soup.find_all('script', src=True):
            script_src = file.get('src')
            full_script_src = urljoin(base_url, script_src)
            self.jsfiles.add(full_script_src)

    def print_banner(self):
        print("-" * 80)
        print(colored(f"Recursive Web Crawler starting at {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 'cyan', attrs=['bold']))
        print("-" * 80)
        print(f"[*] URL".ljust(20, " "), ":", self.url)
        print(f"[*] Max Depth".ljust(20, " "), ":", self.max_depth)
        print("-" * 80)

    def print_results(self):
        if self.subdomains:
            print(f"[+] Subdomains ({len(self.subdomains)}):")
            for subdomain in self.subdomains:
                print(f"  - {subdomain}")
        print()

        if self.links:
            print(f"[+] Links ({len(self.links)}):")
            for link in self.links:
                print(f"  - {link}")
        print()

        if self.jsfiles:
            print(f"[+] JS Files ({len(self.jsfiles)}):")
            for file in self.jsfiles:
                print(f"  - {file}")

def start_crawling_from_gui():
    url = url_entry.get()
    depth = int(depth_entry.get())

    web_crawler = WebCrawler(url, depth)
    web_crawler.start_crawling()
    web_crawler.print_results()
    messagebox.showinfo("Crawling Complete", "Web crawling process completed. Check console for results.")

# GUI Setup
root = tk.Tk()
root.title("Web Crawler")

url_label = tk.Label(root, text="URL:")
url_label.grid(row=0, column=0, padx=10, pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10)

depth_label = tk.Label(root, text="Depth:")
depth_label.grid(row=1, column=0, padx=10, pady=10)
depth_entry = tk.Entry(root, width=10)
depth_entry.grid(row=1, column=1, padx=10, pady=10)

crawl_button = tk.Button(root, text="Start Crawling", command=start_crawling_from_gui)
crawl_button.grid(row=2, columnspan=2, padx=10, pady=10)

root.mainloop()
