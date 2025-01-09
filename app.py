from fastapi import FastAPI, WebSocket, Query, BackgroundTasks
from fastapi.responses import HTMLResponse
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import json
from collections import deque
import os

app = FastAPI()

DEFAULT_PRODUCT_PATTERNS = [
    r'/product/',
    r'/item/',
    r'/p/'
]

def is_valid_domain(domain):
    return re.match(r'^https?://', domain) or re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain)

def might_be_product_url(url, patterns):
    for pattern in patterns:
        if re.search(pattern, url):
            return True
    return False

async def fetch_page(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                return await response.text()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
    return None

async def crawl_domain(domain, websocket: WebSocket, max_pages, product_patterns):
    visited = set()
    product_urls = set()
    queue = deque([domain])

    async with aiohttp.ClientSession() as session:
        while queue and len(visited) < max_pages:
            current_url = queue.popleft()
            if current_url in visited:
                continue
            visited.add(current_url)

            html_content = await fetch_page(session, current_url)
            if not html_content:
                continue

            soup = BeautifulSoup(html_content, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(current_url, href)

                if urlparse(absolute_url).netloc != urlparse(domain).netloc:
                    continue

                if might_be_product_url(absolute_url, product_patterns):
                    if absolute_url not in product_urls:
                        product_urls.add(absolute_url)
                        await websocket.send_text(f"{domain}: {absolute_url}")

                if absolute_url not in visited:
                    queue.append(absolute_url)

    # Save results to a file
    if not os.path.exists('outputs'):
        os.makedirs('outputs')
    with open(f"outputs/{urlparse(domain).netloc}_products.json", "w") as f:
        json.dump(list(product_urls), f, indent=2)

    # Send summary after completing the crawl for the domain
    await websocket.send_text(f"Summary: {domain} - Total links crawled: {len(product_urls)}")

@app.get("/")
async def get():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Multi-Domain Crawler</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f9;
            }
            header {
                background: #6200ea;
                color: #fff;
                padding: 10px 20px;
                text-align: center;
            }
            main {
                padding: 20px;
            }
            form {
                margin-bottom: 20px;
            }
            input, button {
                padding: 10px;
                margin: 5px;
                font-size: 16px;
            }
            button {
                background: #6200ea;
                color: #fff;
                border: none;
                cursor: pointer;
            }
            button:hover {
                background: #3700b3;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            li {
                background: #fff;
                margin: 5px 0;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Multi-Domain Product URL Crawler</h1>
        </header>
        <main>
            <form id="domain-form">
                <label for="domains">Enter Domains (comma-separated):</label>
                <input type="text" id="domains" name="domains" required>
                <label for="max_pages">Max Pages:</label>
                <input type="number" id="max_pages" name="max_pages" value="100" required>
                <label for="patterns">Custom Patterns (comma-separated):</label>
                <input type="text" id="patterns" name="patterns" placeholder="/product/, /item/">
                <button type="submit">Start Crawl</button>
            </form>
            <h2>Product URLs</h2>
            <ul id="results"></ul>
        </main>
        <script>
            const form = document.getElementById('domain-form');
            const resultsList = document.getElementById('results');

            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const domainsInput = document.getElementById('domains').value;
                const maxPages = document.getElementById('max_pages').value;
                const patternsInput = document.getElementById('patterns').value;
                const domains = domainsInput.split(',').map(d => d.trim());
                const patterns = patternsInput.split(',').map(p => p.trim());
                resultsList.innerHTML = ''; // Clear previous results

                const domain = window.location.protocol === "https:" ? "wss://multi-domain-bfs-crawling.onrender.com" : "ws://localhost:8000";
                const ws = new WebSocket(`${domain}/ws?domains=${JSON.stringify(domains)}&max_pages=${maxPages}&patterns=${JSON.stringify(patterns)}`);
                ws.onmessage = (event) => {
                    const li = document.createElement('li');
                    li.textContent = event.data;
                    resultsList.appendChild(li);
                };
                ws.onclose = () => {
                    const li = document.createElement('li');
                    li.textContent = 'Crawling complete. Results saved to file.';
                    resultsList.appendChild(li);
                };
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

def normalize_domain(domain):
    """Ensure the domain has a valid scheme (http or https)."""
    if not domain.startswith(("http://", "https://")):
        domain = f"https://{domain}"
    return domain

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, 
    domains: str = Query(...), 
    max_pages: int = Query(100), 
    patterns: str = Query(None)
):
    await websocket.accept()
    domains_list = json.loads(domains)
    product_patterns = json.loads(patterns) if patterns else DEFAULT_PRODUCT_PATTERNS

    # Normalize domains
    normalized_domains = [normalize_domain(domain) for domain in domains_list if is_valid_domain(domain)]

    if not normalized_domains:
        await websocket.send_text("No valid domains provided.")
        await websocket.close()
        return

    tasks = [
        crawl_domain(domain, websocket, max_pages, product_patterns) 
        for domain in normalized_domains
    ]
    await asyncio.gather(*tasks)
    await websocket.close()
