Facebook Keyword Scraper with Timestamp Support

This project automates the collection of fraud-related posts from Facebook, featuring an enhanced timestamp-based data extraction process. The script uses token-based requests, manages dynamic web content, and stores extracted data with detailed timestamps for further analysis.

Table of Contents
	1.	Project Overview
	2.	Features
	3.	Installation
	4.	Usage
	5.	File Descriptions
	6.	Data and Privacy Disclaimer
	7.	Acknowledgments

Project Overview

This project targets fraud-related public content on Facebook by extracting posts based on specific keywords. It extends a prior scraping model by adding timestamp management, enabling time-sensitive data collection and analysis.

Features
	•	Timestamped Data Collection: Extracts posts with accurate timestamps.
	•	Automated Request Management: Uses requests with dynamic headers and tokens.
	•	Error Handling and Retry Logic: Built-in retrying mechanism to handle failed requests.
	•	Data Storage: Saves extracted data in CSV format.

Installation

Prerequisites:
	•	Python 3.x
	•	Libraries:

pip install requests pandas retrying

Usage
	1.	Clone the Repository:

git clone https://github.com/your-repo/facebook-keyword-scraper.git
cd facebook-keyword-scraper


	2.	Run the Script:

python succeed_2_timestamp.py


	3.	Data Output:
	•	Extracted data is saved as CSV files with timestamped filenames in the /data directory.

File Descriptions
	1.	succeed_2_timestamp.py: The main script implementing timestamped data scraping.
	2.	requirements.txt: List of required libraries and versions.
	3.	datasets/: Folder containing cleaned and processed data.
	4.	README.md: Project documentation.

Data and Privacy Disclaimer
	•	This project is intended for research and educational purposes only.
	•	Data Privacy Compliance: Ensure compliance with relevant data privacy laws and Facebook’s terms of service. Unauthorized scraping may lead to account suspension or legal consequences.

Acknowledgments

Special thanks to:
	•	The open-source community for valuable libraries and frameworks.
	•	GitHub contributors for project improvements and feedback.
