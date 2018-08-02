import pandas as pd
import numpy

NUMBER_OF_TEAMS = 12
NUMBER_OF_ROUNDS = 16
# NUMBER_BIGGEST_GAPS is used for findBiggestPositionalGaps(), tells function to find the n largest gaps between
# consecutively projected players of same position
NUMBER_BIGGEST_GAPS = 5
N_PLAYERS_MOST_STATS = 5 # display top n players for stats

# other ideas for functions are top n touchdowns for QB, RB, WR, TE
# top receptions for RB, TE, WR
# top yards for QB, RB, WR, TE, don't include rushing yards for QB


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
def AveragePointsForRound(projectionsDF, roundNumber, position):
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
def MaxProjPointsForRound(projectionsDF, roundNumber, position):
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

def valueAboveBenchPlayer(projectionsDF, playerIndex,NumberOfTeams ,TwoQBFlag):
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

    return valueAboveBenchPlayer

def main():
    report = open("Fantasy Report.txt", "w")

    # set up data frames
    projections = pd.read_csv("Web Scraped Projections.csv")
    defenses = pd.read_csv("Defense Projections.csv")

    # rank the players by position based on total projected points and average draft position (ADP)
    # e.g. RB1, RB2, QB1, QB2, WR1, WR2, etc.
    rankingsDict = {}
    rankingsDict['RB_PROJ_Rank'] = 1
    rankingsDict['WR_PROJ_Rank'] = 1
    rankingsDict['QB_PROJ_Rank'] = 1
    rankingsDict['TE_PROJ_Rank'] = 1
    rankingsDict['D_PROJ_Rank'] = 1
    rankingsDict['K_PROJ_Rank'] = 1
    projections['POS PROJ RANK'] = ""
    defenses['POS PROJ RANK'] = 0

    # rank the players by position on projected points
    for i in range(0, len(projections)):
        rankByProjection(projections, i, rankingsDict, 'PROJ')

    # rank the defenses by projected points
    defenses = defenses.sort_values(by=['PROJ PTS'], ascending=False)
    defenses = defenses.reset_index(drop=True)
    for i in range(0, len(defenses)):
        defenses.loc[i, 'POS PROJ RANK'] = rankingsDict['D_PROJ_Rank']
        rankingsDict['D_PROJ_Rank'] += 1


    # concatenate the player and ADP columns of projections and defense to get rank by ADP
    # need PROJ PTS column to sort on if ADP is null
    PlayersAndDefense = pd.concat([projections[['PLAYER','POSITION','ADP','2QB RANK','PROJ PTS']],
                                   defenses[['TEAM','POSITION','ADP','2QB RANK','PROJ PTS']].rename(columns={'TEAM': 'PLAYER'})],
                                  ignore_index=True)
    PlayersAndDefense = PlayersAndDefense.sort_values(by=['ADP', 'PROJ PTS'], ascending=[True, False])
    PlayersAndDefense = PlayersAndDefense.reset_index(drop=True)
    ADP_Rank = 1
    PlayersAndDefense['ADP RANK'] = 0
    # rank in order or ADP, if no ADP then by projected points
    for i in range(0, len(PlayersAndDefense)):
        playerADP = PlayersAndDefense.loc[i, 'ADP']
        PlayersAndDefense.loc[i, 'ADP RANK'] = ADP_Rank
        ADP_Rank += 1

    # merge ADP Rank onto the projections and defense tables
    projections = projections.merge(PlayersAndDefense[['PLAYER', 'ADP RANK']], left_on='PLAYER', right_on='PLAYER',
                                    how='left')
    defenses = defenses.merge(PlayersAndDefense[['PLAYER', 'ADP RANK']], left_on='TEAM', right_on='PLAYER', how='left')

    runningBacks = projections[projections['POSITION'] == 'RB']
    wideRecievers = projections[projections['POSITION'] == 'WR']
    quarterbacks = projections[projections['POSITION'] == 'QB']
    tightEnds = projections[projections['POSITION'] == 'TE']
    kickers = projections[projections['POSITION'] == 'K']

    # for each position or all positions, generate the average and max projected points for each round, write to report
    for position in ['ALL', 'RB', 'WR', 'QB', 'TE', 'D/ST']:
        # set up a header for stats on this position
        if (position == 'ALL'):
            report.write("AVERAGE AND MAX PROJECTED POINTS FOR ALL PLAYERS IN EACH ROUND\n\n")
        else:
            report.write("AVERAGE AND MAX PROJECTED POINTS FOR " + position + " IN EACH ROUND\n\n")
        # get average per round
        for i in range(1, NUMBER_OF_ROUNDS + 1):
            if position == 'ALL':
                report.write("Average projected points per player in Round " +
                             str(i) + ": " + str(AveragePointsForRound(PlayersAndDefense, i, position)) + "\n")
            else:
                report.write("Average projected points per " + position + " in Round " +
                             str(i) + ": " + str(AveragePointsForRound(PlayersAndDefense, i, position)) + "\n")
        report.write("\n")
        # get max per round
        for i in range(1, NUMBER_OF_ROUNDS + 1):
            if position == 'ALL':
                report.write("Max points of player projected to be drafted in Round " + str(i) + ": " +
                             str(MaxProjPointsForRound(PlayersAndDefense, i, position)) + "\n")
            else:
                report.write("Max points of " + position + " projected to be drafted in Round " + str(i) + ": " +
                             str(MaxProjPointsForRound(PlayersAndDefense, i, position)) + "\n")
        report.write("\n")
        report.write("----------------------------------------------------------------")
        report.write("\n\n")


    # find the biggest gaps in projected points between consecutively ranked players for each set of positions
    RB_Gaps = findBiggestPostionalGaps(runningBacks,NUMBER_BIGGEST_GAPS)
    WR_Gaps = findBiggestPostionalGaps(wideRecievers,NUMBER_BIGGEST_GAPS)
    QB_Gaps = findBiggestPostionalGaps(quarterbacks,NUMBER_BIGGEST_GAPS)
    TE_Gaps = findBiggestPostionalGaps(tightEnds,NUMBER_BIGGEST_GAPS)
    K_Gaps = findBiggestPostionalGaps(kickers,NUMBER_BIGGEST_GAPS)

    # write the information on biggest gaps to the report
    report.write("THE " + str(NUMBER_BIGGEST_GAPS) + " BIGGEST GAPS IN PROJECTED POINTS BETWEEN "
                                                     "CONSECUTIVELY PROJECTED RUNNING BACKS\n")
    writeStats(report, RB_Gaps)
    report.write("\nTHE " + str(NUMBER_BIGGEST_GAPS) + " BIGGEST GAPS IN PROJECTED POINTS BETWEEN "
                                                     "CONSECUTIVELY PROJECTED WIDE RECEIVERS\n")
    writeStats(report, WR_Gaps)
    report.write("\nTHE " + str(NUMBER_BIGGEST_GAPS) + " BIGGEST GAPS IN PROJECTED POINTS BETWEEN "
                                                     "CONSECUTIVELY PROJECTED QUARTERBACKS\n")
    writeStats(report, QB_Gaps)
    report.write("\nTHE " + str(NUMBER_BIGGEST_GAPS) + " BIGGEST GAPS IN PROJECTED POINTS BETWEEN "
                                                     "CONSECUTIVELY PROJECTED TIGHT ENDS\n")
    writeStats(report, TE_Gaps)
    report.write("\nTHE " + str(NUMBER_BIGGEST_GAPS) + " BIGGEST GAPS IN PROJECTED POINTS BETWEEN "
                                                     "CONSECUTIVELY PROJECTED KICKERS\n")
    writeStats(report, K_Gaps)

    report.write("\n")
    report.write("----------------------------------------------------------------")
    report.write("\n\n")

    # write most yards per position
    for positionName in ["quarterbacks", "running backs", "wide receivers", "tight ends"]:
        positionalDF = runningBacks
        if positionName == "quarterbacks":
            positionalDF = quarterbacks
        elif positionName == "tight ends":
            positionalDF = tightEnds
        elif positionName == "wide receivers":
            positionalDF = wideRecievers
        writeTDsYdsRec("yards", positionName, positionalDF, N_PLAYERS_MOST_STATS, report)

    # write most touchdowns per position
    for positionName in ["quarterbacks", "running backs", "wide receivers", "tight ends"]:
        positionalDF = runningBacks
        if positionName == "quarterbacks":
            positionalDF = quarterbacks
        elif positionName == "tight ends":
            positionalDF = tightEnds
        elif positionName == "wide receivers":
            positionalDF = wideRecievers
        writeTDsYdsRec("touchdowns", positionName, positionalDF, N_PLAYERS_MOST_STATS, report)

    # write most receptions for position
    for positionName in ["running backs", "wide receivers", "tight ends"]:
        positionalDF = runningBacks
        if positionName == "tight ends":
            positionalDF = tightEnds
        elif positionName == "wide receivers":
            positionalDF = wideRecievers
        writeTDsYdsRec("receptions", positionName, positionalDF, N_PLAYERS_MOST_STATS, report)

    # get value above bench player for each player
    PlayersAndDefense = PlayersAndDefense.sort_values(by=['PROJ PTS'], ascending=False)
    PlayersAndDefense = PlayersAndDefense.reset_index(drop=True)
    for i in range(0,len(PlayersAndDefense)):
        PlayersAndDefense.loc[i,'VABP'] = valueAboveBenchPlayer(PlayersAndDefense,i,NUMBER_OF_TEAMS,True)

    PlayersAndDefense = PlayersAndDefense.sort_values(by=['VABP'], ascending=False)
    PlayersAndDefense = PlayersAndDefense.reset_index(drop=True)
    print(PlayersAndDefense)
    report.close()

    return 0


main()
