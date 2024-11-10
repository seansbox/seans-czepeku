# seans-czepeku

## Setup

- Subscribe to Cze and Peku's Patreon
- Install python and know how to get to your module folders from a terminal
- Browse to https://www.patreon.com/posts/master-master-27816327

      cd build
      python -m pip install invoke
      python -m invoke download

This will generate JavaScript code that you can paste into your browser's console to download any map files that you don't already have in the `raw/maps-zipped` folder

- Move the downloaded .zip files to `raw/maps-zipped`
- Run the following to unzip the files

      cd build
      python -m pip install invoke
      python -m invoke unzip

- Done!
