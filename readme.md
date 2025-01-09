
# Multi-Domain Product URL Crawler

## Overview

This project is a **Multi-Domain Product URL Crawler** built with FastAPI. It efficiently crawls multiple e-commerce websites to discover and list product URLs. The tool identifies product pages by matching URL patterns such as `/product/`, `/item/`, `/p/`, and others provided by the user.

### Core Features:
- Crawl multiple e-commerce domains concurrently.
- Discover product URLs based on customizable URL patterns.
- Handle large websites efficiently with asynchronous crawling using `aiohttp`.
- Output results in structured JSON files, one per domain.
- Interactive web-based interface for input and live progress tracking.

---

## Key Functionalities

1. **URL Discovery**:
   - Identifies potential product URLs using regex patterns.
   - Filters URLs to ensure they belong to the provided domains.

2. **Scalability**:
   - Asynchronous crawling for parallel execution of multiple domains.
   - Configurable `max_pages` parameter to limit the number of pages crawled.

3. **Customizable Patterns**:
   - Supports user-defined URL patterns to adapt to various website structures.

4. **Output**:
   - Saves discovered product URLs for each domain into structured JSON files.

5. **Interactive UI**:
   - Web-based interface with real-time progress updates via WebSocket.

---

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Dependencies: `aiohttp`, `beautifulsoup4`, `fastapi`, `uvicorn`

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Gya7329/multi-domain-bfs-crawling.git
   cd multi-domain-bfs-crawling
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   python -m uvicorn app:app --reload
   ```

4. Access the application:
   - Open your browser and navigate to `http://127.0.0.1:8000`.

---

## Usage

1. **Enter Domains**:
   - Input a list of domains (comma-separated).
   - Example: `flipkart.com, amazon.in , meesho.com`

2. **Set Parameters**:
   - `Max Pages`: Limit the number of pages to crawl.
   - `Custom Patterns`: Provide additional URL patterns to identify product pages.

3. **Start Crawl**:
   - Click "Start Crawl" to initiate the process.
   - The progress and discovered URLs will be displayed in real-time.

4. **Output**:
   - Discovered product URLs are saved in JSON files (`<domain>_products.json`).

---

## Example

### Input
- Domains: `flipkart.com, amazon.in`
- Max Pages: `50`
- Patterns: `/product/, /item/`

### Output
#### `flipkart.com_products.json`
```json
[
  "https://www.flipkart.com/product/12345",
  "https://www.flipkart.com/item/67890"
]
```

#### `amazon.in_products.json`
```json
[
  "https://www.amazon.in/product/abcde",
  "https://www.amazon.in/item/fghij"
]
```

---

## File Structure

```
.
├── app.py                # Main application code
├── README.md             # Documentation
├── requirements.txt      # Dependencies
└── outputs/              # Directory for output JSON files
```

---

## Technologies Used

- **FastAPI**: For building the web application and WebSocket endpoint.
- **aiohttp**: For asynchronous HTTP requests.
- **BeautifulSoup**: For HTML parsing and extracting links.
- **Uvicorn**: ASGI server to run the application.

---





### Steps to Finalize

1. Save this content in a `README.md` file in your project directory.
2. Create a `requirements.txt` file with the following content:
   ```plaintext
   fastapi
   uvicorn
   aiohttp
   beautifulsoup4
   ```
3. Create a sample `outputs/` directory to store JSON files.

