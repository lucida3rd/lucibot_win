#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : トラヒック
# 
# ::Update= 2021/1/11
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   __init__(self):
#   Get(self):
#   View(self):
#   Run(self):
#
# Class Function(static):
#   (none)
#
#####################################################

from osif import CLS_OSIF
from gval import gVal
#####################################################
class CLS_Traffic():

#####################################################
# トラヒック情報の取得
#####################################################
	@classmethod
	def sGet(cls):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Traffic"
		wRes['Func']  = "Get"
		
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "PC時間の取得に失敗しました"
			return wRes
		### wTD['TimeDate']
		wARR_TD = wTD['TimeDate'].split(" ")
		
		#############################
		# DBの今日のトラヒック情報取得
		wQuery = "select * from tbl_traffic_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "' " + \
					" and day = '" + wARR_TD[0] + "';"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		#############################
		# 辞書型に整形
		wARR_RateTraffic = {}
		gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateTraffic )
		
		#############################
		# 今日の記録がなければ
		#   =空行を作成する
		if len(wARR_RateTraffic)==0 :
			#############################
			# DBに空行を挿入
			wResIns = cls.__insert_Traffic( wTD['TimeDate'] )
			if wResIns['Result']!=True :
				##失敗
				wRes['Reason'] = "__insert_Traffic is failed: " + CLS_OSIF.sCatErr( wResIns )
				return wRes
		
		#############################
		# 今日の記録があれば
		# [0]を今日とする
		else:
			wARR_RateTraffic = wARR_RateTraffic[0]
			
			gVal.STR_TrafficInfo['timeline'] = wARR_RateTraffic['timeline']
			
			gVal.STR_TrafficInfo['favo'] = wARR_RateTraffic['favo']
			gVal.STR_TrafficInfo['favoremove']  = wARR_RateTraffic['favoremove']
			
			gVal.STR_TrafficInfo['myfollow']  = wARR_RateTraffic['myfollow']
			gVal.STR_TrafficInfo['follower']  = wARR_RateTraffic['follower']
			gVal.STR_TrafficInfo['piefollow'] = wARR_RateTraffic['piefollow']
			gVal.STR_TrafficInfo['newfollower'] = wARR_RateTraffic['newfollower']
			gVal.STR_TrafficInfo['selremove']   = wARR_RateTraffic['selremove']
			
			gVal.STR_TrafficInfo['autofollow']  = wARR_RateTraffic['autofollow']
			gVal.STR_TrafficInfo['autofavo']  = wARR_RateTraffic['autofavo']
			
			gVal.STR_TrafficInfo['arashi']  = wARR_RateTraffic['arashi']
			gVal.STR_TrafficInfo['arashii'] = wARR_RateTraffic['arashii']
			gVal.STR_TrafficInfo['arashir'] = wARR_RateTraffic['arashir']
			
			gVal.STR_TrafficInfo['dbreq'] = wARR_RateTraffic['dbreq']
			gVal.STR_TrafficInfo['dbins'] = wARR_RateTraffic['dbins']
			gVal.STR_TrafficInfo['dbup']  = wARR_RateTraffic['dbup']
			gVal.STR_TrafficInfo['dbdel'] = wARR_RateTraffic['dbdel']
			
			gVal.STR_TrafficInfo['run']    = wARR_RateTraffic['run']
			gVal.STR_TrafficInfo['update'] = wTD['TimeDate']
		
		#############################
		# 正常終了
		wRes['Result'] = True
		return wRes

	#####################################################
	@classmethod
	def __insert_Traffic( cls, inTimeDate ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Traffic"
		wRes['Func']  = "__insert_Traffic"
		
		#############################
		# 日時だけ取り出し
		wARR_TD = inTimeDate.split(" ")
		
		#############################
		# 空行を挿入
		wQuery = "insert into tbl_traffic_data values (" + \
					"'" + gVal.STR_UserInfo['Account'] + "'," + \
					"'" + str( inTimeDate ) + "'," + \
					"'" + str( inTimeDate ) + "'," + \
					"'" + str( wARR_TD[0] ) + "'," + \
					"false," + \
					"0," + \
					"0, 0," + \
					"0, 0, 0, 0, 0," + \
					"0," + \
					"0," + \
					"0, 0, 0," + \
					"0, 0, 0, 0," + \
					"0" + \
					") ;"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		#############################
		# 初期化
		gVal.STR_TrafficInfo['timeline'] = 0
		
		gVal.STR_TrafficInfo['favo'] = 0
		gVal.STR_TrafficInfo['favoremovet'] = 0
		gVal.STR_TrafficInfo['favoremove']  = 0
		
		gVal.STR_TrafficInfo['myfollow']  = 0
		gVal.STR_TrafficInfo['follower']  = 0
		gVal.STR_TrafficInfo['piefollow'] = 0
		gVal.STR_TrafficInfo['newfollower'] = 0
		gVal.STR_TrafficInfo['selremove']   = 0
		
		gVal.STR_TrafficInfo['autofollowt'] = 0
		gVal.STR_TrafficInfo['autofollow']  = 0
		
		gVal.STR_TrafficInfo['autofavot'] = 0
		gVal.STR_TrafficInfo['autofavo']  = 0
		
		gVal.STR_TrafficInfo['arashi']  = 0
		gVal.STR_TrafficInfo['arashii'] = 0
		gVal.STR_TrafficInfo['arashir'] = 0
		
		gVal.STR_TrafficInfo['dbreq'] = 0
		gVal.STR_TrafficInfo['dbins'] = 0
		gVal.STR_TrafficInfo['dbup']  = 0
		gVal.STR_TrafficInfo['dbdel'] = 0
		
		gVal.STR_TrafficInfo['run']    = 0
		gVal.STR_TrafficInfo['update'] = inTimeDate
		
		#############################
		# 正常終了
		wRes['Result'] = True
		return wRes



#####################################################
# トラヒック情報の記録
#####################################################
	@classmethod
	def sSet(cls):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Traffic"
		wRes['Func']  = "Set"
		
		wRes['Responce'] = False
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "PC時間の取得に失敗しました"
			return wRes
		### wTD['TimeDate']
		wARR_NowTD = wTD['TimeDate'].split(" ")
		
		#############################
		# 更新
		wQuery = "update tbl_traffic_data set " + \
					"timeline = " + str( gVal.STR_TrafficInfo['timeline'] ) + "," + \
					"favo = " + str( gVal.STR_TrafficInfo['favo'] ) + "," + \
					"favoremove = " + str( gVal.STR_TrafficInfo['favoremove'] ) + "," + \
					"myfollow = " + str( gVal.STR_TrafficInfo['myfollow'] ) + "," + \
					"follower = " + str( gVal.STR_TrafficInfo['follower'] ) + "," + \
					"piefollow = " + str( gVal.STR_TrafficInfo['piefollow'] ) + "," + \
					"newfollower = " + str( gVal.STR_TrafficInfo['newfollower'] ) + "," + \
					"selremove = " + str( gVal.STR_TrafficInfo['selremove'] ) + "," + \
					"autofollow = " + str( gVal.STR_TrafficInfo['autofollow'] ) + "," + \
					"autofavo = " + str( gVal.STR_TrafficInfo['autofavo'] ) + "," + \
					"arashi = " + str( gVal.STR_TrafficInfo['arashi'] ) + "," + \
					"arashii = " + str( gVal.STR_TrafficInfo['arashii'] ) + "," + \
					"arashir = " + str( gVal.STR_TrafficInfo['arashir'] ) + "," + \
					"dbreq = " + str( gVal.STR_TrafficInfo['dbreq'] ) + "," + \
					"dbins = " + str( gVal.STR_TrafficInfo['dbins'] ) + "," + \
					"dbup = " + str( gVal.STR_TrafficInfo['dbup'] ) + "," + \
					"dbdel = " + str( gVal.STR_TrafficInfo['dbdel'] ) + "," + \
					"run = " + str( gVal.STR_TrafficInfo['run'] ) + "," + \
					"update = '" + str( gVal.STR_TrafficInfo['update'] ) + "' " + \
					"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					" and day = '" + str( wARR_NowTD[0] ) + "' ;"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		#############################
		# 日付が変わったか
		wARR_TD = gVal.STR_TrafficInfo['update'].split(" ")
		
		if wARR_NowTD[0]!=wARR_TD[0] :
			### 日付=変わった
			###   DBに空行を挿入
			wResIns = cls.__insert_Traffic( wTD['TimeDate'] )
			if wResIns['Result']!=True :
				##失敗
				wRes['Reason'] = "__insert_Traffic is failed: " + CLS_OSIF.sCatErr( wResIns )
				return wRes
			wRes['Responce'] = True	#日付変更したことを知らせる
		
		#############################
		# 正常終了
		wRes['Result'] = True
		return wRes



#####################################################
# 未報告のトラヒック情報を報告する
#####################################################
	@classmethod
	def sReport( cls, inToday=False, inAll=True ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Traffic"
		wRes['Func']  = "sReport"
		
		wRes['Responce'] = False
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "PC時間の取得に失敗しました"
			return wRes
		### wTD['TimeDate']
		wARR_TD = wTD['TimeDate'].split(" ")
		
		#############################
		# DBの未報告のトラヒック情報取得
		wQuery = "select * from tbl_traffic_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "' " + \
					" and reported = False" + \
					" and day = '" + wARR_TD[0] + "'" + \
					" order by day desc ;"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		#############################
		# 辞書型に整形
		wARR_RateTraffic = {}
		gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateTraffic )
		
		wReportNum = len( wARR_RateTraffic )
		#############################
		# 未報告の記録がなければ終わり
		if wReportNum==0 :
			wRes['Result'] = True
			return wRes
		
		wReported = 0	#報告した数
		wIndex = 0
		while True :
			#############################
			# 全て報告した
			if wReportNum<=wIndex :
				break
			
			#############################
			# 今日分はスキップする
			if wARR_RateTraffic[wIndex]['day']==wARR_TD[0] and inToday==False :
				wIndex += 1
				continue
			
			#############################
			# 表示する
			cls.__view_Traffic( wARR_RateTraffic[wIndex] )
			
			#############################
			# 報告済みにする
			wQuery = "update tbl_traffic_data set " + \
						"reported = True " + \
						"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
						" and day = '" + str( wARR_TD[0] ) + "' ;"
			
			wResDB = gVal.OBJ_DB.RunQuery( wQuery )
			wResDB = gVal.OBJ_DB.GetQueryStat()
			if wResDB['Result']!=True :
				##失敗
				wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
				return wRes
			wReported += 1
			wIndex += 1
			
			#############################
			# Twitterに送信する
###			if gVal.STR_UserInfo['Traffic']==False :
###				### 有効でない場合、送信するか確認する
###				wResSend = CLS_OSIF.sInp( '\n' + "このトラヒックをTwitterに送信しますか？(y=送信する / other=送信しない)=> " )
###				if wResSend=="y" :
###					### Twitterに送信する
###					wResTwitter = cls.__send_Twitter( wARR_RateTraffic[wIndex] )
###					if wResTwitter['Result']!=True :
###						##失敗
###						wResTwitter['Reason'] = "__send_Twitter is failed: " + CLS_OSIF.sCatErr( wResTwitter )
###						gVal.OBJ_L.Log( "B", wResTwitter )
###			else:
###				### 無確認でTwitterに送信する
			wResTwitter = cls.__send_Twitter( wARR_RateTraffic[wIndex] )
			if wResTwitter['Result']!=True :
				##失敗
				wResTwitter['Reason'] = "__send_Twitter is failed(Traffic=True): " + CLS_OSIF.sCatErr( wResTwitter )
				gVal.OBJ_L.Log( "B", wResTwitter )
			
			#############################
			# 1回だけならループ終了
			if inAll==False :
				break
			
		
		#############################
		# 1件以上報告した
		if wReportNum>=1 :
			wRes['Responce'] = True
		
		#############################
		# 正常終了
		wRes['Result'] = True
		return wRes

	#####################################################
	@classmethod
	def __view_Traffic( cls, inTraffic, inConfirm=True ):
##		#############################
##		# 画面クリア
##		CLS_OSIF.sDispClr()
##		
		#############################
		# ヘッダ表示
###		wStr = "--------------------" + '\n'
		wStr = '\n' + "--------------------" + '\n'
		wStr = wStr + " トラヒック情報 報告" + '\n'
		wStr = wStr + "--------------------" + '\n'
		wStr = wStr + str( inTraffic['update'] ) + '\n'
		wStr = wStr + '\n'
		
		#############################
		# 情報の作成
		wStr = wStr + "Bot実行回数        : " + str( inTraffic['run'] ) + '\n'
		wStr = wStr + "取得タイムライン数 : " + str( inTraffic['timeline'] ) + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "現いいね数         : " + str( inTraffic['favo'] ) + '\n'
		wStr = wStr + "解除実行 いいね数  : " + str( inTraffic['favoremove'] ) + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "現フォロー数       : " + str( inTraffic['myfollow'] ) + '\n'
		wStr = wStr + "現フォロワー数     : " + str( inTraffic['follower'] ) + '\n'
		wStr = wStr + "片フォロワー数     : " + str( inTraffic['piefollow'] ) + '\n'
###		wStr = wStr + "新規フォロワー数   : " + str( inTraffic['newfollower'] ) + '\n'
		wStr = wStr + "被リムーブ数       : " + str( inTraffic['selremove'] ) + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "自動リムーブ実行数 : " + str( inTraffic['autofollow'] ) + '\n'
		wStr = wStr + "自動いいね実施数   : " + str( inTraffic['autofavo'] ) + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "荒らし登録者数     : " + str( inTraffic['arashi'] ) + '\n'
		wStr = wStr + "荒らし検出回数     : " + str( inTraffic['arashii'] ) + '\n'
		wStr = wStr + "荒らし解除者数     : " + str( inTraffic['arashir'] ) + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "クエリ要求回数     : " + str( inTraffic['dbreq'] ) + '\n'
		wStr = wStr + "DB挿入回数         : " + str( inTraffic['dbins'] ) + '\n'
		wStr = wStr + "DB更新回数         : " + str( inTraffic['dbup'] ) + '\n'
		wStr = wStr + "DB削除回数         : " + str( inTraffic['dbdel'] ) + '\n'
		wStr = wStr + '\n'
		
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 確認しなくていいなら終了
		if inConfirm==False :
			return
		
		CLS_OSIF.sInp( "確認したらリターンキーを押してください。[RT]" )
		return

	#####################################################
	@classmethod
	def __send_Twitter( cls, inTraffic ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Traffic"
		wRes['Func']  = "__send_Twitter"
		
		#############################
		# 文の組み立て
		wTweet = "Traffic: " + str(gVal.STR_TrafficInfo['update']) + '\n'
		wTweet = "run " + str(gVal.STR_TrafficInfo['run']) + '\n'
###		wTweet = "newfollower " + str(gVal.STR_TrafficInfo['newfollower']) + '\n'
		wTweet = "selfremove " + str(gVal.STR_TrafficInfo['selremove']) + '\n'
		wTweet = "arashi detect " + str(gVal.STR_TrafficInfo['arashii'])
		
		#############################
		# Twitterに送信
###		wTwitterRes = gVal.OBJ_Twitter.Tweet( wTweet )
		wTwitterRes = gVal.OBJ_Twitter.SendDM( gVal.STR_UserInfo['id'], wTweet )
		if wTwitterRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error: " + wTwitterRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		
		#############################
		# 正常終了
		wRes['Result'] = True
		return wRes



#####################################################
# トラヒック情報を表示する
#####################################################
	@classmethod
	def sView(cls):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Traffic"
		wRes['Func']  = "sView"
		
		#############################
		# DBの未報告のトラヒック情報取得
		wQuery = "select * from tbl_traffic_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "' " + \
					" order by day desc ;"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		#############################
		# 辞書型に整形
		wARR_RateTraffic = {}
		gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateTraffic )
		
		wReportNum = len( wARR_RateTraffic )
		#############################
		# トラヒックがなければ終わり
		if wReportNum==0 :
			wRes['Result'] = True
			return wRes
		
		wIndex = 0
		while True :
			#############################
			# 表示する
			cls.__view_Traffic( wARR_RateTraffic[wIndex], False )
			wIndex += 1
			
			#############################
			# 全て報告した
			if wReportNum<=wIndex :
				break
			
			#############################
			# 停止するか
			wResNext = CLS_OSIF.sInp( '\n' + "次のトラヒック情報を表示しますか？(q=中止 / other=表示する)=> " )
			if wResNext=="y" :
				break
		
		#############################
		# 正常終了
		wRes['Result'] = True
		return wRes



