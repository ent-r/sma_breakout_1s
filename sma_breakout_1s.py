import websocket
import _thread
from datetime import datetime
import json
from binance.client import Client
import time
import pickle
from ftplib import FTP
import os
import copy
            
host = "..."
user = "..."
password = "..."

event_type="kline"
interval="1s"
numbersymbolsmin=289
numbersymbols=432
threshold=66
fee=0.001  #0.1% fee
budgetquant=1000

listchrono=[]   # liste des listsymbol
listalready=[]
listsymbol=[]	# liste de listes/symbols : 1 liste par symbol

listlock=_thread.allocate_lock()
list_lock_chrono=_thread.allocate_lock()
ftplock=_thread.allocate_lock()

def save_list(l):
	now = datetime.now()
	s="listsymbol_"+str(int(now.second/30))
	with open(s, 'wb') as f:
		pickle.dump(l, f)

def read_list(filpath):
    with open(filpath, 'rb') as fp:
        try:
            l = pickle.load(fp)
            #print(l)
        except:
            return 0
        return l

def create_list(lexcinfo):
	print("len(lexcinfo)",len(lexcinfo))
	global listsymbol
	try:
		for i in range(2):
			s="listsymbol_"+str(i)
			savedlistsymbol=read_list(s)
			if savedlistsymbol:break
	except:
		savedlistsymbol=0
	if savedlistsymbol:
		listsymbol=savedlistsymbol.copy()
		print("if savedlistsymbol")

def info_():
	lexcinfo=[]
	api_key = "..."
	api_secret = "..."
	client = Client(api_key, api_secret)
	exchange_info = client.get_exchange_info()
	linfo=[]
	i=0
	for s in exchange_info['symbols']:
		if s['symbol'].lower().endswith("usdt"):
			linfo.append(s['symbol'].lower())
			if i>=numbersymbolsmin: lexcinfo.append(s['symbol'].lower()+"@"+event_type+"_"+interval)
			if i>=(numbersymbols-1): break
			i+=1
	req_='{ "method": "SUBSCRIBE", "params": ' + str(lexcinfo).replace("'","\"") + ', "id": 1}'
	print("info_")
	create_list(lexcinfo.copy())  
	return req_
	
def alreadyin(tuplalready):
        for la in listalready:
            if la==tuple(tuplalready):
                return 1
        return 0

def ws_message (ws,message):
    m=json.loads(message)
    tuplalready=(m['e'],m['E'],m['s'])
    b9=alreadyin(tuplalready)
    if b9!=1:        
                listalready.append(tuplalready)
                if len(listalready)>numbersymbols*2:
                    del listalready[0]
                _thread.start_new_thread(compute,( m['e'],m['E'],m['s'],m['k']['t'],m['k']['T'],m['k']['s'], m['k']['i'],m['k']['f'],m['k']['L'],m['k']['o'],m['k']['c'],m['k']['h'],m['k']['l'],m['k']['v'],m['k']['n'],m['k']['x'],m['k']['q'],m['k']['V'],m['k']['Q'],m['k']['B'], ))
                _thread.start_new_thread(save_list,(listsymbol.copy(),))

def ws_open(ws):
	print(requete_)
	ws.send(requete_)

def ws_thread(*args):
	ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws", on_open = ws_open, on_message = ws_message)
	ws.run_forever()

def compute(e,E,s,kt,kT,ks,ki,kf,kL,ko,kc,kh,kl,kv,kn,kx,kq,kV,kQ,kB):
	open = float(ko)
	close = float(kc)
	high  = float(kh)
	low = float(kl)
	
	evenement=""
	
	initlist = [e,E,s,kt,kT,ks,ki,kf,kL,float(ko),float(kc),float(kh),float(kl),kv,kn,kx,kq,kV,kQ,kB]
	
	worklist = [e,E,s,kt,kT,ks,ki,kf,kL,float(ko),float(kc),float(kh),float(kl),kv,kn,kx,kq,kV,kQ,kB]
	
	for i in range(80):
		worklist.append(0)
	listlock.acquire()  # zone critique, peut-être à agrandir et supprimer worklist
	for l in reversed(listsymbol):
		if s in l:
			worklist=l.copy()
			#print("______",l)
			break
	listlock.release()
	#print (worklist)
	closeprev=worklist[10]
	sma7sprev=worklist[30]
	sma8sprev=worklist[31]
	sma9sprev=worklist[32]
	sma1hprev=worklist[33]
	sma2hprev=worklist[34]
	sma12hprev=worklist[35]
	sma24hprev=worklist[36]
	ranksma1h=worklist[37]
	ranksma12h=worklist[38]
	ranksma24h=worklist[39]
	rankcloseprev=worklist[40]
	breakoutprocess=worklist[41]
	breakouthigh=worklist[42]
	breakoutcountdown=worklist[43]
	evenement=""

    # sma
	sma7s=round((sma7sprev*1+close)/2,6)
	sma8s=round((sma8sprev*7+close)/8,6)
	sma9s=round((sma9sprev*8+close)/9,6)
	sma1h=round((sma1hprev*4+close)/5,6)       #3600
	sma2h=round((sma2hprev*7199+close)/7200,6)  #7200
	sma12h=round((sma12hprev*9+close)/10,6)    #43200
	sma24h=round((sma24hprev*19+close)/20,6)    #86400
	
	# breakout ###############################################
	
	ranklist=[0,0,0,0]
	rankdict={}
	rankdict.update({0: close})                # worklist[40]
	rankdict.update({1: sma1h})                # worklist[37]
	rankdict.update({2: sma12h})               # worklist[38]
	rankdict.update({3: sma24h})               # worklist[39]
	rankdict_=dict(sorted(rankdict.items(), key=lambda item: float(item[1])))
	rr=0
	for r in rankdict_:
		#print(ranklist[r],int(rr))
		ranklist[r]=int(rr)
		rr+=1
	rankclose=ranklist[0]
	ranksma1h=ranklist[1]
	ranksma12h=ranklist[2]
	ranksma24h=ranklist[3]
	print(rankclose,ranksma1h,ranksma12h,ranksma24h)

	if rankclose > rankcloseprev and rankclose >= 3:
		#print(s,"rankclose > rankcloseprev",rankclose,rankcloseprev)
		if breakoutprocess == 0 or breakoutcountdown <= 0 :
			#breakoutcountdown=60 	# compte à rebours
			breakouthigh=close
			breakoutprocess=1  	# chercher un high du close_price, 
		                		# booléen 1 du high, 2 de la descente et remontée
		
	if breakoutprocess==1 :
		print(s,"breakoutprocess==1",breakoutcountdown)
		#breakoutcountdown-=1
		if close > closeprev :
			print("breakouthigh=close",close,closeprev)
			breakouthigh=close
		else:
			breakoutprocess=2
			
	if breakoutprocess==2 :
		print(s,"breakoutprocess==2",breakoutcountdown)
		#breakoutcountdown-=1
		if sma7s < sma7sprev and close > breakouthigh :
			#print("sma7s < sma7sprev and close > breakouthigh",close,breakouthigh)
			breakoutprocess=0
			evenement="breakout"
			title=s+"-"+str(E)+"-"+evenement
			_thread.start_new_thread(sendlistcsv,(worklist.copy(),title))	# envoie de worklist csv
		elif breakoutcountdown<0 or rankclose<=1 : 
			breakoutprocess=0
			
	for i in range(20):
		worklist[i]=initlist[i]
	worklist[30]=sma7s
	worklist[31]=sma8s
	worklist[32]=sma9s
	worklist[33]=sma1h
	worklist[34]=sma2h
	worklist[35]=sma12h
	worklist[36]=sma24h
	worklist[37]=ranksma1h
	worklist[38]=ranksma12h
	worklist[39]=ranksma24h
	worklist[40]=rankclose
	worklist[41]=breakoutprocess
	worklist[42]=breakouthigh
	#print("breakouthigh out",worklist[42])
	worklist[43]=breakoutcountdown
	worklist[44]=evenement
    
	# mise à jour de listsymbol
	listlock.acquire()
	if len(listsymbol)>200:
		listsymbol.pop(0)
	#print("before",len(listsymbol))
	listsymbol.append(worklist.copy())
	#print("after",len(listsymbol))
	listlock.release()

	# envoie pour graph
	if evenement=="breakout":
		listftp=[]
		print("breakout")
		list_lock_chrono.acquire()
		listlock.acquire()
		for l in (listsymbol):
			if s in l:
				listftp.append(l.copy())
		listlock.release()
		list_lock_chrono.release()
		title=s+"-"+str(E)+"-"+evenement
		_thread.start_new_thread(sendlistgraph,(listftp.copy(),title))

	_thread.exit()
	    
def sendlistgraph(l,title):
	ftplock.acquire()
	filpath="./uploaddirgraph/"+title
	with open(filpath, 'wb') as fp:
		print(filpath)
		pickle.dump(l, fp)
	filserverpath="domain.com/hft/graphin/"+title
	with FTP(host, user, password) as ftp :
		with open(filpath, "rb") as f:
			print(filpath,filserverpath)
			ftp.storbinary("STOR " + filserverpath, f)
	os.remove(filpath)
	ftplock.release()
	
def sendlistcsv(l,title):
	ftplock.acquire()
	filpath="./uploaddircsv/"+title
	with open(filpath, 'wb') as fp:
		print(filpath)
		pickle.dump(l, fp)
	filserverpath="domain.com/hft/in/"+title
	with FTP(host, user, password) as ftp :
		with open(filpath, "rb") as f:
			print(filpath,filserverpath)
			ftp.storbinary("STOR " + filserverpath, f)
	os.remove(filpath)
	ftplock.release()

requete_=info_()

_thread.start_new_thread(ws_thread, ())

while True:
	yves=1
