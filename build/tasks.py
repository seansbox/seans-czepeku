from invoke import task
from custom_tasks.unzip_files import unzip_files
from custom_tasks.sync_symlinks import sync_symlinks
from custom_tasks.delete_files import delete_files
from custom_tasks.make_manifest import make_manifest
from custom_tasks.download_file import download_font
from custom_tasks.draw_favicons import draw_favicons

import json
import re
import os

PATREON_URLS = [
    ["animated_maps", "https://www.patreon.com/posts/animated-maps-49184370"],
    ["animated_scenes", "https://www.patreon.com/posts/10-master-post-79200864"],
    ["maps", "https://www.patreon.com/posts/master-master-27816327"],
    ["scenes", "https://www.patreon.com/posts/5-tier-master-79200795"],
]


WORDS_TO_REMOVE = [
    "- $5 Rewards",
    "- $10 Rewards",
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
    "- Animated Battlemaps",
    "- Animated Battlemap",
    "-Animated Battlemaps",
    "-Animated Battlemap",
    "- Animated",
    "Scenes",
    "-",
    "Animated",
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
        segment = re.sub(r"__", "_", segment)
        segment = re.sub(r"^_|_$", "", segment)
        segment = re.sub(r"_\.", ".", segment)
        updated_segments.append(segment)

    # Join the segments back together
    dst = os.sep.join(updated_segments)
    dst = dst.replace("Gridless/", "")
    dst = dst.replace("Gridded/", "")

    return dst.lower()


@task
def build(c):
    """
    Build the project
    """
    unzip(c)
    for name, url in PATREON_URLS:
        sync_symlinks(c, f"../unzipped/{name}", f"../{name}", rename_func)
        make_manifest(c, f"../unzipped/{name}", f"../manifest_{name}.json")


@task
def unzip(c):
    """
    Unzip the Patreon .zip files
    """
    for name, url in PATREON_URLS:
        unzip_files(c, f"../zipped/{name}/*.zip", f"../unzipped/{name}")
    delete_files(c, "../unzipped/**/*ridded*")
    # delete_files(c, "../unzipped/**/*mp4")
    # delete_files(c, "../unzipped/**/*4K*")
    delete_files(c, "../unzipped/**/__MACOSX")
    delete_files(c, "../unzipped/**/.DS_Store")


@task
def download(c):
    """
    Generate JavaScript code to initialize a browser window to download any zip files not found in ../raw/maps-zipped
    """
    for name, url in PATREON_URLS:
        download_from_patreon(c, url, f"../zipped/{name}", 7)


def download_from_patreon(c, url, download_folder, delay=10):
    """
    Download a group of files from Patreon article
    """
    # Find all zip files in the directory
    zip_files = [f for f in os.listdir(download_folder) if f.endswith(".zip")]
    # Create JavaScript code to set the alreadyDownloaded array
    print(f"Browse to {url} ({download_folder})")
    input("Press Enter when you are ready to continue...")
    js_code = """
// Helper function to create a delay using Promise and await
function delay(ms) {{
  return new Promise((resolve) => setTimeout(resolve, ms));
}}

// Set alreadyDownloaded based on files already in {download_folder}
window.alreadyDownloaded = {existing_files};

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
    await delay({delay}*1000); // Wait for x seconds before processing the next link
    window.alreadyDownloaded.push(fname); // Add the file to the alreadyDownloaded list
  }}
}}

// Run the downloadZips function
downloadZips();
""".format(
        existing_files=json.dumps(zip_files), url=url, delay=delay, download_folder=download_folder
    )
    print(js_code)
    input("Press Enter when you are ready to continue...")
