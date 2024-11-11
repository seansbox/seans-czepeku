# seans-czepeku

## Setup

- Subscribe to Cze and Peku's Patreon!
- Install python and know how to get to your module folders from a terminal:

      cd build
      python -m pip install invoke
      python -m invoke download

This will generate JavaScript code that you can paste into your browser's console to download any map files that you don't already have in the local folders.

- Move each group of downloadeded .zip files to the correct `zipped/` subfolder.
- Run the following to unzip the files into the correct `unzipped/` subfolder:

      cd build
      python -m pip install invoke pillow
      python -m invoke unzip

- Done!
