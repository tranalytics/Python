import pandas as pd 
import jellyfish
nielsen=pd.read_csv("D:\\PersonalData\\TranAlex\\Documents\\python\\New folder\\nielsen_reduced2.csv",header=0)
bev_journal=pd.read_csv("D:\\PersonalData\\TranAlex\\Documents\\python\\New folder\\bev_journal_reduced2.csv",header=0, encoding="ISO-8859-1")

max_bdesc=[]
max_desc=[]
counter=0
nielsen.shape
for row in nielsen["BRAND EXTENSION"]:
	print (row)
	hold_bdesc=[]
	hold_desc=[]
	for test in bev_journal["bdesc"]:
		a=jellyfish.damerau_levenshtein_distance(row,test)
		dl={"bdesc":test,
			"score":a}
		hold_bdesc.append(dl)
		
	for test2 in bev_journal["description"]:
		test2=str(test2)
		test3=test2.replace("\"","")
		j=jellyfish.damerau_levenshtein_distance(row,test3)
		
		dl2={"description":test3,
			"score":j}
	
		hold_desc.append(dl2)
	maxbdesc= max(hold_bdesc, key=lambda x:x['score'])
	maxdesc=max(hold_desc,key=lambda x:x['score'])
	max_bdesc.append(maxbdesc)
	max_desc.append(maxdesc)
	counter=counter+1
	if counter%100==0:
		print (counter)

nielsen["maxbdesc"]=max_bdesc
nielsen["maxdesc"]=max_desc
nielsen.to_csv('output_dl.csv', index=False, header=True)