from invoke import task
from custom_tasks.unzip_files import unzip_files
from custom_tasks.sync_symlinks import sync_symlinks
from custom_tasks.delete_files import delete_files
from custom_tasks.make_manifest import make_manifest

import json
import re
import os

WORDS_TO_REMOVE = [
    "- $5 Rewards",
    "(Gridded Part 1)",
    "(Gridded Part 2)",
    "(Gridless Part 1)",
    "(Gridless Part 2)",
    "(Gridded Pt.1)",
    "(Gridded Pt.2)",
    "(Gridless Pt.1)",
    "(Gridless Pt.2)",
    "Pt 1",
    "Pt 2",
    "Pt 3",
    "Pt1",
    "Pt2",
    "Pt3",
    "Pt.1",
    "Pt.2",
    "Pt.3",
    "Pt. 1",
    "Pt. 2",
    "Pt. 3",
    "- Part 1",
    "- Part 2",
    "- Part 3",
    "Part 1",
    "Part 2",
    "Part 3",
    "- Gridless",
    "- Gridded",
    "(Gridded)",
    "(Gridless)",
    "Gridless",
    "Gridded",
]


def rename_func(src):
    # Skip gridded files
    if "ridded" in src or "/G_" in src:
        return None
    dst = src
    # Remove all the extra words
    for word in WORDS_TO_REMOVE:
        dst = dst.replace(word, "")

    updated_segments = []
    for segment in dst.split(os.sep):
        # Remove extra spaces, replace with underscore, and strip leading/trailing underscores
        segment = re.sub(r"[\(\)\[\]\']", "", segment)
        segment = re.sub(r"\s+", "_", segment)
        segment = re.sub(r"^_|_$", "", segment)
        segment = re.sub(r"_\.", ".", segment)
        updated_segments.append(segment)

    # Join the segments back together
    dst = os.sep.join(updated_segments)
    dst = dst.replace("Gridless/", "")
    dst = dst.replace("Gridded/", "")

    return dst


@task
def build(c):
    """
    Build the project
    """
    unzip(c)
    # Create symlinks for the maps that we can use to track changes
    sync_symlinks(c, "../raw/maps-unzipped", "../maps", rename_func)
    make_manifest(c, "../maps", "../maps-manifest.json")


@task
def unzip(c):
    """
    Unzip the Patreon .zip files in raw/maps
    """
    unzip_files(c, "../raw/maps-zipped/*.zip", "../raw/maps-unzipped")
    # Remove gridded maps
    delete_files(c, "../raw/maps-unzipped/**/*ridded*")
    # Remove macOS junk files
    delete_files(c, "../raw/**/__MACOSX")
    delete_files(c, "../raw/**/.DS_Store")


@task
def download(c):
    """
    Generate JavaScript code to initialize a browser window to download any zip files not found in ../raw/maps-zipped
    """
    # Path to the directory containing zip files
    directory_path = "../raw/maps-zipped"
    # Find all zip files in the directory
    zip_files = [f for f in os.listdir(directory_path) if f.endswith(".zip")]
    # Create JavaScript code to set the alreadyDownloaded array
    js_code = """
// Initialize alreadyDownloaded array if not already set
window.alreadyDownloaded = window.alreadyDownloaded || [];

// Set alreadyDownloaded based on files found in ../raw/maps-zipped
window.alreadyDownloaded = {existing_files};

// Helper function to create a delay using Promise and await
function delay(ms) {{
  return new Promise((resolve) => setTimeout(resolve, ms));
}}

// Function to find and download new zip files
async function downloadZips() {{
  // Find all links to zip files
  let links = Array.from(document.querySelectorAll("a[href]"));
  links = links.filter((link) => link.innerHTML && link.innerHTML.includes(".zip"));

  for (const link of links) {{
    let fname = link.textContent.trim(); // Declare fname before using it

    // Skip if filename contains 'ridded' or has already been downloaded
    if (fname.includes("ridded") || window.alreadyDownloaded.includes(fname)) continue;

    console.log(fname);
    link.click(); // Initiates download
    await delay(7000); // Wait for x seconds before processing the next link
    window.alreadyDownloaded.push(fname); // Add the file to the alreadyDownloaded list
  }}
}}

// Run the downloadZips function
downloadZips();
""".format(
        existing_files=json.dumps(zip_files)
    )

    print(js_code)
