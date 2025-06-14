import mysql.connector
from bs4 import BeautifulSoup
import requests

def getAllGames(url):
    allGames=[]
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    scoreTable = soup.find_all('table', {'class','ss-data'})
    for table in scoreTable:
        #rows of the the individual games in the game table
        gameRows = table.find_all('tr',{'class','notranslate'})
        for game in gameRows:
            allGames.append(game)
    return allGames
    

def gameFormatter(games):
    formattedGames = []
    for game in games:
        name = game.find('td',{'class','cls_player'}).text
        #first nine frames have the same name, but the tenth frame is named differently
        firstNine = game.find_all('td', {'class','cls_frame'})
        tenthFrame = game.find('td',{'class','cls_frame10'})
        invalidGame = False
        currentGame = []
        for i in range(10):
            #if it isn't the tenth frame, there isn't a thirdThrow to find
            if(i < 9):
                firstThrow = firstNine[i].find('td',{'class','cls_ball1'})
                secondThrow = firstNine[i].find('td',{'class','cls_ball2'})
            #tenth frame
            thirdThrow = 0
            if(i == 9):
                firstThrow = tenthFrame.find('td',{'class','cls_ball1'})
                secondThrow = tenthFrame.find('td',{'class','cls_ball2'})
                thirdThrow = tenthFrame.find('td',{'class', 'cls_ball3'})
            frame = []
            
            #all the possible outcomes for the first shot
            if(firstThrow):
                if(firstThrow.text == 'X'):
                    frame.append(10)
                elif(firstThrow.text == '-'):
                    frame.append(0)
                #this indicates this game is incomplete
                elif(firstThrow.text == ' ' or firstThrow.text == ''):
                    invalidGame = True
                else:
                    frame.append(int(firstThrow.text))
            else:
                invalidGame = True
            
            #all possible outcomes for the second shot
            if(secondThrow):
                
                #strike only possible for secondThrow in the tenth frame
                if(secondThrow.text == 'X'):
                    frame.append(10)
                elif(secondThrow.text == '-' or secondThrow.text == ' ' or secondThrow.text == ''):
                    frame.append(0)
                elif(secondThrow.text == '/'):
                    if(firstThrow.text == '-'):
                        frame.append(10)
                    else:
                        #finds the number of pins down using the first shot
                        score = 10 - int(firstThrow.text)
                        frame.append(score)
                else:
                    frame.append(int(secondThrow.text))
            
            #tenth frame
            if(i == 9):    
                
                #all possible outcomes for the third shot
                if(thirdThrow):
                    if(thirdThrow.text == 'X'):
                        frame.append(10)
                    elif(thirdThrow.text == '-' or thirdThrow.text == ' ' or thirdThrow.text == ''):
                        frame.append(0)
                    elif(thirdThrow.text == '/'):
                        if(secondThrow.text == '-'):
                            frame.append(10)
                        else:
                            score = 10 - int(secondThrow.text)
                            frame.append(score)
                    else:
                        frame.append(int(thirdThrow.text))
            currentGame.append(frame)
            #reset the frame list
            frame = []
        #if the game was finished to completion, add it to the list of games
        if(not invalidGame):
            currentGame.append(name)
            formattedGames.append(currentGame)
        #reset the invalid game checker and the currentGame list
        invalidGame = False
        currentGame = []
    return formattedGames


def calculateScores(game):
    totalScore = 0
    prevShot = 0 #0-open,1-spare,2-strike
    twoStrikes = False
    
    #loops through 10 frames
    for i in range(10):
        firstShot = 0
        secondShot = 0
        thirdShot = 0
        
        #gets the amount of pins per shot
        if game[i][0]:
            firstShot = game[i][0]
        if len(game[i]) >= 2:
            secondShot = game[i][1]
        if i == 9 and len(game[i]) == 3:
            thirdShot = game[i][2]
        #last shot was open
        if prevShot == 0:
            totalScore += int(firstShot)
            totalScore += int(secondShot)
        #last shot was a spare
        elif prevShot == 1:
            totalScore += (int(firstShot) * 2)
            totalScore += int(secondShot)
        #last shot was a strike
        elif prevShot == 2:
            #last two shots were strikes
            if twoStrikes:
                totalScore += (int(firstShot) * 3)
                totalScore += (int(secondShot) * 2)
            else:
                totalScore += (int(firstShot) * 2)
                totalScore += (int(secondShot) * 2)
        if(int(firstShot) + int(secondShot)) >= 10:
            if int(firstShot) == 10:
                if prevShot == 2:
                    twoStrikes = True
                prevShot = 2
                
            else:
                prevShot = 1
                twoStrikes = False
        else: 
            prevShot = 0
            twoStrikes = False
        totalScore += int(thirdShot)
    return totalScore

def strikeCounter(game):
    strikes = 0
    for i in range(10):
        firstShot = 0
        secondShot = 0
        thirdShot = 0
        #gets the amount of pins per shot if that shot exists
        if game[i][0]:
            firstShot = game[i][0]
        if len(game[i]) >= 2:
            secondShot = game[i][1]
        if i == 9 and len(game[i]) == 3:
            thirdShot = game[i][2]
        
        #got the strike
        if(int(firstShot) == 10):
            strikes+=1
            #tenth frame
            if(i==9):
                #if the first shot was a strike in the 10th frame, another chance at a strike
                if(int(secondShot) == 10):
                    strikes+=1
                    #if the second shot was also a strike in the 10th, thats another strike opportunity
                    if(int(thirdShot == 10)):
                        strikes+=1
        #didn't get the strike(chance for a spare)
        else:
            if(int(firstShot) + int(secondShot) == 10):
                #if spare in the 10th frame, the third shot could be a strike
                if(i==9):
                    if(int(thirdShot) == 10):
                        strikes+=1
    return strikes

def spareCounter(game):
    spares = 0
    for i in range(10):
        firstShot = 0
        secondShot = 0
        thirdShot = 0
        
        #gets the amount of pins per shot if that shot exists
        if game[i][0]:
            firstShot = game[i][0]
        if len(game[i]) >= 2:
            secondShot = game[i][1]
        if i == 9 and len(game[i]) == 3:
            thirdShot = game[i][2]
        
        #got the strike
        if(int(firstShot) == 10):
            #tenth frame
            if(i==9):
                #if the first shot was a strike in the 10th frame and the second one wasn't,
                #another spare opportunity
                if(int(secondShot) < 10):               
                    if(int(secondShot)+int(thirdShot) == 10):
                        spares+=1
        #didn't get the strike(chance for a spare)
        else:
            if(int(firstShot) + int(secondShot) == 10):
                spares+=1
    return spares

def strikeOpportunityCounter(game):
    strikeOpportunity = 0
    for i in range(10):
        #the start of every frame is a strike opportunity, so minimum is ten
        strikeOpportunity+=1
        firstShot = 0
        secondShot = 0
        thirdShot = 0
        
        #gets the amount of pins per shot if that shot exists
        if game[i][0]:
            firstShot = game[i][0]
        if len(game[i]) >= 2:
            secondShot = game[i][1]
        if i == 9 and len(game[i]) == 3:
            thirdShot = game[i][2]
        
        #got the strike
        if(int(firstShot) == 10):
            #tenth frame, the second shot is another strike opportunity
            if(i==9):
                strikeOpportunity+=1
                #if the second shot was also a strike, thats another shot opportunity
                if(int(secondShot) == 10):                    
                    strikeOpportunity+=1
        else:
            if(int(firstShot) + int(secondShot) == 10):
                if(i==9):
                    strikeOpportunity+=1
    return strikeOpportunity

def spareOpportunityCounter(game):
    spareOpportunity = 0
    for i in range(10):
        firstShot = 0
        secondShot = 0
        thirdShot = 0
        
        #gets the amount of pins per shot if that shot exists
        if game[i][0]:
            firstShot = game[i][0]
        if len(game[i]) >= 2:
            secondShot = game[i][1]
        if i == 9 and len(game[i]) == 3:
            thirdShot = game[i][2]
        
        #got the strike
        if(int(firstShot) == 10):
            #tenth frame
            if(i==9):
                #if the first shot was a strike in the 10th frame and the second shot wasn't thats another
                #spare opportunity
                if(int(secondShot) < 10):                 
                    spareOpportunity+=1
        else:
            spareOpportunity+=1
    
    return spareOpportunity

def getDate(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    date = soup.find('h2',{'class', 'scoredate'}).text
    date = date.split()
    return date[1]

def getName(game):
    length = len(game)
    nameIndex = length-1
    return game[nameIndex]

def dateFormatter(date):
    dateList = date.split('/')
    if(int(dateList[0]) < 10 and int(dateList[1]) < 10):
        date = dateList[2]+'-0'+dateList[0]+'-0'+dateList[1]
    elif(int(dateList[0]) >= 10 and int(dateList[1]) < 10):
        date = dateList[2]+'-'+dateList[0]+'-0'+dateList[1]
    elif(int(dateList[0]) < 10 and int(dateList[1]) >= 10):
        date = dateList[2]+'-0'+dateList[0]+'-'+dateList[1]
    else:
        date = dateList[2]+'-'+dateList[0]+'-'+dateList[1]
    return date
if __name__ == "__main__":
    bowlingUrls = ['https://www.syncpassport.com/MyScores/ScSession?eid=Z2NGQOpgHXNW3u0xxOhRHVqB4KAxYQFCOS6aCWzZvUvqdj4xw6lrY9czHEO_gZW60&sessionIdentifier=35e240ba44044b648e359cc84320db4a',
    'https://www.syncpassport.com//MyScores/ScSession?eid=gcF%40%ea%60%1dsV%de%ed1%c4%e8Q%1dZ%81%e0%a01a%01B9.%9a%09l%d9%bdK%eav%3e1%c3%a9kc%d73%1cC%bf%81%95%ba&sessionIdentifier=0fa73314d1a4429282edfe6ff47ec0e8',
    'https://www.syncpassport.com//MyScores/ScSession?eid=TBC&sessionIdentifier=eadb3a5c741343ad8fe00a243369c066',
    'https://www.syncpassport.com/MyScores/ScSession?eid=Z2NGQOpgHXNW3u0xxOhRHVqB4KAxYQFCOS6aCWzZvUvqdj4xw6lrY9czHEO_gZW60&sessionIdentifier=49bb20eb7ab44443944a39895bc2f0e7',
    'https://www.syncpassport.com/MyScores/ScSession?eid=Z2NGQOpgHXNW3u0xxOhRHVqB4KAxYQFCOS6aCWzZvUvqdj4xw6lrY9czHEO_gZW60&sessionIdentifier=e2fac6a2cbb54110adf9885023d4b45e',
    'https://www.syncpassport.com/MyScores/ScSession?eid=Z2NGQOpgHXNW3u0xxOhRHVqB4KAxYQFCOS6aCWzZvUvqdj4xw6lrY9czHEO_gZW60&sessionIdentifier=423aea5edde04e79b097997b6235a9e0',
    'https://www.syncpassport.com//MyScores/ScSession?eid=gcF%40%ea%60%1dsV%de%ed1%c4%e8Q%1dZ%81%e0%a01a%01B9.%9a%09l%d9%bdK%eav%3e1%c3%a9kc%d73%1cC%bf%81%95%ba&sessionIdentifier=a9048f36096c4e3dbc510ddad20140dc',
    'https://www.syncpassport.com//MyScores/ScSession?eid=gcF%40%ea%60%1dsV%de%ed1%c4%e8Q%1dZ%81%e0%a01a%01B9.%9a%09l%d9%bdK%eav%3e1%c3%a9kc%d73%1cC%bf%81%95%ba&sessionIdentifier=c887392fed4a4a219efe609df17857b9',
    'https://www.syncpassport.com//MyScores/ScSession?eid=TBC&sessionIdentifier=677b7305cd7642b7af4eb07c62950600',
    'https://www.syncpassport.com//MyScores/ScSession?eid=TBC&sessionIdentifier=7ddeb42f512f4261b87752e7ff1ae07f',
    'https://www.syncpassport.com//MyScores/ScSession?eid=TBC&sessionIdentifier=d7eed73f9e23495b84b786011fe6c76c',
    'https://www.syncpassport.com//MyScores/ScSession?eid=TBC&sessionIdentifier=bd521892116b4ee78b09dd49b427f87a',
    'https://www.syncpassport.com//MyScores/ScSession?eid=TBC&sessionIdentifier=b7c8e15a94874a7ba794c9ca6a4f2f28',
    'https://www.syncpassport.com//MyScores/ScSession?eid=TBC&sessionIdentifier=4925dac1c53b4ad9a27f561b3cc5c42d',
    'https://www.syncpassport.com//MyScores/ScSession?eid=TBC&sessionIdentifier=57512d0528274bd2af5bff89ebd9be53',
    'https://www.syncpassport.com//MyScores/ScSession?eid=TBC&sessionIdentifier=a6961e3095504c53885fa9572427b698',
    'https://www.syncpassport.com//MyScores/ScSession?eid=TBC&sessionIdentifier=4400e567f377459db887df5a102c472d',
    'https://www.syncpassport.com//MyScores/ScSession?eid=TBC&sessionIdentifier=e2a2efd827624123800a2f7f9654470d',
    'https://www.syncpassport.com//MyScores/ScSession?eid=TBC&sessionIdentifier=e9e9844fe9084886bb38c5bb1ffee3b8',
    'https://www.syncpassport.com//MyScores/ScSession?eid=TBC&sessionIdentifier=903b2f6586384367abf68934cf3cf59a',
    'https://www.syncpassport.com//MyScores/ScSession?eid=TBC&sessionIdentifier=fd11fdb3cfe8426aba1f5721020f494a',
    'https://www.syncpassport.com//MyScores/ScSession?eid=TBC&sessionIdentifier=f8762facca714a5b92c26f9b271f5d73',
    'https://www.syncpassport.com//MyScores/ScSession?eid=TBC&sessionIdentifier=541b9d571a034984b425a3c43a609f89',
    'https://www.syncpassport.com//MyScores/ScSession?eid=TBC&sessionIdentifier=45b519e595244b8e9c8429f7909ac307',
    'https://www.syncpassport.com//MyScores/ScSession?eid=TBC&sessionIdentifier=6d72876ea08c4723bfdc765a0ede1650',
    'https://www.syncpassport.com//MyScores/ScSession?eid=TBC&sessionIdentifier=7e622993ddf54c7c9cde338aa1d96ba5',
    'https://www.syncpassport.com//MyScores/ScSession?eid=%9a%26%abx%f9%19%3a%f8%b28+%ce%22%f5%9f%c3%0c%5d%e3w%a7%3c%8c%ea%b1%c4%96%9d%f5o%d6%ba%dd%cf%ae%ae%b9%13L2m%98t%08%fd%a90%e5&sessionIdentifier=4a8a762b1066411e880e32195b948a4c',
    'https://www.syncpassport.com//MyScores/ScSession?eid=%9a%26%abx%f9%19%3a%f8%b28+%ce%22%f5%9f%c3%0c%5d%e3w%a7%3c%8c%ea%b1%c4%96%9d%f5o%d6%ba%dd%cf%ae%ae%b9%13L2m%98t%08%fd%a90%e5&sessionIdentifier=fa159362a4754871a39842e0a180e4d9',
    'https://www.syncpassport.com/MyScores/ScSession?eid=miarePkZOviyOCDOIvWfwwxd43enPIzqscSWnfVv1rrdz66uuRNMMm2YdAj9qTDl0&sessionIdentifier=fd6008e2dd2b4e9fb0266e1ed2c194f6',
    'https://www.syncpassport.com/MyScores/ScSession?eid=miarePkZOviyOCDOIvWfwwxd43enPIzqscSWnfVv1rrdz66uuRNMMm2YdAj9qTDl0&sessionIdentifier=8fe35c145061499cbc595f96f1c7f105',
    'https://www.syncpassport.com//MyScores/ScSession?eid=%9a%26%abx%f9%19%3a%f8%b28+%ce%22%f5%9f%c3%0c%5d%e3w%a7%3c%8c%ea%b1%c4%96%9d%f5o%d6%ba%dd%cf%ae%ae%b9%13L2m%98t%08%fd%a90%e5&sessionIdentifier=6f2e28d676c24e8ca0893af70e948c0b',
    'https://www.syncpassport.com/MyScores/ScSession?eid=miarePkZOviyOCDOIvWfwwxd43enPIzqscSWnfVv1rrdz66uuRNMMm2YdAj9qTDl0&sessionIdentifier=317cbc52a7fa4f868b3c0ba30e4e1d7b',
    'https://www.syncpassport.com/MyScores/ScSession?eid=miarePkZOviyOCDOIvWfwwxd43enPIzqscSWnfVv1rrdz66uuRNMMm2YdAj9qTDl0&sessionIdentifier=ef3b07dc183b4cd09941937120ce5ba3',
    'https://www.syncpassport.com/MyScores/ScSession?eid=miarePkZOviyOCDOIvWfwwxd43enPIzqscSWnfVv1rrdz66uuRNMMm2YdAj9qTDl0&sessionIdentifier=fba0fdd5308344cc94c4159056c7f1ff',
    'https://www.syncpassport.com/MyScores/ScSession?eid=miarePkZOviyOCDOIvWfwwxd43enPIzqscSWnfVv1rrdz66uuRNMMm2YdAj9qTDl0&sessionIdentifier=7b7ca5e78253418eb5bddd8dc2d460b9',
    'https://www.syncpassport.com//MyScores/ScSession?eid=TBC&sessionIdentifier=80b1e9aa5d2d497faaec3dcb48139041']

      mydb = mysql.connector.connect(host = <host>, 
                                user = <user>, 
                                passwd=<password>)

    cursor = mydb.cursor()
    idCounter = 0
    cursor.execute("CREATE DATABASE Bowling_Data;")
    cursor.execute("USE Bowling_Data;")
    games = (
        "CREATE TABLE `games` ("
        "  `gameID` int,"
        "  `name` varchar(255),"
        "  `date` date,"
        "  `score` int,"
        "  `strikes` int,"
        "  `strikeOs` int,"
        "  'spares' ,int"
        " 'spareOs', int"
        "'url', varchar(255)"
        ")")
    cursor.execute("CREATE TABLE games ("
    "  `gameID` int,"
    "  `name` varchar(255),"
    "  `date` date,"
    "  `score` int,"
    "  `strikes` int,"
    "  `strikeOs` int,"
    "  `spares` int,"
    "  `spareOs` int,"
    "  `url` varchar(255)"
    ")")
    for url in bowlingUrls:
        date = getDate(url)
        date = dateFormatter(date)
        gameTables = getAllGames(url)
        formattedGames = gameFormatter(gameTables)
        if(formattedGames):
            scores = []
            for game in formattedGames:
                name = getName(game)
                score = calculateScores(game)
                strikes = strikeCounter(game)
                strikeOs = strikeOpportunityCounter(game)
                spares = spareCounter(game)
                spareOs = spareOpportunityCounter(game)
                cursor.execute("""
                INSERT INTO games (gameID, name, date, score, strikes, strikeOs, spares, spareOs, url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (idCounter, name, date, score, strikes, strikeOs, spares, spareOs, url))
                idCounter+=1

    mydb.commit()
    cursor.close()
    mydb.close()