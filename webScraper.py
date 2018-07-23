# this file scrapes live projection and ADP data from ESPN websites, puts data in data frames, manipulates the data frames
# then writes the data frames to csv files to be used in analysis script
import pandas
from bs4 import BeautifulSoup
import requests

def getHTMLText(HTMLList):
    textList = []
    for item in HTMLList:
        textList.append(item.getText().strip())
    return textList

def main():
    # these are all of the urls for the projection pages, 40 players on each page
    ESPN_Projections1 = requests.get("http://games.espn.com/ffl/tools/projections?")
    ESPN_Projections2 = requests.get("http://games.espn.com/ffl/tools/projections?&startIndex=40")
    ESPN_Projections3 = requests.get("http://games.espn.com/ffl/tools/projections?&startIndex=80")
    ESPN_Projections4 = requests.get("http://games.espn.com/ffl/tools/projections?&startIndex=120")
    ESPN_Projections5 = requests.get("http://games.espn.com/ffl/tools/projections?&startIndex=160")
    ESPN_Projections6 = requests.get("http://games.espn.com/ffl/tools/projections?&startIndex=200")
    ESPN_Projections7 = requests.get("http://games.espn.com/ffl/tools/projections?&startIndex=240")
    projectionHTMLPages = [ESPN_Projections1,ESPN_Projections2,ESPN_Projections3,ESPN_Projections4,
                           ESPN_Projections5,ESPN_Projections6,ESPN_Projections7]
    # ESPN_ADP is different from other pages, only want player name and average draft position from this table
    ESPN_ADP = requests.get("http://games.espn.com/ffl/livedraftresults")
    # Fantasy Football Calculator ADP for 2QB league
    #FFC_2QB_ADP = requests.get("https://fantasyfootballcalculator.com/rankings/2qb")

    # get all of the column names, one time thing, all pages of table have same columns so don't repeat
    soup = BeautifulSoup(ESPN_Projections1.text, 'html.parser')
    header = soup.select('tr.playerTableBgRowSubhead td')
    colNames = getHTMLText(header)

    # rename some columns with repeat names
    # there are multiple YDS and TD columns
    PassYardsIndex = colNames.index('YDS')
    colNames[PassYardsIndex] = 'PASS YDS'
    RushYardsIndex = colNames.index('YDS')
    colNames[RushYardsIndex] = 'RUSH YDS'
    RecYardsIndex = colNames.index('YDS')
    colNames[RecYardsIndex] = 'REC YDS'
    PassTDIndex = colNames.index('TD')
    colNames[PassTDIndex] = 'PASS TD'
    RushTDIndex = colNames.index('TD')
    colNames[RushTDIndex] = 'RUSH TD'
    RecTDIndex = colNames.index('TD')
    colNames[RecTDIndex] = 'REC TD'

    # make dataframe with the column names
    playerInfoTable = pandas.DataFrame(columns = colNames)
    tableRowIndex = 0

    # for each page, extract the player data and append it to the data frame
    for page in projectionHTMLPages:
        soup = BeautifulSoup(page.text, 'html.parser')
        # get the rows that hold the player information and statistics
        playerData = soup.select('table.playerTableTable tr.pncPlayerRow td')
        playerDataText = getHTMLText(playerData)
        # separate out the individual players from each other since everything is combined in one list
        # also insert the rows into the data frame
        for i in range(0,len(playerDataText),len(colNames)):
            playerRow = playerDataText[i:i+len(colNames)]
            playerInfoTable.loc[tableRowIndex] = playerRow
            tableRowIndex += 1

    # get ADP data from ADP table
    ADP_Soup = BeautifulSoup(ESPN_ADP.text, 'html.parser')
    ADP_Table_Header = ADP_Soup.select('tr.tableSubHead td')[4:]
    ADP_Col_Names = getHTMLText(ADP_Table_Header)
    ADP_Table = pandas.DataFrame(columns=ADP_Col_Names)

    # td at start are for header, the last one is blank
    ADP_Player_Rows = ADP_Soup.select('table.tableBody tr td')[13:-1]
    ADP_Player_Rows_Text = getHTMLText(ADP_Player_Rows)
    ADP_Row_Index = 0

    # insert the ADP data into ADP data frame
    for i in range(0, len(ADP_Player_Rows_Text), len(ADP_Col_Names)):
        ADP_Player_Row = ADP_Player_Rows_Text[i:i + len(ADP_Col_Names)]
        ADP_Table.loc[ADP_Row_Index] = ADP_Player_Row
        ADP_Row_Index += 1

    # get the team name for each player in the ADP table, used later for the join to other table
    ADP_Player_Names = []
    for i in range(0, len(ADP_Table)):
        playerTeam = ADP_Table.loc[i]['PLAYER, TEAM']
        playerName = ""
        if (playerTeam[-4:] == 'D/ST'):
            playerTeamSplit = playerTeam.split(" ")
            playerName = playerTeamSplit[0]
        else: # normal player
            playerTeamSplit = playerTeam.split(",")
            playerName = playerTeamSplit[0]
        ADP_Player_Names.append(playerName)

    ADP_Table['PLAYER'] = ADP_Player_Names
    # only want these two columns from ADP_Table
    ADP_Table = ADP_Table[['PLAYER','AVG PICK']]


    # data frame to hold the defenses separate from other players
    # team name is [:-10]
    defenses = pandas.DataFrame(columns=['TEAM', 'PROJ PTS'])
    defenseNamesList = []
    defensePointsList = []

    # identify the defenses in playerInfoTable df, drop them from that df and add them to defenses df
    for i in range(len(playerInfoTable) - 1, -1, -1):
        if (playerInfoTable.loc[i]['PLAYER, TEAM POS'][-4:] == "D/ST"):
            teamName = playerInfoTable.loc[i][1][:-10]
            defensePoints = playerInfoTable.loc[i]['PTS']
            defenseNamesList.append(teamName)
            defensePointsList.append(defensePoints)
            playerInfoTable = playerInfoTable.drop(playerInfoTable.index[i])

    defenses['TEAM'] = defenseNamesList
    defenses['PROJ PTS'] = defensePointsList

    # split the playerInfoTable player/team/pos column into separate columns
    positionList = []
    teamList = []
    playerNameList = []
    for i in range(0, len(playerInfoTable)):
        name, position = playerInfoTable.iloc[i, 1].split(",")
        playerNameList.append(name)
        position = position[1:]
        # split by space
        teamPositionSplit = position.split("\xa0")
        team = teamPositionSplit[0]
        teamList.append(team)
        position = teamPositionSplit[1]
        positionList.append(position)
    playerInfoTable = playerInfoTable.rename(columns={'PLAYER, TEAM POS': 'PLAYER'})
    playerInfoTable['PLAYER'] = playerNameList
    playerInfoTable['TEAM'] = teamList
    playerInfoTable['POSITION'] = positionList
    # merge the ADP into playerInfoTable, defenses
    playerInfoTable = playerInfoTable.merge(ADP_Table, left_on='PLAYER', right_on='PLAYER', how='left')
    defenses = defenses.merge(ADP_Table, left_on='TEAM', right_on='PLAYER', how='left')

    # make the tables more neat and organized, rename/reorder/drop columns
    defenses = defenses.drop(['PLAYER'], axis=1)
    defenses = defenses.rename(columns={'PTS': 'PROJ PTS', 'AVG PICK': 'ADP'})
    playerInfoTable = playerInfoTable.rename(columns={'PTS': 'PROJ PTS', 'AVG PICK': 'ADP'})
    playerInfoTable = playerInfoTable[['PLAYER', 'POSITION', 'TEAM', 'PASS YDS', 'PASS TD', 'INT', 'RUSH', 'RUSH YDS',
                                       'RUSH TD', 'REC', 'REC YDS', 'REC TD', 'PROJ PTS', 'ADP']]

    print(playerInfoTable)

    # export the data frame to a csv
    # need to remove the weird Â symbol from some columns so change encoding
    playerInfoTable.to_csv('Web Scraped Projections.csv',index=False, encoding='utf-8-sig')
    defenses.to_csv('Defense Projections.csv',index=False, encoding='utf-8-sig')

    return 0

main()