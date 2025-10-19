import scraper
import process_data
import csv
from sys import argv


def read_csv_to_dict(filename):
    data_dict = {}
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 2:
                key = row[0]
                value = row[1]
                data_dict[key] = value
    return data_dict

def scrape(link, output, team, tag=None):
    try:
        scraper.run(link, output, team, tag)
        return
    except Exception as e:
        print(e)
        scrape(link, team, tag)

def update_data(key=None):
    filename = "HockeyBackend.csv"
    data_sources = read_csv_to_dict(filename)

    for team in data_sources.keys():
        if not key or team == key:
            link = data_sources[team]

            formatted_team = team.replace("_", " ")
            print(f'Looking at team: {formatted_team}, at the link: {link}')

            scrape(link, team, formatted_team)

            process_data.run(team, formatted_team)

if __name__ == '__main__':
    if len(argv) > 1:
        team = argv[1]
        update_data(team)
    else:
        update_data()