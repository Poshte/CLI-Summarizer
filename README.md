# Claude CLI Summarizer

A command-line tool built with Python that uses Anthropic's Claude API (Haiku) to generate bulleted summaries of text files. It includes a custom usage logger that tracks token consumption and estimates API costs locally.

## Features

* **Quick Summarization:** Pass any local text file via the CLI to get a concise, bulleted summary.
* **Cost & Token Tracking:** Automatically logs input/output tokens and calculates estimated USD costs per run, appending them to a `usage_log.jsonl` file.
* **Safe Parsing:** Handles Claude's extended thinking blocks and automatically filters for final text output.
* **Cost Reporting:** Generates a cumulative usage report at the end of every run.

## Prerequisites

* Python 3.7+
* An [Anthropic API Key](https://console.anthropic.com/)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/claude-cli-summarizer.git
   cd claude-cli-summarizer
   ```

2. **Install dependencies:**
   ```bash
   pip install anthropic python-dotenv
   ```

3. **Set up your API Key:**
   Create a `.env` file in the root directory and add your Anthropic API key:
   ```text
   ANTHROPIC_API_KEY=your_actual_api_key_here
   ```
   *(Note: `.env` is included in `.gitignore` to prevent leaking your key).*
   *(You may use .env.example as an example of how to set up your key. Never paste your key in this file, it is tracked by git.).*

## Usage

Run the script from your terminal, passing the path to the text file you want to summarize:

```bash
python main.py path/to/your/file.txt
```

### Example Output

```text
Sending 'article.txt' to Claude...

--- SUMMARY ---
* Point 1 from the text.
* Point 2 from the text.
* Point 3 from the text.

--- USAGE REPORT ---
claude-haiku-5-5: 1 calls, 7,301 in, 500 out, ~$0.0010
TOTAL: ~$0.0010
```

## Files

* `main.py`: The CLI script that handles file reading and orchestrates information between API calls and logging.
* `summarizer.py`: Contains the core logic for communicating with the Claude API and handling the response blocks.
* `usage_logger.py`: A reusable, framework-agnostic class that calculates costs and logs token usage.
* `usage_log.jsonl`: Generated automatically after your first run to store local telemetry.
