import pandas as pd
import numpy

NUMBER_OF_TEAMS = 12
NUMBER_OF_ROUNDS = 16
# NUMBER_BIGGEST_GAPS is used for findBiggestPositionalGaps(), tells function to find the n largest gaps between
# consecutively projected players of same position
NUMBER_BIGGEST_GAPS = 5

# other ideas for functions are top n touchdowns for QB, RB, WR, TE
# top receptions for RB, TE, WR
# top yards for QB, RB, WR, TE, don't include rushing yards for QB


def rankByProjection(dataFrame, playerIndex, rankingsDict, rankType):
    position = dataFrame.loc[playerIndex, 'POSITION']
    positionRankingVar = position + "_" + rankType + "_Rank"
    positionRanking = position + str(rankingsDict[positionRankingVar])
    rankingsDict[positionRankingVar] += 1
    rankColName = "POS " + rankType + " RANK"
    dataFrame.loc[playerIndex, rankColName] = positionRanking
    return positionRanking


# get the average projected points for the round and position passed, position can be "ALL" to include all positions
# round number passed should be greater than or equal to one
def AveragePointsForRound(projectionsDF, roundNumber, position):
    # first pick is offset by the number of picks already made in previous rounds
    firstPick = NUMBER_OF_TEAMS * (roundNumber - 1) + 1
    lastPick = firstPick + 11
    if (position == "ALL"):
        projectedPlayersInRound = projectionsDF[(projectionsDF['ADP RANK'] >= firstPick) &
                                                (projectionsDF['ADP RANK'] <= lastPick)]
        average = projectedPlayersInRound['PROJ PTS'].sum() / NUMBER_OF_TEAMS
    else:
        projectedPlayersInRound = projectionsDF[(projectionsDF['ADP RANK'] >= firstPick) &
                                                (projectionsDF['ADP RANK'] <= lastPick) &
                                                (projectionsDF['POSITION'] == position)]
        NumPlayersOfPositionInRound = len(projectedPlayersInRound)
        if (NumPlayersOfPositionInRound > 0):
            average = projectedPlayersInRound['PROJ PTS'].sum() / NumPlayersOfPositionInRound
        else:
            average = 0
    return average


def MaxProjPointsForRound(projectionsDF, roundNumber, position):
    # first pick is offset by the number of picks already made in previous rounds
    firstPick = NUMBER_OF_TEAMS * (roundNumber - 1) + 1
    lastPick = firstPick + 11
    if (position == "ALL"):
        projectedPlayersInRound = projectionsDF[(projectionsDF['ADP RANK'] >= firstPick) &
                                                (projectionsDF['ADP RANK'] <= lastPick)]
        max = projectedPlayersInRound['PROJ PTS'].max()
    else:
        projectedPlayersInRound = projectionsDF[(projectionsDF['ADP RANK'] >= firstPick) &
                                                (projectionsDF['ADP RANK'] <= lastPick) &
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
            # replace if the minimum difference from the list if this difference is greater than it
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

def writeGaps(reportFile,gapList):
    for i in range(0,len(gapList)):
        reportFile.write("\t" + gapList[i] + "\n")


def main():
    report = open("Fantasy Report.txt", "w")

    # set up data frames
    projections = pd.read_csv("Web Scraped Projections.csv")
    defenses = pd.read_csv("Defense Projections.csv")

    # rank the players by position based on total projected points and average draft position
    # e.g. RB1, RB2, QB1, QB2, WR1, WR2, etc.
    rankingsDict = {}
    rankingsDict['RB_PROJ_Rank'] = 1
    rankingsDict['WR_PROJ_Rank'] = 1
    rankingsDict['QB_PROJ_Rank'] = 1
    rankingsDict['TE_PROJ_Rank'] = 1
    rankingsDict['D_PROJ_Rank'] = 1
    rankingsDict['K_PROJ_Rank'] = 1
    # rankingsDict['RB_ADP_Rank'] = 1
    # rankingsDict['WR_ADP_Rank'] = 1
    # rankingsDict['QB_ADP_Rank'] = 1
    # rankingsDict['TE_ADP_Rank'] = 1
    # rankingsDict['D_ADP_Rank'] = 1
    # rankingsDict['K_ADP_Rank'] = 1
    projections['POS PROJ RANK'] = ""
    # projections['POS ADP RANK'] = ""
    defenses['POS PROJ RANK'] = 0

    # rank the players by position on projected points
    projections = projections.sort_values(by=['PROJ PTS'], ascending=False)
    projections = projections.reset_index(drop=True)
    for i in range(0, len(projections)):
        rankByProjection(projections, i, rankingsDict, 'PROJ')

    # rank the defenses by projected points
    defenses = defenses.sort_values(by=['PROJ PTS'], ascending=False)
    defenses = defenses.reset_index(drop=True)
    for i in range(0, len(defenses)):
        defenses.loc[i, 'POS PROJ RANK'] = rankingsDict['D_PROJ_Rank']
        rankingsDict['D_PROJ_Rank'] += 1

    # rankings are essentially the same for projected and ADP
    # rank the players by position on ADP
    # projections.sort_values(by=['ADP', 'PROJ PTS'], ascending=False)
    # for i in range(0,len(projections)):
    #     rankByProjection(projections, i, rankingsDict, 'ADP')

    # concatenate the player and ADP columns of projections and defense to get rank by ADP
    # need PROJ PTS column to sort on if ADP is null
    PlayersAndDefense = pd.concat([projections[['PLAYER', 'ADP', 'PROJ PTS']],
                                   defenses[['TEAM', 'ADP', 'PROJ PTS']].rename(columns={'TEAM': 'PLAYER'})],
                                  sort=False, ignore_index=True)
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
    for position in ['ALL', 'RB', 'WR', 'QB', 'TE']:
        # set up a header for stats on this position
        if (position == 'ALL'):
            report.write("AVERAGE AND MAX PROJECTED POINTS FOR ALL PLAYERS IN EACH ROUND\n\n")
        else:
            report.write("AVERAGE AND MAX PROJECTED POINTS FOR " + position + " IN EACH ROUND\n\n")
        # get average per round
        for i in range(1, NUMBER_OF_ROUNDS + 1):
            if position == 'ALL':
                report.write("Average projected points per player in Round " +
                             str(i) + ": " + str(AveragePointsForRound(projections, i, position)) + "\n")
            else:
                report.write("Average projected points per " + position + " in Round " +
                             str(i) + ": " + str(AveragePointsForRound(projections, i, position)) + "\n")
        report.write("\n")
        # get max per round
        for i in range(1, NUMBER_OF_ROUNDS + 1):
            if position == 'ALL':
                report.write("Max points of player projected to be drafted in Round " + str(i) + ": " +
                             str(MaxProjPointsForRound(projections, i, position)) + "\n")
            else:
                report.write("Max points of " + position + " projected to be drafted in Round " + str(i) + ": " +
                             str(MaxProjPointsForRound(projections, i, position)) + "\n")
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
    writeGaps(report, RB_Gaps)
    report.write("\nTHE " + str(NUMBER_BIGGEST_GAPS) + " BIGGEST GAPS IN PROJECTED POINTS BETWEEN "
                                                     "CONSECUTIVELY PROJECTED WIDE RECEIVERS\n")
    writeGaps(report, WR_Gaps)
    report.write("\nTHE " + str(NUMBER_BIGGEST_GAPS) + " BIGGEST GAPS IN PROJECTED POINTS BETWEEN "
                                                     "CONSECUTIVELY PROJECTED QUARTERBACKS\n")
    writeGaps(report, QB_Gaps)
    report.write("\nTHE " + str(NUMBER_BIGGEST_GAPS) + " BIGGEST GAPS IN PROJECTED POINTS BETWEEN "
                                                     "CONSECUTIVELY PROJECTED TIGHT ENDS\n")
    writeGaps(report, TE_Gaps)
    report.write("\nTHE " + str(NUMBER_BIGGEST_GAPS) + " BIGGEST GAPS IN PROJECTED POINTS BETWEEN "
                                                     "CONSECUTIVELY PROJECTED KICKERS\n")
    writeGaps(report, K_Gaps)

    report.close()

    return 0


main()
