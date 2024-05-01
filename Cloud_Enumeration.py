import requests 
import os
import re
import xml.etree.ElementTree as ET
import concurrent.futures
class Azure:
    baseurl = '.blob.core.windows.net'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
    def __init__(self, domain):
        self.domains = domain
        self.accounts = []
        self.found_accounts = []
        self.containers_counter = 0
        self.containers = []
        self.containers_dict = {}
        self.debug_counter = 0
    
    def get_storage_accounts(self, wordlist, num_threads):
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for word in wordlist:
                account = word + self.baseurl
                futures.append(executor.submit(self.check_account, account))
            
            for future in concurrent.futures.as_completed(futures):
                account = future.result()
                if account:
                    self.found_accounts.append(account)
        
        return self.found_accounts
    
    def check_account(self, account):
        try:
            print("Sending request to: ", "https://" + account)
            response = requests.get(f"https://{account}", headers=self.headers, timeout=0.6)
            print("\033[92m")
            print("Found account: ", account)
            return account
        except:
            return None
    
    def get_container_names(self, containers_wordlist, num_threads):
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for account in self.found_accounts:
                for word in containers_wordlist:
                    url = f"https://{account}/{word}?restype=container&comp=list"
                    futures.append(executor.submit(self.check_container, url))
            
            for future in concurrent.futures.as_completed(futures):
                container = future.result()
                if container:
                    self.containers.append(container)
        
        return self.containers
    
    def check_container(self, url):
        try:
            print("\033[90m", "Trying to access container: ", url)
            response = requests.get(url)
            if response.status_code == 200:                        
                print("\033[92m")
                print("Found container: ", url)
                return url
        except:
            return None
    
    def parseXML(self, link):
        try:
            response = requests.get(link)
            xml_data = response.content
            root = ET.fromstring(xml_data)
            urls = []
            for url in root.iter('Url'):
                urls.append(url.text)
            
        except:
            pass
        
        return urls
    
    def __del__(self):
        pass


class AWS: # Find public buckets, syntax is: {Domain}.s3.amazonaws.com
    baseurl = '.s3.amazonaws.com'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'}
    
    def __init__(self, domain):
        self.domain = domain
        self.urls = []
        self.buckets = []
        self.found_buckets = []

    def get_buckets(self, wordlist, num_threads):
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for word in wordlist:
                bucket = word + self.baseurl
                futures.append(executor.submit(self.check_bucket, bucket))
            
            for future in concurrent.futures.as_completed(futures):
                bucket = future.result()
                if bucket:
                    print("\033[92m")
                    print("Found bucket: ", bucket)
                    self.found_buckets.append(bucket)
        
        return self.found_buckets
    
    def check_bucket(self, bucket):
        try:
            print("\033[90m")
            print("Sending request to: ", "https://" + bucket)
            response = requests.get(f"https://{bucket}", headers=self.headers)
            
            if response.status_code == 200:
                return bucket
        except:
            pass
    
    def get_urls(self):
        for bucket in self.found_buckets:
            response = requests.get(f"https://{bucket}")
            xml_data = response.content
            root = ET.fromstring(xml_data)
            relative_link = []
            #pattern = r'<Key>(.*?)</Key>'

            pattern = r'<Key>(.*?)</Key>'  #  pattern
            relative_link = re.findall(pattern, response.text)  
            print("\033[94m")
            print("Relative links found in bucket: ", bucket)
            print("\033[91m")
            print(relative_link)
            
            for link in relative_link:
                url = f"https://{bucket}/{link}"
                self.urls.append(url)

        return self.urls
    
    def __del__(self):
        pass


class GCP:
    baseurl = 'storage.googleapis.com/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'}
    
    def __init__(self, domain):
        self.domain = domain
        self.urls = []
        self.buckets = []
        self.found_buckets = []
    
    def get_buckets(self, wordlist, num_threads):
        self.found_buckets = []
        def check_bucket(bucket):
            try:
                print("\033[90m")
                print("Sending request to: ", "https://" + bucket)
                response = requests.get(f"https://{bucket}", headers=self.headers)
                if response.status_code == 200:
                    print("\033[92m")
                    print("Found public bucket: ", bucket)
                    self.found_buckets.append(bucket)
                if response.status_code == 403:
                    print("\033[94m")
                    print("Found protected bucket: ", bucket)
            except:
                pass

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            executor.map(check_bucket, [self.baseurl + word for word in wordlist])

        return self.found_buckets
    
    def get_urls(self):
        for bucket in self.found_buckets:
            response = requests.get(f"https://{bucket}")
            xml_data = response.content
            root = ET.fromstring(xml_data)
            relative_link = []

            pattern = r'<Key>(.*?)</Key>'  #  pattern
            relative_link = re.findall(pattern, response.text)  
            for link in relative_link:
                url = f"https://{bucket}/{link}"
                if url not in self.urls:
                    self.urls.append(url)

        return self.urls
       
if __name__ == "__main__":
    
    domain = input("Enter domain: (without .com): ")
    
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
    found_accounts = azure.get_storage_accounts(wordlist)
    print("\033[92m")
    print("List of all valid storage accounts: ")
    print("\033[91m")
    print(found_accounts)
    
    
    with open("containers.txt", "r") as file:
        containers_wordlist = file.read().splitlines()
        
    containers = azure.get_container_names(containers_wordlist)
    print("\033[92m")
    print("List of all valid containers: ")
    print("\033[94m")
    for container in containers:
        print(container)
    # add valid containers to Azure_Valid_Containers.txt
    with open("Azure_Valid_Containers.txt", "w") as file:
        for container in containers:
            file.write(container + "\n")
    
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
        
        # add valid URLs of {container} to {container}_Valid_URLs.txt
        with open(f"{container}_Valid_URLs.txt", "w") as file:
            for url in urls:
                file.write(url + "\n")
    
    
    print("#### BRUTEFORCING AWS ####")
    aws = AWS('wizardcyber')
    found_buckets = aws.get_buckets(wordlist)
    print("\033[92m")
    print("List of all valid buckets: ")
    print("\033[91m")
    
    for bucket in found_buckets:
        print(bucket)
    
    # add valid buckets to AWS_Valid_Buckets.txt
    with open("AWS_Valid_Buckets.txt", "w") as file:
        for bucket in found_buckets:
            file.write(bucket + "\n")
    
    urls = aws.get_urls()
    print("\033[92m")
    print("List of all valid URLs: ")
    print("\033[91m")
    for url in urls:
        print(url)
    
    # add valid URLs to {Container}_Valid_URLs.txt
    with open("AWS_Valid_URLs.txt", "w") as file:
        for url in urls:
            file.write(url + "\n")

    print("#### BRUTEFORCING GCP ####")
    gcp = GCP(domain)
    gcp_buckets = gcp.get_buckets(wordlist)
    print("\033[92m")
    print("List of all valid buckets: ")
    print("\033[90m")
    for bucket in gcp_buckets:
        print(bucket)
    
    # add valid buckets to GCP_Valid_Buckets.txt
    with open("GCP_Valid_Buckets.txt", "w") as file:
        for bucket in gcp_buckets:
            file.write(bucket + "\n")

    print("\033[92m")
    print(f"List of all valid URLs: ")
    urls = gcp.get_urls()
    for url in urls:
        print("\033[94m")
        print(url)
    # add valid URLs to GCP_Valid_URLs.txt
    with open("GCP_Valid_URLs.txt", "w") as file:
        for url in urls:
            file.write(url + "\n")
    print("\033[92m")      
    
    