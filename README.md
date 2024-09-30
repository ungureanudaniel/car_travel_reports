# CSV to PDF Report Generator

## Description
This application processes CSV files containing vehicle data and generates PDF reports. It extracts key information such as vehicle title, start date, end date, and fuel consumption, compiling this data into a well-structured PDF document.

## Features
- **CSV File Input**: Select and read CSV files containing vehicle data.
- **Dynamic Column Deletion**: Allows users to specify which columns to exclude from the report.
- **Fuel Difference Calculation**: Inserts the remaining fuel difference into the report.
- **Customizable PDF Output**: Generates a PDF with a custom title, fuel information, and formatted table.
- **Supports Romanian Diacritics**: Correctly displays Romanian characters in the generated PDF.

## Requirements
- Docker
- Docker Compose

## Installation Using Docker Compose
1. Clone this repository or download the code:
   ```bash
   git clone <repo-url>
   cd <repo-directory>
2. Build and run the Docker container:
    ```bash
    docker-compose up --build

## CSV File Format
1. The application expects the CSV file to have a specific format:
Rows 1-25 contain summary data.
Row 26 should contain the header for the main data table.
Rows 27 onward contain the GPS data.

## Contact
For any inquiries or issues, please contact



