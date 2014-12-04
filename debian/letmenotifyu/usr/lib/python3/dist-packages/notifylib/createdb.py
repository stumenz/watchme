import sqlite3
import logging
from notifylib import settings
import os

logging.getLogger(__name__)


class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.connect = sqlite3.connect(self.db_file)
        self.cursor = self.connect.cursor()

    def create_database(self):
        "create new database"
        logging.info("***Creating new Database***")
        self.cursor.execute("PRAGMA foreign_keys = ON")
        logging.info("****Creating table Genre****")
        self.cursor.execute("CREATE TABLE genre(" +
                            "Id INTEGER PRIMARY KEY," +
                            "genre VARCHAR(10) UNIQUE NOT NULL )")
        logging.info("****Creating movie table****")
        self.cursor.execute('CREATE TABLE movies(' +
                            'id INTEGER PRIMARY KEY, ' +
                            'genre_id INTEGER  NOT NULL,' +
                            ' title VARCHAR(20) UNIQUE NOT NULL,' +
                            ' link VARCHAR(20) NOT NULL,' +
                            'date_added TIMESTAMP NOT NULL,' +
                            ' FOREIGN KEY(genre_id) REFERENCES genre(Id) ON UPDATE CASCADE ON DELETE CASCADE)')
        logging.info("****Creating series table****")
        self.cursor.execute('CREATE TABLE series(' +
                            'id INTEGER PRIMARY KEY,' +
                            'title VARCHAR(30) UNIQUE NOT NULL,' +
                            'series_link VARCHAR(60) NOT NULL,' +
                            'number_of_episodes INTEGER NOT NULL,' +
                            'number_of_seasons INTEGER NOT NULL,' +
                            'current_season INTEGER NOT NULL,' +
                            'last_update TIMESTAMP NOT NULL,' +
                            'status BOOLEAN NOT NULL)')
        logging.info("****Creating episodes table****")
        self.cursor.execute('CREATE TABLE episodes(' +
                            'id INTEGER PRIMARY KEY,' +
                            'series_id INTEGER  NOT NULL,' +
                            'episode_name VARCHAR(15) NOT NULL,' +
                            'episode_link VARCHAR(40) NOT NULL,' +
                            'Date TIMESTAMP,' +
                            ' FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE)')
        logging.info("****Creating Config table****")
        self.cursor.execute('CREATE TABLE config(' +
                            'id INTEGER PRIMARY KEY, ' +
                            'key VARCHAR(20) NOT NULL,' +
                             'value VARCHAR(20) NOT NULL)')
        self.cursor.execute('CREATE TABLE torrents(' +
                            'Id INTEGER PRIMARY KEY,' +
                            'name VARCHAR(20) UNIQUE NOT NULL,' +
                            'link VARCHAR(20) NOT NULL)')
        logging.info("****Creating Images table****")
        self.cursor.execute('CREATE table series_images(' +
                            'id INTEGER PRIMARY KEY,' +
                            'series_id INTEGER NOT NULL,'
                            'path VARCHAR(20) NOT NULL,' +
                            'FOREIGN KEY (series_id) REFERENCES series(id))')
        logging.info("****Creating movie images table")
        self.cursor.execute('CREATE table movie_images(' +
                            'id INTEGER PRIMARY KEY,' +
                            'movie_id INTEGER NOT NULL,' +
                            'path VARCHAR(20) UNIQUE NOT NULL,' +
                            'FOREIGN KEY(movie_id) REFERENCES movies(Id))')
        self.cursor.execute("INSERT INTO config(key,value) VALUES('version','2.0')")
        self.cursor.execute("INSERT INTO config(key,value) VALUES('update_interval','3600')")
        self.cursor.execute("INSERT INTO config(key,value) VALUES('last_movie_id', '0')")
        self.cursor.execute("INSERT INTO config(key,value) VALUES('last_series_id','0')")
        self.cursor.execute("INSERT INTO torrents(name,link) VALUES('Kickass','http://kickass.to/usearch/')")
        self.cursor.execute("INSERT INTO torrents(name,link) VALUES('The Pirate Bay','http://thepiratebay.se/search/')")
        self.cursor.execute("INSERT INTO config(key,value)" +
                                 " VALUES('movie_duration','7')")
        self.cursor.execute("INSERT INTO config(key,value)" +
                                 " VALUES('series_duration','7')")
        self.connect.commit()
        logging.info("***Creating Images Directory***")
        os.mkdir(settings.IMAGE_PATH)
        logging.info("***Database has been created***")
        self.connect.close()

    def upgrade_database(self):
        self.cursor.execute("SELECT value FROM config WHERE key='version'")
        version = self.cursor.fetchone()
        database_version = version[0]

        if database_version == '1.10':
            logging.info("***Upgrading database***")
            logging.info("***Modifying Movie table***")
            self.cursor.execute("CREATE TEMP TABLE movie_temp as SELECT * from movies")
            self.cursor.execute("DROP TABLE movies")
            self.cursor.execute('CREATE TABLE movies(' +
                            'Id INTEGER PRIMARY KEY, ' +
                            'genre_id INTEGER  NOT NULL,' +
                            ' title VARCHAR(20) UNIQUE NOT NULL,' +
                            ' link VARCHAR(20) NOT NULL,' +
                            'date_added TIMESTAMP NOT NULL DEFAULT(0),' +
                            ' FOREIGN KEY(genre_id) REFERENCES genre(Id) ON UPDATE CASCADE ON DELETE CASCADE)')
            self.cursor.execute('INSERT INTO movies(' + 
                                'genre_id,' +
                                'title,'+
                                'link) SELECT genre_id,title,link from movie_temp')
            self.connect.commit()
            logging.info("***Modifying Series Table***")
            self.cursor.execute("CREATE TEMP TABLE series_temp as SELECT * FROM series")
            self.cursor.execute("DROP TABLE series")
            self.connect.commit()
            self.cursor.execute('CREATE TABLE series(' +
                            'id INTEGER PRIMARY KEY,' +
                            'title VARCHAR(30) UNIQUE NOT NULL,' +
                            'series_link VARCHAR(60) NOT NULL,' +
                            'number_of_episodes INTEGER NOT NULL,' +
                            'number_of_seasons INTEGER NOT NULL,' +
                            'current_season INTEGER NOT NULL,' +
                            'last_update TIMESTAMP NOT NULL,' +
                            'status BOOLEAN NOT NULL)')
            self.cursor.execute('INSERT INTO series(' +
                                'title,' +
                                'series_link,' +
                                'number_of_episodes,' +
                                'number_of_seasons,' +
                                'current_season,' +
                                'last_update,' +
                                'status) SELECT * from temp.series_temp')
            self.connect.commit()
            logging.info("****Modifying Torrent Table****")
            self.cursor.execute("CREATE TEMP TABLE torrent_temp as SELECT * FROM torrents")
            self.cursor.execute("DROP TABLE torrents")
            logging.info("****Creating new torrents table****")
            self.cursor.execute('CREATE TABLE torrent_sites(' +
                            'id INTEGER PRIMARY KEY,' +
                            'name VARCHAR(20) UNIQUE NOT NULL,' +
                            'link VARCHAR(20) NOT NULL)')
            self.cursor.execute('INSERT INTO torrent_sites(' +
                                'id,'+
                                'name,' +
                                'link) SELECT * from torrent_temp')
            self.connect.commit()
            self.cursor.execute('CREATE table series_images(' +
                            'id INTEGER PRIMARY KEY,' +
                            'series_id INTEGER NOT NULL,'
                            'path VARCHAR(20) NOT NULL,' +
                            'FOREIGN KEY(series_id) REFERENCES series(title))')
            logging.info("****Creating next images table****")
            self.cursor.execute('CREATE table movie_images(' +
                            'id INTEGER PRIMARY KEY,' +
                            'movie_id INTEGER NOT NULL,' +
                            'path VARCHAR(20) UNIQUE NOT NULL,' +
                            'FOREIGN KEY(movie_id) REFERENCES movies(id))')
            self.cursor.execute("DROP TABLE episodes")
            self.cursor.execute('CREATE TABLE episodes(' +
                            'id INTEGER PRIMARY KEY,' +
                            'series_id INTEGER  NOT NULL,' +
                            'episode_name VARCHAR(15) NOT NULL,' +
                            'episode_link VARCHAR(40) UNIQUE NOT NULL,' +
                            'Date TIMESTAMP,' +
                            ' FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE)')
            self.cursor.execute("UPDATE series SET number_of_episodes=0")
            self.cursor.execute("DELETE FROM episodes")
            self.cursor.execute("INSERT INTO config(key,value) VALUES('last_movie_id', '0')")
            self.cursor.execute("INSERT INTO config(key,value) VALUES('last_series_id','0')")
            self.cursor.execute("INSERT INTO config(key,value)" +
                                 " VALUES('movie_duration','7')")
            self.cursor.execute("INSERT INTO config(key,value)" +
                                 " VALUES('series_duration','7')")
            self.cursor.execute("UPDATE config set value='2.0' where key='version'")
            self.connect.commit()
            logging.info("***Database has been upgraded***")
            logging.info("***Creating Images Directory***")
            os.mkdir(settings.IMAGE_PATH)
            database_version = '2.0'

        if database_version == '2.0':
            logging.info("***Database upto date***")