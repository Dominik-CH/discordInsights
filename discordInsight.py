from discord import Client
import discord
from config import APIKEY
import time
import sqlite3
import sys
import random
import asyncio


class insightClient(Client):
    def __init__(self):
        Client.__init__(self)
        self.conn = sqlite3.connect("discordData.db")
        self.sourceChannel = None
        self.speak = None
    def didUserSelfDeafen(self, member, before, after):
        if (after.self_deaf == True) and (before.self_deaf == False):
            #            print("MUTED")
            self.dbEntry(member.id, member.name, int(time.time()), before.channel.name, after.channel.name,
                         before.channel.id, after.channel.id, before.self_deaf, after.self_deaf, "SOUND MUTED")
            return True
        elif (after.self_deaf == False) and (before.self_deaf == True):
            self.dbEntry(member.id, member.name, int(time.time()), before.channel.name, after.channel.name,
                         before.channel.id, after.channel.id, before.self_deaf, after.self_deaf, "SOUND UNMUTED")

            #            print("ENTMUTED")
            return True
        else:
            return False

    def didUserSwitchChannel(self, member, before, after):
        if (before.channel != after.channel) and (after.channel != None) and (before.channel != None):
            #            print("User swicthed channel")
            self.dbEntry(member.id, member.name, int(time.time()), before.channel.name, after.channel.name,
                         before.channel.id, after.channel.id, before.self_deaf, after.self_deaf, "CHANNEL SWITCHED")
            return True
        elif (before.channel != after.channel) and (after.channel == None) and (before.channel != None):
            #            print("User disconnected")
            self.dbEntry(member.id, member.name, int(time.time()), before.channel.name, "None",
                         before.channel.id, "None", before.self_deaf, "None", "DISCONNECTED")
            return True
        elif (before.channel != after.channel) and (after.channel != None) and (before.channel == None):
            #print("User connected")
            self.dbEntry(member.id, member.name, int(time.time()), "None", after.channel.name,
                         "None", after.channel.id, "None", after.self_deaf, "CONNECTED")
            return True

    def dbEntry(self, discordID, username, time, channelBeforeName, channelAfterName, channelBeforeID, channelAfterID,
                selfmuteBefore, selfmuteAfter, actionTaken):

        c = self.conn.cursor()
        c.execute(
            """insert into userData (discordID, username, time, channelBeforeName, channelAfterName, channelBeforeID, channelAfterID, selfmuteBefore, selfmuteAfter, actionTaken) values (?,?,?,?,?,?,?,?,?,?)"""
            , (discordID, username, time, channelBeforeName, channelAfterName, channelBeforeID, channelAfterID,
               selfmuteBefore, selfmuteAfter, actionTaken,))
        self.conn.commit()


client = insightClient()


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_voice_state_update(member, before, after):
    try:
        if client.didUserSelfDeafen(member, before, after):
            return
        elif client.didUserSwitchChannel(member, before, after):
            return
        else:
            pass
            #            print("Something else")
            return
    except Exception as ex:
        print(ex)
        client.conn.close()
        sys.exit()




client.run(APIKEY)
