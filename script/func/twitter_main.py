#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : Twitter監視 メインモジュール
# 
# ::Update= 2020/10/8
#####################################################
# Private Function:
#   __checkTwitterPatt( self, inROW ):
#   __getTwitterPatt(self):
#
# Instance Function:
#   __init__(self):
#   GetCope(self):
#   GetNewFollower(self):
#   Run(self):

#   __get_FavoInfo(self):
#   ViewFavo(self):

#   Get_RunFavoAdmin(self):
#   Get_Run_FollowerAdmin(self):
#
# Class Function(static):
#   (none)
#
#####################################################
###import threading
###import sys, time

from osif import CLS_OSIF
from filectrl import CLS_File
from gval import gVal
#####################################################
class CLS_TwitterMain():
#####################################################
###	Obj_Parent = ""				#親クラス実体
	
	STR_Cope = {				#処理カウンタ
		"FavoNum"			: 0,	#現いいね数
		"tFavoRemove"		: 0,	#解除対象 いいね数
		"FavoRemove"		: 0,	#解除実行 いいね数
		
		"MyFollowNum"		: 0,	#現フォロー数
		"FollowerNum"		: 0,	#現フォロワー数
		"NewFollowerNum"	: 0,	#新規フォロワー数
		"tMyFollowRemove"	: 0,	#自動リムーブ 対象数
		"MyFollowRemove"	: 0,	#自動リムーブ 実行数
		
		"DB_Num"			: 0,	#DB登録数
		"DB_Insert"			: 0,	#DB挿入
		"DB_Update"			: 0,	#DB更新
		"DB_Delete"			: 0,	#DB削除
		
		"dummy"				: 0		#(未使用)
	}

###	VAL_WaitCount = 0

	STR_newFollower = {}
	VAL_newFollower = 0



#####################################################
# 集計取得
#####################################################
	def GetCope(self):
		return self.STR_Cope	#返すだけ



#####################################################
# 新規フォロワー取得
#####################################################
	def GetNewFollower(self):
		return self.STR_newFollower	#返すだけ



#####################################################
# Init
#####################################################
###	def __init__( self, parentObj=None ):
	def __init__(self):
##		if parentObj==None :
##			###親クラス実体の未設定
##			CLS_OSIF.sPrn( "CLS_Twitter_Ctrl: __init__: You have not set the parent class entity for parentObj" )
##			return
##		
##		self.Obj_Parent = parentObj
		return



#####################################################
# 監視情報の取得 実行
#####################################################
	def Run(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# 集計のリセット
		self.STR_Cope['FavoNum'] = 0
		self.STR_Cope['tFavoRemove'] = 0
		self.STR_Cope['FavoRemove']  = 0
		
		self.STR_Cope['MyFollowNum'] = 0
		self.STR_Cope['FollowerNum'] = 0
		self.STR_Cope['NewFollowerNum']  = 0
		self.STR_Cope['tMyFollowRemove'] = 0
		self.STR_Cope['MyFollowRemove']  = 0
		
		self.STR_Cope['DB_Num']    = 0
		self.STR_Cope['DB_Insert'] = 0
		self.STR_Cope['DB_Update'] = 0
		self.STR_Cope['DB_Delete'] = 0
		
		#############################
		# いいね情報の取得
		wResSub = self.__get_FavoInfo()
		if wResSub['Result']!=True :
			wRes['Reason'] = wResSub['Reason']
			return wRes
		
		#############################
		# フォロワー情報の取得
		wResSub = self.__get_FollowerInfo()
		if wResSub['Result']!=True :
			wRes['Reason'] = wResSub['Reason']
			return wRes
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " 監視情報 結果" + '\n'
		wStr = wStr + "--------------------" + '\n'
		
		#############################
		# 情報組み立て
		wStr = wStr + "現いいね数        = " + str(self.STR_Cope['FavoNum']) + '\n'
		wStr = wStr + "解除対象 いいね数 = " + str(self.STR_Cope['tFavoRemove']) + '\n'
		wStr = wStr + "解除済み いいね数 = " + str(self.STR_Cope['FavoRemove']) + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "現フォロー数        = " + str(self.STR_Cope['MyFollowNum']) + '\n'
		wStr = wStr + "現フォロワー数      = " + str(self.STR_Cope['FollowerNum']) + '\n'
		wStr = wStr + "新規フォロワー数    = " + str(self.STR_Cope['NewFollowerNum']) + '\n'
		wStr = wStr + "自動リムーブ 対象数 = " + str(self.STR_Cope['tMyFollowRemove']) + '\n'
		wStr = wStr + "自動リムーブ 実行数 = " + str(self.STR_Cope['MyFollowRemove']) + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "DB登録数 = " + str(self.STR_Cope['DB_Num']) + '\n'
		wStr = wStr + "DB挿入   = " + str(self.STR_Cope['DB_Insert']) + '\n'
		wStr = wStr + "DB更新   = " + str(self.STR_Cope['DB_Update']) + '\n'
		wStr = wStr + "DB削除   = " + str(self.STR_Cope['DB_Delete']) + '\n'
		
		#############################
		# コンソールに表示
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# いいね情報の取得
#####################################################
	def __get_FavoInfo(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# DBのいいね一覧取得
		wQuery = "select * from tbl_favo_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_TwitterMain: __get_FavoInfo: Run Query is failed(1): " + wDBRes['Reason'] + " query=" + wDBRes['Query']
			return wRes
		
		#############################
		# 辞書型に整形
		wARR_RateFavoID = {}
		gVal.OBJ_DB.ChgDict( wDBRes['Responce']['Collum'], wDBRes['Responce']['Data'], outDict=wARR_RateFavoID )
		self.STR_Cope['DB_Num'] = len(wARR_RateFavoID)
		
		#############################
		# 取得
		wTwitterRes = gVal.OBJ_Twitter.GetFavolist()
		if wTwitterRes['Result']!=True :
			wRes['Reason'] = "CLS_TwitterMain: __get_FavoInfo: Twitter API Error: " + wTwitterRes['Reason']
			return wRes
		self.STR_Cope['FavoNum'] = len(wTwitterRes['Responce'])
		
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "CLS_TwitterMain: __get_FavoInfo: PC時間の取得に失敗しました"
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
				wRes['Reason'] = "CLS_TwitterMain: __get_FavoInfo: sGetTimeformat_Twitter is failed: " + str(wROW['created_at'])
				return wRes
			
			###記録を探す
			wFLG_Ditect = False
			wKeylist = wARR_RateFavoID.keys()
			for wIndex in wKeylist :
				if str(wARR_RateFavoID[wIndex]['id'])==str(wROW['id']) :
					wFLG_Ditect = True	#DB記録あり
					break
			
			if wFLG_Ditect==True :
				###DBに記録されている
				
				###  既にリムーブor期間外ならばスキップ
				if wARR_RateFavoID[wIndex]['removed']==True or \
				   wARR_RateFavoID[wIndex]['limited']==True :
					continue
				
				###  いいね期間外かを求める (変換＆差)
				wFavoLimmin = gVal.DEF_STR_TLNUM['favoLimmin'] * 60	#秒に変換
				wGetLag = CLS_OSIF.sTimeLag( str(wARR_RateFavoID[wIndex]['regdate']), inThreshold=wFavoLimmin )
				if wGetLag['Result']!=True :
					wRes['Reason'] = "CLS_TwitterMain: __get_FavoInfo: sTimeLag failed"
					return wRes
				if wGetLag['Beyond']==True :
					###いいね期間外
					###  limited をONにする
					wQuery = "update tbl_favo_data set " + \
								"limited = True " + \
								"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
								" and id = '" + str(wROW['id']) + "' ;"
					
					wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
					wDBRes = gVal.OBJ_DB.GetQueryStat()
					if wDBRes['Result']!=True :
						##失敗
						wRes['Reason'] = "CLS_TwitterMain: __get_FavoInfo: Run Query is failed(2): " + wDBRes['Reason']
						return wRes
					
					###  カウント
					self.STR_Cope['DB_Update'] += 1
			
			else:
				###DBに記録されていない
				###  記録する
				wQuery = "insert into tbl_favo_data values (" + \
							"'" + gVal.STR_UserInfo['Account'] + "'," + \
							"'" + str(wTD['TimeDate']) + "'," + \
							"False," + \
							"False," + \
							"'" + str(wROW['id']) + "'," + \
							"'" + str(wROW['user']['name']) + "'," + \
							"'" + str(wROW['user']['screen_name']) + "'," + \
							"'" + str(wROW['text']) + "'," + \
							"'" + str(wTime['TimeDate']) + "'" + \
							") ;"
				
				wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
				wDBRes = gVal.OBJ_DB.GetQueryStat()
				if wDBRes['Result']!=True :
					##失敗
					wRes['Reason'] = "CLS_TwitterMain: __get_FavoInfo: Run Query is failed(3): " + wDBRes['Reason']
					return wRes
				
				self.STR_Cope['DB_Insert'] += 1
		
		#############################
		# DBに記録があるのに、Twitterのいいね一覧にない情報
		#   リムーブ済みでなければ、リムーブ済みにする
		# 保存期間を過ぎた情報
		#   DBから削除する
		wKeylist = wARR_RateFavoID.keys()
		for wIndex in wKeylist :
			### DBに記録があるのに、Twitterのいいね一覧にない
			###   リムーブ済みにする
			if wARR_RateFavoID[wIndex]['id'] not in wARR_FavoID :
				###まだリムーブ済みではない
				if wARR_RateFavoID[wIndex]['removed']==False :
					wQuery = "update tbl_favo_data set " + \
								"removed = True " + \
								"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
								" and id = '" + str(wARR_RateFavoID[wIndex]['id']) + "' ;"
					
					wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
					wDBRes = gVal.OBJ_DB.GetQueryStat()
					if wDBRes['Result']!=True :
						##失敗
						wRes['Reason'] = "CLS_TwitterMain: __get_FavoInfo: Run Query is failed(4): " + wDBRes['Reason']
						return wRes
					
					self.STR_Cope['FavoRemove'] += 1
					self.STR_Cope['DB_Update'] += 1
				
				continue
			
			### Twitterのいいね一覧にある
			else:
				###リムーブ済み
				if wARR_RateFavoID[wIndex]['removed']==True :
					self.STR_Cope['FavoRemove'] += 1
				###期間外
				elif wARR_RateFavoID[wIndex]['limited']==True :
					self.STR_Cope['tFavoRemove'] += 1
			
			###保存期間外かを求める (変換＆差)
			wFavoLimmin = gVal.DEF_STR_TLNUM['favoDBLimmin'] * 60	#秒に変換
			wGetLag = CLS_OSIF.sTimeLag( str(wARR_RateFavoID[wIndex]['regdate']), inThreshold=wFavoLimmin )
			if wGetLag['Result']!=True :
				wRes['Reason'] = "CLS_TwitterMain: __get_FavoInfo: sTimeLag failed(2)"
				return wRes
			if wGetLag['Beyond']==True :
				###期間外
				###  削除する
				wQuery = "delete from tbl_favo_data " + \
							"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
							" and id = '" + str(wARR_RateFavoID[wIndex]['id']) + "' ;"
				
				wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
				wDBRes = gVal.OBJ_DB.GetQueryStat()
				if wDBRes['Result']!=True :
					##失敗
					wRes['Reason'] = "CLS_TwitterMain: __get_FavoInfo: Run Query is failed(5): " + wDBRes['Reason']
					return wRes
				
				self.STR_Cope['DB_Delete'] += 1
		
		#############################
		# 正常終了
		wRes['Result'] = True
		return wRes



#####################################################
# フォロワー情報の取得
#####################################################
	def __get_FollowerInfo(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# DBのフォロワー一覧取得
		wQuery = "select * from tbl_follower_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_Twitter_Ctrl: __get_FollowerInfo: Run Query is failed(1): " + wDBRes['Reason'] + " query=" + wDBRes['Query']
			return wRes
		
		#############################
		# 辞書型に整形
		wARR_RateFollowers = {}
		gVal.OBJ_DB.ChgDict( wDBRes['Responce']['Collum'], wDBRes['Responce']['Data'], outDict=wARR_RateFollowers )

		#############################
		# フォロー一覧 取得(idだけ)
		wMyFollowRes = gVal.OBJ_Twitter.GetMyFollowList()
		if wMyFollowRes['Result']!=True :
			wRes['Reason'] = "CLS_Twitter_Ctrl: __get_FollowerInfo: Twitter API Error(GetMyFollowList): " + wMyFollowRes['Reason']
			return wRes
		wARR_MyFollowID = []
		for wROW in wMyFollowRes['Responce'] :
			wARR_MyFollowID.append( str(wROW['id']) )
		self.STR_Cope['MyFollowNum'] = len(wARR_MyFollowID)
		
		#############################
		# フォロワー一覧 取得
		wFollowerRes = gVal.OBJ_Twitter.GetFollowerList()
		if wFollowerRes['Result']!=True :
			wRes['Reason'] = "CLS_Twitter_Ctrl: __get_FollowerInfo: Twitter API Error(GetFollowerList): " + wFollowerRes['Reason']
			return wRes
		wARR_FollowerID = []
		for wROW in wFollowerRes['Responce'] :
			wARR_FollowerID.append( str(wROW['id']) )
		self.STR_Cope['FollowerNum'] = len(wARR_FollowerID)
		
		#############################
		# normal登録者 取得(idだけ)
		wListsRes = gVal.OBJ_Twitter.GetLists()
		if wListsRes['Result']!=True :
			wRes['Reason'] = "CLS_Twitter_Ctrl: __get_FollowerInfo: Twitter API Error(GetLists): " + wListsRes['Reason']
			return wRes
		wListsRes = gVal.OBJ_Twitter.GetListMember( gVal.STR_UserInfo['NorList'] )
		if wListsRes['Result']!=True :
			wRes['Reason'] = "CLS_Twitter_Ctrl: __get_FollowerInfo: Twitter API Error(GetListMember): " + wListsRes['Reason']
			return wRes
		wARR_NormalListMenberID = []
		for wROW in wListsRes['Responce'] :
			wARR_NormalListMenberID.append( str(wROW['id']) )
		
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "CLS_TwitterMain: __get_FollowerInfo: PC時間の取得に失敗しました"
			return wRes
		### wTD['TimeDate']
		
		#############################
		# Twitterのフォロワー一覧を取得
		#   DBに記録されていなければ、記録する
		#   DBに記録されていたら、フォロー状態を更新する
		wARR_FollowerID = []
		for wROW in wFollowerRes['Responce'] :
			wARR_FollowerID.append( str(wROW['id']) )	#フォロワーIDだけ記録
			
			###記録を探す
			wFLG_Ditect = False
			wKeylist = wARR_RateFollowers.keys()
			for wIndex in wKeylist :
				if str(wARR_RateFollowers[wIndex]['id'])==str(wROW['id']) :
					wFLG_Ditect = True	#DB記録あり
					break
			
			###フォロー状態
			wFLG_MyFollow = False
			wCHR_FolDate  = "1900-01-01 00:00:00"
			if str(wROW['id']) in wARR_MyFollowID :
				###フォロー済み
				wFLG_MyFollow = True
				wCHR_FolDate  = str(wTD['TimeDate'])
			
			if wFLG_Ditect==True :
				###DBに記録されている
				
				###記録上フォローしたことある かつ 未フォローなら記録
				if wARR_RateFollowers[wIndex]['r_myfollow']==True and \
				   wFLG_MyFollow==False :
###					continue
					wQuery = "update tbl_follower_data set " + \
								"r_myfollow = True, " + \
								"rc_follower = True, " + \
								"foldate = '" + str(wCHR_FolDate) + "' " + \
								"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
								" and id = '" + str(wROW['id']) + "' ;"
				else:
					###前回もフォロワーならスキップ
					if wARR_RateFollowers[wIndex]['rc_follower']==True :
						continue
					###前回フォロワーではない かつ 今回フォロワーなら記録
					wQuery = "update tbl_follower_data set " + \
								"rc_follower = True " + \
								"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
								" and id = '" + str(wROW['id']) + "' ;"
				
				###フォロー済み 前回フォロワー状態、フォロー日時を記録
				wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
				wDBRes = gVal.OBJ_DB.GetQueryStat()
				if wDBRes['Result']!=True :
					##失敗
					wRes['Reason'] = "CLS_TwitterMain: __get_FollowerInfo: Run Query is failed(2): " + wDBRes['Reason']
					return wRes
				
				###  カウント
				self.STR_Cope['DB_Update'] += 1
			
			else:
				###DBに記録されていない
				###  記録する
				wQuery = "insert into tbl_follower_data values (" + \
							"'" + gVal.STR_UserInfo['Account'] + "'," + \
							"'" + str(wTD['TimeDate']) + "'," + \
							str(wFLG_MyFollow) + "," + \
							"False," + \
							"True," + \
							"'" + str(wCHR_FolDate) + "'," + \
							"False," + \
							"False," + \
							"'" + str(wROW['id']) + "'," + \
							"'" + str(wROW['name']) + "'," + \
							"'" + str(wROW['screen_name']) + "'," + \
							str(wROW['statuses_count']) + "," + \
							"'" + str(wTD['TimeDate']) + "'" + \
							") ;"
				
				wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
				wDBRes = gVal.OBJ_DB.GetQueryStat()
				if wDBRes['Result']!=True :
					##失敗
					wRes['Reason'] = "CLS_TwitterMain: __get_FollowerInfo: Run Query is failed(3): " + wDBRes['Reason']
					return wRes
				
				self.STR_Cope['DB_Insert'] += 1
		
		#############################
		# DBのフォロワー一覧 再取得
		wQuery = "select * from tbl_follower_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_Twitter_Ctrl: __get_FollowerInfo: Run Query is failed(4): " + wDBRes['Reason'] + " query=" + wDBRes['Query']
			return wRes
		
		#############################
		# 辞書型に整形
		wARR_RateFollowers = {}
		gVal.OBJ_DB.ChgDict( wDBRes['Responce']['Collum'], wDBRes['Responce']['Data'], outDict=wARR_RateFollowers )
		self.STR_Cope['DB_Num'] = len(wARR_RateFollowers)
		
		#############################
		# 自動リムーブ対象を設定する
		#   ・フォロー者 かつ アンフォロワー
		#   ・一度もリムーブしたことがない
		#   ・normalリスト
		#   ・フォローしてから一定期間過ぎた
		# 自動リムーブ対象で、既にアンフォロワーならリムーブ済みにする
		
		wFLG_UnRemove = False	#自動リムーブ対象外か
		wFLG_UnFollow = False	#フォロー状態
		wFLG_Follower = False	#フォロワー状態
		wKeylist = wARR_RateFollowers.keys()
		for wIndex in wKeylist :
			wFLG_LastCount = False
			wLast_Count = str(wARR_RateFollowers[wIndex]['lastcount'])
			wLast_Date  = wARR_RateFollowers[wIndex]['lastdate']
			
			### フォロワーなら 自動リムーブ対象外
			if str(wARR_RateFollowers[wIndex]['id']) in wARR_FollowerID :
				wFLG_UnRemove = True
				wFLG_Follower = True	#フォロワー
				
				wF_Count = -1
				for wF_ROW in wFollowerRes['Responce'] :
					if wARR_RateFollowers[wIndex]['id']==str(wF_ROW['id']) :
						wF_Count = wF_ROW['statuses_count']
						break
				
				if wFLG_Ditect==False :
					wRes['Reason'] = "CLS_Twitter_Ctrl: __get_FollowerInfo: key is not found"
					return wRes
				###ツイート数変化 =更新あり
				if str(wF_Count)!=wLast_Count :
					wFLG_LastCount = True
					wLast_Count = str( wF_Count )
					wLast_Date  = wTD['TimeDate']
			
			###※少なくともフォロワーではない
			
			###  フォローしてないなら 自動リムーブ対象外
			if str(wARR_RateFollowers[wIndex]['id']) not in wARR_MyFollowID :
				wFLG_UnRemove = True
				wFLG_UnFollow = True	#未フォロー
			
			###  一度リムーブしたことあるなら 自動リムーブ対象外
			if wARR_RateFollowers[wIndex]['r_remove']==True :
				wFLG_UnRemove = True
			
			###  normalリスト以外ならば  自動リムーブ対象外
			if str(wROW['id']) not in wARR_NormalListMenberID :
				wFLG_UnRemove = True
			
			###  既にリムーブ済みorリムーブ対象ならばスキップ
			if wARR_RateFollowers[wIndex]['removed']==True or \
			   wARR_RateFollowers[wIndex]['limited']==True :
				wFLG_UnRemove = True
			
			###  ここまで自動リムーブ候補(False)で、フォローしてからの時間が範囲内なら  自動リムーブ対象外
			if wFLG_UnRemove==False :
				wRemoveLimmin = gVal.DEF_STR_TLNUM['removeLimmin'] * 60	#秒に変換
				wGetLag = CLS_OSIF.sTimeLag( str(wARR_RateFollowers[wIndex]['foldate']), inThreshold=wRemoveLimmin )
				if wGetLag['Result']!=True :
					wRes['Reason'] = "CLS_Twitter_Ctrl: __get_FollowerInfo: sTimeLag failed"
					return wRes
				if wGetLag['Beyond']==False :
					###期間内 =自動リムーブ対象外
					wFLG_UnRemove = True
			
			###  ここまでで自動リムーブ対象(False)なら記録する
			if wFLG_UnRemove==False :
				wQuery = "update tbl_follower_data set " + \
							"limited = True, " + \
							"removed = False, " + \
							"rc_follower = False, " + \
							"lastcount = " + wLast_Count + ", " + \
							"lastdate = '" + str(wLast_Date) + "' " + \
							"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
							" and id = '" + str(wARR_RateFollowers[wIndex]['id']) + "' ;"
				
				self.STR_Cope['tMyFollowRemove'] += 1
			
			else:
				###前回もフォロワー かつ フォロー状態に変化がなければスキップ
				if wARR_RateFollowers[wIndex]['rc_follower']==wFLG_Follower and \
				   wARR_RateFollowers[wIndex]['removed']==wFLG_UnFollow and \
				   wFLG_LastCount==False :
					continue
				
				wQuery = "update tbl_follower_data set " + \
							"rc_follower = " + str(wFLG_Follower) + ", " + \
							"removed = " + str(wFLG_UnFollow) + ", " + \
							"lastcount = " + wLast_Count + ", " + \
							"lastdate = '" + str(wLast_Date) + "' " + \
							"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
							" and id = '" + str(wARR_RateFollowers[wIndex]['id']) + "' ;"
			
			###フォロー済み 前回フォロワー状態、フォロー日時を記録
			wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
			wDBRes = gVal.OBJ_DB.GetQueryStat()
			if wDBRes['Result']!=True :
				##失敗
				wRes['Reason'] = "CLS_TwitterMain: __get_FollowerInfo: Run Query is failed(5): " + wDBRes['Reason']
				return wRes
			
			###  カウント
			self.STR_Cope['DB_Update'] += 1
		
		#############################
		# 正常終了
		wRes['Result'] = True
		return wRes






		#
		# 新規フォロワー
		#   ・フォロー者ではない かつ フォロワー
		#   ・一度もフォローしたことがない
		#   ・一度もリムーブしたことがない
#				#############################
#				# 新規フォロワー
#				### フォロワーではなければスキップ
#				if str(wROW['id']) not in wARR_FollowerID :
#					continue
#				







#####################################################
# いいね情報の表示
#####################################################
	def ViewFavo(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# 集計のリセット
		self.STR_Cope['FavoNum'] = 0
		self.STR_Cope['tFavoRemove'] = 0
		self.STR_Cope['FavoRemove']  = 0
		
		self.STR_Cope['DB_Num']    = 0
		
		#############################
		# DBのいいね一覧取得
		wQuery = "select * from tbl_favo_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_TwitterMain: ViewFavo: Run Query is failed(1): " + wDBRes['Reason'] + " query=" + wDBRes['Query']
			return wRes
		
		#############################
		# 辞書型に整形
		wARR_RateFavoID = {}
		gVal.OBJ_DB.ChgDict( wDBRes['Responce']['Collum'], wDBRes['Responce']['Data'], outDict=wARR_RateFavoID )
		self.STR_Cope['DB_Num'] = len(wARR_RateFavoID)
		
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
			wStr = wStr + "  ユーザ=" + str(wARR_RateFavoID[wIndex]['screen_name']) + "(@" + str(wARR_RateFavoID[wIndex]['user_name']) + ")" + '\n'
			wStr = wStr + "登録日=" + str(wARR_RateFavoID[wIndex]['regdate'])
			if wARR_RateFavoID[wIndex]['removed']==True :
				wStr = wStr + " [☆いいね解除済み]"
				self.STR_Cope['FavoRemove'] += 1
			elif wARR_RateFavoID[wIndex]['limited']==True :
				wStr = wStr + " [★いいね解除対象]"
				self.STR_Cope['tFavoRemove'] += 1
			wStr = wStr + '\n'
			wStr = wStr + "--------------------" + '\n'
		
		#############################
		# 統計
		wStr = wStr + "--------------------" + '\n'
###		wStr = wStr + "現いいね数        = " + str(self.STR_Cope['FavoNum']) + '\n'
		wStr = wStr + "DB登録数          = " + str(self.STR_Cope['DB_Num']) + '\n'
		wStr = wStr + "解除対象 いいね数 = " + str(self.STR_Cope['tFavoRemove']) + '\n'
		wStr = wStr + "解除済み いいね数 = " + str(self.STR_Cope['FavoRemove']) + '\n'
###		wStr = wStr + '\n'
###		wStr = wStr + "DB登録数 = " + str(self.STR_Cope['DB_Num']) + '\n'
		
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
	def Run_FavoRemove(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# 集計のリセット
		self.STR_Cope['tFavoRemove'] = 0
		self.STR_Cope['FavoRemove']  = 0
		
		self.STR_Cope['DB_Update'] = 0
		
		#############################
		# DBのいいね一覧取得 (いいね解除対象の抜き出し)
		wQuery = "select * from tbl_favo_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "' and " + \
					"limited = True and " + \
					"removed = False " + \
					";"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_TwitterMain: Run_FavoRemove: Run Query is failed(1): " + wDBRes['Reason'] + " query=" + wDBRes['Query']
			return wRes
		
		#############################
		# 辞書型に整形
		wARR_RateFavoID = {}
		gVal.OBJ_DB.ChgDict( wDBRes['Responce']['Collum'], wDBRes['Responce']['Data'], outDict=wARR_RateFavoID )
		self.STR_Cope['tFavoRemove'] = len(wARR_RateFavoID)
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " いいね監視 実行" + '\n'
		wStr = wStr + "--------------------" + '\n'
		
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
				wRes['Reason'] = "CLS_TwitterMain: Run_FavoRemove: Twitter API Error: " + wRemoveRes['Reason']
				return wRes
			
			###  解除したいいねを表示
			wStr = str(wARR_RateFavoID[wIndex]['text']) + '\n'
			wStr = wStr + "ツイ日=" + str(wARR_RateFavoID[wIndex]['created_at'])
			wStr = wStr + "  ユーザ=" + str(wARR_RateFavoID[wIndex]['screen_name']) + "(@" + str(wARR_RateFavoID[wIndex]['user_name']) + ")" + '\n'
			wStr = wStr + "登録日=" + str(wARR_RateFavoID[wIndex]['regdate'])
			wStr = wStr + " [☆いいね解除済み]"
			wStr = wStr + '\n'
			wStr = wStr + "--------------------" + '\n'
			CLS_OSIF.sPrn( wStr )
			
			self.STR_Cope['FavoRemove'] += 1
			
			###  limited をOFF、removed をONにする
			wQuery = "update tbl_favo_data set " + \
						"limited = False, " + \
						"removed = True " + \
						"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
						" and id = '" + wID + "' ;"
			
			wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
			wDBRes = gVal.OBJ_DB.GetQueryStat()
			if wDBRes['Result']!=True :
				##失敗
				wRes['Reason'] = "CLS_TwitterMain: Run_FavoRemove: Run Query is failed(2): " + wDBRes['Reason']
				return wRes
			
			###  カウント
			self.STR_Cope['DB_Update'] += 1
			
			wFavoLimNum += 1
			wVAL_ZanNum -= 1
			#############################
			# 1回の解除数チェック
			if gVal.DEF_STR_TLNUM['rFavoLimNum']<=wFavoLimNum :
				###解除数限界ならウェイトする
				CLS_OSIF.sPrn( "Twitter規制回避のため、待機します。" )
				CLS_OSIF.sPrn( "CTRL+Cで中止することもできます。残り処理数= " + str(wVAL_ZanNum) + " 個" )
				
				wResStop = self.__wait_FavoRemove( gVal.DEF_STR_TLNUM['favoLimWait'] )
				if wResStop==False :
					CLS_OSIF.sPrn( "処理を中止しました。" + '\n' )
					break	#ウェイト中止
				wFavoLimNum = 0
		
		#############################
		# 統計
		wStr = "--------------------" + '\n'
		wStr = wStr + "DB更新数          = " + str(self.STR_Cope['DB_Update']) + '\n'
		wStr = wStr + "解除対象 いいね数 = " + str(self.STR_Cope['tFavoRemove']) + '\n'
		wStr = wStr + "解除済み いいね数 = " + str(self.STR_Cope['FavoRemove']) + '\n'
		
		#############################
		# コンソールに表示
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes

	#####################################################
	def __wait_FavoRemove( self, inCount ):
		wCount = inCount
		try:
			while True:
				if wCount==0 :
					break
				
				#############################
				# 1行にカウントを表示
				# ctrl+cでウェイト中止
				wStr = "残り待機時間 " + str(self.VAL_WaitCount) + " 秒"
				CLS_OSIF.sPrnER( wStr )
				CLS_OSIF.sSleep(1)
				wCount -= 1
		
		except KeyboardInterrupt:
			return False 	#ウェイト中止
		
		return True			#ウェイト完了



#####################################################
# フォロワー情報の表示
#####################################################
	def ViewFollower(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# 集計のリセット
		self.STR_Cope['MyFollowNum'] = 0
		self.STR_Cope['FollowerNum'] = 0
		self.STR_Cope['NewFollowerNum']  = 0
		self.STR_Cope['tMyFollowRemove'] = 0
		self.STR_Cope['MyFollowRemove']  = 0
		
		self.STR_Cope['DB_Num']    = 0
		
		#############################
		# DBのフォロワー一覧取得
		wQuery = "select * from tbl_follower_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_TwitterMain: ViewFollower: Run Query is failed(1): " + wDBRes['Reason'] + " query=" + wDBRes['Query']
			return wRes
		
		#############################
		# 辞書型に整形
		wARR_RateFollowers = {}
		gVal.OBJ_DB.ChgDict( wDBRes['Responce']['Collum'], wDBRes['Responce']['Data'], outDict=wARR_RateFollowers )
		self.STR_Cope['DB_Num'] = len(wARR_RateFollowers)
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " 保持中のフォロワー情報" + '\n'
		wStr = wStr + "--------------------" + '\n'
		
		#############################
		# 情報組み立て
		wKeylist = wARR_RateFollowers.keys()
		for wIndex in wKeylist :
			if wARR_RateFollowers[wIndex]['twitterid']!=gVal.STR_UserInfo['Account'] :
				continue	#自分以外の情報はスキップ
			
			wStr = wStr + "ユーザ=" + str(wARR_RateFollowers[wIndex]['screen_name']) + "(@" + str(wARR_RateFollowers[wIndex]['user_name']) + ")" + '\n'
			
			wStr = wStr + "登録日=" + str(wARR_RateFollowers[wIndex]['regdate'])
			if wARR_RateFollowers[wIndex]['removed']==True :
				wStr = wStr + " [●非フォロー]"
##				self.STR_Cope['MyFollowRemove'] += 1
			else:
				wStr = wStr + " [〇フォロー]  "
			
			if wARR_RateFollowers[wIndex]['rc_follower']==False :
				wStr = wStr + " [●非フォロワー]"
			else:
				wStr = wStr + " [〇フォロワー]  "
			
			if wARR_RateFollowers[wIndex]['limited']==True :
				wStr = wStr + " [★いいね解除対象]"
				self.STR_Cope['tFavoRemove'] += 1
			
			wStr = wStr + '\n'
			
			wStr = wStr + "更新日=" + str(wARR_RateFollowers[wIndex]['lastdate']) + "  ツイ数=" + str(wARR_RateFollowers[wIndex]['lastcount'])
			wStr = wStr + '\n'
			wStr = wStr + "--------------------" + '\n'
		
		#############################
		# 統計
		wStr = wStr + "--------------------" + '\n'
		wStr = wStr + "DB登録数          = " + str(self.STR_Cope['DB_Num']) + '\n'
		wStr = wStr + "自動リムーブ対象  = " + str(self.STR_Cope['tMyFollowRemove']) + '\n'
		
		#############################
		# コンソールに表示
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes

















#####################################################
# フォロワー監視の実行
#####################################################
	def Get_Run_FollowerAdmin(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# 集計のリセット
		self.STR_Cope['FollowerNum']    = 0
		self.STR_Cope['NewFollowerNum'] = 0
		self.STR_Cope['MyFollowRemove'] = 0
		self.STR_Cope['DB_Num']    = 0
		self.STR_Cope['DB_Insert'] = 0
		self.STR_Cope['DB_Update'] = 0
		self.STR_Cope['DB_Delete'] = 0
		
		#############################
		# DBのフォロワー一覧取得(id, created_at)
		wQuery = "select * from tbl_follower_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wDBRes = self.Obj_Parent.OBJ_DB.RunQuery( wQuery )
		wDBRes = self.Obj_Parent.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_Twitter_Ctrl: Get_Run_FollowerAdmin: Run Query is failed(1): " + wDBRes['Reason'] + " query=" + wDBRes['Query']
			return wRes
		
		#############################
		# 辞書型に整形
		wARR_RateFollowers = {}
		self.Obj_Parent.OBJ_DB.ChgDict( wDBRes['Responce']['Collum'], wDBRes['Responce']['Data'], outDict=wARR_RateFollowers )
###		self.STR_Cope['DB_Num'] = len(wARR_Followers)
		
		#############################
		# フォロー一覧 取得
		wMyFollowRes = self.Obj_Parent.OBJ_Twitter.GetMyFollowList()
		if wMyFollowRes['Result']!=True :
			wRes['Reason'] = "CLS_Twitter_Ctrl: Get_Run_FollowerAdmin: Twitter API Error(1): " + wMyFollowRes['Reason']
			return wRes
		wARR_MyFollowID = []
		for wROW in wMyFollowRes['Responce'] :
			wARR_MyFollowID.append( str(wROW['id']) )
		
		#############################
		# フォロワー一覧 取得
		wFollowerRes = self.Obj_Parent.OBJ_Twitter.GetFollowerList()
		if wFollowerRes['Result']!=True :
			wRes['Reason'] = "CLS_Twitter_Ctrl: Get_Run_FollowerAdmin: Twitter API Error(2): " + wFollowerRes['Reason']
			return wRes
		
		#############################
		# normal登録者 取得
		wListsRes = self.Obj_Parent.OBJ_Twitter.GetListMember( gVal.STR_UserInfo['NorList'] )
		if wListsRes['Result']!=True :
			wRes['Reason'] = "CLS_Twitter_Ctrl: Get_Run_FollowerAdmin: Twitter API Error(3): " + wListsRes['Reason']
			return wRes
		wARR_NormalListMenberID = []
		for wROW in wListsRes['Responce'] :
			wARR_NormalListMenberID.append( str(wROW['id']) )
		
##		#############################
##		# un_refollow登録者 取得
##		wListsRes = self.Obj_Parent.OBJ_Twitter.GetListMember( gVal.STR_UserInfo['UrfList'] )
##		if wListsRes['Result']!=True :
##			wRes['Reason'] = "CLS_Twitter_Ctrl: Get_Run_FollowerAdmin: Twitter API Error(4): " + wListsRes['Reason']
##			return wRes
##		wARR_UrfollowListMenberID = []
##		for wROW in wListsRes['Responce'] :
##			wARR_UrfollowListMenberID.append( wROW['id'] )
		
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "CLS_Twitter_Ctrl: Get_Run_FollowerAdmin: PC時間の取得に失敗しました"
			return
		### wTD['TimeDate']
		
		#############################
		# DBに記録されていなければ、記録する
		
		wSTR_wk_RateFollower = {}
###		wSTR_wk_RateFollower.update({ "twitterid"   : "" })
		wSTR_wk_RateFollower.update({ "regdate"     : "" })
		wSTR_wk_RateFollower.update({ "r_myfollow"  : False })
		wSTR_wk_RateFollower.update({ "r_remove"    : False })
		wSTR_wk_RateFollower.update({ "rc_follower" : False })
		wSTR_wk_RateFollower.update({ "foldate"     : "1900-01-01 00:00:00" })
		wSTR_wk_RateFollower.update({ "remdate"     : "1900-01-01 00:00:00" })
		wSTR_wk_RateFollower.update({ "id"          : -1 })
		wSTR_wk_RateFollower.update({ "user_name"   : "" })
		wSTR_wk_RateFollower.update({ "screen_name" : "" })
		wSTR_wk_RateFollower.update({ "created_at"  : "" })
		
		self.STR_newFollower = {}
		self.VAL_newFollower = 0
		
		wVAL_rFavoLimNum = 0
		self.STR_Cope['FollowerNum'] = len(wFollowerRes['Responce'])
		for wROW in wFollowerRes['Responce'] :
			wTime = CLS_OSIF.sGetTimeformat_Twitter( wROW['created_at'] )
			if wTime['Result']!=True :
				wRes['Reason'] = "CLS_Twitter_Ctrl: Get_Run_FollowerAdmin: sGetTimeformat_Twitter is failed: " + str(wROW['created_at'])
				return wRes
			
			###記録を探す
###			wFLG_Ditect = False
			wGetIndex = -1
			wKeylist = wARR_RateFollowers.keys()
			for wIndex in wKeylist :
				if str(wARR_RateFollowers[wIndex]['id'])==str(wROW['id']) :
##					wFLG_Ditect = True	#DB記録あり
					wGetIndex = wIndex	#DB記録あり
					break
			
##			if wFLG_Ditect==True :
			if wGetIndex>=0 :
				###DBに記録されてる
				wSTR_wk_RateFollower['regdate']     = wARR_RateFollowers[wGetIndex]['regdate']
				wSTR_wk_RateFollower['r_myfollow']  = wARR_RateFollowers[wGetIndex]['r_myfollow']
				wSTR_wk_RateFollower['r_remove']    = wARR_RateFollowers[wGetIndex]['r_remove']
				wSTR_wk_RateFollower['rc_follower'] = wARR_RateFollowers[wGetIndex]['rc_follower']
				wSTR_wk_RateFollower['foldate']     = wARR_RateFollowers[wGetIndex]['foldate']
				wSTR_wk_RateFollower['remdate']     = wARR_RateFollowers[wGetIndex]['remdate']
				wSTR_wk_RateFollower['id']          = wARR_RateFollowers[wGetIndex]['id']
				wSTR_wk_RateFollower['user_name']   = wARR_RateFollowers[wGetIndex]['user_name']
				wSTR_wk_RateFollower['screen_name'] = wARR_RateFollowers[wGetIndex]['screen_name']
				wSTR_wk_RateFollower['created_at']  = wARR_RateFollowers[wGetIndex]['created_at']
				
				###フォローしてたら既フォローにする
				if wSTR_wk_RateFollower['r_myfollow']==False :
					if wSTR_wk_RateFollower['id'] in wARR_MyFollowID :
						wSTR_wk_RateFollower['r_myfollow'] = True	#既フォロー
						wSTR_wk_RateFollower['foldate']    = wTD['TimeDate']
				
				wQuery = "update tbl_follower_data set " + \
							"r_myfollow = " + str(wSTR_wk_RateFollower['r_myfollow']) + "," + \
							"foldate = '" + str(wSTR_wk_RateFollower['foldate']) + "' " + \
							"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
							" and id = '" + str(wSTR_wk_RateFollower['id']) + "' ;"
				
				wDBRes = self.Obj_Parent.OBJ_DB.RunQuery( wQuery )
				wDBRes = self.Obj_Parent.OBJ_DB.GetQueryStat()
				if wDBRes['Result']!=True :
					##失敗
					wRes['Reason'] = "CLS_Twitter_Ctrl: Get_RunFavoAdmin: Run Query is failed(2): " + wDBRes['Reason']
					return wRes
				
			else:
				###DBに記録されていない
				###  記録する
				wSTR_wk_RateFollower['regdate']     = wTD['TimeDate']
				wSTR_wk_RateFollower['r_myfollow']  = False
				wSTR_wk_RateFollower['r_remove']    = False
				wSTR_wk_RateFollower['rc_follower'] = True
				wSTR_wk_RateFollower['foldate']     = "1900-01-01 00:00:00"
				wSTR_wk_RateFollower['remdate']     = "1900-01-01 00:00:00"
				wSTR_wk_RateFollower['id']          = wROW['id']
				wSTR_wk_RateFollower['user_name']   = wROW['name']
				wSTR_wk_RateFollower['screen_name'] = wROW['screen_name']
				wSTR_wk_RateFollower['created_at']  = wTime['TimeDate']
###				wFLG_r_myfollow = False
				if wROW['id'] in wARR_MyFollowID :
###					wFLG_r_myfollow = True	#既フォロー
					wSTR_wk_RateFollower['r_myfollow'] = True	#既フォロー
					wSTR_wk_RateFollower['foldate']    = wTD['TimeDate']
				
				wQuery = "insert into tbl_follower_data values (" + \
							"'" + gVal.STR_UserInfo['Account'] + "'," + \
							"'" + str(wSTR_wk_RateFollower['regdate']) + "'," + \
							"'" + str(wSTR_wk_RateFollower['r_myfollow']) + "'," + \
							"'" + str(wSTR_wk_RateFollower['r_remove']) + "'," + \
							"'" + str(wSTR_wk_RateFollower['rc_follower']) + "'," + \
							"'" + str(wSTR_wk_RateFollower['foldate']) + "'," + \
							"'" + str(wSTR_wk_RateFollower['remdate']) + "'," + \
							"'" + str(wSTR_wk_RateFollower['id']) + "'," + \
							"'" + str(wSTR_wk_RateFollower['user_name']) + "'," + \
							"'" + str(wSTR_wk_RateFollower['screen_name']) + "'," + \
							"'" + str(wSTR_wk_RateFollower['created_at']) + "'" + \
							") ;"
				
				wDBRes = self.Obj_Parent.OBJ_DB.RunQuery( wQuery )
				wDBRes = self.Obj_Parent.OBJ_DB.GetQueryStat()
				if wDBRes['Result']!=True :
					##失敗
					wRes['Reason'] = "CLS_Twitter_Ctrl: Get_RunFavoAdmin: Run Query is failed(3): " + wDBRes['Reason']
					return wRes
				
				self.STR_Cope['DB_Insert'] += 1
			
			#############################
			# 新規フォロワー
			# ・フォローしてない
			# ・1度もフォローしたことがない
			# ・1度もリムーブしたことがない
			if wSTR_wk_RateFollower['r_myfollow']==False and \
			   wSTR_wk_RateFollower['r_remove']==False :
				if wSTR_wk_RateFollower['id'] not in wARR_MyFollowID :
					wSTR_Line = {}
					wSTR_Line.update({ "id" : str(wSTR_wk_RateFollower['id']) })
					wSTR_Line.update({ "user_name"   : str(wSTR_wk_RateFollower['user_name']) })
					wSTR_Line.update({ "screen_name" : str(wSTR_wk_RateFollower['screen_name']) })
					
					self.STR_newFollower.update({ self.VAL_newFollower : wSTR_Line })
					self.VAL_newFollower += 1
					self.STR_Cope['NewFollowerNum'] += 1
		
		#############################
		# DBのフォロワー一覧 再取得
		wQuery = "select * from tbl_follower_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wDBRes = self.Obj_Parent.OBJ_DB.RunQuery( wQuery )
		wDBRes = self.Obj_Parent.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_Twitter_Ctrl: Get_Run_FollowerAdmin: Run Query is failed(4): " + wDBRes['Reason'] + " query=" + wDBRes['Query']
			return wRes
		
		#############################
		# 辞書型に整形
		wARR_RateFollowers = {}
		self.Obj_Parent.OBJ_DB.ChgDict( wDBRes['Responce']['Collum'], wDBRes['Responce']['Data'], outDict=wARR_RateFollowers )
		self.STR_Cope['DB_Num'] = len(wARR_RateFollowers)
		
		#############################
		# 自動リムーブ
		# ・フォローしてる
		# ・前のチェックでフォローされている
		# ・リムーブされている
		# ・normalリストの登録者
		wVAL_rRemoveLimNum = 0
		for wFollowID in wARR_MyFollowID :	#フォローしてるユーザで検索
			
			###  処理回数を上回ったらスキップ
			if gVal.DEF_STR_TLNUM['rRemoveLimNum']<=wVAL_rRemoveLimNum :
				break
			
			###今フォローされているか
			wFLG_Follower = False
			for wROW in wFollowerRes['Responce'] :
				if wROW['id']==wFollowID :
					wFLG_Follower = True	#現フォロワー
					break
			
			###normalリストの登録者ではない
			if wFollowID not in wARR_NormalListMenberID :
				continue
			

			print("xxxx1")


			###DBのキーを検索
			wKeylist = wARR_RateFollowers.keys()
			wDBkey = -1
			for wIndex in wKeylist :
				### DBを検索
				if wARR_RateFollowers[wIndex]['id']==wFollowID :
					wDBkey = wIndex
					break
			if wDBkey==-1 :
				continue	#DB登録外 =今フォロワーではないし、1度もフォローされたことがない人 (片思い)
			



			###※記録があるのは現フォロワーか、過去のフォロワー
			
			###前のチェックでフォローされていて、今フォローされていない
			wFLG_AutoRemove = False
			if wARR_RateFollowers[wDBkey]['rc_follower']==True and \
			   wFLG_Follower==False :
				###自動リムーブ対象
				wFLG_AutoRemove = True
				
				###リムーブリストへ追加
				wRemoveRes = self.Obj_Parent.OBJ_Twitter.AddUserList( gVal.STR_UserInfo['UrfList'], str( wFollowID ) )
				if wRemoveRes['Result']!=True :
					wRes['Reason'] = "CLS_Twitter_Ctrl: Get_Run_FollowerAdmin: Twitter API Error(11): " + wRemoveRes['Reason']
					return wRes
				
				###ノーマルリストから削除
				wRemoveRes = self.Obj_Parent.OBJ_Twitter.RemoveUserList( gVal.STR_UserInfo['NorList'], str( wFollowID ) )
				if wRemoveRes['Result']!=True :
					wRes['Reason'] = "CLS_Twitter_Ctrl: Get_Run_FollowerAdmin: Twitter API Error(12): " + wRemoveRes['Reason']
					return wRes
				
				###リムーブする
				wRemoveRes = self.Obj_Parent.OBJ_Twitter.RemoveFollow( str(wFollowID) )
				if wRemoveRes['Result']!=True :
					wRes['Reason'] = "CLS_Twitter_Ctrl: Get_Run_FollowerAdmin: Twitter API Error(13): " + wRemoveRes['Reason']
					return wRes
				
				###カウント
				self.STR_Cope['MyFollowRemove'] += 1
				wVAL_rRemoveLimNum += 1
			
			###DBに記録する
			###  自動リムーブ
			if wFLG_AutoRemove==True :
				wQuery = "update tbl_follower_data set " + \
							"r_remove = True," + \
							"remdate = '" + str(wTD['TimeDate']) + "' " + \
							"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
							" and id = '" + str(wROW['id']) + "' ;"
				
				wDBRes = self.Obj_Parent.OBJ_DB.RunQuery( wQuery )
				wDBRes = self.Obj_Parent.OBJ_DB.GetQueryStat()
				if wDBRes['Result']!=True :
					##失敗
					wRes['Reason'] = "CLS_Twitter_Ctrl: Get_RunFavoAdmin: Run Query is failed(11): " + wDBRes['Reason']
					return wRes
				
				###  カウント
				self.STR_Cope['DB_Update'] += 1
			
			###  フォロワー状態が更新された
			elif wSTR_wk_RateFollower['rc_follower']!=wFLG_Follower :
				wQuery = "update tbl_follower_data set " + \
							"rc_follower = " + str(wFLG_Follower) + " " + \
							"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
							" and id = '" + str(wROW['id']) + "' ;"
				
				wDBRes = self.Obj_Parent.OBJ_DB.RunQuery( wQuery )
				wDBRes = self.Obj_Parent.OBJ_DB.GetQueryStat()
				if wDBRes['Result']!=True :
					##失敗
					wRes['Reason'] = "CLS_Twitter_Ctrl: Get_RunFavoAdmin: Run Query is failed(12): " + wDBRes['Reason']
					return wRes
				
				###  カウント
				self.STR_Cope['DB_Update'] += 1
		
		wRes['Result'] = True
		return wRes



