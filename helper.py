# helper file to hold functions for projectionAnalysis.py
import pandas as pd
import numpy

def rankByProjection(dataFrame, playerIndex, rankingsDict, rankType):
    dataFrame = dataFrame.sort_values(by=['PROJ PTS'], ascending=False)
    dataFrame = dataFrame.reset_index(drop=True)
    position = dataFrame.loc[playerIndex, 'POSITION']
    positionRankingVar = position + "_" + rankType + "_Rank"
    positionRanking = position + str(rankingsDict[positionRankingVar])
    rankingsDict[positionRankingVar] += 1
    rankColName = "POS " + rankType + " RANK"
    dataFrame.loc[playerIndex, rankColName] = positionRanking
    return positionRanking


# get the average projected points for the round and position passed, position can be "ALL" to include all positions
# round number passed should be greater than or equal to one
# I am in a league with 2 quarterbacks so that's why I project based on this column rather than ADP RANK
def AveragePointsForRound(projectionsDF, roundNumber, position, NUMBER_OF_TEAMS):
    # first pick is offset by the number of picks already made in previous rounds
    firstPick = NUMBER_OF_TEAMS * (roundNumber - 1) + 1
    lastPick = firstPick + 11
    if (position == "ALL"):
        projectedPlayersInRound = projectionsDF[(projectionsDF['2QB RANK'] >= firstPick) &
                                                (projectionsDF['2QB RANK'] <= lastPick)]
        average = projectedPlayersInRound['PROJ PTS'].sum() / NUMBER_OF_TEAMS
    else:
        projectedPlayersInRound = projectionsDF[(projectionsDF['2QB RANK'] >= firstPick) &
                                                (projectionsDF['2QB RANK'] <= lastPick) &
                                                (projectionsDF['POSITION'] == position)]
        NumPlayersOfPositionInRound = len(projectedPlayersInRound)
        if (NumPlayersOfPositionInRound > 0):
            average = projectedPlayersInRound['PROJ PTS'].sum() / NumPlayersOfPositionInRound
        else:
            average = 0
    return average


# I am in a league with 2 quarterbacks so that's why I project based on this column rather than ADP RANK
def MaxProjPointsForRound(projectionsDF, roundNumber, position, NUMBER_OF_TEAMS):
    # first pick is offset by the number of picks already made in previous rounds
    firstPick = NUMBER_OF_TEAMS * (roundNumber - 1) + 1
    lastPick = firstPick + 11
    if (position == "ALL"):
        projectedPlayersInRound = projectionsDF[(projectionsDF['2QB RANK'] >= firstPick) &
                                                (projectionsDF['2QB RANK'] <= lastPick)]
        max = projectedPlayersInRound['PROJ PTS'].max()
    else:
        projectedPlayersInRound = projectionsDF[(projectionsDF['2QB RANK'] >= firstPick) &
                                                (projectionsDF['2QB RANK'] <= lastPick) &
                                                (projectionsDF['POSITION'] == position)]
        NumPlayersOfPositionInRound = len(projectedPlayersInRound)
        if (NumPlayersOfPositionInRound > 0):
            max = projectedPlayersInRound['PROJ PTS'].max()
        else:
            max = 0
    return max

# finds the top 5 largest differences in projected points for a given position
# returns list holding strings containing point difference and player involved
def findBiggestPostionalGaps(positionalDF, NumberOfGaps):
    positionalDF = positionalDF.sort_values(by=['PROJ PTS'], ascending=False)
    positionalDF = positionalDF.reset_index(drop=True)
    biggestPointDifferencesList = []
    biggestPointDifferencesPlayersList = []
    for i in range(0,len(positionalDF) - 1):
        firstPlayerPoints = positionalDF.loc[i,'PROJ PTS']
        firstPlayerName = positionalDF.loc[i,'PLAYER']
        secondPlayerPoints = positionalDF.loc[i + 1, 'PROJ PTS']
        secondPlayerName = positionalDF.loc[i + 1, 'PLAYER']
        # players are sorted by projected points so this will always be positive
        pointDiff = round(firstPlayerPoints - secondPlayerPoints, 1)
        # store the difference and players if it is one of 5 biggest differences
        if (len(biggestPointDifferencesList) < NumberOfGaps):
            biggestPointDifferencesList.append(pointDiff)
            biggestPointDifferencesPlayersList.append(firstPlayerName + " and " + secondPlayerName)
        else:
            # check if the difference is greater than the smallest difference stored
            minDifference = min(biggestPointDifferencesList)
            minDifferenceIndex = biggestPointDifferencesList.index(minDifference)
            # replace the minimum difference from the list if this difference is greater than it
            if (pointDiff > minDifference):
                biggestPointDifferencesList[minDifferenceIndex] = pointDiff
                biggestPointDifferencesPlayersList[minDifferenceIndex] = (firstPlayerName + " and " + secondPlayerName)
    # put the largest differences in order after going through the differences for all consecutive players
    sortedDifferences = biggestPointDifferencesList.copy()
    sortedDifferences.sort(reverse=True)
    orderedPointDifferencesPlayers = [""] * NumberOfGaps
    # argsort returns a list that is the order of indeces that would result in sorted order
    # e.g. argsort([1,2,0]) yields [2,0,1]
    # changed result of argsort to do descending order
    sorted_indeces = numpy.argsort(biggestPointDifferencesList)[::-1]
    # put players in same order as their sorted differences
    for j in range(0,NumberOfGaps):
        orderedIndex = sorted_indeces[j]
        orderedPointDifferencesPlayers[j] = biggestPointDifferencesPlayersList[orderedIndex]
    combinedPointsPlayersList = []
    # combine the difference and player names into one array
    for k in range(0, NumberOfGaps):
        combinedPointsPlayersList.append(str(sortedDifferences[k]) + " points between " + orderedPointDifferencesPlayers[k])
    return combinedPointsPlayersList

def writeStats(reportFile,statList):
    for i in range(0,len(statList)):
        reportFile.write("\t" + statList[i] + "\n")

# input a dataframe, stat (touchdowns, yards, receptions), and number of players to return
def findHighestForStat(positionalDF, stat, numPlayers):
    positionalDF = positionalDF.reset_index(drop=True)
    highestNums = []
    highestPlayers = []
    statColNames = []
    if (stat == 'touchdowns'):
        statColNames = ['PASS TD', 'RUSH TD', 'REC TD']
    elif (stat == 'yards'):
        statColNames = ['PASS YDS', 'RUSH YDS', 'REC YDS']
    elif (stat == 'receptions'):
        statColNames = ['REC']

    for i in range(0,len(positionalDF)):
        calculatedStat = 0
        for colName in statColNames:
            calculatedStat += positionalDF.loc[i,colName]
        calculatedStat = round(calculatedStat,1)
        if (len(highestNums) < numPlayers):
            highestNums.append(calculatedStat)
            highestPlayers.append(positionalDF.loc[i,'PLAYER'])
        else:
            minimumStat = min(highestNums)
            minimumStatIndex = highestNums.index(minimumStat)
            # replace the minimum stat from the list if this calculated stat is greater than it
            if (calculatedStat > minimumStat):
                highestNums[minimumStatIndex] = calculatedStat
                highestPlayers[minimumStatIndex] = positionalDF.loc[i,'PLAYER']
    sortedStats = highestNums.copy()
    sortedStats.sort(reverse=True)
    orderedStatsPlayers = [""] * numPlayers
    # argsort returns a list that is the order of indeces that would result in sorted order
    # e.g. argsort([1,2,0]) yields [2,0,1]
    # changed result of argsort to do descending order
    sorted_indeces = numpy.argsort(highestNums)[::-1]
    # put players in same order as their sorted stats
    for k in range(0,numPlayers):
        orderedIndex = sorted_indeces[k]
        orderedStatsPlayers[k] = highestPlayers[orderedIndex]
    combinedStatsPlayersList = []
    # combine the stat and player names into one array
    for n in range(0, numPlayers):
        combinedStatsPlayersList.append(str(sortedStats[n]) + " " + stat + " for " + orderedStatsPlayers[n])
    return combinedStatsPlayersList

def writeTDsYdsRec(statName, position, positionalDF, numPlayers, reportFile):
    highestStatsInPosition = findHighestForStat(positionalDF,statName,numPlayers)
    reportFile.write("MOST PROJECTED " + statName.upper() + " FOR " + position.upper() + "\n")
    writeStats(reportFile,highestStatsInPosition)
    reportFile.write("\n")

def valueOverBenchPlayer(projectionsDF, playerIndex,NumberOfTeams ,TwoQBFlag):
    projectionsDF = projectionsDF.sort_values(by=['PROJ PTS'], ascending=False)
    projectionsDF = projectionsDF.reset_index(drop=True)
    # determine the baseline player, which is best bench player at the position
    position = projectionsDF.loc[playerIndex,'POSITION']
    if (position == 'RB'):
        firstBenchIndex = 2 * NumberOfTeams
    elif (position =='QB'):
        if (TwoQBFlag):
            firstBenchIndex = 2 * NumberOfTeams
        else:
            firstBenchIndex = NumberOfTeams
    elif (position == 'WR'):
        firstBenchIndex = 3 * NumberOfTeams
    elif (position == 'TE' or position == 'K' or position == 'D/ST'):
        firstBenchIndex = NumberOfTeams
    positionalDF = projectionsDF[projectionsDF['POSITION'] == position]
    positionalDF = positionalDF.reset_index(drop=True)
    baselinePlayerPoints = positionalDF.loc[firstBenchIndex]['PROJ PTS']

    # determine value of current player over baseline player
    currentPlayerProjPts = projectionsDF.loc[playerIndex]['PROJ PTS']
    valueAboveBenchPlayer = currentPlayerProjPts - baselinePlayerPoints

    return round(valueAboveBenchPlayer,1)