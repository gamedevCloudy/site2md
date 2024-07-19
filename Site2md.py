from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import os
import time
from urllib.parse import urljoin, urlparse
from urllib.parse import urlparse, urljoin, urldefrag

class Site2MD:

    def site_2_md(self, site: str, dir_name: str):
        driver = self.setup_driver()
        if not driver:
            print("Failed to set up a web driver. Exiting.")
            return

        start_url = site
        urls = self.get_all_urls(start_url, driver)

        os.makedirs(dir_name, exist_ok=True)

        for i, url in enumerate(urls):
            try:
                text = self.get_page_text(url, driver)
                filename = f"{dir_name}/page_{i+1}.md"
                self.save_as_markdown(text, filename)

                print(f"Saved {url} as {filename}")
            except Exception as e:
                print(f"Error processing {url}: \n {str(e)}")

            time.sleep(2)

        driver.quit()

    def setup_driver(self):
        try:
            firefox_options = FirefoxOptions()
            firefox_options.add_argument('--headless')

            return webdriver.Firefox(options=firefox_options)

        except Exception as e:
            print(f"Failed to get Firefox: {str(e)}")

            try:
                chrome_options = ChromeOptions()
                chrome_options.add_argument('--headless')

                return webdriver.Chrome(options=chrome_options)

            except Exception as e:
                print(f"Couldn't get Chrome running: {str(e)}")

                return None

    def get_all_urls(self, start_url, driver):
        driver.get(start_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        domain = urlparse(start_url).netloc
        urls_to_visit = set([start_url])
        visited_urls = set()
        
        def normalize_url(url):
            # Remove query parameters and fragments
            parsed = urlparse(url)
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            return clean_url

        while urls_to_visit:
            current_url = urls_to_visit.pop()
            current_url = normalize_url(current_url)
            if current_url not in visited_urls:
                try:
                    driver.get(current_url)
                    visited_urls.add(current_url)
                    print(f"Processed: {current_url}")
                    
                    links = driver.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        href = link.get_attribute('href')
                        if href and not href.startswith('mailto:'):
                            parsed_href = urlparse(href)
                            if parsed_href.netloc == domain or not parsed_href.netloc:
                                full_url = normalize_url(urljoin(start_url, href))
                                if full_url not in visited_urls and full_url not in urls_to_visit:
                                    urls_to_visit.add(full_url)
                                    print(f"Added to queue: {full_url}")
                except Exception as e:
                    print(f"Error processing {current_url}: {str(e)}")
                
                time.sleep(1)
        
        return list(visited_urls)

    def get_page_text(self, url, driver):
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')
        text = soup.get_text(separator="\n", strip=True)

        return text

    @staticmethod
    def save_as_markdown(text, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)


if __name__ == "__main__":
    url = "https://mokobara.com/"
    dir_name = "mokobara"

    site2md = Site2MD()
    site2md.site_2_md(url, dir_name)