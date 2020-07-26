import sqlite3
import plotly.express as px
import plotly

db = sqlite3.connect("discordData.db")

cursor = db.cursor()

all = cursor.execute("SELECT discordID,time,actionTaken FROM userData WHERE actionTaken == 'DISCONNECTED' OR actionTaken == 'CONNECTED' ORDER BY time").fetchall()


userTimes = {}

uniqueUsers = [] #Jeder User der in der Datenbank vorkommt ist in diesem Array gespeichert (unique)

for dbEntry in all:
    user = dbEntry[0]
    if user in uniqueUsers:
        pass
    else:
        uniqueUsers.append(user)
print(uniqueUsers)


pairs = []
for user in uniqueUsers:
    print(user)
    group = []
    query = cursor.execute("SELECT time,actionTaken from userData WHERE (actionTaken == 'DISCONNECTED' OR actionTaken == 'CONNECTED') AND discordID = ? ORDER BY time",(user,)).fetchall()
    count = 0
    for entry in query:
        #print(entry,datetime.utcfromtimestamp(int(entry[0])).strftime('%Y-%m-%d %H:%M:%S'))
        if entry[1] == "CONNECTED":
            if count+1 < len(query):
                if query[count+1][1] != "CONNECTED":
                    group.append([entry[0],query[count+1][0]])
                else:
                    continue
            else:
                #print("ENDE GELÄNDE")
                break
        count+=1
    userTimes[user] = group

print(userTimes)


usernames = []
connectedMinutes = []
totalDiscordMinutes = 0



usersConnectedMuted = {}

for user in userTimes:
    totalTimeConnected = 0
    for timePair in userTimes[user]:
        totalTimeConnected += int(timePair[1]) - int(timePair[0])
    username = cursor.execute("SELECT username FROM userData WHERE discordID=?",(user,)).fetchone()
    print("UserID {}: was connected for {}".format(username[0],int(totalTimeConnected/60)))
    usernames.append(username[0])
    connectedMinutes.append(int(totalTimeConnected/60))
    totalDiscordMinutes += int(totalTimeConnected/60)

    usersConnectedMuted[user] = [username[0],int(totalTimeConnected/60),0,0]
# Pie chart, where the slices will be ordered and plotted counter-clockwise:

count = 0
for minutes in connectedMinutes:
    percentage = str(round(minutes/totalDiscordMinutes*100,2))
    usernames[count] = usernames[count] + " " + percentage + "%"
    count += 1

for user in userTimes:
    print()
    print(user)
    totalTimeMuted = 0
    for timeInterval in userTimes[user]:
        interval = cursor.execute("SELECT time,selfMuteAfter FROM userData WHERE (time>=? AND time<=?) AND discordID = ? ORDER BY time",(timeInterval[0],timeInterval[1],user,)).fetchall()
        set = False
        lastMutedTimestamp = 0
        for entry in interval:
            if (entry[1] == "1") and (set == False):
                lastMutedTimestamp = entry[0]
                set = True
            elif (entry[1] == "0") and (set==True):
                totalTimeMuted += (entry[0] - lastMutedTimestamp)
                lastMutedTimestamp = 0
                set = False
            elif (lastMutedTimestamp != 0) and (entry[1] == 'None') and (set==True):
                totalTimeMuted += entry[0] - lastMutedTimestamp
                lastMutedTimestamp = 0
                set = False
            else:
                pass


    username = cursor.execute("SELECT username FROM userData WHERE discordID=?", (user,)).fetchone()
    print(username[0])
    print("UserID {}: was muted for {}".format(user,totalTimeMuted/60))
    usersConnectedMuted[user][2] = int(totalTimeMuted/60)
    usersConnectedMuted[user][3] = round(usersConnectedMuted[user][2]/usersConnectedMuted[user][1]*100,2)

db.close()


print(usersConnectedMuted)          #[0] Username, [1] Connected, [2] Muted, [3] Wie viel % der Zeit die man hier ist ist die Person muted

#patches, texts = plt.pie(connectedMinutes, startangle=90)
#plt.legend(patches, usernames, loc=(0.85,0))
#plt.tight_layout()
#plt.show()


chars = ["Total Time"]
parents = [""]
values = [totalDiscordMinutes/60]

for entry in usersConnectedMuted:
    username = usersConnectedMuted[entry][0]
    usernameAFK = username + " Muted"
    chars.append(username)
    chars.append(usernameAFK)
    parents.append("Total Time")
    parents.append(username)
    connectedMinutes = usersConnectedMuted[entry][1]/60     #Divided by 60 to get hours
    mutedMinutes = usersConnectedMuted[entry][2]/60
    values.append(connectedMinutes)
    values.append(mutedMinutes)


data = dict(
    character=chars,
    parent=parents,
    value=values)

fig =px.sunburst(
    data,
    names='character',
    parents='parent',
    values='value',
    branchvalues='total',
    title="Connection Times on Jukemasters Discord plotted by Users",

)
fig.show()
plotly.offline.plot(fig, filename = 'discordData.html', auto_open=False)