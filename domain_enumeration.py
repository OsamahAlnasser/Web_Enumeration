import requests
import socket
import json
import whois 


class CrtSubdomains:
    def __init__(self, domain):
        self.domain = domain
        self.subdomains = []


    def get_subdomains_json(self): 
        response = requests.get(f"https://crt.sh/?q={self.domain}&output=json")

        if response.status_code == 200:
            data = json.loads(response.text)            
            for item in data:
                if item['common_name'] not in self.subdomains:
                    self.subdomains.append(item['common_name'])

            for subdomain in self.subdomains:
                print("Subdomain: ", subdomain)
        else:
            print("Error fetching subdomains from crt.sh")
        
        return self.subdomains

    def get_subdomains(self):
        response = requests.get(f"https://crt.sh/?q={self.domain}")
        
        elements = response.text.split("\n")
             
        for element in elements:
            # Check if the element ends with ".arabbank.com</td>"
            if element.endswith(f".{self.domain}</TD>"):
                subdomain = element.replace("<TD>", "").replace("</TD>", "")
                # if subdomain contains <BR>, don't add it to the list 
                if "<BR>" in subdomain:
                    continue
                # remove duplicates
                subdomain = subdomain.strip()
                if subdomain not in self.subdomains:
                    self.subdomains.append(subdomain)
        return self.subdomains
                
                
    def __del__(self):
        pass
    
# Class to fetch subdomains from rapiddns.io
class RapidSubdomains:
    def __init__(self, domain):
        self.domain = domain
        self.subdomains = []
        
    def get_subdomains(self):
        response = requests.get(f"https://rapiddns.io/s/{self.domain}#result")
        elements = response.text.split("\n")
        with open ("rapid.txt", "w") as file:
            file.write(str(response.text))
         
        for element in elements:   
            if element.endswith(f".{self.domain}</td>"):
                    subdomain = element.replace("<td>", "").replace("</td>", "")
                    subdomain = subdomain.strip()
                    # remove duplicates
                    if subdomain not in self.subdomains:
                        self.subdomains.append(subdomain)
        return self.subdomains  
            
    def __del__(self):
        pass


# Dictionary to store live subdomains and their IPs 
subdomains_ips = {}
# Check if subdomain is alive. Return 1 if alive and 0 otherwise
def check_subdomain(subdomain):
    try:
        socket.gethostbyname(subdomain)
        # add subdomain to the dictionary
        subdomains_ips[subdomain] = socket.gethostbyname(subdomain)
        return 1
    except socket.error:
        print("Error resolving subdomain: ", subdomain)
        return 0

# WHOIS Enumeration 
def whois_enum(domain):
    try:
        w = whois.whois(domain)
        # print the whois information in a well formatted way: 
        print("\033[36m")
        print("Domain Name: ", w.domain_name)
        print("Registrar: ", w.registrar)
        # convert the list of datetime objects to strings
        w.creation_date = [str(date) for date in w.creation_date]
        print("Creation Date: ", w.creation_date)
        w.expiration_date = [str(date) for date in w.expiration_date]
        print("Expiration Date: ", w.expiration_date)
        w.updated_date = [str(date) for date in w.updated_date]
        print("Updated Date: ", w.updated_date)
        print("Name Servers: ", w.name_servers)
        print("Emails: ", w.emails)
        print("Name: ", w.name)
        print("Organization: ", w.org)
        print("Address: ", w.address)
        print("City: ", w.city)
        print("State: ", w.state)
        print("Zipcode: ", w.zipcode)
        print("Country: ", w.country)
        print("Name: ", w.name)
        print("Phone: ", w.phone)

    except Exception as e:
        print("Error fetching whois information: ", e) 
if __name__ == '__main__':
    
    ### TASK 2 ###
    

    # color the print statements in blue 
    print("\033[94m")    
    domain = input("Enter a domain: ")
    
    crt_subdomains = CrtSubdomains(domain)
    list_crt = crt_subdomains.get_subdomains_json()
    #list_crt = crt_subdomains.get_subdomains()
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
    print("Whois enumeration for the domain: ")
    
    print("Domain: ", domain)
    whois_enum(domain)
    print("\033[91m")
    
    
    ### END OF TASK 2 ###
    
    
    
    

    