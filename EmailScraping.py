import re
import urllib.request
import csv
import time
import os

emailRegex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

def is_valid_email(email):
    # Exclude email-like strings that are not valid emails
    excluded_patterns = [r'\b\w+\.\w+\b']  # Exclude patterns like ".com", "test.com"
    for pattern in excluded_patterns:
        if re.match(pattern, email):
            return False
    return True

def extractEmailsFromUrlText(url, urlText, writer):
    extractedEmail = emailRegex.findall(urlText)
    for email in extractedEmail:
        if is_valid_email(email):
            writer.writerow([url, email])

def htmlPageRead(url, i, writer, success_urls):
    try:
        start = time.time()
        headers = {'User-Agent': 'Mozilla/5.0'}
        request = urllib.request.Request(url, None, headers)
        response = urllib.request.urlopen(request)
        urlHtmlPageRead = response.read()
        urlText = urlHtmlPageRead.decode(errors='ignore') # Ignore decoding errors
        print("%s.%s\tFetched in : %s" % (i, url, (time.time() - start)))
        extractEmailsFromUrlText(url, urlText, writer)
        success_urls.append(url)
    except Exception as e:
        print("Error fetching or processing URL:", e)

def move_successful_urls(success_urls):
    with open("already_scraped_urls.txt", 'a') as f:
        for url in success_urls:
            f.write(url + '\n')

def emailsLeechFunc(url, i, writer, success_urls):
    try:
        htmlPageRead(url, i, writer, success_urls)
    except urllib.error.HTTPError as err:
        if err.code == 404:
            try:
                url = 'http://webcache.googleusercontent.com/search?q=cache:' + url
                htmlPageRead(url, i, writer, success_urls)
            except Exception as e:
                print("Error fetching or processing cached URL:", e)
        else:
            print("HTTP Error:", err)

start = time.time()
success_urls = []
urls_to_process = []

# Read URLs from output_urls.txt
print("Reading URLs from output_urls.txt")
with open("output_urls.txt", 'r') as urlFile:
    for urlLink in urlFile.readlines():
        urls_to_process.append(urlLink.strip('\'"'))

with open("emails.csv", 'a', newline='', encoding='utf-8') as emailFile:
    writer = csv.writer(emailFile)
    i = 0
    for url in urls_to_process:
        i += 1
        print(f"Processing URL {i}: {url}")
        emailsLeechFunc(url, i, writer, success_urls)
    print("Elapsed Time: %s" % (time.time() - start))

print("Moving successfully scraped URLs to already_scraped_urls.txt")
move_successful_urls(success_urls)

# Remove successfully scraped URLs from output_urls.txt
remaining_urls = set(urls_to_process) - set(success_urls)
print("Updating output_urls.txt with remaining URLs")
with open("output_urls.txt", 'w') as f:
    for url in remaining_urls:
        f.write(url + '\n')
