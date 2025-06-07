import os
import sys

# --- Configuration ---
# Default directory to scan for files and where _headers will be created.
# This can be overridden by a command-line argument.
# For Cloudflare Pages, if your site output is in a directory like 'public' or 'dist',
# you might run this script from the repo root like: python build.py public
DEFAULT_TARGET_DIRECTORY = "."
HEADERS_FILE_NAME = "_headers"  # Name of the headers file Cloudflare Pages uses.
EXCLUDED_DIRS = {".git"}      # Directories to completely exclude from scanning.
# Add other directories like 'node_modules' if needed: {".git", "node_modules"}

def generate_headers_content(target_dir):
    """
    Scans the target_dir, identifies non-HTML files, and generates
    the content for the _headers file.
    Specified directories (like .git) and this build script itself (if inside target_dir) are excluded.

    Args:
        target_dir (str): The directory to scan.

    Returns:
        str: The content for the _headers file.
    """
    headers_rules = []
    script_full_path = os.path.realpath(__file__)
    target_full_path = os.path.realpath(target_dir)

    # Walk through the directory
    for root, dirs, files in os.walk(target_dir, topdown=True):
        # Filter out excluded directories from further traversal
        # To make sure we're comparing apples to apples, normalize paths before comparison.
        dirs[:] = [
            d for d in dirs
            if d not in EXCLUDED_DIRS
        ]

        for file_name in files:
            full_file_path = os.path.join(root, file_name)
            full_file_path_real = os.path.realpath(full_file_path)

            # Skip the build script itself
            if full_file_path_real == script_full_path:
                continue

            # Skip the _headers file itself from being listed
            if file_name == HEADERS_FILE_NAME and os.path.realpath(os.path.dirname(full_file_path)) == target_full_path :
                continue

            # Get the file path relative to the target_dir for URL generation
            relative_file_path = os.path.relpath(full_file_path, target_dir)

            # Ensure URL paths use forward slashes, as expected by web servers and _headers
            url_path = "/" + relative_file_path.replace(os.sep, "/")

            # Get the file extension
            _, file_extension = os.path.splitext(file_name)
            file_extension = file_extension.lower() # Normalize to lowercase

            # Check if the file is not an HTML file
            if file_extension not in [".html", ".htm"]:
                # Add a rule to set Content-Type to text/plain
                rule = (
                    f"{url_path}\n"
                    f"  Content-Type: text/plain"
                )
                headers_rules.append(rule)

    if not headers_rules:
        return "# No custom header rules generated. All files might be HTML, or no applicable files found."
    
    # Join rules with two newlines for better readability in the _headers file
    return "\n\n".join(headers_rules)

def write_headers_file(content, target_dir):
    """
    Writes the generated content to the _headers file in the target_dir.

    Args:
        content (str): The content to write to the _headers file.
        target_dir (str): The directory where _headers file will be created.
    """
    headers_file_path = os.path.join(target_dir, HEADERS_FILE_NAME)
    try:
        with open(headers_file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Successfully created/updated {headers_file_path}")
    except IOError as e:
        print(f"Error writing {headers_file_path}: {e}")
        sys.exit(1) # Exit if we can't write the file

def main():
    """
    Main function to orchestrate the generation and writing of the _headers file.
    The target directory can be specified as a command-line argument.
    """
    # Determine the target directory: use command-line argument if provided, else default.
    if len(sys.argv) > 1:
        target_directory = sys.argv[1]
    else:
        target_directory = DEFAULT_TARGET_DIRECTORY

    # Validate if the target directory exists
    if not os.path.isdir(target_directory):
        print(f"Error: Target directory '{target_directory}' does not exist or is not a directory.")
        print("Please specify a valid directory as a command-line argument or ensure the default directory exists.")
        sys.exit(1) # Exit if the directory is invalid

    print(f"Starting build process to generate {HEADERS_FILE_NAME} in '{os.path.abspath(target_directory)}'...")
    print(f"Scanning directory: {os.path.abspath(target_directory)}")
    print(f"Excluding directories named: {EXCLUDED_DIRS}")
    print(f"Excluding build script: {os.path.basename(__file__)}")

    # Generate the content for the _headers file
    headers_content = generate_headers_content(target_directory)
    
    # Write the content to the _headers file
    write_headers_file(headers_content, target_directory)

    print("Build process finished.")

if __name__ == "__main__":
    # This allows the script to be run directly.
    main()
