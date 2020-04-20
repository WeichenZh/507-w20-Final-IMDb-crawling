import sqlite3
import requests
from bs4 import BeautifulSoup
import re
import os
import json

CACHE_FILE_NAME = "imdb_cache.json"
BASE_URL = "http://www.imdb.com"
DATABASE_FILE = "imdb.sqlite"

class Movie():
    def __init__(self, name=None, rank=None, category=None, length=None, genre=None, release_date=None, release_country=None, 
        rating=None, director=None, stars=None, relevant_moives=None):
        self.name = name
        self.rank = rank
        self.category = category
        self.length = self.cal_length(length)
        self.genre = genre
        self.release_date = self.transform_date(release_date)
        self.release_country = release_country
        self.rating = rating
        self.director = director
        self.stars = stars
        self.relevant_moives = relevant_moives

    ##############################
    # TODO
    ##############################
    def info(self):
        info = '''
        Tile: {title}
        Rank:{rank}                Rating:{rating}
        {genre} | {length} mins | {category} | {release_date} | {release_country}
        Director:{diretor}
        '''.format(title=self.name, rank=self.rank, rating=self.rating, genre=self.genre, length=self.length, category=" ".join(self.category),
        release_date=self.release_date, release_country=self.release_country, director=list(self.director.keys())[0])

        return info

    def cal_length(self, len_str):
        length = 0
        len_str_list = len_str.split(" ")
        for l in len_str_list:
            if 'h' in l:
                length += 60 * int(l[:-1])
            elif 'min' in l:
                length += int(l[:-3])
        return length

    def transform_date(self, date_str):
        Monthes = {"January":"01", "February":"02", "March":"03", "April":"04", 
                    "May":"05", "June":"06", "July":"07", "August":"08", 
                    "September":"09", "October":"10", "November":"11", "December":"12"}
        date_str_list = date_str.split(" ")
        if len(date_str_list) == 2:
            month = Monthes[date_str_list[0]]
            year = date_str_list[-1]
            date = year + "-" + month
        else:
            day = date_str_list[0]
            month = Monthes[date_str_list[1]]
            year = date_str_list[-1]

            if len(day) < 2:
                day = "0" + day

            date = year + "-" + month + "-" + day

        # print(date)
        return date
            
def load_cache():
    '''Load cache from the path

    Parameters
    ----------
    None

    Returns
    -------
    dict: cache

    '''
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_content = cache_file.read()
        cache = json.loads(cache_file_content)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    '''save cache from RAM to file

    Parameters
    ----------
    dict: cache

    Returns
    -------
    None
    '''
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()


def build_movie_url_dict(route_path):
    base_url = BASE_URL

    cache = load_cache()

    movie_url_dict = {}

    if base_url + route_path in cache:
        print('Using cache')
        movie_url_dict = cache[base_url + route_path]
    else:
        print('Fetching')
        response = requests.get(base_url + route_path)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'lxml')
            movies = soup.find('tbody',class_='lister-list')
            movies = movies.find_all('td', class_='titleColumn')
            for i, item in enumerate(movies):
                title_info = item.find('a')
                # movie_url_dict[i+1] = (title_info.text.strip(' '), base_url + title_info['href'])
                movie_url_dict[title_info.text.strip(' ')] = base_url + title_info['href']
        cache[base_url+route_path] = movie_url_dict
        save_cache(cache)

    return movie_url_dict


def bulid_movie_instances(movie_url):
    cache = load_cache()

    if movie_url in cache:
        print('Using cache')
        soup = BeautifulSoup(cache[movie_url], 'html.parser')
    else:
        print('Fetching')
        resp = requests.get(movie_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        cache[movie_url] = resp.text
        save_cache(cache)

    name = soup.find('div', class_='title_wrapper').find('h1').get_text(strip=True).split('(')[0]
    rank_str = soup.find('div', class_='article highlighted', id='titleAwardsRanks').find('strong').get_text(strip=True)
    if rank_str.startswith('Top Rated Movies'):
        rank = int(rank_str.split('#')[-1])
    else:
        rank = 'N/A'
    sub_info = soup.find('div', class_='subtext').get_text(strip=True).split('|')
    if len(sub_info) <= 3:
        genre = 'Not Rated'
    else:
        genre = sub_info[-4]
    length = sub_info[-3]
    category = sub_info[-2].split(',')
    release_date = sub_info[-1].split('(')[0].strip(' ')
    release_country = sub_info[-1].split('(')[-1].strip(')')

    rating = float(soup.find('span', itemprop='ratingValue').get_text(strip=True))
    people = soup.find_all('div', class_='credit_summary_item')
    director_info = people[0].find('a')
    director = {director_info.get_text(strip=True): BASE_URL + director_info['href']}
    stars_info = people[2].find_all('a')
    stars = {}
    for star in stars_info[:-1]:                            # ignore 'See full cast & crew' link
        stars[star.get_text(strip=True)] = BASE_URL + star['href']

    relevant_moives = {}
    rel_movies_info = soup.find_all('div', class_='rec_overview')
    for rel_mv in rel_movies_info:
        mv_info = rel_mv.find('div', class_='rec-title').find('a')
        relevant_moives[mv_info.get_text(strip=True)] = BASE_URL + mv_info['href']

    # print(name)
    # print(rank)
    # print(category)
    # print(genre)
    # print(length)
    # print(release_date)
    # print(release_country)
    # print(rating)
    # print(director)
    # print(stars)
    # print(relevant_moives)

    return Movie(name, rank, category, length, genre, release_date, release_country, rating, director, stars, relevant_moives)

def get_director_knownfor(director_page_url):
    cache = load_cache()

    if director_page_url in cache:
        print('Using cache')
        soup = BeautifulSoup(cache[director_page_url], 'html.parser')
    else:
        print('Fetching')
        resp = requests.get(director_page_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        cache[director_page_url] = resp.text
        save_cache(cache)

    knownfor = {}
    knownfor_infos = soup.find('div', id='knownfor').find_all('div', class_='knownfor-title')
    for work_info in knownfor_infos:
        work_info = work_info.find('div', class_="knownfor-title-role").find('a')
        knownfor[work_info.get_text(strip=True)] = BASE_URL + work_info['href']

    return knownfor

def print_director_knownfor(director, knownfor):
    pass

def get_top_ranked_movies(movie_url_dict, top_num=250):
    top_movies = []
    limit_num = min(len(movie_url_dict), top_num)
    for i, movie in enumerate(movie_url_dict):
        if i >= limit_num:
            break
        top_movies.append(bulid_movie_instances(movie_url_dict[movie]))
    
    return top_movies

def get_directors_from_movies(movie_instances):
    directors = []
    for movie in movie_instances:
        if movie.director in directors:
            continue
        else:
            directors.append(tuple(movie.director.items())[0])

    return directors

def create_sql_tables():
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()

    drop_movies = '''
        DROP TABLE IF EXISTS "Movies";
    '''

    create_movies = '''
        CREATE TABLE IF NOT EXISTS "Movies" (
            "Id"            INTEGER PRIMARY KEY AUTOINCREMENT,
            "MovieTile"     TEXT NOT NULL,
            "Rank"          INTEGER,
            "Category"      TEXT NOT NULL,
            "Length"        INTEGER NOT NULL,
            "Genre"         TEXT,
            "ReleaseDate"   TEXT NOT NULL,
            "ReleaseCounty" TEXT NOT NULL,
            "Rating"        REAL NOT NULL,
            "DirectorId"    INTEGER NOT NULL,
            FOREIGN KEY ("DirectorId") REFERENCES Directors("Id")
        );
    '''

    drop_directors = '''
        DROP TABLE IF EXISTS "Directors";
    '''

    create_directors = '''
        CREATE TABLE IF NOT EXISTS "Directors" (
            "Id"            INTEGER PRIMARY KEY AUTOINCREMENT,
            "FistName"      TEXT NOT NULL,
            "LastName"      TEXT NOT NULL,
            "Link"          TEXT
        );
    '''

    cur.execute(drop_directors)
    cur.execute(create_directors)
    cur.execute(drop_movies)
    cur.execute(create_movies)

    conn.commit()
    conn.close()

def insert_raw_into_table(db_cur, table_name, values):
    value_format = ""
    value_format += "(NULL"
    for i in range(len(values)):
        value_format += ", ?"
    value_format += ")"

    insert_command = '''
        INSERT INTO {TABLE}
        VALUES {VALUE}
    '''.format(TABLE=table_name, VALUE=value_format)

    db_cur.execute(insert_command, values)


def insert_movies(movies, url2fk):
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()

    insert_command = '''
        INSERT INTO Movies
        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    for movie in movies:
        directorId = url2fk[list(movie.director.values())[0]]
        values = [movie.name, movie.rank, " ".join(movie.category), movie.length, movie.genre, movie.release_date, movie.release_country, movie.rating, directorId]
        cur.execute(insert_command, values)

    conn.commit()
    conn.close()


def insert_directors(directors):
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()

    insert_command = '''
        INSERT INTO Directors
        VALUES (NULL, ?, ?, ?)
    '''

    url2id = {}
    for i, director in enumerate(directors):
        url2id[director[1]] = i+1              # director's name is not unique, thus using url as the index key
        values = [director[0].split(' ')[0], director[0].split(' ')[-1], director[1]]
        # insert_raw_into_table(cur, table_name=Directors, values=values)  
        cur.execute(insert_command, values)

    conn.commit()
    conn.close()

    return url2id


if __name__ == "__main__":
    dic = build_movie_url_dict("/chart/top")
    movies_top_250 = get_top_ranked_movies(dic, 80)
    directors = get_directors_from_movies(movies_top_250)

    #if not os.path.exists(DATABASE_FILE):
    create_sql_tables()

    url2fk = insert_directors(directors)
    insert_movies(movies_top_250, url2fk)

    # conn = sqlite3.connect("imdb22.sqlite")