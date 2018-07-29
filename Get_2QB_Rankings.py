import pandas
from bs4 import BeautifulSoup
import requests

def getHTMLText(HTMLList):
    textList = []
    for item in HTMLList:
        textList.append(item.getText().strip())
    return textList

def main():
    # almost all the time of this program is spent getting this request for FFC
    FFC_2QB_ADP = requests.get("https://fantasyfootballcalculator.com/rankings/2qb")
    FFC_Soup = BeautifulSoup(FFC_2QB_ADP.text, 'html.parser')

    # get header information for 2QB rankings
    FFC_Header = FFC_Soup.select('thead tr')
    FFC_ColNames = getHTMLText(FFC_Header)
    FFC_ColNames = FFC_ColNames[0].split("\n")

    # get data from the FFC table for each player, put it in data frame
    FFC_Player_Rankings = pandas.DataFrame(columns = FFC_ColNames)
    FFC_Table_Row_Index = 0

    FFC_Player_Data = FFC_Soup.select('tbody tr')
    FFC_Player_Data_Text = getHTMLText(FFC_Player_Data)

    for i in range(0, len(FFC_Player_Data_Text)):
        playerData = FFC_Player_Data_Text[i].split("\n")
        # get rid of the period in the rank, transform 100. to 100
        playerData[0] = playerData[0][:-1]
        FFC_Player_Rankings.loc[FFC_Table_Row_Index] = playerData
        FFC_Table_Row_Index += 1

    FFC_Player_Rankings = FFC_Player_Rankings[['Rank', 'Name']]
    FFC_Player_Rankings = FFC_Player_Rankings.rename(columns={'Rank': '2QB RANK','Name': 'PLAYER'})
    # convert 2QB RANK to int so it can be sorted on this rank
    FFC_Player_Rankings['2QB RANK'] = FFC_Player_Rankings['2QB RANK'].apply(int)

    # map the non-matching names to the ESPN names
    map = {}
    with open("Name Mapping.txt") as NameMappingFile:
        for line in NameMappingFile:
            (FFC_Name, ESPN_Name) = line.split(",")
            map[FFC_Name] = ESPN_Name.strip()
    for i in range(len(FFC_Player_Rankings)):
        FFC_Player_Name = FFC_Player_Rankings.loc[i,'PLAYER']
        if FFC_Player_Name in map.keys():
            FFC_Player_Rankings.loc[i,'PLAYER'] = map[FFC_Player_Name]

    print(FFC_Player_Rankings)
    return 0

main()