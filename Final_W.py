import requests
from bs4 import BeautifulSoup
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st
import pandas as pd

# Streamlit caching for loading data
@st.cache_data
def load_data(file_name):
    return pd.read_csv(file_name)

# Scrape a single page
def scrape_page(page_number):
    print(f"Scraping page {page_number}")  # Debugging statement
    url = f'https://dealsheaven.in?page={page_number}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    deals_data = []
    deals = soup.find_all('div', class_='deatls-inner')

    for deal in deals:
        try:
            title = deal.find('h3').text.strip()
            price = deal.find('p', class_='price').text.strip()
            special_price_tag = deal.find('p', class_='spacail-price')
            special_price = special_price_tag.text.strip() if special_price_tag else "N/A"
            link_tag = deal.find('a', href=True)
            link = link_tag['href'] if link_tag else "N/A"
            site = deal.find('div', class_='esite-logo').find('img')['title'] if deal.find('div', class_='esite-logo') else "N/A"
            
            deals_data.append([title, price, special_price, link, site])

        except Exception as e:
            print(f"Error processing deal: {e}")

    return deals_data

# Scrape pages concurrently and save to a unique CSV file
def scrape_deals_concurrently(start_page, end_page):
    # Create a unique CSV filename based on the page range
    file_name = f'deals_{start_page}to{end_page}.csv'
    
    # Write the header for the CSV file
    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Price", "Special Price", "Link", "Site"])

    # Collect data concurrently
    all_deals = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(scrape_page, page): page for page in range(start_page, end_page + 1)}
        
        for future in as_completed(futures):
            page_number = futures[future]
            try:
                page_data = future.result()
                all_deals.extend(page_data)
                print(f"Completed scraping page {page_number}")  # Debugging statement
            except Exception as e:
                print(f"Error on page {page_number}: {e}")
    
    # Write all data to the CSV file after scraping
    with open(file_name, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(all_deals)
    
    return file_name

# Streamlit front end
def main():
    st.title("Deals Dashboard")
    st.write("Choose a page range to scrape data and select a site to view.")

    # Take page range input
    start_page = st.number_input("Start Page", min_value=1, max_value=500, value=1)
    end_page = st.number_input("End Page", min_value=1, max_value=500, value=5)
    
    if st.button("Scrape and Display"):
        if start_page > end_page:
            st.error("Start page must be less than or equal to end page.")
        else:
            # Scrape data and get the CSV filename
            file_name = scrape_deals_concurrently(start_page, end_page)
            data = load_data(file_name)
            data = data.sort_values(by="Site")  # Sort by Site for easier selection

            # Get unique site names for the dropdown
            site_names = data['Site'].unique()
            selected_site = st.selectbox("Select a site", site_names)

            # Filter data for the selected site
            if selected_site:
                site_data = data[data['Site'] == selected_site]
                st.write(f"**Deals for site: {selected_site}**")
                st.dataframe(site_data)

if __name__ == '__main__':
    main()
