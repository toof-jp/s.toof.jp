import os
import sys
import datetime # For adding a timestamp to the generated index.html

# --- Configuration ---
# Default directory to scan for files and where _headers and index.html files will be created.
# This can be overridden by a command-line argument.
DEFAULT_TARGET_DIRECTORY = "."
HEADERS_FILE_NAME = "_headers"  # Name of the headers file Cloudflare Pages uses.
INDEX_HTML_FILENAME = "index.html" # Name of the HTML file to generate in each directory.
# Files with these names will be treated as HTML documents for Content-Type in _headers.
HTML_DOCUMENT_FILENAMES = {INDEX_HTML_FILENAME, "index.htm"}
# Directories to completely exclude from scanning, index generation, and _headers rules.
EXCLUDED_DIRS = {".git", "node_modules"} # Add more like "venv", ".vscode" if needed.
# Files/Dirs to exclude from the generated index.html listing specifically (relative to the dir they are in).
# The build script itself should also be excluded from listing if it's inside the target_dir.
EXCLUDED_FROM_INDEX_LISTING = {HEADERS_FILE_NAME, INDEX_HTML_FILENAME, os.path.basename(__file__)}

def generate_index_html_for_directory(current_dir_path, root_output_dir):
    """
    Generates an index.html file for the given current_dir_path, listing its contents.
    Links are relative to the current directory. Breadcrumbs link to parent index.html files.
    """
    items = []
    script_basename = os.path.basename(__file__) # To exclude script from listing if present

    try:
        entries = os.listdir(current_dir_path)
    except OSError as e:
        print(f"Warning: Could not list directory {current_dir_path}: {e}. Skipping index.html generation for it.")
        return

    # Sort entries for consistent ordering: directories first, then files
    dirs_in_current = sorted([
        d for d in entries
        if os.path.isdir(os.path.join(current_dir_path, d)) and d not in EXCLUDED_DIRS
    ])
    files_in_current = sorted([
        f for f in entries
        if os.path.isfile(os.path.join(current_dir_path, f))
    ])

    # Add sub-directories to the list
    for name in dirs_in_current:
        # EXCLUDED_FROM_INDEX_LISTING is usually for files, EXCLUDED_DIRS handles directory exclusion.
        items.append(f'<li><a href="{name}/">{name}/</a></li>') # Link to subdir's index.html

    # Add files to the list
    for name in files_in_current:
        # Exclude items specified, and the build script itself if it's in this directory
        if name in EXCLUDED_FROM_INDEX_LISTING or \
           (os.path.join(current_dir_path, name) == os.path.join(root_output_dir, script_basename) and current_dir_path == root_output_dir) : # more precise script check
            continue
        items.append(f'<li><a href="{name}">{name}</a></li>')

    # Construct HTML content
    relative_path_from_root = os.path.relpath(current_dir_path, root_output_dir)
    if relative_path_from_root == ".":
        display_path_title = "/"
        page_title_suffix = os.path.basename(root_output_dir)
        if not page_title_suffix : page_title_suffix = "Root" # if root_output_dir was "."
    else:
        display_path_title = "/" + relative_path_from_root.replace(os.sep, "/") + "/"
        page_title_suffix = relative_path_from_root.replace(os.sep, "/")


    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Index of {page_title_suffix}</title>
    <style>
        body {{ font-family: sans-serif; margin: 20px; font-size: 16px; }}
        ul {{ list-style-type: none; padding-left: 0; }}
        li {{ margin-bottom: 8px; font-size: 1.1em; }}
        a {{ text-decoration: none; color: #0066cc; }}
        a:hover {{ text-decoration: underline; }}
        h1 {{ color: #333; border-bottom: 1px solid #eee; padding-bottom: 10px;}}
        .breadcrumb {{ margin-bottom: 20px; font-size: 0.9em; }}
        .breadcrumb a, .breadcrumb span {{ color: #555; }}
        .breadcrumb a:hover {{ color: #0066cc; }}
        footer {{ margin-top: 30px; padding-top:10px; border-top: 1px solid #eee; font-size: 0.8em; color: #777; }}
    </style>
</head>
<body>
    <h1>Index of {display_path_title}</h1>
"""
    # Breadcrumbs
    if relative_path_from_root != ".":
        parts = relative_path_from_root.split(os.sep)
        breadcrumb_html = '<p class="breadcrumb"><a href="/毗邻">[root]</a>' # Assuming / will go to root index
        path_accumulator = []
        for i, part_name in enumerate(parts):
            path_accumulator.append(part_name)
            # Link should be relative to current index.html's location
            levels_up = len(parts) - (i + 1)
            link_path = "../" * levels_up
            if not link_path : link_path = "./" # Should not happen for [root] and intermediate parts

            if i < len(parts) - 1: # Not the current directory itself
                 # For breadcrumb to "root/level1" from "root/level1/level2/index.html", link is "../index.html" (or just "../")
                breadcrumb_html += f' / <a href="{link_path}">{part_name}</a>'
            else: # Current directory
                breadcrumb_html += f' / <span>{part_name}</span>'
        breadcrumb_html += '</p>'
        html_content += breadcrumb_html
    else: # Root directory
        html_content += '<p class="breadcrumb"><span>[root]</span></p>'


    if items:
        html_content += f"<ul>\n{'    \n'.join(items)}\n</ul>"
    else:
        html_content += "<p>This directory is empty or contains only excluded items.</p>"

    html_content += f"""
    <footer>
        <p>This index was automatically generated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}.</p>
    </footer>
</body>
</html>
"""
    # Write the index.html file
    index_html_file_path = os.path.join(current_dir_path, INDEX_HTML_FILENAME)
    try:
        with open(index_html_file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
    except IOError as e:
        print(f"Error writing {index_html_file_path}: {e}")


def generate_all_indexes_recursively(current_dir, root_output_dir):
    """
    Recursively generates index.html for current_dir and its subdirectories.
    Ensures that EXCLUDED_DIRS are not processed.
    """
    # First, generate index for the current directory itself (if not excluded)
    if os.path.basename(current_dir) in EXCLUDED_DIRS and current_dir != root_output_dir:
        # Allow processing root if it's accidentally named like an excluded dir, but don't recurse into actual excluded dirs
        return

    print(f"Generating {INDEX_HTML_FILENAME} for ./{os.path.relpath(current_dir, root_output_dir) or '.'}")
    generate_index_html_for_directory(current_dir, root_output_dir)

    # Then, recurse for subdirectories
    try:
        for item_name in os.listdir(current_dir):
            item_path = os.path.join(current_dir, item_name)
            if os.path.isdir(item_path):
                if item_name not in EXCLUDED_DIRS: # Check before recursing
                    generate_all_indexes_recursively(item_path, root_output_dir)
                # else: print(f"Skipping excluded directory for recursion: {item_path}")
    except OSError as e:
        print(f"Warning: Could not list subdirectories in {current_dir} for recursion: {e}")
        pass


def generate_headers_content(target_dir):
    """
    Scans the target_dir (which now contains all generated index.html files)
    and generates the content for the _headers file.
    index.html files get text/html, others get text/plain.
    """
    headers_rules = []
    script_full_path = os.path.realpath(__file__) # Full path of this build script
    target_full_path = os.path.realpath(target_dir)

    for root, dirs, files in os.walk(target_dir, topdown=True):
        # Exclude specified directories from _headers rules and further traversal for _headers
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file_name in files:
            full_file_path = os.path.join(root, file_name)
            full_file_path_real = os.path.realpath(full_file_path)

            # Skip the build script itself from having a header rule
            if full_file_path_real == script_full_path:
                continue

            # Skip the _headers file itself from being listed in _headers
            if file_name == HEADERS_FILE_NAME and os.path.realpath(os.path.dirname(full_file_path)) == target_full_path:
                continue

            relative_file_path = os.path.relpath(full_file_path, target_dir)
            # Ensure URL paths use forward slashes, as expected by web servers and _headers
            url_path = "/" + relative_file_path.replace(os.sep, "/")

            rule_content_type = ""
            # Check if the file is one of the designated HTML document names (e.g., index.html)
            if file_name.lower() in HTML_DOCUMENT_FILENAMES:
                rule_content_type = "text/html"
            else:
                rule_content_type = "text/plain"

            rule = (
                f"{url_path}\n"
                f"  Content-Type: {rule_content_type}"
            )
            headers_rules.append(rule)

    if not headers_rules:
        return "# No custom header rules generated. No applicable files found in the target directory."
    return "\n\n".join(headers_rules)


def write_headers_file(content, target_dir):
    """
    Writes the generated content to the _headers file in the target_dir.
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
    Main function to:
    1. Recursively generate index.html files for all directories.
    2. Generate and write the _headers file for Cloudflare Pages.
    """
    if len(sys.argv) > 1:
        target_directory_arg = sys.argv[1]
    else:
        target_directory_arg = DEFAULT_TARGET_DIRECTORY

    # Resolve to an absolute path for consistency
    abs_target_dir = os.path.abspath(target_directory_arg)

    if not os.path.isdir(abs_target_dir):
        print(f"Error: Target directory '{abs_target_dir}' does not exist or is not a directory.")
        sys.exit(1)

    print(f"Starting build process in '{abs_target_dir}'...")

    # 1. Recursively generate index.html files for all directories
    print(f"\nGenerating {INDEX_HTML_FILENAME} files recursively...")
    # The root_output_dir argument for generate_all_indexes_recursively helps with relative path calculations
    generate_all_indexes_recursively(abs_target_dir, abs_target_dir)


    # 2. Generate _headers content based on all files (including all new index.html files)
    print(f"\nGenerating {HEADERS_FILE_NAME}...")
    # Log details for _headers generation
    print(f"Scanning directory: {abs_target_dir} for _headers rules.")
    print(f"Excluding directories named: {EXCLUDED_DIRS} from _headers rules and traversal.")
    print(f"Files named matching {HTML_DOCUMENT_FILENAMES} will be set to Content-Type: text/html in _headers.")
    print(f"All other files will be set to Content-Type: text/plain in _headers.")
    # The build script is excluded from _headers rules by path comparison within generate_headers_content

    headers_content = generate_headers_content(abs_target_dir)
    write_headers_file(headers_content, abs_target_dir)

    print("\nBuild process finished.")

if __name__ == "__main__":
    main()
