import sys
import argparse
from pathlib import Path
from summarizer import summarize
from usage_logger import UsageLogger

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

    logger = UsageLogger()

    # 4. Generate the summary
    try:
        summary = summarize(text_content, logger)

        print("--- SUMMARY ---")
        print(summary)

        # Print your custom logger report to see the cost
        print("\n--- USAGE REPORT ---")
        print(logger.report())

    except Exception as e:
        print(f"API Error: {e}")
        sys.exit(1)