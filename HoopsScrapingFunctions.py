#seasonspage

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np 
#Create function to get Team shooting and Opponent shooting from season page
def SeasonYearShooting(years_list):
	year_urls={str(year):'http://www.basketball-reference.com/leagues/NBA_'
			+str(year)+'.html' for year in years_list}
	SeasonYearShooting={}
	for year, url in year_urls.items():
		print (year)
		html=urlopen(url)
		soup=BeautifulSoup(html,'lxml')
		#team shooting first
		teamheader=['Team','G','MP','FG%','Avg_Dist','FGA%2P','FGA%0_3','FGA%3_10','FGA%10_16','FGA%16<3','FGA%3P',
		'FG2P','FG%0_3','FG%3_10','FG%10_16','FG%16<3','FG%3P',
		'AST2P%','DUNKSFGA%','DUNKS_M','LAYFGA%','LAY_M','AST3PT$','CORNER3PA%','CORNER3P%','HEAVES_ATT','HEAVES_M']
		#Comment in html mess up regular table extraction, need to extract for comment 
		divfind=soup.find('div',{'id':'all_team_shooting'})
		comment=str(divfind.contents[5]) #location of the table in comment
		soup2=BeautifulSoup(comment,'lxml') #convert comment to beautifulsoup 
		table_team=soup2.find('table',{'id':'team_shooting'}) #find table
		team_rows=table_team.findAll('tr')[3:] #skip the first 3 rows because header
		#td is entries, get entries for each row
		team_shooting=[[td.getText() for td in team_rows[i].findAll('td')]
						for i in range(len(team_rows))]
		divfind2=soup.find('div',{'id':'all_opponent_shooting'})
		stringer2=str(divfind2.contents[5])
		soup3=BeautifulSoup(stringer2,'lxml')		
		table_opp=soup3.find('table',{'id':'opponent_shooting'})
		opp_rows=table_opp.findAll('tr')[3:]
		opp_shooting=[[td.getText() for td in opp_rows[i].findAll('td')]
						for i in range(len(opp_rows))]
		#convert to dataframe
		teamShootingDF=pd.DataFrame(team_shooting,columns=teamheader)
		oppheader=['Team','G','MP','FG%','Avg_Dist','FGA%2P','FGA%0_3','FGA%3_10','FGA%10_16','FGA%16<3','FGA%3P',
		'FG2P','FG%0_3','FG%3_10','FG%10_16','FG%16<3','FG%3P',
		'AST2P%','DUNKSFGA%','DUNKS_M','LAYFGA%','LAY_M','AST3PT$','CORNER3PA%','CORNER3P%']
		oppShootingDF=pd.DataFrame(opp_shooting,columns=oppheader)
		teamShootingDF[teamShootingDF.columns[1:]]=teamShootingDF[teamShootingDF.columns[1:]].astype(float)
		oppShootingDF[oppShootingDF.columns[1:]]=oppShootingDF[oppShootingDF.columns[1:]].astype(float)


		SeasonYearShooting[year]={'team': teamShootingDF,'opp':oppShootingDF}
	return SeasonYearShooting
	
# AKA url_dictionary,Function to get URLs based on landing page, storeas dictionary
def TeamUrlsDict(seasons,
    site='http://www.basketball-reference.com/',
    teams=['GSW','SAS','OKC','CLE','LAC','TOR','ATL','BOS',
            'CHO','UTA','IND','MIA','POR','DET','HOU','DAL','WAS',
            'CHI','ORL','MEM','SAC','NYK','DEN','MIN','NOP','MIL','PHO','BRK','LAL','PHI'],
            ):
    """"Inputs are:
    Seasons: list of years (as strings) of desired rosters
    site: frontpage url (basketball-reference,baseball-reference etc)
    teams= list of teams """
    #We create a nested dictionary where first key is year, second is team, with urls as value
    teamurlsbyseasons={}
    for year in seasons:
        year=str(year)
        print (year)
        season_roster={team: site+'teams/'+team+'/'+year for team in teams} 
        teamurlsbyseasons['{0}'.format(year)]=season_roster
    return teamurlsbyseasons
#function to get team gamelogs
def GetTeamGameLogs(url_dictionary):
    """Input is a dictionary of urls, created in same format as TeamUrlsDict"""

    gamelogsbyseason={}
    for year, teamdict in url_dictionary.items():
        team_gamelogs={}
        print (year)
        for team, url in url_dictionary[year].items():
            print (team)

            url_gamelog=url+'/gamelog'
            html=urlopen(url_gamelog)
            soup=BeautifulSoup(html,'lxml')
            table = soup.find('table',{'id':'tgl_basic'})
            column_headers=[]
            column_headers=[th.getText() for th in 
                    table.findAll('tr', limit=2)[1].findAll('th')]
            column_headers=column_headers[1:]
            column_headers[2]='Location'
            column_headers[4:7]=['Result','PS','PA']
            for i in range(len(column_headers)):
                if i<=23: continue
                column_headers[i]='Opp_'+column_headers[i]
            data_rows=table.findAll('tr')[2:] #skip the first two row because header
            gamelog_data = []
            for i in range(len(data_rows)):
                team_row=[]
                if data_rows[i].has_attr('class'): continue #skips the redudant header
                for td in data_rows[i].findAll('td'):
                    team_row.append(td.getText())
                gamelog_data.append(team_row)
            df=pd.DataFrame(gamelog_data,columns= column_headers)            
            df.drop(df.columns[[23]], axis=1, inplace=True)
            df.loc[df.Location!='@','Location']='Home'
            df.loc[df.Location =='@','Location']='Away'
            df['Date']=pd.to_datetime(df['Date'])
            df['G']=df['G'].astype('int')
            df.iloc[:,5:]=df.iloc[:,5:].apply(pd.to_numeric,errors='raise')
            team_gamelogs['{0}'.format(team)]=df    
        gamelogsbyseason['{0}'.format(year)]=team_gamelogs
    return gamelogsbyseason
#Function to get advanced team gamelogs
def GetTeamAdvancedGameLogs(url_dictionary):
    """Input is a dictionary of urls, created in same format as TeamUrlsDict"""
    advancedgamelogsbyseason={}
    for year, teamdict in url_dictionary.items():
        team_advancedgamelogs={}
        for team, url in url_dictionary[year].items():
            print (team)
            url_gamelog=url+'/gamelog-advanced'
            html=urlopen(url_gamelog)            
            soup=BeautifulSoup(html,'lxml')
            table = soup.find('table',{'id':'tgl_advanced'})
            column_headers=[th.getText() for th in 
                    table.findAll('tr', limit=2)[1].findAll('th')]
            column_headers=column_headers[1:]
            column_headers[2]='Location'
            column_headers[4:7]=['Result','PS','PA']
            for i in (17,18,19,20):
                column_headers[i]='Off4f_'+column_headers[i]
            for i in (21,22,23,24):
                column_headers[i]='Def4f_'+column_headers[i]
            data_rows=table.findAll('tr')[2:] #skip the first two row because header
            gamelog_data = []
            for i in range(len(data_rows)):
                team_row=[]
                if data_rows[i].has_attr('class'): continue
                for td in data_rows[i].findAll('td'):
                    team_row.append(td.getText())
                gamelog_data.append(team_row)
            df=pd.DataFrame(gamelog_data,columns= column_headers)            
            df.loc[df.Location!='@','Location']='Home'
            df.drop(df.columns[[17,22]], axis=1, inplace=True)
            df.loc[df.Location =='@','Location']='Away'
            df.apply(lambda x: pd.to_numeric(x, errors='ignore'))
            df['G']=df['G'].astype('int')
            df['Date']=pd.to_datetime(df['Date'])
            df.iloc[:,5:]=df.iloc[:,5:].apply(pd.to_numeric,errors='raise')
            team_advancedgamelogs['{0}'.format(team)]=df    
        advancedgamelogsbyseason['{0}'.format(year)]=team_advancedgamelogs
    return advancedgamelogsbyseason
#function to get team rosters
def GetTeamRosters(url_dictionary):
    """Input is a dictionary of urls, created in same format as TeamUrlsDict"""
    rostersbyseason={}
    for year, teamdict in url_dictionary.items():
        team_roster={}
        for team, url in url_dictionary[year].items():
            teamurl=url+'.html'
            html=urlopen(teamurl)
            soup=BeautifulSoup(html,'lxml')
            table=soup.find('table',{'id':'roster'})
            column_headers=[th.getText() for th in 
                    table.findAll('tr', limit=1)[0].findAll('th')]
            column_headers[6]='Country'
            column_headers.append('Id')    

            data_rows=table.findAll('tr')[1:] #skip the first row because header
            player_data = []
            for i in range(len(data_rows)):
                player_row=[]
                for th in data_rows[i].findAll('th'):
                    player_row.append(th.getText())
                for td in data_rows[i].findAll('td'):
                    player_row.append(td.getText())
                    playerurl=data_rows[i].find('a').get('href')
                    playerid=playerurl[11:-5]
                player_row.append(playerid)
                player_data.append(player_row)
            print(team)
            team_roster[team]=pd.DataFrame(player_data,columns=column_headers)
            team_roster[team]['Exp']=team_roster[team]['Exp'].replace('R',0)
        rostersbyseason[year]=pd.concat(team_roster.values(), ignore_index=True)
    return rostersbyseason
