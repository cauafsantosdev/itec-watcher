# Scientific Initiation Opportunities Monitor - iTec FURG

This project is an automation tool (web scraper) developed to daily monitor the call for proposals page of iTec-FURG. The primary objective is to identify new Scientific Initiation (IC) scholarship opportunities as soon as they are published.

---

## Overview

The system operates autonomously using GitHub Actions infrastructure. It scans the target page at pre-defined intervals, compares the results with a local history, and notifies the user via GitHub Issues if a new opportunity matching the filter criteria is found.

---

## Key Features

* **Continuous Monitoring:** Automatic daily execution via cron jobs.
* **Smart Filtering:** Uses keywords to specifically identify "Scientific Initiation" opportunities, ignoring other types of announcements.
* **Data Persistence:** Maintains a history of previously seen links in a JSON file, preventing duplicate notifications.
* **Integrated Notifications:** Automatically creates an Issue in the repository with the link and title of the detected opportunity, triggering an email alert to the owner.
* **Zero Cost:** Serverless architecture based entirely on the GitHub Actions free tier.

---

## Technologies Used

* **Language:** Python 3.10
* **Libraries:**
  * `requests`: For HTTP requests.
  * `beautifulsoup4`: For HTML parsing and data extraction.
  * `json`: For file-based database management.
* **Infrastructure:** GitHub Actions (CI/CD).

---

## Project Architecture

The execution flow follows these steps:

1. **Initialization:** The GitHub Actions workflow is triggered by the schedule (cron) or manually.
2. **Request:** The Python script accesses the target URL (`https://itecfurg.org/?page_id=2695`).
3. **Parsing:** The HTML content is processed to extract all available announcement links.
4. **Verification:**
   * The system loads the `seen_opportunities.json` file (history).
   * It compares the extracted links against the history.
   * It checks if the new links contain keywords such as "Iniciação Científica" or "IC".
5. **Action:**
   * If a new and relevant opportunity is found: An Issue is created in the repository.
   * If it is the first execution: It populates the database without notifying.
6. **Persistence:** The system updates the `seen_opportunities.json` file and commits the changes back to the repository.

---

## How to Run Locally

To run the script on your local machine for testing or development purposes:

1. Clone the repository:

   ```bash
   git clone https://github.com/cauafsantosdev/itec-watcher.git
   cd itec-watcher
   ```
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Run the script:

   ```bash
   python main.py
   ```

---

## GitHub Configuration

For the automation to function correctly on GitHub Actions, repository permissions must be adjusted:

1. Go to the repository **Settings** tab.
2. Select **Actions** > **General** from the sidebar menu.
3. Under **Workflow permissions**, select **Read and write permissions**.
4. Save the changes.

This allows the bot to update the JSON file and create Issues automatically.
