import discord
import sqlite3
import threading
import credentials
from contextlib import closing
from os.path import exists


databaseFilename = "sniper.db"

client = discord.Client()

databaseLock = threading.Lock()
#getting contradictory data online on if sqlite is thread safe, so locking it regardless

def databaseInit():
    #makes sure database exists and is initialized if it doesn't already exist
    if not exists(databaseFilename):
        with databaseLock:
            with closing(sqlite3.connect(databaseFilename)) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute("CREATE TABLE channels (channelID INTEGER)")
                    cursor.execute("CREATE TABLE snipes (snipeID INTEGER, sniperID INTEGER, snipeeID INTEGER, voided BOOL)")
                    connection.commit()
    return


#########################

#CLIENT EVENTS

#########################

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    splitContent = message.content.split()
    if len(splitContent) > 1 and splitContent[0] == "snipe":
        print("Processing message " + message.content)
        if splitContent[1] == "admin":
            if message.author.guild_permissions.administrator:
                await processAdminCommand(message)
            else:
                await message.channel.send("You are not an administrator, please ping an administrator if you need to issue this command.")
        else:
            #we need to grab active channels here, admin doesn't require this channel and is active everywhere, but sniper game should be
            #delegated to its specific channel
            with databaseLock:
                with closing(sqlite3.connect(databaseFilename)) as connection:
                    with closing(connection.cursor()) as cursor:
                        validChannels = cursor.execute("SELECT channelID FROM channels").fetchall()
            if (message.channel.id,) in validChannels: #replace with dictionary/switch if it gets big enough
                if splitContent[1] == "leaderboard":
                    await getTop(message)
                elif splitContent[1] == "rank":
                    await getOwnRank(message)
                else:
                    await processSnipe(message)


#########################

#COMMAND FUNCTIONS

#########################

async def processSnipe(m):
    if(len(m.raw_mentions) == 0):
        #no mentions
        await m.channel.send("No snipee mention, please try again")
        return
    else:
        with databaseLock:
            with closing(sqlite3.connect(databaseFilename)) as connection:
                with closing(connection.cursor()) as cursor:
                    for snipee in m.raw_mentions:
                        cursor.execute("INSERT INTO snipes VALUES (?, ?, ?, 0)", (m.id, m.author.id, snipee))
                    connection.commit()
        await m.channel.send("Entry recorded")
    return

def createLeaderboards():
    #creates leaderboards of snipers and snipees
    #perhaps its better to keep a persistent leaderboard, but this is less prone to errors and shouldn't be run often
    with databaseLock:
        with closing(sqlite3.connect(databaseFilename)) as connection:
            with closing(connection.cursor()) as cursor:
                snipes = cursor.execute("SELECT * from snipes").fetchall()
    sniperMap = {}
    snipeeMap = {}
    for _, sniper, snipee, voided in snipes:
        if not voided:
            if sniper in sniperMap:
                sniperMap[sniper] = sniperMap[sniper] + 1
            else:
                sniperMap[sniper] = 1
            if snipee in snipeeMap:
                snipeeMap[snipee] = snipeeMap[snipee] + 1
            else:
                snipeeMap[snipee] = 1
    sniperLeaderboard = sniperMap.items()
    sniperLeaderboard = sorted(sniperLeaderboard, key = lambda x: x[1], reverse=True)
    #sniperLeaderboard.sort( reverse = True, key = lambda x: x[1])
    snipeeLeaderboard = snipeeMap.items()
    snipeeLeaderboard = sorted(snipeeLeaderboard, reverse = True, key = lambda x: x[1])
    return sniperLeaderboard, snipeeLeaderboard, sniperMap, snipeeMap



async def getTop(m):
    sniperLead, snipeeLead, _ , _ = createLeaderboards()
    sniperTable = "```\nSNIPER LEADERBOARD\nRANK    USER    SNIPES\n"
    for rank, entry in enumerate(sniperLead):
        if rank >= 20:
            break
        userID, snipeCount = entry
        user = client.get_user(userID)
        if user is None:
            user = await client.fetch_user(userID)
        sniperTable += str(rank + 1) + "    " + user.name + "#" + user.discriminator + "    " + str(snipeCount) + "\n"
    sniperTable += "```"

    #bit of boilerplate, possibly fix
    snipeeTable = "```\nSNIPEE LEADERBOARD\nRANK    USER    SNIPES\n" #wont be the nicest looking table but still should work for now
    for rank, entry in enumerate(snipeeLead):
        if rank >= 20: #currently only making a top 20 leaderboard
            break
        userID, snipeCount = entry
        user = client.get_user(userID)
        if user is None:
            user = await client.fetch_user(userID)
        snipeeTable += str(rank + 1) + "    " + user.name + "#" + user.discriminator + "    " + str(snipeCount) + "\n"
    snipeeTable += "```"
    await m.channel.send(sniperTable)
    await m.channel.send(snipeeTable)



async def getOwnRank(m):
    _, _, sniperLead, snipeeLead = createLeaderboards()
    rankString = ""
    if m.author.id not in sniperLead:
        rankString += "No snipes found"
    else:
        rankString += str(sniperLead[m.author.id]) + " snipes by you"
    rankString += "    |    "
    if m.author.id not in snipeeLead:
        rankString += "Never been sniped"
    else:
        rankString += str(snipeeLead[m.author.id]) + " snipes of you"
    if m.author.id in sniperLead and m.author.id in snipeeLead:
        rankString += "    |    " + "KDR is " + str(round(sniperLead[m.author.id]/snipeeLead[m.author.id], 3))
    await m.channel.send(rankString)

    


async def processAdminCommand(m):
    splitContent = m.content.split()

    if len(splitContent) == 4 and splitContent[2] == "void" and splitContent[3].isnumeric():
            #we void an entry here
            with databaseLock:
                with closing(sqlite3.connect(databaseFilename)) as connection:
                    with closing(connection.cursor()) as cursor:
                        cursor.execute("UPDATE snipes SET voided = 1 where snipeID = (?)", (splitContent[3],))
                        connection.commit()
            await m.channel.send("Voided")
    elif len(splitContent) == 3:
        if splitContent[2] == "setChannel":
            with databaseLock:
                with closing(sqlite3.connect(databaseFilename)) as connection:
                    with closing(connection.cursor()) as cursor:
                        print("INSERT INTO channels(channelID) VALUES (?) ", m.channel.id)
                        cursor.execute("INSERT INTO channels(channelID) VALUES (?)", (m.channel.id,))
                        connection.commit()
            await m.channel.send("Channel set")
                        
        elif splitContent[2] == "removeChannel":
            with databaseLock:
                with closing(sqlite3.connect(databaseFilename)) as connection:
                    with closing(connection.cursor()) as cursor:
                        print("DELETE FROM channels WHERE channelID=(?)", m.channel.id)
                        cursor.execute("DELETE FROM channels WHERE channelID=(?)", (m.channel.id,))
                        connection.commit()
            await m.channel.send("Channel removed")





databaseInit()
client.run(credentials.BOT_TOKEN)