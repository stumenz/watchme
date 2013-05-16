#!/usr/bin/python


from pysqlite2 import dbapi2 as sqlite

def make_movie_table(cursor):
    i=0
    cursor.execute('CREATE TABLE movies(id INTEGER PRIMARY KEY, title VARCHAR(20), link VARCHAR(20))')
    while i <=23:
        cursor.execute("INSERT INTO movies VALUES(null,'#####','#####')")
        i+=1

        
def make_series_table(cursor):
     cursor.execute('CREATE TABLE series(title VARCHAR(30) PRIMARY KEY,series_link VARCHAR(30),number_of_episodes INTEGER,number_of_seasons INTEGER)')

def make_episode_table(cursor):
    cursor.execute('CREATE TABLE episodes(id INTEGER PRIMARY KEY,title VARCHAR(30),episode_name VARCHAR(15), episode_link VARCHAR(40), FOREIGN KEY (title) REFERENCES series(title) ON DELETE CASCADE)')

def create_database(sqlite_file):
    connection=sqlite.connect(sqlite_file)
    cursor=connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    connection.commit()
    make_movie_table(cursor)
    connection.commit()
    make_series_table(cursor)
    connection.commit()
    make_episode_table(cursor)
    connection.commit()
    connection.close()

