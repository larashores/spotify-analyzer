# spotify-analyzer

This is a program built with tkinter used to analyze user data provided by spotify.

To request your data, visit https://www.spotify.com/us/account/privacy. They will only deliver your data within the past year, so for a complete picture, be sure to download your data at least twice a year.

## Usage

To use the program, simply open the directory containing your Spotify data, or open a director containing directories of multiple instances of Spotify data (the program will account for duplicates).

## Images

<img src="https://raw.githubusercontent.com/larashores/spotify-analyzer/master/images/listens_per_day.png" title=listens_per_day.py width="800">

<img src="https://raw.githubusercontent.com/larashores/spotify-analyzer/master/images/weekly_color_mesh.png" title=weekly_color_mesh.py width="800">

<img src="https://raw.githubusercontent.com/larashores/spotify-analyzer/master/images/top_artists.png" title=top_artists.py width="800">

## Installation

    git clone https://github.com/larashores/spotify-analyzer.git
    pipenv install

## Running

To start the program, simply run:

    pipenv run python src\main.py
