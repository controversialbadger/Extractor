# Email Extractor

A professional email extraction tool that extracts email addresses from websites. The tool first attempts HTTP requests and falls back to Playwright for JavaScript-heavy sites.

## Features

- Extracts emails from homepage and up to 5 contact pages
- Intelligent contact page discovery supporting all EU languages
- Handles various email obfuscation techniques
- Cookie consent and anti-bot protection
- Timeout mechanisms to prevent freezing
- Saves extracted emails to `output.txt`

## Requirements

- Python 3.7+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:

```bash
python -m playwright install
```

## Usage

Run the main script:

```bash
python main.py
```

The script will prompt you to enter URLs one by one. For each URL, it will:

1. Attempt to extract emails using HTTP requests
2. If no emails are found, it will use Playwright as a fallback
3. Save any found emails to `output.txt`

To exit the program, type `exit`, `quit`, or `q`, or press Ctrl+C.

## Project Structure

- `main.py`: Main script - handles input, orchestration, output
- `extractor.py`: Core email extraction logic
- `crawler.py`: Contact page discovery logic
- `http_handler.py`: Handles HTTP requests
- `playwright_handler.py`: Handles Playwright interactions
- `utils.py`: Utility functions
- `config.py`: Configuration settings

## Configuration

You can modify the settings in `config.py` to adjust:

- Timeouts
- User agents
- Crawler parameters
- Playwright settings
- Output file path

## License

MIT