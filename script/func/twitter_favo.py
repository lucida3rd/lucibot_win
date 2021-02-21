#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : Twitter監視 いいね監視系
# 
# ::Update= 2021/2/21
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   __init__( self, parentObj=None ):
#   Get(self):
#   View(self):
#   Run(self):
#
# Class Function(static):
#   (none)
#
#####################################################

from osif import CLS_OSIF
from mydisp import CLS_MyDisp
from gval import gVal
#####################################################
class CLS_TwitterFavo():
#####################################################
	OBJ_Parent = ""				#親クラス実体
	VAL_ZanNum = 0

#####################################################
# Init
#####################################################
	def __init__( self, parentObj=None ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterFavo"
		wRes['Func']  = "__init__"
		
		if parentObj==None :
			###親クラス実体の未設定
			wRes['Reason'] = "You have not set the parent class entity for parentObj"
			gVal.OBJ_L.Log( "A", wRes )
			return
		
		self.OBJ_Parent = parentObj
		return



#####################################################
# いいね情報の取得
#####################################################
	def Get(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterFavo"
		wRes['Func']  = "Get"
		
		#############################
		# 取得開始の表示
		CLS_OSIF.sPrn( "いいね情報を取得中。しばらくお待ちください......" )
		
		#############################
		# DBのいいね一覧取得
		wQuery = "select * from tbl_favo_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		gVal.STR_TrafficInfo['dbreq'] += 1
		
		#############################
		# 辞書型に整形
		wARR_RateFavo = {}
		gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateFavo )
		
		#############################
		# 取得
		wTwitterRes = gVal.OBJ_Twitter.GetFavolist()
		if wTwitterRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error: " + wTwitterRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		gVal.STR_TrafficInfo['favo'] = len(wTwitterRes['Responce'])
		
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "PC時間の取得に失敗しました"
			gVal.OBJ_L.Log( "B", wRes )
			return
		### wTD['TimeDate']
		
		#############################
		# Twitterのいいね一覧を取得
		#   DBに記録されていなければ、記録する
		#   DBに記録されている かつ期間外なら limited をONにする
		wARR_FavoID = []
		for wROW in wTwitterRes['Responce'] :
			wARR_FavoID.append( str(wROW['id']) )	#Favo IDだけ記録
			
			wTime = CLS_OSIF.sGetTimeformat_Twitter( wROW['created_at'] )
			if wTime['Result']!=True :
				wRes['Reason'] = "sGetTimeformat_Twitter is failed: " + str(wROW['created_at'])
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			###wTime['TimeDate']
			
			#############################
			# 記録を探す
			#   記録されている場合、いいね期間外であれば解除対象にする
			#   記録されていない場合、DBに記録する
			wFLG_Ditect = False
			wKeylist = wARR_RateFavo.keys()
			for wIndex in wKeylist :
				if str(wARR_RateFavo[wIndex]['id'])==str(wROW['id']) :
					wFLG_Ditect = True	#DB記録あり
					break
			
			if wFLG_Ditect==True :
				###DBに記録されている
				
				###  既にリムーブor期間外ならばスキップ
				if wARR_RateFavo[wIndex]['removed']==True or \
				   wARR_RateFavo[wIndex]['limited']==True :
					continue
				
				###  いいね期間外かを求める (変換＆差)
				wFavoLimmin = gVal.DEF_STR_TLNUM['favoLimmin'] * 60	#秒に変換
				wGetLag = CLS_OSIF.sTimeLag( str(wARR_RateFavo[wIndex]['regdate']), inThreshold=wFavoLimmin )
				if wGetLag['Result']!=True :
					wRes['Reason'] = "sTimeLag failed"
					gVal.OBJ_L.Log( "B", wRes )
					return wRes
				if wGetLag['Beyond']==True :
					###いいね期間外
					###  limited をONにする
					wQuery = "update tbl_favo_data set " + \
								"limited = True " + \
								"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
								" and id = '" + str(wROW['id']) + "' ;"
					
					wResDB = gVal.OBJ_DB.RunQuery( wQuery )
					wResDB = gVal.OBJ_DB.GetQueryStat()
					if wResDB['Result']!=True :
						##失敗
						wRes['Reason'] = "Run Query is failed(2): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
						gVal.OBJ_L.Log( "B", wRes )
						return wRes
					
					###  カウント
					gVal.STR_TrafficInfo['dbreq'] += 1
					gVal.STR_TrafficInfo['dbup'] += 1
			
			else:
				###DBに記録されていない
				###  記録する
				wText = str(wROW['text'])
				wText = wText.replace( "'", "''" )
				
				wName = str(wROW['user']['name']).replace( "'", "''" )
				wQuery = "insert into tbl_favo_data values (" + \
							"'" + gVal.STR_UserInfo['Account'] + "'," + \
							"'" + str(wTD['TimeDate']) + "'," + \
							"False," + \
							"False," + \
							"'" + str(wROW['id']) + "'," + \
							"'" + wName + "'," + \
							"'" + str(wROW['user']['screen_name']) + "'," + \
							"'" + wText + "'," + \
							"'" + str(wTime['TimeDate']) + "'" + \
							") ;"
				
				wResDB = gVal.OBJ_DB.RunQuery( wQuery )
				wResDB = gVal.OBJ_DB.GetQueryStat()
				if wResDB['Result']!=True :
					##失敗
					wRes['Reason'] = "Run Query is failed(3): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
					gVal.OBJ_L.Log( "B", wRes )
					return wRes
				
				gVal.STR_TrafficInfo['dbreq'] += 1
				gVal.STR_TrafficInfo['dbins'] += 1
		
		#############################
		# DBのいいね一覧 再取得
		wQuery = "select * from tbl_favo_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(3): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		gVal.STR_TrafficInfo['dbreq'] += 1
		
		#############################
		# 辞書型に整形
		wARR_RateFavo = {}
		gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateFavo )
		
		#############################
		# DBに記録があるのに、Twitterのいいね一覧にない情報
		#   リムーブ済みでなければ、リムーブ済みにする
		# 保存期間を過ぎた情報
		#   DBから削除する
		wKeylist = wARR_RateFavo.keys()
		for wIndex in wKeylist :
			### DBに記録があるのに、Twitterのいいね一覧にない
			###   リムーブ済みにする
			if wARR_RateFavo[wIndex]['id'] not in wARR_FavoID :
				###まだリムーブ済みではない
				if wARR_RateFavo[wIndex]['removed']==False :
					wQuery = "update tbl_favo_data set " + \
								"removed = True " + \
								"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
								" and id = '" + str(wARR_RateFavo[wIndex]['id']) + "' ;"
					
					wResDB = gVal.OBJ_DB.RunQuery( wQuery )
					wResDB = gVal.OBJ_DB.GetQueryStat()
					if wResDB['Result']!=True :
						##失敗
						wRes['Reason'] = "Run Query is failed(4): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
						gVal.OBJ_L.Log( "B", wRes )
						return wRes
					
					gVal.STR_TrafficInfo['favoremove'] += 1
					gVal.STR_TrafficInfo['dbreq'] += 1
					gVal.STR_TrafficInfo['dbup'] += 1
				
				continue
			
			### Twitterのいいね一覧にある
			else:
				###リムーブ済み
				if wARR_RateFavo[wIndex]['removed']==True :
					gVal.STR_TrafficInfo['favoremove'] += 1
				###期間外
				elif wARR_RateFavo[wIndex]['limited']==True :
					gVal.STR_TrafficInfo['favoremovet'] += 1
			
			###保存期間外かを求める (変換＆差)
			wFavoLimmin = gVal.DEF_STR_TLNUM['favoDBLimmin'] * 60	#秒に変換
			wGetLag = CLS_OSIF.sTimeLag( str(wARR_RateFavo[wIndex]['regdate']), inThreshold=wFavoLimmin )
			if wGetLag['Result']!=True :
				wRes['Reason'] = "sTimeLag failed(2)"
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			if wGetLag['Beyond']==True :
				###期間外
				###  削除する
				wQuery = "delete from tbl_favo_data " + \
							"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
							" and id = '" + str(wARR_RateFavo[wIndex]['id']) + "' ;"
				
				wResDB = gVal.OBJ_DB.RunQuery( wQuery )
				wResDB = gVal.OBJ_DB.GetQueryStat()
				if wResDB['Result']!=True :
					##失敗
					wRes['Reason'] = "Run Query is failed(5): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
					gVal.OBJ_L.Log( "B", wRes )
					return wRes
				
				gVal.STR_TrafficInfo['dbreq'] += 1
				gVal.STR_TrafficInfo['dbdel'] += 1
		
		#############################
		# 正常終了
		wRes['Result'] = True
		return wRes



#####################################################
# いいね情報の表示
#####################################################
	def View(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterFavo"
		wRes['Func']  = "View"
		
		#############################
		# DBのいいね一覧取得
		wQuery = "select * from tbl_favo_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		gVal.STR_TrafficInfo['dbreq'] += 1
		
		#############################
		# 辞書型に整形
		wARR_RateFavoID = {}
		gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateFavoID )
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " 保持中のいいね情報" + '\n'
		wStr = wStr + "--------------------" + '\n'
		
		#############################
		# 情報組み立て
		wKeylist = wARR_RateFavoID.keys()
		for wIndex in wKeylist :
			if wARR_RateFavoID[wIndex]['twitterid']!=gVal.STR_UserInfo['Account'] :
				continue	#自分以外の情報はスキップ
			
			wStr = wStr + str(wARR_RateFavoID[wIndex]['text']) + '\n'
			wStr = wStr + "ツイ日=" + str(wARR_RateFavoID[wIndex]['created_at'])
			wStr = wStr + "  ユーザ=" + str(wARR_RateFavoID[wIndex]['user_name']) + "(@" + str(wARR_RateFavoID[wIndex]['screen_name']) + ")" + '\n'
			wStr = wStr + "登録日=" + str(wARR_RateFavoID[wIndex]['regdate'])
			if wARR_RateFavoID[wIndex]['removed']==True :
				wStr = wStr + " [☆いいね解除済み]"
			elif wARR_RateFavoID[wIndex]['limited']==True :
				wStr = wStr + " [★いいね解除対象]"
			wStr = wStr + '\n'
			wStr = wStr + "--------------------" + '\n'
		
		#############################
		# 統計
		wStr = wStr + "--------------------" + '\n'
		wStr = wStr + "解除対象 いいね数 = " + str(gVal.STR_TrafficInfo['favoremovet']) + '\n'
		wStr = wStr + "解除済み いいね数 = " + str(gVal.STR_TrafficInfo['favoremove']) + '\n'
		
		#############################
		# コンソールに表示
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# いいね監視の実行
#####################################################
	def Run(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterFavo"
		wRes['Func']  = "Run"
		
		#############################
		# DBのいいね一覧取得 (いいね解除対象の抜き出し)
		wQuery = "select * from tbl_favo_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "' and " + \
					"limited = True and " + \
					"removed = False " + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		gVal.STR_TrafficInfo['dbreq'] += 1
		
		#############################
		# 辞書型に整形
		wARR_RateFavoID = {}
		gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateFavoID )
		gVal.STR_TrafficInfo['favoremovet'] = len(wARR_RateFavoID)
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " いいね監視 実行" + '\n'
		wStr = wStr + "--------------------" + '\n'
		wStr = wStr + "以下のいいね解除対象をいいね解除します......" + '\n'
		CLS_OSIF.sPrn( wStr )
		
		wVAL_ZanNum = len(wARR_RateFavoID)
		wFavoLimNum = 0
		wResStop = False
		#############################
		# いいね解除していく
		wKeylist = wARR_RateFavoID.keys()
		for wIndex in wKeylist :
			wID = str( wARR_RateFavoID[wIndex]['id'] )
			
			###  いいねを外す
			wRemoveRes = gVal.OBJ_Twitter.RemoveFavo( wID )
			if wRemoveRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error: " + wRemoveRes['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			
			###  解除したいいねを表示
			wStr = str(wARR_RateFavoID[wIndex]['text']) + '\n'
			wStr = wStr + "ツイ日=" + str(wARR_RateFavoID[wIndex]['created_at'])
			wStr = wStr + "  ユーザ=" + str(wARR_RateFavoID[wIndex]['user_name']) + "(@" + str(wARR_RateFavoID[wIndex]['screen_name']) + ")" + '\n'
			wStr = wStr + "登録日=" + str(wARR_RateFavoID[wIndex]['regdate'])
			wStr = wStr + " [☆いいね解除済み]"
			wStr = wStr + '\n'
			wStr = wStr + "--------------------" + '\n'
			CLS_OSIF.sPrn( wStr )
			
			gVal.STR_TrafficInfo['favoremove'] += 1
			
			###  limited をOFF、removed をONにする
			wQuery = "update tbl_favo_data set " + \
						"limited = False, " + \
						"removed = True " + \
						"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
						" and id = '" + wID + "' ;"
			
			wResDB = gVal.OBJ_DB.RunQuery( wQuery )
			wResDB = gVal.OBJ_DB.GetQueryStat()
			if wResDB['Result']!=True :
				##失敗
				wRes['Reason'] = "Run Query is failed(2): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			
			###  カウント
			gVal.STR_TrafficInfo['dbreq'] += 1
			gVal.STR_TrafficInfo['dbup'] += 1
			
			wFavoLimNum += 1
			wVAL_ZanNum -= 1
			#############################
			# 処理全て終わり
			if wVAL_ZanNum==0 :
				break
			
			#############################
			# 1回の解除数チェック
			elif gVal.DEF_STR_TLNUM['rFavoLimNum']<=wFavoLimNum :
				###解除数限界ならウェイトする
				CLS_OSIF.sPrn( "Twitter規制回避のため、待機します。" )
				CLS_OSIF.sPrn( "CTRL+Cで中止することもできます。残り処理数= " + str(wVAL_ZanNum) + " 個" )
				
				wResStop = CLS_OSIF.sPrnWAIT( gVal.DEF_STR_TLNUM['favoLimWait'] )
				if wResStop==False :
					CLS_OSIF.sPrn( "処理を中止しました。" + '\n' )
					break	#ウェイト中止
				wFavoLimNum = 0
			
			#############################
			# 残り処理回数がまだある =5秒ウェイトする
			else :
				CLS_OSIF.sSleep( 5 )
		
		#############################
		# 統計
		wStr = "--------------------" + '\n'
		wStr = wStr + "解除対象 いいね数 = " + str(gVal.STR_TrafficInfo['favoremovet']) + '\n'
		wStr = wStr + "解除済み いいね数 = " + str(gVal.STR_TrafficInfo['favoremove']) + '\n'
		
		#############################
		# コンソールに表示
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# 指定いいねの実行
#####################################################
	def DesiFavo(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterFavo"
		wRes['Func']  = "DesiFavo"
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# 実行の確認
		wStr = "--------------------" + '\n'
		wStr = wStr + " 指定いいね 実行" + '\n'
		wStr = wStr + "--------------------"
		CLS_OSIF.sPrn( wStr )
		
		CLS_OSIF.sPrn( "いいねするユーザを抽出しています......" + '\n' )
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "PC時間の取得に失敗しました"
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		### wTD['TimeDate']
		
		#############################
		# DBのフォロワー情報取得
		wQuery = "select * from tbl_follower_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "' " + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		gVal.STR_TrafficInfo['dbreq'] += 1
		
		#############################
		# 辞書型に整形
		wARR_RateFollowers = {}
		gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateFollowers )
		
		#############################
		# フォロー一覧 取得(idだけ)
		wMyFollowRes = gVal.OBJ_Twitter.GetMyFollowList()
		if wMyFollowRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetMyFollowList): " + wMyFollowRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		wARR_MyFollowID = []
		for wROW in wMyFollowRes['Responce'] :
			wARR_MyFollowID.append( str(wROW['id']) )
		
		#############################
		# フォロワー一覧 取得(idだけ)
		wFollowerRes = gVal.OBJ_Twitter.GetFollowerList()
		if wFollowerRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetFollowerList): " + wFollowerRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		wARR_FollowerID = []
		for wROW in wFollowerRes['Responce'] :
			wARR_FollowerID.append( str(wROW['id']) )
		
		#############################
		# favolist登録者とマージする
		wListsRes = gVal.OBJ_Twitter.GetListMember( gVal.STR_UserInfo['FavoList'] )
		if wListsRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetListMember:UrfList): " + wListsRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		wARR_FavoUsers = []
		for wROW in wListsRes['Responce'] :
			wARR_FavoUsers.append( str(wROW['id']) )
		if len(wARR_FavoUsers)==0 :
			wRes['Reason'] = "favolist user is zero."
			gVal.OBJ_L.Log( "D", wRes )
			return wRes
		
		#############################
		# 指定いいね候補IDの作成
		# DB登録者 かつ フォロー者orフォロワーであること
		wKeylist = list(wARR_RateFollowers)
		wDstFavoID = []
		wFLG_DstUser = False
		for wKey in wKeylist :
			if wARR_RateFollowers[wKey]['id'] not in wARR_FavoUsers :
				continue
			if wARR_RateFollowers[wKey]['id'] in wARR_MyFollowID :
				wFLG_DstUser = True
			if wARR_RateFollowers[wKey]['id'] in wARR_FollowerID :
				wFLG_DstUser = True
			if wFLG_DstUser!=True :
				continue
			wDstFavoID.append( wARR_RateFollowers[wKey]['id'] )
		
		###トラヒック
		gVal.STR_TrafficInfo['dejifavot'] = len( wDstFavoID )
		
		self.VAL_ZanNum = len( wDstFavoID )
		#############################
		# 候補のツイートを取得し、いいねしていく
		for wID in wDstFavoID :
			#############################
			# キーを抽出
			wIndex = -1
			for wKey in wKeylist :
				if wARR_RateFollowers[wKey]['id']==wID :
					wIndex = wKey
					break
			if wIndex==-1 :
				###キーが見当たらない(ここではありえない)
				wRes['Reason'] = "Key is not found: id=" + wID
				gVal.OBJ_L.Log( "B", wRes )
				CLS_OSIF.sPrn( "▼キーの取得に失敗したためスキップします" + '\n' )
				if self.__wait_DejiFavo( gVal.DEF_STR_TLNUM['AutoFavoSkipWait'] )!=True :
					break	#ウエイト中止
				continue	#スキップ
			
			#############################
			# 対象ユーザの表示
			wText = '\n' + "--------------------" + '\n'
			wText = wText + "処理ユーザ: " + wARR_RateFollowers[wIndex]['user_name']
			wText = wText + " (@" + wARR_RateFollowers[wIndex]['screen_name'] + ")"
			CLS_OSIF.sPrn( wText )
			
			### 前のいいねから一定期間以上経ったか
			if wARR_RateFollowers[wIndex]['favodate']!=None :
				wLimmin = gVal.DEF_STR_TLNUM['AutoFavoRateHour'] * 60 * 60	#秒に変換
				wGetLag = CLS_OSIF.sTimeLag( str(wARR_RateFollowers[wIndex]['favodate']), inThreshold=wLimmin )
				if wGetLag['Result']!=True :
					wRes['Reason'] = "sTimeLag failed"
					gVal.OBJ_L.Log( "B", wRes )
					continue
				if wGetLag['Beyond']==False :
					### 1日以内は除外
					CLS_OSIF.sPrn( "▼前回の自動いいねから1日経ってないためスキップします" )
					self.VAL_ZanNum -= 1
					if self.VAL_ZanNum==0 :
						break	#ウエイト中止
					continue	#スキップ
			
			#############################
			# ユーザの直近のツイートを取得
			wTweetRes = gVal.OBJ_Twitter.GetTL( inTLmode="user", inFLG_Rep=False, inFLG_Rts=False,
				 inScreenName=wARR_RateFollowers[wIndex]['screen_name'], inCount=gVal.DEF_STR_TLNUM['AutoFavoCount'] )
			if wTweetRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error(GetTL): " + wTweetRes['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				CLS_OSIF.sPrn( "▼ツイートの取得に失敗したためスキップします" + '\n' )
				if self.__wait_DejiFavo( gVal.DEF_STR_TLNUM['AutoFavoSkipWait'] )!=True :
					break	#ウエイト中止
				continue	#スキップ
			
			if len(wTweetRes['Responce'])==0 :
				CLS_OSIF.sPrn( "▼取得ツイートがないためスキップします" + '\n' )
				if self.__wait_DejiFavo( gVal.DEF_STR_TLNUM['AutoFavoSkipWait'] )!=True :
					break	#ウエイト中止
				continue	#スキップ
			gVal.STR_TrafficInfo['timeline'] += len(wTweetRes['Responce'])
			
			#############################
			# いいねするツイートIDを取得する
			wFavoTweetID = None
			for wTweet in wTweetRes['Responce'] :
				### リプライは除外
				if gVal.STR_AutoFavo['Rip']==False :
					if wTweet['in_reply_to_status_id']!=None :
						continue
				
				### リツイートは除外
				if gVal.STR_AutoFavo['Ret']==False :
					if "retweeted_status" in wTweet :
						continue
				
				### 引用リツイートは除外
				if gVal.STR_AutoFavo['iRet']==False :
					if "quoted_status" in wTweet :
						continue
				
				### 前回いいねしたIDは除外
				if wARR_RateFollowers[wIndex]['favoid']==str(wTweet['id']) :
					continue
				
				### 文字数不足は除外
				if len(wTweet['text'])<20 :
					continue
				
				### タグ付きは除外
				if gVal.STR_AutoFavo['Tag']==False :
					if wTweet['text'].find("#")!=-1 :
						continue
				
				###ツイートの先頭が @文字=リプライ
				if wTweet['text'].find("@")==0 :
					continue
				
				###ツイートに除外文字が含まれている場合は除外
				if self.OBJ_Parent.CheckExcWord( wTweet['text'] )==False :
					continue
				
				###日時の変換
				wTime = CLS_OSIF.sGetTimeformat_Twitter( wTweet['created_at'] )
				if wTime['Result']!=True :
					wRes['Reason'] = "sGetTimeformat_Twitter is failed(1): " + str(wTweet['created_at'])
					gVal.OBJ_L.Log( "B", wRes )
					continue
				wTweet['created_at'] = wTime['TimeDate']
				
				### 範囲時間内のツイートか
				wLimmin = gVal.STR_AutoFavo['Len'] * 60 * 60
				wGetLag = CLS_OSIF.sTimeLag( str(wTweet['created_at']), inThreshold=wLimmin )
				if wGetLag['Result']!=True :
					wRes['Reason'] = "sTimeLag failed"
					gVal.OBJ_L.Log( "B", wRes )
					continue
				if wGetLag['Beyond']==True :
					### 1日超経過は除外
					continue
				
				### ID決定
				wFavoTweetID = str(wTweet['id'])
				break
			
			if wFavoTweetID==None :
				CLS_OSIF.sPrn( "▼いいねするツイートがないためスキップします" + '\n')
				if self.__wait_DejiFavo( gVal.DEF_STR_TLNUM['AutoFavoSkipWait'] )!=True :
					break	#ウエイト中止
				continue	#スキップ
			
			#############################
			# いいねを実行する
			wFavoRes = gVal.OBJ_Twitter.CreateFavo( wFavoTweetID )
			if wFavoRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error: " + wFavoRes['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				continue
			
			CLS_OSIF.sPrn( "◎いいねしました：" + '\n' )
			CLS_OSIF.sPrn( wTweet['text'] + '\n' + "【ツイート日時: " + str(wTweet['created_at']) + "】" )
			gVal.STR_TrafficInfo['dejifavo'] += 1
			
			#############################
			# DBに記録する
			wQuery = "update tbl_follower_data set " + \
						"favoid = '" + str(wFavoTweetID) + "', " + \
						"favodate = '" + str(wTD['TimeDate']) + "' " + \
						"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
						" and id = '" + str(wID) + "' ;"
			
			wResDB = gVal.OBJ_DB.RunQuery( wQuery )
			wResDB = gVal.OBJ_DB.GetQueryStat()
			if wResDB['Result']!=True :
				##失敗
				wRes['Reason'] = "Run Query is failed(6): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
				gVal.OBJ_L.Log( "B", wRes )
				continue
			
			###  カウント
			gVal.STR_TrafficInfo['dbreq'] += 1
			gVal.STR_TrafficInfo['dbup'] += 1
			
			#############################
			# 次へのウェイト
			CLS_OSIF.sPrn("")
			if self.__wait_DejiFavo( gVal.DEF_STR_TLNUM['AutoFavoWait'] )!=True :
				break	#ウエイト中止
		
		#############################
		# 統計
		wStr = "--------------------" + '\n'
		wStr = wStr + "指定いいね対象数 = " + str(gVal.STR_TrafficInfo['dejifavot']) + '\n'
		wStr = wStr + "指定いいね実行数 = " + str(gVal.STR_TrafficInfo['dejifavo']) + '\n'
		
		#############################
		# コンソールに表示
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes

	#####################################################
	def __wait_DejiFavo( self, inWaitSec ):
		self.VAL_ZanNum -= 1
		#############################
		# 処理全て終わり
		if self.VAL_ZanNum==0 :
			return False	#ウェイト中止
		
		#############################
		# 処理ウェイト
		else:
			CLS_OSIF.sPrn( "CTRL+Cで中止することもできます。残り処理数= " + str(self.VAL_ZanNum) + " 個" )
			
			wResStop = CLS_OSIF.sPrnWAIT( inWaitSec )
			if wResStop==False :
				CLS_OSIF.sPrn( "処理を中止しました。" + '\n' )
				return False	#ウェイト中止
		
		return True



#####################################################
# 自動いいねの実行
#####################################################
	def AutoFavo(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterFavo"
		wRes['Func']  = "AutoFavo"
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# 実行の確認
		wStr = "--------------------" + '\n'
		wStr = wStr + " 自動いいね 実行" + '\n'
		wStr = wStr + "--------------------" + '\n'
		wStr = wStr + "いいねするユーザを抽出しています......" + '\n'
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "PC時間の取得に失敗しました"
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		### wTD['TimeDate']
		
		#############################
		# DBのフォロワー情報取得
		wQuery = "select * from tbl_follower_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "' " + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		gVal.STR_TrafficInfo['dbreq'] += 1
		
		#############################
		# 辞書型に整形
		wARR_RateFollowers = {}
		gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateFollowers )
		
		#############################
		# フォロー一覧 取得(idだけ)
		wMyFollowRes = gVal.OBJ_Twitter.GetMyFollowList()
		if wMyFollowRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetMyFollowList): " + wMyFollowRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		wARR_MyFollowID = []
		for wROW in wMyFollowRes['Responce'] :
			wARR_MyFollowID.append( str(wROW['id']) )
		
		#############################
		# フォロワー一覧 取得(idだけ)
		wFollowerRes = gVal.OBJ_Twitter.GetFollowerList()
		if wFollowerRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetFollowerList): " + wFollowerRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		wARR_FollowerID = []
		for wROW in wFollowerRes['Responce'] :
			wARR_FollowerID.append( str(wROW['id']) )
		
		#############################
		# 自動いいね候補IDの作成
		# 現Twitter相互フォロー かつ 監視時フォロワーであること
		wKeylist = list(wARR_RateFollowers)
		wDstAutoFavoID = []
		if gVal.STR_AutoFavo['PieF']==False :
			for wKey in wKeylist :
				if wARR_RateFollowers[wKey]['id'] not in wARR_MyFollowID :
					continue
				if wARR_RateFollowers[wKey]['id'] not in wARR_FollowerID :
					continue
				wDstAutoFavoID.append( wARR_RateFollowers[wKey]['id'] )
		else:
			for wKey in wKeylist :
				if wARR_RateFollowers[wKey]['id'] not in wARR_MyFollowID :
					continue
				wDstAutoFavoID.append( wARR_RateFollowers[wKey]['id'] )
		###トラヒック
		gVal.STR_TrafficInfo['autofavot'] = len( wDstAutoFavoID )
		
		###リツイートor引用リツイートメモ用
		wARR_SetTweet = {
			"flg"			: False,
			"id"			: -1,
			"name"			: None,
			"screen_name"	: None,
			"tw_id"			: -1,
			"tw_text"		: None,
			"created_at"	: None
		}
		
		self.VAL_ZanNum = len( wDstAutoFavoID )
		#############################
		# 候補のツイートを取得し、いいねしていく
		for wID in wDstAutoFavoID :
			
			wARR_SetTweet['flg'] = False
			#############################
			# キーを抽出
			wIndex = -1
			for wKey in wKeylist :
				if wARR_RateFollowers[wKey]['id']==wID :
					wIndex = wKey
					break
			if wIndex==-1 :
				###キーが見当たらない(ここではありえない)
				wRes['Reason'] = "Key is not found: id=" + wID
				gVal.OBJ_L.Log( "B", wRes )
				CLS_OSIF.sPrn( "▼キーの取得に失敗したためスキップします" + '\n' )
				if self.__wait_AutoFavo( gVal.DEF_STR_TLNUM['AutoFavoSkipWait'] )!=True :
					break	#ウエイト中止
				continue	#スキップ
			
			#############################
			# 対象ユーザの表示
			wText = '\n' + "--------------------" + '\n'
			wText = wText + "処理ユーザ: " + wARR_RateFollowers[wIndex]['user_name']
			wText = wText + " (@" + wARR_RateFollowers[wIndex]['screen_name'] + ")"
			CLS_OSIF.sPrn( wText )
			
			### 自動いいね失敗判定
			if wARR_RateFollowers[wIndex]['favo_f_cnt']>=gVal.DEF_STR_TLNUM['AutoFavoFailCnt'] :
				CLS_OSIF.sPrn( "▼自動いいね失敗判定のためスキップします: " + str(wARR_RateFollowers[wIndex]['favo_f_cnt']) + " 回目" )
				self.__failRec_AutoFavo( wRes, wID, wARR_RateFollowers[wIndex]['favo_f_cnt'], wTD['TimeDate'] )
				
				###※仮で 10回失敗したら 失敗カウントをリセットするようにする
				wFavo_f_cnt = wARR_RateFollowers[wIndex]['favo_f_cnt'] + 1
				if wFavo_f_cnt>= 10 :
					wQuery = "update tbl_follower_data set " + \
								"favo_f_cnt = 0 " + \
								"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
								" and id = '" + str(wID) + "' ;"
					
					wResDB = gVal.OBJ_DB.RunQuery( wQuery )
					wResDB = gVal.OBJ_DB.GetQueryStat()
					if wResDB['Result']!=True :
						##失敗
						wRes['Reason'] = "Run Query is failed(30): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
						gVal.OBJ_L.Log( "B", wRes )
					
					###  カウント
					gVal.STR_TrafficInfo['dbreq'] += 1
					gVal.STR_TrafficInfo['dbup'] += 1
					CLS_OSIF.sPrn( "☆10回失敗したので、カウンタをリセットしました" )
				
				self.VAL_ZanNum -= 1
				if self.VAL_ZanNum==0 :
					break	#ウエイト中止
				continue	#スキップ
			
			### 前のいいねから一定期間以上経ったか
			if wARR_RateFollowers[wIndex]['favodate']!=None :
				wLimmin = gVal.DEF_STR_TLNUM['AutoFavoRateHour'] * 60 * 60	#秒に変換
				wGetLag = CLS_OSIF.sTimeLag( str(wARR_RateFollowers[wIndex]['favodate']), inThreshold=wLimmin )
				if wGetLag['Result']!=True :
					wRes['Reason'] = "sTimeLag failed"
					gVal.OBJ_L.Log( "B", wRes )
					continue
				if wGetLag['Beyond']==False :
					### 1日以内は除外
					CLS_OSIF.sPrn( "▼前回の自動いいねから1日経ってないためスキップします" )
					self.VAL_ZanNum -= 1
					if self.VAL_ZanNum==0 :
						break	#ウエイト中止
					continue	#スキップ
			
			#############################
			# ユーザの直近のツイートを取得
			wTweetRes = gVal.OBJ_Twitter.GetTL( inTLmode="user", inFLG_Rep=False, inFLG_Rts=False,
				 inScreenName=wARR_RateFollowers[wIndex]['screen_name'], inCount=gVal.DEF_STR_TLNUM['AutoFavoCount'] )
			if wTweetRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error(GetTL): " + wTweetRes['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				CLS_OSIF.sPrn( "▼ツイートの取得に失敗したためスキップします" + '\n' )
				self.__failRec_AutoFavo( wRes, wID, wARR_RateFollowers[wIndex]['favo_f_cnt'], wTD['TimeDate'] )
				if self.__wait_AutoFavo( gVal.DEF_STR_TLNUM['AutoFavoSkipWait'] )!=True :
					break	#ウエイト中止
				continue	#スキップ
			
			if len(wTweetRes['Responce'])==0 :
				CLS_OSIF.sPrn( "▼取得ツイートがないためスキップします" + '\n' )
				self.__failRec_AutoFavo( wRes, wID, wARR_RateFollowers[wIndex]['favo_f_cnt'], wTD['TimeDate'] )
				if self.__wait_AutoFavo( gVal.DEF_STR_TLNUM['AutoFavoSkipWait'] )!=True :
					break	#ウエイト中止
				continue	#スキップ
			gVal.STR_TrafficInfo['timeline'] += len(wTweetRes['Responce'])
			
			#############################
			# いいねするツイートIDを取得する
			wFavoTweetID = None
			for wTweet in wTweetRes['Responce'] :
				### リプライは除外
				if gVal.STR_AutoFavo['Rip']==False :
					if wTweet['in_reply_to_status_id']!=None :
						continue
				
				### リツイートは除外
				if gVal.STR_AutoFavo['Ret']==False :
					if "retweeted_status" in wTweet :
						if wARR_SetTweet['flg']==False :
							wARR_SetTweet['id']          = wTweet['retweeted_status']['user']['id']
							wARR_SetTweet['name']        = wTweet['retweeted_status']['user']['name']
							wARR_SetTweet['screen_name'] = wTweet['retweeted_status']['user']['screen_name']
							wARR_SetTweet['tw_id']   = wTweet['retweeted_status']['id']
							wARR_SetTweet['tw_text'] = wTweet['retweeted_status']['text']
							wARR_SetTweet['created_at'] = wTweet['retweeted_status']['created_at']
							wARR_SetTweet['flg'] = True
						continue
				
				### 引用リツイートは除外
				if gVal.STR_AutoFavo['iRet']==False :
					if "quoted_status" in wTweet :
						if wARR_SetTweet['flg']==False :
							wARR_SetTweet['id']          = wTweet['quoted_status']['user']['id']
							wARR_SetTweet['name']        = wTweet['quoted_status']['user']['name']
							wARR_SetTweet['screen_name'] = wTweet['quoted_status']['user']['screen_name']
							wARR_SetTweet['tw_id']   = wTweet['quoted_status']['id']
							wARR_SetTweet['tw_text'] = wTweet['quoted_status']['text']
							wARR_SetTweet['created_at'] = wTweet['quoted_status']['created_at']
							wARR_SetTweet['flg'] = True
						continue
				
				### 前回いいねしたIDは除外
				if wARR_RateFollowers[wIndex]['favoid']==str(wTweet['id']) :
					continue
				
				### 文字数不足は除外
				if len(wTweet['text'])<20 :
					continue
				
				### タグ付きは除外
				if gVal.STR_AutoFavo['Tag']==False :
					if wTweet['text'].find("#")!=-1 :
						continue
				
				###ツイートの先頭が @文字=リプライ
				if wTweet['text'].find("@")==0 :
					continue
				
				###ツイートに除外文字が含まれている場合は除外
				if self.OBJ_Parent.CheckExcWord( wTweet['text'] )==False :
					continue
				
				###日時の変換
				wTime = CLS_OSIF.sGetTimeformat_Twitter( wTweet['created_at'] )
				if wTime['Result']!=True :
					wRes['Reason'] = "sGetTimeformat_Twitter is failed(1): " + str(wTweet['created_at'])
					gVal.OBJ_L.Log( "B", wRes )
					continue
				wTweet['created_at'] = wTime['TimeDate']
				
				### 範囲時間内のツイートか
				wLimmin = gVal.STR_AutoFavo['Len'] * 60 * 60
				wGetLag = CLS_OSIF.sTimeLag( str(wTweet['created_at']), inThreshold=wLimmin )
				if wGetLag['Result']!=True :
					wRes['Reason'] = "sTimeLag failed"
					gVal.OBJ_L.Log( "B", wRes )
					continue
				if wGetLag['Beyond']==True :
					### 1日超経過は除外
					continue
				
				### ID決定
				wFavoTweetID = str(wTweet['id'])
				
				wARR_SetTweet['id']          = wTweet['user']['id']
				wARR_SetTweet['name']        = wTweet['user']['name']
				wARR_SetTweet['screen_name'] = wTweet['user']['screen_name']
				wARR_SetTweet['tw_id']      = wTweet['id']
				wARR_SetTweet['tw_text']    = wTweet['text']
				wARR_SetTweet['created_at'] = wTweet['created_at']
				wARR_SetTweet['flg'] = False	#通常ツイートなのでフラグを落とす
				break
			
			if wFavoTweetID==None :
###				CLS_OSIF.sPrn( "▼いいねするツイートがないためスキップします" + '\n')
###				self.__failRec_AutoFavo( wRes, wID, wARR_RateFollowers[wIndex]['favo_f_cnt'] )
###				
###				if self.__wait_AutoFavo( gVal.DEF_STR_TLNUM['AutoFavoSkipWait'] )!=True :
###					break	#ウエイト中止
###				continue	#スキップ
###				
				### ID未決定
				if wARR_SetTweet['flg']==False :
					### リツイート＆引用リツイートもなし
					CLS_OSIF.sPrn( "▼いいねするツイートがないためスキップします" + '\n')
					self.__failRec_AutoFavo( wRes, wID, wARR_RateFollowers[wIndex]['favo_f_cnt'], wTD['TimeDate'] )
					
					if self.__wait_AutoFavo( gVal.DEF_STR_TLNUM['AutoFavoSkipWait'] )!=True :
						break	#ウエイト中止
					continue	#スキップ
				else:
					### ID未決定だけどリツイートor引用リツイートは取得している
					wFavoTweetID = wARR_SetTweet['tw_id']	#リツイートor引用リツイートのIDをセット
			
			#############################
			# いいねを実行する
			wFavoRes = gVal.OBJ_Twitter.CreateFavo( wFavoTweetID )
			if wFavoRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error: " + wFavoRes['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				continue
			
###			CLS_OSIF.sPrn( "◎いいねしました：" + '\n' )
###			CLS_OSIF.sPrn( wTweet['text'] + '\n' + "【ツイート日時: " + str(wTweet['created_at']) + "】" )
			
			if wARR_SetTweet['flg']==False :
				wStr = "◎いいねしました：" + '\n'
			else:
				wStr = "●リツイートをいいねしました：" + '\n'
			wStr = wStr + wARR_SetTweet['tw_text'] + '\n'
			wStr = wStr + "　ツイート日時: " + wARR_SetTweet['created_at'] + '\n'
			wStr = wStr + "  ユーザ　　　: " + wARR_SetTweet['name']
			wStr = wStr + " (@" + wARR_SetTweet['screen_name'] + ")"
			CLS_OSIF.sPrn( wStr )
			gVal.STR_TrafficInfo['autofavo'] += 1
			
###			#############################
###			# ふぁぼカウンタを設定
###			wARR_RateFollowers[wIndex]['favo_cnt'] += 1
###			wARR_RateFollowers[wIndex]['favo_f_cnt'] = 0	#ふぁぼできたのでリセットする
###			
			#############################
			# DBに記録する(通常ツイートの場合)
			if wARR_SetTweet['flg']==False :
				#### ふぁぼカウンタを設定
				wARR_RateFollowers[wIndex]['favo_cnt'] += 1
				wARR_RateFollowers[wIndex]['favo_f_cnt'] = 0	#ふぁぼできたのでリセットする
				
				wQuery = "update tbl_follower_data set " + \
							"favoid = '" + str(wFavoTweetID) + "', " + \
							"favodate = '" + str(wTD['TimeDate']) + "'," + \
							"favo_cnt = " + str(wARR_RateFollowers[wIndex]['favo_cnt']) + ", " + \
							"favo_f_cnt = 0 " + \
							"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
							" and id = '" + str(wID) + "' ;"
				
				wResDB = gVal.OBJ_DB.RunQuery( wQuery )
				wResDB = gVal.OBJ_DB.GetQueryStat()
				if wResDB['Result']!=True :
					##失敗
					wRes['Reason'] = "Run Query is failed(6): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
					gVal.OBJ_L.Log( "B", wRes )
					continue
				
				###  カウント
				gVal.STR_TrafficInfo['dbreq'] += 1
				gVal.STR_TrafficInfo['dbup'] += 1
			
			#############################
			# 次へのウェイト
			CLS_OSIF.sPrn("")
			if self.__wait_AutoFavo( gVal.DEF_STR_TLNUM['AutoFavoWait'] )!=True :
				break	#ウエイト中止
		
		#############################
		# 統計
		wStr = "--------------------" + '\n'
		wStr = wStr + "自動いいね対象数 = " + str(gVal.STR_TrafficInfo['autofavot']) + '\n'
		wStr = wStr + "自動いいね実行数 = " + str(gVal.STR_TrafficInfo['autofavo']) + '\n'
		
		#############################
		# コンソールに表示
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes

	#####################################################
	def __wait_AutoFavo( self, inWaitSec ):
		self.VAL_ZanNum -= 1
		#############################
		# 処理全て終わり
		if self.VAL_ZanNum==0 :
			return False	#ウェイト中止
		
		#############################
		# 処理ウェイト
		else:
			CLS_OSIF.sPrn( "CTRL+Cで中止することもできます。残り処理数= " + str(self.VAL_ZanNum) + " 個" )
			
			wResStop = CLS_OSIF.sPrnWAIT( inWaitSec )
			if wResStop==False :
				CLS_OSIF.sPrn( "処理を中止しました。" + '\n' )
				return False	#ウェイト中止
		
		return True

	#####################################################
	def __failRec_AutoFavo( self, inRes, inID, inFavo_f_cnt, inDate ):
		
		#############################
		# カウンタ+
		wCnt = inFavo_f_cnt + 1
		
		#############################
		# DBに記録する (ふぁぼ失敗カウント)
		wQuery = "update tbl_follower_data set " + \
					"favodate = '" + str(inDate) + "', " + \
					"favo_f_cnt = " + str(wCnt) + " " + \
					"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					" and id = '" + str(inID) + "' ;"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			inRes['Reason'] = "Run Query is failed(20): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			gVal.OBJ_L.Log( "B", inRes )
			return False
		
		###  カウント
		gVal.STR_TrafficInfo['dbreq'] += 1
		gVal.STR_TrafficInfo['dbup'] += 1
		
		return True



#####################################################
# 無差別いいねの実行
#####################################################
	def CaoFavo(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterFavo"
		wRes['Func']  = "CaoFavo"
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# 実行の確認
		wStr = "--------------------" + '\n'
		wStr = wStr + " 無差別いいね 実行" + '\n'
		wStr = wStr + "--------------------" + '\n'
		wStr = wStr + "ツイートを抽出しています......" + '\n'
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "PC時間の取得に失敗しました"
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		### wTD['TimeDate']
		
		#############################
		# DBのフォロワー情報取得
		wQuery = "select id from tbl_follower_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "' " + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		gVal.STR_TrafficInfo['dbreq'] += 1
		
		#############################
		# リスト型に整形
		wARR_RateUserID = []
		gVal.OBJ_DB.ChgList( wResDB['Responce']['Data'], outList=wARR_RateUserID )
		
		#############################
		# un_refollowl登録者 取得(idだけ)
		wListsRes = gVal.OBJ_Twitter.GetLists()
		if wListsRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetLists): " + wListsRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		
		wListsRes = gVal.OBJ_Twitter.GetListMember( gVal.STR_UserInfo['UrfList'] )
		if wListsRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetListMember:UrfList): " + wListsRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		wARR_UnRefollowListMenberID = []
		for wROW in wListsRes['Responce'] :
			wARR_UnRefollowListMenberID.append( str(wROW['id']) )
		
		#############################
		# いいね一覧取得
		wFavoListID = []
		wTwitterRes = gVal.OBJ_Twitter.GetFavolist()
		if wTwitterRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error: " + wTwitterRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		for wLine in wTwitterRes['Responce'] :
			wFavoListID.append( wLine['id'] )
		
		#############################
		# Home TLの取得
###		wHomeTL_Res = gVal.OBJ_Twitter.GetTL( inTLmode="home", inFLG_Rep=True, inFLG_Rts=False, inScreenName=STR_TWITTERdata['TwitterID'], gVal.inCount=DEF_STR_TLNUM['CaoFavoTL'] )
		wHomeTL_Res = gVal.OBJ_Twitter.GetTL( inTLmode="home", inFLG_Rts=True, inCount=gVal.DEF_STR_TLNUM['CaoFavoTL'] )
		if wHomeTL_Res['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetMyFollowList): " + wHomeTL_Res['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		
		###トラヒック
		gVal.STR_TrafficInfo['autofavot'] = len( wHomeTL_Res['Responce'] )
		
		self.VAL_ZanNum = len( wHomeTL_Res['Responce'] )
		#############################
		# ふぁぼっていく
		wFavoUserID = []
		wRetweetNum = 0
		for wTweet in wHomeTL_Res['Responce'] :
			### リプライは除外
			if wTweet['in_reply_to_status_id']!=None :
				self.VAL_ZanNum -= 1
				continue
			
			###リツイートの場合 =元ツイートをサルベージ
			if "retweeted_status" in wTweet :
				if wTweet['retweet_count']<10 :
					self.VAL_ZanNum -= 1
					continue
				
				###リツイート制限中
				if wRetweetNum >= gVal.DEF_STR_TLNUM['CaoFavoRetweet'] :
					wRetweetNum = 0
				elif wRetweetNum>0  :
					wRetweetNum += 1
					continue
				
				wTweet = wTweet['retweeted_status']
				wKind = "リツイ"
			
			###引用リツイートの場合 =元ツイートをサルベージ
			elif "quoted_status" in wTweet :
				if wTweet['retweet_count']<10 and wTweet['favorite_count']<10 :
					self.VAL_ZanNum -= 1
					continue
				wTweet = wTweet['quoted_status']
				wKind = "引用　"
			else :
			###通常ツイート
				if wTweet['retweet_count']==0 and wTweet['favorite_count']==0 :
					self.VAL_ZanNum -= 1
					continue
				wKind = "通常　"
			
			### 既にふぁぼったツイートは除外
			if wTweet['id'] in wFavoListID :
				self.VAL_ZanNum -= 1
				continue
			
			### 自分は除外する
			if wTweet['user']['id']==int( gVal.STR_UserInfo['id'] ) :
				self.VAL_ZanNum -= 1
				continue
			
			### 既にふぁぼってるユーザなら除外する
			if wTweet['user']['id'] in wFavoUserID :
				self.VAL_ZanNum -= 1
				continue
			
			### botで認識のあるユーザ、除外リストのユーザは除外する
			wID = str(wTweet['user']['id'])
			if wID in wARR_RateUserID :
				self.VAL_ZanNum -= 1
				continue
			if wID in wARR_UnRefollowListMenberID :
				self.VAL_ZanNum -= 1
				continue
			
			### 文字数不足は除外
			if len(wTweet['text'])<40 :
				self.VAL_ZanNum -= 1
				continue
			
#			### タグ付きは除外
#			if wTweet['text'].find("#")!=-1 :
#				self.VAL_ZanNum -= 1
#				continue
#			
			###ツイートの先頭が @文字=リプライ
			if wTweet['text'].find("@")==0 :
				self.VAL_ZanNum -= 1
				continue
			
			###ツイートに除外文字が含まれている場合は除外
			if self.OBJ_Parent.CheckExcWord( wTweet['text'] )==False :
				self.VAL_ZanNum -= 1
				continue
			
			##※いいね確定
			
			#############################
			# 対象ユーザの表示
			wText = '\n' + "--------------------" + '\n'
			wText = wText + "処理ユーザ: " + wTweet['user']['name']
			wText = wText + " (@" + wTweet['user']['screen_name'] + ")"
			CLS_OSIF.sPrn( wText )
			
			#############################
			# いいねを実行する
			wFavoRes = gVal.OBJ_Twitter.CreateFavo( wTweet['id'] )
			if wFavoRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error: " + wFavoRes['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				self.VAL_ZanNum -= 1
				continue
			
			wText = wKind + ": ◎いいねしました：" + '\n'
			wText = wText + wTweet['text'] + '\n' + "【ツイート日時: " + str(wTweet['created_at']) + "】"
			CLS_OSIF.sPrn( wText )
			gVal.STR_TrafficInfo['autofavo'] += 1
			
			### ふぁぼったユーザIDをメモする
			wFavoUserID.append( wTweet['user']['id'] )
			
			if wRetweetNum==0 :
				###リツイ規制カウンタ進める
				wRetweetNum += 1
			
			#############################
			# 次へのウェイト
			CLS_OSIF.sPrn("")
			if self.__wait_AutoFavo( gVal.DEF_STR_TLNUM['AutoFavoWait'] )!=True :
				break	#ウエイト中止
		
		#############################
		# 統計
		wStr = "--------------------" + '\n'
		wStr = wStr + "自動いいね対象数 = " + str(gVal.STR_TrafficInfo['autofavot']) + '\n'
		wStr = wStr + "自動いいね実行数 = " + str(gVal.STR_TrafficInfo['autofavo']) + '\n'
		
		#############################
		# コンソールに表示
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# 自動いいね設定
#####################################################
	def SetAutoFavo(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterFavo"
		wRes['Func']  = "SetAutoFavo"
		
		#############################
		# コンソールを表示
		while True :
			#############################
			# 画面クリア
			CLS_OSIF.sDispClr()
			
			#############################
			# 管理画面を表示する
			wWord = self.__view_AutoFavo()
			
			if wWord=="\\q" :
				###終了
				break
			if wWord=="" :
				###未入力は再度入力
				continue
			
			wResSearch = self.__run_AutoFavo( wWord )
			CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
		
		wRes['Result'] = True
		return wRes

	#####################################################
	# 自動いいね設定 画面表示
	#####################################################
	def __view_AutoFavo(self):
		wResDisp = CLS_MyDisp.sViewDisp( "AutoFavoConsole", -1 )
		if wResDisp['Result']==False :
			gVal.OBJ_L.Log( "D", wResDisp )
			return "\\q"	#失敗=強制終了
		
		wWord = CLS_OSIF.sInp( "コマンド？=> " )
		return wWord

	#####################################################
	# 自動いいね設定 実行
	#####################################################
	def __run_AutoFavo( self, inWord ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterFavo"
		wRes['Func']  = "__run_AutoFavo"
		
		#############################
		# コマンドを分解する
		wARR_Cmd = inWord.split(":")
		if len(wARR_Cmd)>2 :
			CLS_OSIF.sPrn( "コマンドが誤ってます" + '\n' )
			return wRes
		wWord = wARR_Cmd[0]
		
		#############################
		# コマンド：リプライを含める
		if wWord=="\\p" :
			if gVal.STR_AutoFavo['Rip']==True :
				gVal.STR_AutoFavo['Rip'] = False
			else:
				gVal.STR_AutoFavo['Rip'] = True
		
		#############################
		# コマンド：リツイートを含める
		elif wWord=="\\r" :
			if gVal.STR_AutoFavo['Ret']==True :
				gVal.STR_AutoFavo['Ret'] = False
			else:
				gVal.STR_AutoFavo['Ret'] = True
		
		#############################
		# コマンド：引用リツイートを含める
		elif wWord=="\\i" :
			if gVal.STR_AutoFavo['iRet']==True :
				gVal.STR_AutoFavo['iRet'] = False
			else:
				gVal.STR_AutoFavo['iRet'] = True
		
		#############################
		# コマンド：タグを含める
		elif wWord=="\\t" :
			if gVal.STR_AutoFavo['Tag']==True :
				gVal.STR_AutoFavo['Tag'] = False
			else:
				gVal.STR_AutoFavo['Tag'] = True
		
		#############################
		# コマンド：片フォローを含める
		elif wWord=="\\f" :
			if gVal.STR_AutoFavo['PieF']==True :
				gVal.STR_AutoFavo['PieF'] = False
			else:
				gVal.STR_AutoFavo['PieF'] = True
		
		#############################
		# コマンド：対象範囲時間
		elif wWord=="\\l" and len(wARR_Cmd)==2 :
			wLengRes = CLS_OSIF.sChgInt( wARR_Cmd[1] )
			if wLengRes['Result']!=True :
				CLS_OSIF.sPrn( "数値ではありません" + '\n' )
				return wRes
			if wLengRes['Value']<1 or wLengRes['Value']>24 :
				CLS_OSIF.sPrn( "数値が範囲外です(1-24)" + '\n' )
				return wRes
			gVal.STR_AutoFavo['Len'] = wLengRes['Value']
		
		#############################
		# 不明なコマンド
		else :
			CLS_OSIF.sPrn( "不明なコマンドです" + '\n' )
			return wRes
		
		#############################
		# 正常終了
		wRes['Result'] = True
		return wRes



