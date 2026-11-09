import sys
import anthropic
import time
import argparse
from pathlib import Path
from dotenv import load_dotenv
from UsageLogger import UsageLogger

load_dotenv()
logger = UsageLogger()

def summarize(text: str) -> str:
    client = anthropic.Anthropic()
    start_time = time.time()

    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=500,
        system="You summarize documents. Reply with a concise bulleted summary only.",
        messages=[
            {
                "role": "user",
                "content": f"<document>\n{text}\n</document>"}
        ],
    )

    latency = time.time() - start_time

    # 2. Log the execution
    logger.log(
        model="claude-haiku-5-5",  # Hardcoded to match your dict key
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        latency_s=latency,
        action="summarize_file",
        # You can pass any **extra args here
    )

    # 3. Return the generated text
    summary_text = "".join(
        block.text for block in response.content if block.type == "text"
    )

    return summary_text

if __name__ == "__main__":
    # 1. Set up command-line arguments
    parser = argparse.ArgumentParser(description="Summarize a text file using Claude Haiku.")
    parser.add_argument("filepath", help="Path to the text file to summarize")
    args = parser.parse_args()

    file_path = Path(args.filepath)

    # 2. Validate the file exists
    if not file_path.is_file():
        print(f"Error: Could not find file at '{file_path}'")
        sys.exit(1)

    # 3. Read the file into a string
    try:
        text_content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print("Error: File must be plain text (UTF-8 encoded).")
        sys.exit(1)

    print(f"Sending '{file_path.name}' to Claude...\n")

    # 4. Generate the summary
    try:
        summary = summarize(text_content)

        print("--- SUMMARY ---")
        print(summary)

        # Print your custom logger report to see the cost
        print("\n--- USAGE REPORT ---")
        print(logger.report())

    except Exception as e:
        print(f"API Error: {e}")
        sys.exit(1)