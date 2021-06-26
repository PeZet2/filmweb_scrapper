import random
import time
from sys import argv

import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
}


class EpisodeManager:
    full_episode_list = []


class Episode:

    def setSeason(self, season):
        self.season = season

    def setNumber(self, number):
        self.number = number

    def setName(self, name):
        self.name = name

    def setDate(self, date):
        self.date = date


def wait():
    """
    Waits for a random amount of time between 1 and 9 seconds
    :return: None
    """
    t = random.randint(1, 10)
    print(f'Waiting {t} seconds...')
    time.sleep(t)


def get_episode_data(episode_element: str, season: int) -> Episode:
    """
    Scraps a piece of html page in search of episode data
    :param episode_element: Piece of html document with unparsed episode data
    :return: Episode object
    """
    episode = Episode()
    # episode.setSeason(int(episode_element.get('data-season-number') or 0))
    episode.setSeason(season or 0)
    episode.setNumber(int(episode_element.get('data-episode-number')))
    episode.setDate(episode_element.get('data-air-date'))
    episode.setName(episode_element.find('a', {'itemprop': 'url'}).get('title'))

    # Add episode to a global list
    EpisodeManager.full_episode_list.append(episode)

    print(
        f'S{"0"+str(episode.season) if episode.season < 10 else str(episode.season)}E{"0"+str(episode.number) if episode.number < 10 else str(episode.number)} '
        f'- {episode.date} - {episode.name}'
        )
    return episode


def get_season_data(season: int) -> list:
    """
    Scraps a season webpage in search of episodes
    :param season: Number of season
    :return: List of episode objects
    """
    wait()

    # Building url for a specific season
    if isinstance(season, int) and season < 2000:
        season_url = f'{base_url}/episode/{season}/list'
    elif isinstance(season, str) and season == 'Lista odcinków':
        season = 1
        season_url = f'{base_url}/episode/list'
    elif isinstance(season, str) and 'Rok' in season:
        season = int(season.replace('Rok', '').replace(' ', ''))
        season_url = f'{base_url}/episode/list?serialYear={season}'
    elif isinstance(season, int) and season > 2000:
        season_url = f'{base_url}/episode/list?serialYear={season}'
    else:
        season_url = f'{base_url}/episode/list'
    print('-' * 70)
    print(f'Parsing season {season} -> {season_url}')
    print('-' * 70)

    response = requests.get(season_url, headers).text
    season_page = BeautifulSoup(response, 'html.parser')

    # Fetching list of all episodes
    episode_list = season_page.findAll('div', {'class': 'episodePreview EpisodePreview episodeSource'})
    print(f'Found {len(episode_list)} episodes:')

    # Getting data for each episode
    for episode_element in episode_list:
        get_episode_data(episode_element, season)


def run(base_url):
    # Create BeautifulSoup page representation
    response = requests.get(base_url, headers).text
    main_page = BeautifulSoup(response, 'html.parser')

    # Get TvShow name
    show_name = main_page.find('header', class_='filmCoverSection__info').find('h1', {
        'class': 'filmCoverSection__title'}).find('span').text
    show_name_original = main_page.find('header', class_='filmCoverSection__info').find('h2', {
        'class': 'filmCoverSection__orginalTitle'}) or 'Brak'
    print(f'TvShow: {show_name}\n'
          f'Original title: {show_name_original}')

    all_season_links = main_page.find('div', {'class': 'filmInfo__info'}).findAll('a', {'class': 'link'})
    print(all_season_links)
    seasons = [int(s.get('data-number')) for s in all_season_links if s.get('data-number')] or [s.text for s in
                                                                                                all_season_links if
                                                                                                'see-all' not in s.get(
                                                                                                    'class')]

    print(f'Season list: {sorted(seasons)}')

    for season in sorted(seasons):
        get_season_data(season)


if __name__ == '__main__':
    if len(argv) > 1:
        base_url = argv[1]
        # base_url = 'https://www.filmweb.pl/serial/Bar+Karma-2010-620628'
        # base_url = 'https://www.filmweb.pl/serial/Odysseja-2002-40700'
        run(base_url)
    else:
        print('No url provided.')
        exit()
