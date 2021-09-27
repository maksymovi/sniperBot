import discord
import sqlite3
from os.path import exists

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    cirspr 
    if message.content.startswith('snipe'):
        if message.content.startswith('snipe admin'):
            #admin actions here
            pass
        elif 
            processSnipe(message)
        #await message.channel.send('Hello!')

async def processSnipe(m):
    

def botInit():
    database_exists = exists("./data.db")
    connection = sqlite3.connect("aquarium.db")
    if not database_exists:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE channels (channelID INTEGER)")
        cursor.execute("CREATE TABLE snipes (snipeID INTEGER, sniperID INTEGER, snipeeID INTEGER, voided BOOL)")
    return connection
connection = botInit()
client.run('your token here')