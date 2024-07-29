import tkinter as tk
from tkinter import ttk
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
def scrape_linkedin_jobs(keyword, location, num_pages=1):
    driver = webdriver.Chrome()  

    search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location={location}"
    driver.get(search_url)

    job_listings = []

    for page in range(num_pages):
        time.sleep(5)  

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_cards = soup.find_all('a', class_='result-card__full-card-link')

        for card in job_cards:
            try:
                job_title = card.find('h3', class_='result-card__title').get_text(strip=True)
                company_name = card.find('h4', class_='result-card__subtitle').get_text(strip=True)
                location = card.find('span', class_='job-result-card__location').get_text(strip=True)
                job_url = card['href']

                job_listings.append({
                    'Job Title': job_title,
                    'Company Name': company_name,
                    'Location': location,
                    'Job URL': job_url
                })
            except Exception as e:
                print(f"Error scraping job card: {e}")

        try:
            next_button = driver.find_element(By.CLASS_NAME, 'artdeco-pagination__button--next')
            next_button.click()
        except:
            print("No more pages or pagination button not found.")
            break

    driver.quit()
    return pd.DataFrame(job_listings)

# Example scraping usage
# Adjust the parameters as needed
df = scrape_linkedin_jobs('Data Scientist', 'San Francisco', num_pages=2)
df.to_csv('linkedin_jobs.csv', index=False)

# 2. Data Cleaning Function
def clean_data(csv_file):
    df = pd.read_csv(csv_file)

    # Drop duplicates based on Job URL
    df.drop_duplicates(subset=['Job URL'], inplace=True)

    # Additional cleaning steps
    df['Job Title'] = df['Job Title'].str.strip()
    df['Company Name'] = df['Company Name'].str.strip()
    df['Location'] = df['Location'].str.strip()

    # Save cleaned data to a new CSV
    df.to_csv('cleaned_linkedin_jobs.csv', index=False)

    return df

# Clean the scraped data
cleaned_df = clean_data('linkedin_jobs.csv')

# 3. Tkinter Dashboard
class JobDashboard(tk.Tk):
    def __init__(self, csv_file):
        super().__init__()
        self.title("Job Dashboard")
        self.geometry("900x600")

        self.data_frame = pd.read_csv(csv_file)
        self.filtered_df = self.data_frame.copy()  # For holding filtered data
        self.create_widgets()

    def create_widgets(self):
        # Create a frame for the Treeview
        frame = tk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True)

        # Create Treeview to display data
        self.tree = ttk.Treeview(frame)
        self.tree['columns'] = list(self.data_frame.columns)
        
        # Define columns and headings
        for col in self.data_frame.columns:
            self.tree.column(col, width=150, anchor='center')
            self.tree.heading(col, text=col)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add data to Treeview
        self.populate_treeview(self.data_frame)
        self.tree.pack(expand=True, fill='both')
        
        # Add Search Bar
        self.search_label = tk.Label(self, text="Search:")
        self.search_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.search_entry = tk.Entry(self)
        self.search_entry.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.search_button = tk.Button(self, text="Search", command=self.search_data)
        self.search_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Add Reset Button
        self.reset_button = tk.Button(self, text="Reset", command=self.reset_data)
        self.reset_button.pack(side=tk.LEFT, padx=10, pady=10)

    def populate_treeview(self, data):
        # Clear the current Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add new data to Treeview
        for index, row in data.iterrows():
            self.tree.insert("", "end", values=list(row))

    def search_data(self):
        query = self.search_entry.get().lower()
        filtered_df = self.data_frame[self.data_frame.apply(lambda row: query in row.astype(str).str.lower().to_string(), axis=1)]
        
        self.filtered_df = filtered_df
        self.populate_treeview(filtered_df)

    def reset_data(self):
        self.populate_treeview(self.data_frame)
        self.filtered_df = self.data_frame.copy()
        self.search_entry.delete(0, tk.END)

# Create and run the dashboard
app = JobDashboard('cleaned_linkedin_jobs.csv')
app.mainloop()
