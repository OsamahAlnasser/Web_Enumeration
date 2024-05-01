import socket 
import requests
import random
from bs4 import BeautifulSoup
import os
import time 
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import re
import concurrent.futures


class Subdomains_Bruteforce:
    def __init__(self, domain):
        self.domain = domain
        self.subdomains = []
        self.wordlist = []
        self.subdomains_ips = {}
        self.wordlist_path = "subdomains-top1million-5000.txt"
        
        self.load_wordlist()
        
    def load_wordlist(self):
        with open(self.wordlist_path, "r") as file:
            self.wordlist = file.read().split("\n")
    
    def get_subdomains(self, num_threads):
        def check_subdomain(subdomain):
            try:
                subdomain = subdomain.strip()
                domain = subdomain + "." + self.domain
                print("Bruteforcing: ", domain)
                ip = socket.gethostbyname(domain)
                self.subdomains_ips[domain] = ip
            except (socket.gaierror, socket.herror):
                pass

        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for subdomain in self.wordlist:
                future = executor.submit(check_subdomain, subdomain)
                futures.append(future)
            for future in concurrent.futures.as_completed(futures):
                pass

        return self.subdomains_ips

    def __del__(self):
        pass
    

# Class to scrape the website and get links
class Web_Crawler:
    def __init__(self, domain):
        self.domain = domain.strip() 

    def get_links(self, is_main_domain):
        links = []
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
        
        protocols = ["http://", "https://"]  
        for protocol in protocols:
            try:
                if is_main_domain:
                    response = requests.get(protocol + self.domain, headers=header)
                else:
                    response = requests.get(self.domain, headers=header) 

                soup = BeautifulSoup(response.text, 'html.parser')

                # Find and process anchor tags
                for tag in soup.find_all('a'):
                    link = tag.get('href')
                    if link is not None and link not in links:  
                        if link.startswith("#"): 
                            continue
                        
                        # Clean the link (remove spaces, excessive slashes)
                        link = re.sub(r"\s+", "", link)  # Remove spaces
                        
                        if link.startswith(protocols[0]) or link.startswith(protocols[1]):  # Full link
                            print("Found Link: ", link)
                            links.append(link)
                        else:  # Relative link
                            if is_main_domain:  
                                print("Found Link: ", protocol + self.domain + link)
                                links.append(protocol + self.domain + link)
                            else:
                                print("Found Link: ", self.domain + link)
                                links.append(self.domain + link)

                # Find and process src elements 
                for element in soup.find_all(src=True):
                    link = element['src']
                    if link is not None and link not in links:

                        # Clean the link
                        link = re.sub(r"\s+", "", link)
                        
                        if link.startswith(protocols[0]) or link.startswith(protocols[1]):  # Full link
                            print("Found Link: ", link)
                            links.append(link)
                        else:  # Relative link
                            if is_main_domain:
                                print("Found Link: ", protocol + self.domain + link)
                                links.append(protocol + self.domain + link)
                            else:
                                print("Found Link: ", self.domain + link)
                                links.append(self.domain + link)

            except requests.exceptions.RequestException:
                pass
        return links

    def __del__(self):
        pass


# Class to take screenshots of the found domains
class ScreenshotTaker:
    def __init__(self, filename):
        self.filename = filename
        
    def take_screenshots(self):
        with open(self.filename, "r") as file:
            domains = file.readlines()
        
        print("Taking screenshots for: ", domains)
        directory = r"C:\Users\osama\OneDrive\Desktop\Python_Training\Screenshots"

        # **Removing the screenshots directory**
        try:
            shutil.rmtree(directory)
        except OSError as e:
            print(f"Error deleting directory: {e}")
        # **Creating the directory again to ensure it's empty**
        try:
            os.makedirs(directory)
        except OSError as e:
            print(f"Error creating directory: {e}")

        for domain in domains:   
            try:
                options = Options()
                options.add_argument("headless=new")
                options.add_argument("disable-extensions")
                options.add_argument("log-level=3")
                driver = webdriver.Chrome()
                driver.set_page_load_timeout(10) 
                driver.get("https://" + domain.strip())
                print("domain: ", domain)
                screenshot_path = os.path.join("Screenshots", domain.replace(".", "_").strip() + '.png')
                driver.save_screenshot(screenshot_path)
                print(f"Took screenshot for {domain}")
                driver.quit()
                time.sleep(1)
            except (WebDriverException):
                print("Error taking screenshot for: ", domain)
                
        print("Done taking screenshots. All taken screenshots have been saved.")
       
    def __del__(self):
        pass 

if __name__ == "__main__":
    
    domain = input("Enter the domain: ")
    live_domains = "alive_subdomains.txt"

   ## SUBDOMAIN BRUTEFORCE ##
    bruteforce = Subdomains_Bruteforce(domain)
    subdomains = bruteforce.get_subdomains()
    print("\033[94m")
    print("Found live subdomains through Bruteforcing: ")
    for subdomain, ip in subdomains.items():
        print(f"{subdomain} : {ip}")
    # AAdd found live subdomains to a file
    with open(live_domains.txt, "w") as file:
        for subdomain, ip in subdomains.items():
            file.write(subdomain + "\n")
            
    ## WEB CRAWLING ##    
    web_crawler = Web_Crawler(domain)
    links = web_crawler.get_links(True)
    print(links)
    print("\033[93m")
    print("Found links: ")
    
    Unduplicated_Links = []
    for link in links:
        if link not in Unduplicated_Links:
            link.strip()
            Unduplicated_Links.append(link)
    
    with open("links.txt", "w") as file:
        for link in Unduplicated_Links:
            file.write(link + "\n")
            
    # print found links for the main domain
    for link in Unduplicated_Links:
        print("Found Link:", link)
        
    for link in Unduplicated_Links:
        try:
            # select a random printing color from red, blue, green, yellow: 
            colors = ["\033[91m", "\033[94m", "\033[92m", "\033[93m"]
            color = colors[random.randint(0, 3)]
            print(color)
            
            print("Crawling link: ", link)
            web_crawler = Web_Crawler(link)
            links = web_crawler.get_links(False)
            for link in links:
                if link not in Unduplicated_Links:
                    Unduplicated_Links.append(link)
            del web_crawler
        except requests.exceptions.RequestException:
            pass
        
    ## SCREENSHOT TAKING ##
    print("Running Selenium to capture screenshots of live domains: ")
    sel = ScreenshotTaker(live_domains)
    sel.take_screenshots()
    del sel
        
