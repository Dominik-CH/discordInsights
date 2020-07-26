import sqlite3
import time

def createDatabase():
    dbName = "discordData.db"
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute('''CREATE TABLE userData
                    (discordID text, username text, time unsigned integer, channelBeforeName text, channelAfterName text, channelBeforeID text, channelAfterID text, selfmuteBefore text, selfmuteAfter text, actionTaken text )''')  # Noch foreign key und datatypes anpassen
    conn.commit()
    conn.close()
    return dbName

def convertColumn():
    dbName = "discordData.db"
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute('''
    ALTER TABLE userData RENAME TO tmp;''')

    c.execute('''CREATE TABLE userData
                    (discordID text, username text, time unsigned integer, channelBeforeName text, channelAfterName text, channelBeforeID text, channelAfterID text, selfmuteBefore text, selfmuteAfter text, actionTaken text);''')


    c.execute('''INSERT INTO userData(discordID, username,time,channelBeforeName,channelAfterName,channelBeforeID,channelAfterID,selfmuteBefore,selfmuteAfter,actionTaken)
        SELECT discordID, username,time,channelBeforeName,channelAfterName,channelBeforeID,channelAfterID,selfmuteBefore,selfmuteAfter,actionTaken
        FROM tmp;''')

    c.execute('''DROP TABLE tmp;''')

    conn.commit()
    conn.close()
    print("Converted.")
    return dbName


createDatabase()    #Sets up a Database so the bot is able to write into it
print(convertColumn())  #Existing database columns had other datatypes so there is a need to convert them to be able to use dataAnalysis.py on them
