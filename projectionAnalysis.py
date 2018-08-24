import pandas as pd
import numpy
import helper as h

NUMBER_OF_TEAMS = 12
NUMBER_OF_ROUNDS = 16
# NUMBER_BIGGEST_GAPS is used for findBiggestPositionalGaps(), tells function to find the n largest gaps between
# consecutively projected players of same position
NUMBER_BIGGEST_GAPS = 5
N_PLAYERS_MOST_STATS = 5 # display top n players for stats


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
        h.rankByProjection(projections, i, rankingsDict, 'PROJ')

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
                             str(i) + ": " + str(h.AveragePointsForRound(PlayersAndDefense, i, position, NUMBER_OF_TEAMS)) + "\n")
            else:
                report.write("Average projected points per " + position + " in Round " +
                             str(i) + ": " + str(h.AveragePointsForRound(PlayersAndDefense, i, position, NUMBER_OF_TEAMS)) + "\n")
        report.write("\n")
        # get max per round
        for i in range(1, NUMBER_OF_ROUNDS + 1):
            if position == 'ALL':
                report.write("Max points of player projected to be drafted in Round " + str(i) + ": " +
                             str(h.MaxProjPointsForRound(PlayersAndDefense, i, position, NUMBER_OF_TEAMS)) + "\n")
            else:
                report.write("Max points of " + position + " projected to be drafted in Round " + str(i) + ": " +
                             str(h.MaxProjPointsForRound(PlayersAndDefense, i, position, NUMBER_OF_TEAMS)) + "\n")
        report.write("\n")
        report.write("----------------------------------------------------------------")
        report.write("\n\n")


    # find the biggest gaps in projected points between consecutively ranked players for each set of positions
    RB_Gaps = h.findBiggestPostionalGaps(runningBacks,NUMBER_BIGGEST_GAPS)
    WR_Gaps = h.findBiggestPostionalGaps(wideRecievers,NUMBER_BIGGEST_GAPS)
    QB_Gaps = h.findBiggestPostionalGaps(quarterbacks,NUMBER_BIGGEST_GAPS)
    TE_Gaps = h.findBiggestPostionalGaps(tightEnds,NUMBER_BIGGEST_GAPS)
    K_Gaps = h.findBiggestPostionalGaps(kickers,NUMBER_BIGGEST_GAPS)

    # write the information on biggest gaps to the report
    report.write("THE " + str(NUMBER_BIGGEST_GAPS) + " BIGGEST GAPS IN PROJECTED POINTS BETWEEN "
                                                     "CONSECUTIVELY PROJECTED RUNNING BACKS\n")
    h.writeStats(report, RB_Gaps)
    report.write("\nTHE " + str(NUMBER_BIGGEST_GAPS) + " BIGGEST GAPS IN PROJECTED POINTS BETWEEN "
                                                     "CONSECUTIVELY PROJECTED WIDE RECEIVERS\n")
    h.writeStats(report, WR_Gaps)
    report.write("\nTHE " + str(NUMBER_BIGGEST_GAPS) + " BIGGEST GAPS IN PROJECTED POINTS BETWEEN "
                                                     "CONSECUTIVELY PROJECTED QUARTERBACKS\n")
    h.writeStats(report, QB_Gaps)
    report.write("\nTHE " + str(NUMBER_BIGGEST_GAPS) + " BIGGEST GAPS IN PROJECTED POINTS BETWEEN "
                                                     "CONSECUTIVELY PROJECTED TIGHT ENDS\n")
    h.writeStats(report, TE_Gaps)
    report.write("\nTHE " + str(NUMBER_BIGGEST_GAPS) + " BIGGEST GAPS IN PROJECTED POINTS BETWEEN "
                                                     "CONSECUTIVELY PROJECTED KICKERS\n")
    h.writeStats(report, K_Gaps)

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
        h.writeTDsYdsRec("yards", positionName, positionalDF, N_PLAYERS_MOST_STATS, report)

    # write most touchdowns per position
    for positionName in ["quarterbacks", "running backs", "wide receivers", "tight ends"]:
        positionalDF = runningBacks
        if positionName == "quarterbacks":
            positionalDF = quarterbacks
        elif positionName == "tight ends":
            positionalDF = tightEnds
        elif positionName == "wide receivers":
            positionalDF = wideRecievers
        h.writeTDsYdsRec("touchdowns", positionName, positionalDF, N_PLAYERS_MOST_STATS, report)

    # write most receptions for position
    for positionName in ["running backs", "wide receivers", "tight ends"]:
        positionalDF = runningBacks
        if positionName == "tight ends":
            positionalDF = tightEnds
        elif positionName == "wide receivers":
            positionalDF = wideRecievers
        h.writeTDsYdsRec("receptions", positionName, positionalDF, N_PLAYERS_MOST_STATS, report)

    # get value over bench player for each player
    PlayersAndDefense = PlayersAndDefense.sort_values(by=['PROJ PTS'], ascending=False)
    PlayersAndDefense = PlayersAndDefense.reset_index(drop=True)
    for i in range(0,len(PlayersAndDefense)):
        PlayersAndDefense.loc[i,'VOBP'] = h.valueOverBenchPlayer(PlayersAndDefense,i,NUMBER_OF_TEAMS,True)

    PlayersAndDefense = PlayersAndDefense[['PLAYER', 'POSITION', 'PROJ PTS', 'ADP', 'ADP RANK', '2QB RANK', 'VOBP']]
    PlayersAndDefense = PlayersAndDefense.sort_values(by=['VOBP'], ascending=False)
    PlayersAndDefense = PlayersAndDefense.reset_index(drop=True)
    print(PlayersAndDefense)
    report.close()

    PlayersAndDefense.to_csv('Players and Defense Metrics.csv',index=False)

    return 0


main()
