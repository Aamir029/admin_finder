import os
import requests
from concurrent.futures import ThreadPoolExecutor

def load_admin_paths(file_path):
    """Load admin panel paths from the provided file"""
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

def check_admin_panel(base_url, path):
    """Check if an admin panel exists at the given path"""
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    try:
        response = requests.get(url, timeout=5, allow_redirects=False)
        if response.status_code == 200:
            print(f"[+] Found: {url} (Status: {response.status_code})")
            return url
        elif response.status_code in [301, 302, 303, 307, 308]:
            print(f"[?] Potential redirect: {url} (Status: {response.status_code})")
            return f"Redirect: {url}"
        return None
    except requests.RequestException:
        return None

def find_admin_panels(base_url, admin_paths, max_workers=20):
    """Find admin panels by testing multiple paths"""
    found_panels = []
    
    print(f"\n[*] Starting admin panel scan for: {base_url}")
    print(f"[*] Testing {len(admin_paths)} possible admin paths...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for path in admin_paths:
            futures.append(executor.submit(check_admin_panel, base_url, path))
        
        for future in futures:
            result = future.result()
            if result:
                found_panels.append(result)
    
    print("\n[*] Scan completed!")
    if found_panels:
        print("[+] Found admin panels/redirects:")
        for panel in found_panels:
            print(f"  - {panel}")
    else:
        print("[-] No admin panels found")
    
    return found_panels

def get_user_input():
   
    print("""
  ___       _           _   _____       _     _           
 / _ \     | |         (_) /  __ \     | |   (_)          
/ /_\ \  __| |_ __ ___  _  | /  \/ __ _| |__  _ _ __ ___  
|  _  | / _` | '_ ` _ \| | | |    / _` | '_ \| | '_ ` _ \ 
| | | | (_| | | | | | | | | \__/\ (_| | |_) | | | | | | |
\_| |_/\__,_|_| |_| |_|_|  \____/\__,_|_.__/|_|_| |_| |_| V1.0

Author : Aamir 
                                                          
""")
    
    # Get target URL
    while True:
        base_url = input("\nEnter target URL (e.g., http://example.com): ").strip()
        if base_url.startswith(('http://', 'https://')):
            break
        print("Please enter a valid URL starting with http:// or https://")
    
    # Get wordlist path
    while True:
        wordlist_path = input("\nEnter path to admin paths wordlist [Press Enter for default 'link.txt']: ").strip()
        if not wordlist_path:
            wordlist_path = 'link.txt'
        if os.path.isfile(wordlist_path):
            break
        print(f"Error: File '{wordlist_path}' not found. Please try again.")
    
    # Get thread count
    while True:
        threads = input("\nEnter number of threads to use [10-50, default 20]: ").strip()
        if not threads:
            threads = 20
            break
        try:
            threads = int(threads)
            if 10 <= threads <= 50:
                break
            print("Please enter a number between 10 and 50")
        except ValueError:
            print("Please enter a valid number")
    
    return base_url, wordlist_path, threads

def main():
    base_url, wordlist_path, threads = get_user_input()
    admin_paths = load_admin_paths(wordlist_path)
    find_admin_panels(base_url, admin_paths, threads)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user")
    except Exception as e:
        print(f"\n[!] An error occurred: {str(e)}")
