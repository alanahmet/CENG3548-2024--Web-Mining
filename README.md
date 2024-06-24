# Product Comparison Scraper

This script extracts product information and reviews from Trendyol for comparing two products.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/alanahmet/CENG3548-2024-Web-Mining.git
   cd CENG3548-2024-Web-Mining
   ```

2. Set up a virtual environment using Poetry:
   ```bash
   poetry install
   ```

   If Poetry is not installed, you can install it using:
   ```bash
   pip install poetry
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

4. Run the script:
   ```bash
   python product_comparison.py
   ```

## Description

This Python script fetches detailed information and reviews for two products from Trendyol. It uses web scraping techniques to gather:
- Product descriptions
- Product attributes
- Customer reviews

The script then creates a comparison template with information on both products to assist users in making an informed decision.

## Requirements

- Python 3.x
- Poetry (for dependency management)
- Requests library (`pip install requests`)

## Usage

1. Define product links in the `product_links` list within the script. Each sublist should contain two product URLs.

2. Execute the script. It will scrape and compare the specified products.

3. The output will be saved as `product_info_map.json`, containing scraped data and a comparison template.

## Example

An example of how to use the script:
```python
python product_comparison.py
```

## Output

The script outputs a JSON file (`product_info_map.json`) containing:
- Comments and details for each product
- A comparison template for ai to help users decide between the products