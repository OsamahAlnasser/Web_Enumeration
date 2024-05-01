import requests
import socket
import json
import whois 
import socket 
import random
from bs4 import BeautifulSoup
import os
import time 
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import re
import threading
import sys
import xml.etree.ElementTree as ET
import concurrent.futures
from Cloud_Enumeration import *
from bruteforcing import *
from domain_enumeration import *

if __name__ == '__main__':
    
    ################################################# TASK 2 ####################################################
    
    # Get command line arguments
    args = sys.argv[1:]

    # Check if there are enough arguments
    if len(args) < 4:
        print("\033[91m")
        print("Insufficient arguments provided.")
        print("\033[92m")
        print("Usage: python3 [filename.py] mode -d domainName.com -t numOfThreads")
        print("\033[90m")
        sys.exit(1)

    # Parse command line arguments
    active_option = args[0]
    domain = ""
    num_threads = 0

    # Loop through arguments and extract domain and number of threads
    for i in range(1, len(args), 2):
        if args[i] == "-d":
            domain = args[i+1]
        elif args[i] == "-t":
            num_threads = int(args[i+1])
    print("\033[91m")
    print("Arguments received: ")
    print("\033[90m")
    print("Mode: ", active_option)
    print("Domain: ", domain)
    print("Number of threads: ", num_threads)
    
    # color the print statements in blue 
    print("\033[94m")    
    print("##### Subdomain enumeration using crt.sh and rapiddns.io #####")
    print("\033[91m")
    
    crt_subdomains = CrtSubdomains(domain)
    list_crt = crt_subdomains.get_subdomains_json()
    print("\033[33m")
    print(f"Number of subdomains for {domain} from crt.sh is {len(list_crt)}")

    rapid_subdomains = RapidSubdomains(domain)
    list_rapid = rapid_subdomains.get_subdomains()
    print(f"Number of subdomains for {domain} from rapiddns.io is {len(list_rapid)}")
    
    # Combine both lists and remove duplicates
    combined_list = list_crt + list_rapid   
    combined_list = list(set(combined_list))
    print("\033[94m")    
    print(f"Number of unique subdomains for {domain} from both crt.sh and rapiddns.io is {len(combined_list)}")
    print("List of subdomains: ")
    print("\033[36m")
    for subdomain in combined_list:
        print(subdomain)
    
    # Check if subdomains are alive
    
    print("\033[91m")
    print("Checking alive subdomains...")
    print("\033[92m")
   
    for subdomain in combined_list:
        if check_subdomain(subdomain):
            print(f"{subdomain} is alive")


    print("\033[91m")
    print("Number of alive subdomains: ", len(subdomains_ips))
    with open ("alive_subdomains.txt", "w") as file:
        for subdomain in subdomains_ips.keys():
            file.write(subdomain + "\n")
    print("List of alive subdomains: ")
    print("\033[36m")
    for subdomain in subdomains_ips.keys():
        print(f"{subdomain} - {subdomains_ips[subdomain]}")
        
    print("\033[91m")
    print("WHOIS enumeration for the domain: ")
    
    print("Domain: ", domain)
    whois_enum(domain)
    print("\033[91m")
    
    
    
    ################################################# TASK 3 ####################################################
    if(active_option == "active"):
        print(" ##### Subdomain enumeration using Bruteforcing and Web Crawling ##### ")
        # domain = input("Enter the domain: ")
        live_domains = "alive_subdomains.txt"

    ## SUBDOMAIN BRUTEFORCE ##
        bruteforce = Subdomains_Bruteforce(domain)
        subdomains = bruteforce.get_subdomains(num_threads)
        print("\033[94m")
        print("Found live subdomains through Bruteforcing: ")
        for subdomain, ip in subdomains.items():
            print(f"{subdomain} : {ip}")
    
        '''
        ## WEB CRAWLING ##   
        print("Web Crawler initiated...") 
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
        print("Running Selenium to capture screenshots of live domains... ")
        sel = ScreenshotTaker(live_domains)
        sel.take_screenshots()
        del sel
        '''
        
        ################################################# TASK 4 ####################################################
        
        print(" ##### Cloud Storage Enumeration ##### ")
        # if the domain contains ., take only the first part of the domain
        if "." in domain:
            domain = domain.split(".")[0]
        
        
        # Read permutations from file
        with open("Permutations.txt", "r") as perm_file:
            permutations = perm_file.read().splitlines()

        # Append permutations to wordlist
        
        if os.path.exists("wordlist.txt"):
            os.remove("wordlist.txt")
        
        with open("wordlist.txt", "w") as wordlist_file:
            wordlist_file.write(f"{domain}\n")            
            for perm in permutations:
                wordlist_file.write(f"{domain}{perm}\n")
            for perm in permutations:
                wordlist_file.write(f"{perm}{domain}\n")
            for perm in permutations:
                wordlist_file.write(f"{perm}{domain}{perm}\n")
            for perm in permutations:
                wordlist_file.write(f"{perm}{perm}{domain}\n")
            for perm in permutations:
                wordlist_file.write(f"{domain}{perm}{perm}\n")
        
        
        with open("wordlist.txt", "r") as file:
            wordlist = file.read().splitlines()
        
    
        print("#### BRUTEFORCING AZURE ####")
        azure = Azure(domain)
        found_accounts = azure.get_storage_accounts(wordlist, num_threads)
        print("\033[92m")
        print("List of all valid storage accounts: ")
        print("\033[91m")
        print(found_accounts)
        
        
        with open("containers.txt", "r") as file:
            containers_wordlist = file.read().splitlines()
            
        containers = azure.get_container_names(containers_wordlist, num_threads)
        print("\033[92m")
        print("List of all valid containers: ")
        print("\033[94m")
        for container in containers:
            print(container)
        
        for container in containers:
            urls = azure.parseXML(container)
            print("\033[92m")
            print(f"List of all URLs in {container}: ")
            print("\033[91m")
            if urls:
                for url in urls:
                    print(url)
            else:
                print("No URLs found in the container.")
        
        # make the color blue 
        print("\033[94m")
        print("#### BRUTEFORCING AWS ####")
        aws = AWS('wizardcyber')
        found_buckets = aws.get_buckets(wordlist, num_threads)
        print("\033[92m")
        print("List of all valid buckets: ")
        print("\033[91m")
        
        for bucket in found_buckets:
            print(bucket)
        
        urls = aws.get_urls()
        print("\033[92m")
        print("List of all valid URLs: ")
        print("\033[94m")
        for url in urls:
            print(url)

        print("\033[92m")
        print("#### BRUTEFORCING GCP ####")
        gcp = GCP(domain)
        gcp_buckets = gcp.get_buckets(wordlist, num_threads)
        print("\033[92m")
        print("List of all valid buckets: ")
        print("\033[90m")
        for bucket in gcp_buckets:
            print(bucket)

        print("\033[92m")
        print(f"List of all valid URLs: ")
        urls = gcp.get_urls()
        print("\033[94m")
        for url in urls:
            print(url)
        print("\033[92m")

    
    
    
    