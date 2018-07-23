# Fantasy Football
This repository contains two python scripts.

The first file, webScraper.py, reads in fantasy football projections from ESPN dynamically through web scraping, does a bit of organization on the data, and then writes the information to two csv files, "Web Scraped Projections.csv" containing projections for the normal players you would encounter in fantasy football (QB, RB, WR, TE, K), and "Defense Projections.csv" containing projections for team defenses.

The second file, projectionAnalysis.py, should be run after the webScraper.py so that it has up to date information and files to read from.  It does some analysis on the projections and then writes all of its findings to a report called "Fantasy Report.txt".

I am also including a sample picture of the main table I use from ESPN for convenience and in case the website ever goes down.
I take my data from http://games.espn.com/ffl/tools/projections? and http://games.espn.com/ffl/livedraftresults.
![Fantasy Projection Table](/Pictures/Fantasy_Projection_Table.png)
