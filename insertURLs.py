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
    stopAsking = False
    bowlingUrls =[]
    while(not stopAsking):
        url = input("Enter the URL you want to add to the database.(type END to stop)")
        if(url == 'END'):
            stopAsking = True
        else:
            bowlingUrls.append(url)

    mydb = mysql.connector.connect(host = <host>, 
                                user = <user>, 
                                passwd=<password>,
                                database=<database>)

    cursor = mydb.cursor()
    cursor.execute("select max(gameID) from games")
    result = cursor.fetchone()
    idCounter = int(result[0])+1
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
