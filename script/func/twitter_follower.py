#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : Twitter監視 フォロワー監視系
# 
# ::Update= 2021/1/21
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
class CLS_TwitterFollower():
#####################################################
	OBJ_Parent = ""				#親クラス実体

#####################################################
# Init
#####################################################
	def __init__( self, parentObj=None ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterFollower"
		wRes['Func']  = "__init__"
		
		if parentObj==None :
			###親クラス実体の未設定
			wRes['Reason'] = "You have not set the parent class entity for parentObj"
			gVal.OBJ_L.Log( "A", wRes )
			return
		
		self.OBJ_Parent = parentObj
		return



#####################################################
# フォロワー情報の取得
#####################################################
	def Get(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterFollower"
		wRes['Func']  = "Get"
		
		#############################
		# 取得開始の表示
		CLS_OSIF.sPrn( "フォロワー情報を取得中。しばらくお待ちください......" )
		
		#############################
		# DBのフォロワー一覧取得
		wQuery = "select * from tbl_follower_data where " + \
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
		wARR_RateFollowers = {}
		gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateFollowers )
		
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "PC時間の取得に失敗しました"
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		### wTD['TimeDate']
		
		wARR_ObjUser = {}
		#############################
		# フォロー一覧 取得
		wMyFollowRes = gVal.OBJ_Twitter.GetMyFollowList()
		if wMyFollowRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetMyFollowList): " + wMyFollowRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		self.OBJ_Parent.ARR_MyFollowID = []
		for wROW in wMyFollowRes['Responce'] :
			self.OBJ_Parent.ARR_MyFollowID.append( str(wROW['id']) )
			wName = str(wROW['name']).replace( "'", "''" )
			wCell = {}
			wCell.update({ "MyFollow" : True })
			wCell.update({ "Follower" : False })
			wCell.update({ "FolDate"  : str(wTD['TimeDate']) })
			wCell.update({ "user_name"   : wName })
			wCell.update({ "screen_name" : str(wROW['screen_name']) })
			wCell.update({ "statuses_count" : str(wROW['statuses_count']) })
			wARR_ObjUser.update({ str(wROW['id']) : wCell })
		gVal.STR_TrafficInfo['myfollow'] = len( wMyFollowRes['Responce'] )
		
		#############################
		# フォロワー一覧 取得
		wFollowerRes = gVal.OBJ_Twitter.GetFollowerList()
		if wFollowerRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetFollowerList): " + wFollowerRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		self.OBJ_Parent.ARR_FollowerID = []
		for wROW in wFollowerRes['Responce'] :
			self.OBJ_Parent.ARR_FollowerID.append( str(wROW['id']) )
			
			wKeylist = list(wARR_ObjUser)
			if str(wROW['id']) in wKeylist :
				###フォロー者 =相互フォロー
				wARR_ObjUser[str(wROW['id'])]['Follower'] = True
			else:
				###被フォロワー(被片フォロー)
				wName = str(wROW['name']).replace( "'", "''" )
				wCell = {}
				wCell.update({ "MyFollow" : False })
				wCell.update({ "Follower" : True })
				wCell.update({ "FolDate"  : "1900-01-01 00:00:00" })
				wCell.update({ "user_name"   : wName })
				wCell.update({ "screen_name" : str(wROW['screen_name']) })
				wCell.update({ "statuses_count" : str(wROW['statuses_count']) })
				wARR_ObjUser.update({ str(wROW['id']) : wCell })
		gVal.STR_TrafficInfo['follower'] = len( wFollowerRes['Responce'] )
		
		#############################
		# normal、un_refollowl登録者 取得(idだけ)
		wListsRes = gVal.OBJ_Twitter.GetLists()
		if wListsRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetLists): " + wListsRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		
		wListsRes = gVal.OBJ_Twitter.GetListMember( gVal.STR_UserInfo['NorList'] )
		if wListsRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetListMember:NorList): " + wListsRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		self.OBJ_Parent.ARR_NormalListMenberID = []
		for wROW in wListsRes['Responce'] :
			self.OBJ_Parent.ARR_NormalListMenberID.append( str(wROW['id']) )
		
		wListsRes = gVal.OBJ_Twitter.GetListMember( gVal.STR_UserInfo['UrfList'] )
		if wListsRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetListMember:UrfList): " + wListsRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		self.OBJ_Parent.ARR_UnRefollowListMenberID = []
		for wROW in wListsRes['Responce'] :
			self.OBJ_Parent.ARR_UnRefollowListMenberID.append( str(wROW['id']) )
		
		#############################
		# DBのフォロワーデータを取得・更新する
		#   DBに記録されていなければ、記録する(片フォローも記録する)
		#   DBに記録されていたら、フォロー状態を更新する
		wKeylist = list(wARR_ObjUser)
		for wObjectUserID in wKeylist :
			
			###DBの記録を探す
			wFLG_Ditect = False
			wKeylist = wARR_RateFollowers.keys()
			for wIndex in wKeylist :
				if str(wARR_RateFollowers[wIndex]['id'])==str( wObjectUserID ) :
					wFLG_Ditect = True	#DB記録あり
					break
			
			#############################
			# DBに記録されている場合
			#   情報を更新する
			if wFLG_Ditect==True :
				###記録上フォローしたことがない かつ フォロー=初フォロー
				if wARR_RateFollowers[wIndex]['r_myfollow']==False and \
				   wARR_RateFollowers[wIndex]['rc_myfollow']==False and \
				   wARR_ObjUser[wObjectUserID]['MyFollow']==True :
					wQuery = "update tbl_follower_data set " + \
								"r_myfollow = True, " + \
								"rc_myfollow = True, " + \
								"foldate = '" + wARR_ObjUser[wObjectUserID]['FolDate'] + "', " + \
								"user_name = '" + wARR_ObjUser[wObjectUserID]['user_name'] + "', " + \
								"screen_name = '" + wARR_ObjUser[wObjectUserID]['screen_name'] + "', " + \
								"lastcount = " + wARR_ObjUser[wObjectUserID]['statuses_count'] + ", " + \
								"lastdate = '" + str(wTD['TimeDate']) + "' " + \
								"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
								" and id = '" + str( wObjectUserID ) + "' ;"
					gVal.STR_TrafficInfo['newfollower'] += 1
					
				###記録上リムーブされたことがない かつ リムーブ =初リムーブ
				if wARR_RateFollowers[wIndex]['r_remove']==False and \
				   wARR_RateFollowers[wIndex]['rc_follower']==True and \
				   wARR_ObjUser[wObjectUserID]['Follower']==False :
					wQuery = "update tbl_follower_data set " + \
								"r_remove = True, " + \
								"rc_follower = False, " + \
								"user_name = '" + wARR_ObjUser[wObjectUserID]['user_name'] + "', " + \
								"screen_name = '" + wARR_ObjUser[wObjectUserID]['screen_name'] + "', " + \
								"lastcount = " + wARR_ObjUser[wObjectUserID]['statuses_count'] + ", " + \
								"lastdate = '" + str(wTD['TimeDate']) + "' " + \
								"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
								" and id = '" + str( wObjectUserID ) + "' ;"
								
					gVal.STR_TrafficInfo['selremove'] += 1
				
				###前回のフォロー、フォロワー、カウント値が変わってるなら更新する
				else:
					if wARR_RateFollowers[wIndex]['rc_myfollow']==wARR_ObjUser[wObjectUserID]['MyFollow'] and + \
					   wARR_RateFollowers[wIndex]['rc_follower']==wARR_ObjUser[wObjectUserID]['Follower'] and + \
					   wARR_RateFollowers[wIndex]['lastcount']==wARR_ObjUser[wObjectUserID]['statuses_count'] :
						###更新されてないならスキップ
						continue
					wQuery = "update tbl_follower_data set " + \
								"rc_myfollow = " + str(wARR_ObjUser[wObjectUserID]['MyFollow']) + ", " + \
								"rc_follower = " + str(wARR_ObjUser[wObjectUserID]['Follower']) + ", " + \
								"foldate = '" + wARR_ObjUser[wObjectUserID]['FolDate'] + "', " + \
								"user_name = '" + wARR_ObjUser[wObjectUserID]['user_name'] + "', " + \
								"screen_name = '" + wARR_ObjUser[wObjectUserID]['screen_name'] + "', " + \
								"lastcount = " + wARR_ObjUser[wObjectUserID]['statuses_count'] + ", " + \
								"lastdate = '" + str(wTD['TimeDate']) + "' " + \
								"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
								" and id = '" + str(wROW['id']) + "' ;"
				
				###フォロー済み 前回フォロワー状態、フォロー日時を記録
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
			
			#############################
			# DBに記録されていない場合
			#   記録する
			else:
				wQuery = "insert into tbl_follower_data values (" + \
							"'" + gVal.STR_UserInfo['Account'] + "'," + \
							"'" + str(wTD['TimeDate']) + "'," + \
							str( wARR_ObjUser[wObjectUserID]['MyFollow'] ) + "," + \
							"False," + \
							str( wARR_ObjUser[wObjectUserID]['MyFollow'] ) + "," + \
							str( wARR_ObjUser[wObjectUserID]['Follower'] ) + "," + \
							"'" + str( wARR_ObjUser[wObjectUserID]['FolDate'] ) + "'," + \
							"False," + \
							"False," + \
							"'" + str( wObjectUserID ) + "'," + \
							"'" + str( wARR_ObjUser[wObjectUserID]['user_name'] ) + "'," + \
							"'" + str( wARR_ObjUser[wObjectUserID]['screen_name'] ) + "'," + \
							str( wARR_ObjUser[wObjectUserID]['statuses_count'] ) + "," + \
							"'" + str(wTD['TimeDate']) + "'," + \
							"'', " + \
							"'-1', " + \
							"'1900-01-01 00:00:00' " + \
							") ;"
				
##					"twitterid   TEXT  NOT NULL," + \
##					"regdate     TIMESTAMP," + \
##					"r_myfollow  BOOL  DEFAULT false," + \
##					"r_remove    BOOL  DEFAULT false," + \
##					"rc_myfollow BOOL  DEFAULT false," + \
##					"rc_follower BOOL  DEFAULT false," + \
##					"foldate     TIMESTAMP," + \
##					"limited     BOOL  DEFAULT false," + \
##					"removed     BOOL  DEFAULT false," + \
##					"id          TEXT  NOT NULL," + \
##					"user_name   TEXT  NOT NULL," + \
##					"screen_name TEXT  NOT NULL," + \
##					"lastcount   INTEGER," + \
##					"lastdate    TIMESTAMP," + \
##					"reason      TEXT," + \
##					"favoid      TEXT," + \
##					"favodate     TIMESTAMP," + \
				
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
		# DBのフォロワー一覧 再取得
		wQuery = "select * from tbl_follower_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(4): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		gVal.STR_TrafficInfo['dbreq'] += 1
		
		#############################
		# 辞書型に整形
		wARR_RateFollowers = {}
		gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateFollowers )
		
		gVal.STR_TrafficInfo['piefollow'] = 0
		gVal.STR_TrafficInfo['autofollowt'] = 0
		#############################
		# 自動リムーブ対象を設定する
		#   ・フォロー者 かつ アンフォロワー
		#   ・一度もリムーブしたことがない
		#   ・normalリスト
		#   ・フォローしてから一定期間過ぎた
		# 自動リムーブ対象で、既にアンフォロワーならリムーブ済みにする
		wKeylist = wARR_RateFollowers.keys()
		for wIndex in wKeylist :
			#############################
			# トラヒックの計測
			
###			###新規フォロワー
###			if wARR_RateFollowers[wIndex]['rc_follower']==False and \
###			   wARR_RateFollowers[wIndex]['r_remove']==True and \
###			   str(wARR_RateFollowers[wIndex]['id']) in self.OBJ_Parent.ARR_FollowerID :
###				gVal.STR_TrafficInfo['newfollower'] += 1
###			###リムーブされたか
###			elif wARR_RateFollowers[wIndex]['rc_follower']==True and \
###			     str(wARR_RateFollowers[wIndex]['id']) not in self.OBJ_Parent.ARR_FollowerID :
###				gVal.STR_TrafficInfo['selremove'] += 1
###			
			###片フォローを計測
			if wARR_RateFollowers[wIndex]['rc_myfollow']==True and \
			   wARR_RateFollowers[wIndex]['rc_follower']==False :
				gVal.STR_TrafficInfo['piefollow'] += 1
			
			#############################
			# 自動リムーブ対象外をスキップ
			wFLG_UnRemove = False
			
			###フォローしてない
			if str(wARR_RateFollowers[wIndex]['id']) not in self.OBJ_Parent.ARR_MyFollowID :
				wFLG_UnRemove = True
			
			###一度リムーブされたことがある
			if wARR_RateFollowers[wIndex]['r_remove']==True :
				wFLG_UnRemove = True
			
			###normalリスト以外
			if str(wARR_RateFollowers[wIndex]['id']) not in self.OBJ_Parent.ARR_NormalListMenberID :
				wFLG_UnRemove = True
			
			###既にリムーブ済みorリムーブ対象ならばスキップ
			if wARR_RateFollowers[wIndex]['removed']==True or \
			   wARR_RateFollowers[wIndex]['limited']==True :
				wFLG_UnRemove = True
			
			###フォローしてからの時間が範囲内
			wRemoveLimmin = gVal.DEF_STR_TLNUM['removeLimmin'] * 60	#秒に変換
			wGetLag = CLS_OSIF.sTimeLag( str(wARR_RateFollowers[wIndex]['foldate']), inThreshold=wRemoveLimmin )
			if wGetLag['Result']!=True :
				wRes['Reason'] = "sTimeLag failed"
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			if wGetLag['Beyond']==False :
				###期間内 =自動リムーブ対象外
				wFLG_UnRemove = True
			
			###自動リムーブ対象(False) =記録する
			if wFLG_UnRemove==False :
				wQuery = "update tbl_follower_data set " + \
							"limited = True, " + \
							"removed = False " + \
							"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
							" and id = '" + str(wARR_RateFollowers[wIndex]['id']) + "' ;"
				gVal.STR_TrafficInfo['autofollowt'] += 1
			
			###自動リムーブ対象外 で 既にリムーブ済みだった
###			elif wARR_ObjUser[wObjectUserID]['MyFollow']==False and \
###			     wARR_RateFollowers[wIndex]['removed']==False :
###				wQuery = "update tbl_follower_data set " + \
###							"removed = True " + \
###							"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
###							" and id = '" + str(wARR_RateFollowers[wIndex]['id']) + "' ;"
			else:
				if wARR_RateFollowers[wIndex]['rc_myfollow']==False and \
				   wARR_RateFollowers[wIndex]['removed']==False :
					wQuery = "update tbl_follower_data set " + \
								"removed = True " + \
								"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
								" and id = '" + str(wARR_RateFollowers[wIndex]['id']) + "' ;"
			###その他 スキップ
				else:
					continue
			
###			###その他 スキップ
###			else:
###				continue
###			
			###フォロー済み 前回フォロワー状態、フォロー日時を記録
			wResDB = gVal.OBJ_DB.RunQuery( wQuery )
			wResDB = gVal.OBJ_DB.GetQueryStat()
			if wResDB['Result']!=True :
				##失敗
				wRes['Reason'] = "Run Query is failed(5): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			
			###  カウント
			gVal.STR_TrafficInfo['dbreq'] += 1
			gVal.STR_TrafficInfo['dbup'] += 1
		
		#############################
		# 正常終了
		wRes['Result'] = True
		return wRes



###		#############################
###		# Twitterのフォロワー一覧を取得
###		#   DBに記録されていなければ、記録する
###		#   DBに記録されていたら、フォロー状態を更新する
###		self.OBJ_Parent.ARR_FollowerID = []
###		for wROW in wFollowerRes['Responce'] :
###			self.OBJ_Parent.ARR_FollowerID.append( str(wROW['id']) )	#フォロワーIDだけ記録
###			
###			###記録を探す
###			wFLG_Ditect = False
###			wKeylist = wARR_RateFollowers.keys()
###			for wIndex in wKeylist :
###				if str(wARR_RateFollowers[wIndex]['id'])==str(wROW['id']) :
###					wFLG_Ditect = True	#DB記録あり
###					break
###			
###			###フォロー状態
###			wFLG_MyFollow = False
###			wCHR_FolDate  = "1900-01-01 00:00:00"
###			if str(wROW['id']) in self.OBJ_Parent.ARR_MyFollowID :
###				###フォロー済み
###				wFLG_MyFollow = True
###				wCHR_FolDate  = str(wTD['TimeDate'])
###			
###			if wFLG_Ditect==True :
###				###DBに記録されている
###				
###				###記録上フォローしたことある かつ 未フォローなら記録
###				if wARR_RateFollowers[wIndex]['r_myfollow']==True and \
###				   wFLG_MyFollow==False :
###					wQuery = "update tbl_follower_data set " + \
###								"r_myfollow = True, " + \
###								"rc_follower = True, " + \
###								"foldate = '" + str(wCHR_FolDate) + "' " + \
###								"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
###								" and id = '" + str(wROW['id']) + "' ;"
###				else:
###					###前回もフォロワーならスキップ
###					if wARR_RateFollowers[wIndex]['rc_follower']==True :
###						continue
###					###前回フォロワーではない かつ 今回フォロワーなら記録
###					wQuery = "update tbl_follower_data set " + \
###								"rc_follower = True " + \
###								"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
###								" and id = '" + str(wROW['id']) + "' ;"
###				
###				###フォロー済み 前回フォロワー状態、フォロー日時を記録
###				wResDB = gVal.OBJ_DB.RunQuery( wQuery )
###				wResDB = gVal.OBJ_DB.GetQueryStat()
###				if wResDB['Result']!=True :
###					##失敗
###					wRes['Reason'] = "Run Query is failed(2): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
###					gVal.OBJ_L.Log( "B", wRes )
###					return wRes
###				
###				###  カウント
####			self.OBJ_Parent.STR_Cope['DB_Update'] += 1
###				gVal.STR_TrafficInfo['dbreq'] += 1
###				gVal.STR_TrafficInfo['dbup'] += 1
###			
###			else:
###				###DBに記録されていない
###				###  記録する
###				wName = str(wROW['name']).replace( "'", "''" )
###				wQuery = "insert into tbl_follower_data values (" + \
###							"'" + gVal.STR_UserInfo['Account'] + "'," + \
###							"'" + str(wTD['TimeDate']) + "'," + \
###							str(wFLG_MyFollow) + "," + \
###							"False," + \
###							"True," + \
###							"'" + str(wCHR_FolDate) + "'," + \
###							"False," + \
###							"False," + \
###							"'" + str(wROW['id']) + "'," + \
###							"'" + wName + "'," + \
###							"'" + str(wROW['screen_name']) + "'," + \
###							str(wROW['statuses_count']) + "," + \
###							"'" + str(wTD['TimeDate']) + "'," + \
###							"''" + \
###							") ;"
###							
###					##"r_myfollow  1度フォローした= 状態で判定
###					##"r_remove    1度リムーブした= 新規なのでFalse
###					##"rc_follower 前回フォロワー=  少なくともフォローされている
###					##"foldate     (フォロー日時)
###					##"limited     リムーブ候補= 新規なのでFalse
###					##"removed     リムーブ済み= 新規なのでFalse
###				
###				wResDB = gVal.OBJ_DB.RunQuery( wQuery )
###				wResDB = gVal.OBJ_DB.GetQueryStat()
###				if wResDB['Result']!=True :
###					##失敗
###					wRes['Reason'] = "Run Query is failed(3): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
###					gVal.OBJ_L.Log( "B", wRes )
###					return wRes
###				
####			self.OBJ_Parent.STR_Cope['DB_Insert'] += 1
###				gVal.STR_TrafficInfo['dbreq'] += 1
###				gVal.STR_TrafficInfo['dbins'] += 1
###		
####	#############################
####	# フォロワー数のセット
####	self.OBJ_Parent.STR_Cope['FollowerNum'] = len(self.OBJ_Parent.ARR_FollowerID)
####	
###		#############################
###		# 片フォローをDBに記録する
###		#   ・一度もフォローされたことがない(DBに記録がない)
###		#   ・フォロー者
###		#   ・normalリスト
###		
###		###フォロー一覧
###		for wMyFollowID in self.OBJ_Parent.ARR_MyFollowID :
###			### normalリスト以外ならば対象外
###			if wMyFollowID not in self.OBJ_Parent.ARR_NormalListMenberID :
###				continue
###			### フォロワー(=相互フォロー)ならば対象外
###			if wMyFollowID in self.OBJ_Parent.ARR_FollowerID :
###				continue
###			### DBに記録されていれば対象外
###			wFLG_Ditect = False
###			wKeylist = wARR_RateFollowers.keys()
###			for wIndex in wKeylist :
###				if str(wARR_RateFollowers[wIndex]['id'])==wMyFollowID :
###					wFLG_Ditect = True
###					break
###			if wFLG_Ditect==True :
###				continue
###			
###			# ※片フォロー確定
###			
###			#############################
###			# Twitterフォロー情報から情報を抜き出す
###			wFLG_Ditect = False
###			wMyFollow_Key = 0
###			for wROW in wMyFollowRes['Responce'] :
###				if str(wROW['id'])==wMyFollowID :
###					wFLG_Ditect = True
###					break
###				wMyFollow_Key += 1
###			if wFLG_Ditect!=True :
###				##フォロー一覧に id が見当たらない=失敗(ありえない)
###				wRes['Reason'] = "Key ditect is not found: Follow ID=" + wMyFollowID
###				gVal.OBJ_L.Log( "B", wRes )
###				continue
###			
###			### 情報を抜く
###			wName = str(wMyFollowRes['Responce'][wMyFollow_Key]['name']).replace( "'", "''" )
###			wScreenName = str(wMyFollowRes['Responce'][wMyFollow_Key]['screen_name'])
###			wStatusCount = str(wMyFollowRes['Responce'][wMyFollow_Key]['statuses_count'])
###			
###			### 記録する
###			wQuery = "insert into tbl_follower_data values (" + \
###						"'" + gVal.STR_UserInfo['Account'] + "'," + \
###						"'" + str(wTD['TimeDate']) + "'," + \
###						"True," + \
###						"False," + \
###						"False," + \
###						"'" + str(wTD['TimeDate']) + "'," + \
###						"False," + \
###						"False," + \
###						"'" + str(wROW['id']) + "'," + \
###						"'" + wName + "'," + \
###						"'" + wScreenName + "'," + \
###						wStatusCount + "," + \
###						"'" + str(wTD['TimeDate']) + "'," + \
###						"''" + \
###						") ;"
###			
###					##"r_myfollow  1度フォローした= 既にフォローしている
###					##"r_remove    1度リムーブした= 新規なのでFalse
###					##"rc_follower 前回フォロワー=  フォロワーではないのでFalse
###					##"foldate     (フォロー日時)
###					##"limited     リムーブ候補= 新規なのでFalse
###					##"removed     リムーブ済み= 新規なのでFalse
###			
###			wResDB = gVal.OBJ_DB.RunQuery( wQuery )
###			wResDB = gVal.OBJ_DB.GetQueryStat()
###			if wResDB['Result']!=True :
###				##失敗
###				wRes['Reason'] = "Run Query is failed(4): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
###				gVal.OBJ_L.Log( "B", wRes )
###				return wRes
###			
####		self.OBJ_Parent.STR_Cope['DB_Insert'] += 1
###			gVal.STR_TrafficInfo['dbreq'] += 1
###			gVal.STR_TrafficInfo['dbins'] += 1
###		
###		#############################
###		# DBのフォロワー一覧 再取得
###		wQuery = "select * from tbl_follower_data where " + \
###					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
###					";"
###		
###		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
###		wResDB = gVal.OBJ_DB.GetQueryStat()
###		if wResDB['Result']!=True :
###			##失敗
###			wRes['Reason'] = "Run Query is failed(5): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
###			gVal.OBJ_L.Log( "B", wRes )
###			return wRes
###		gVal.STR_TrafficInfo['dbreq'] += 1
###		
###		#############################
###		# 辞書型に整形
###		wARR_RateFollowers = {}
###		gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateFollowers )
####	self.OBJ_Parent.STR_Cope['DB_Num'] += len(wARR_RateFollowers)
###		
###		#############################
###		# 自動リムーブ対象を設定する
###		#   ・フォロー者 かつ アンフォロワー
###		#   ・一度もリムーブしたことがない
###		#   ・normalリスト
###		#   ・フォローしてから一定期間過ぎた
###		# 自動リムーブ対象で、既にアンフォロワーならリムーブ済みにする
###		
###		self.OBJ_Parent.ARR_OldUserID = []	#一度でもフォロー・リムーブしたことあるユーザID
###		gVal.STR_TrafficInfo['piefollow'] = 0
###		gVal.STR_TrafficInfo['autofollowt'] = 0
###		
###		wKeylist = wARR_RateFollowers.keys()
###		for wIndex in wKeylist :
###			wFLG_UnRemove = False	#自動リムーブ対象外か
###			wFLG_UnFollow = False	#フォロー状態
###			wFLG_Follower = False	#フォロワー状態
###			wFLG_LastCount = False
###			wFLG_Ditect = False
###			wLast_Count = str(wARR_RateFollowers[wIndex]['lastcount'])
###			wLast_Date  = wARR_RateFollowers[wIndex]['lastdate']
###			
###			### フォロワーなら 自動リムーブ対象外
###			if str(wARR_RateFollowers[wIndex]['id']) in self.OBJ_Parent.ARR_FollowerID :
###				wFLG_UnRemove = True
###				wFLG_Follower = True	#フォロワー
###				
###				wF_Count = -1
###				for wF_ROW in wFollowerRes['Responce'] :
###					if wARR_RateFollowers[wIndex]['id']==str(wF_ROW['id']) :
###						wF_Count = wF_ROW['statuses_count']
###						wFLG_Ditect = True
###						break
###				
###				if wFLG_Ditect==False :
###					wRes['Reason'] = "key is not found"
###					gVal.OBJ_L.Log( "C", wRes )
###					return wRes
###				###ツイート数変化 =更新あり
###				if str(wF_Count)!=wLast_Count :
###					wFLG_LastCount = True
###					wLast_Count = str( wF_Count )
###					wLast_Date  = wTD['TimeDate']
###			
###			###リムーブされたか
###			if wARR_RateFollowers[wIndex]['rc_follower']==True and \
###			   str(wARR_RateFollowers[wIndex]['id']) not in self.OBJ_Parent.ARR_FollowerID :
###				gVal.STR_TrafficInfo['selremove'] += 1
###			
###			###※少なくともフォロワーではない
###			
###			###  フォローしてないなら 自動リムーブ対象外
###			if str(wARR_RateFollowers[wIndex]['id']) not in self.OBJ_Parent.ARR_MyFollowID :
###				wFLG_UnRemove = True
###				wFLG_UnFollow = True	#未フォロー
###			else :
###				### フォロー かつ 非フォロワー = 片フォロー
###				if wFLG_Follower==False :
####				self.OBJ_Parent.STR_Cope['PieceFollowNum'] += 1
###					gVal.STR_TrafficInfo['piefollow'] += 1
###			
###			###  一度リムーブしたことあるなら 自動リムーブ対象外
###			if wARR_RateFollowers[wIndex]['r_remove']==True :
###				wFLG_UnRemove = True
###				if str(wARR_RateFollowers[wIndex]['id']) not in self.OBJ_Parent.ARR_OldUserID :
###					self.OBJ_Parent.ARR_OldUserID.append( str(wARR_RateFollowers[wIndex]['id']) )
###			
###			###  一度フォローしたことある
###			if wARR_RateFollowers[wIndex]['r_myfollow']==True :
###				if str(wARR_RateFollowers[wIndex]['id']) not in self.OBJ_Parent.ARR_OldUserID :
###					self.OBJ_Parent.ARR_OldUserID.append( str(wARR_RateFollowers[wIndex]['id']) )
###			
###			###  normalリスト以外ならば  自動リムーブ対象外
###			if str(wARR_RateFollowers[wIndex]['id']) not in self.OBJ_Parent.ARR_NormalListMenberID :
###				wFLG_UnRemove = True
###			
####		###  既にリムーブ済みorリムーブ対象ならばスキップ
####		if wARR_RateFollowers[wIndex]['removed']==True or \
####		   wARR_RateFollowers[wIndex]['limited']==True :
####			wFLG_UnRemove = True
###			
###			###  既にリムーブ済みならばスキップ
###			if wARR_RateFollowers[wIndex]['removed']==True :
###				wFLG_UnRemove = True
###			
###			###  既にリムーブ対象ならばスキップ
###			if wARR_RateFollowers[wIndex]['limited']==True :
####			self.OBJ_Parent.STR_Cope['tMyFollowRemove'] += 1
###				gVal.STR_TrafficInfo['autofollowt'] += 1
###				wFLG_UnRemove = True
###			
###			###  ここまで自動リムーブ候補(False)で、フォローしてからの時間が範囲内なら  自動リムーブ対象外
###			if wFLG_UnRemove==False :
###				wRemoveLimmin = gVal.DEF_STR_TLNUM['removeLimmin'] * 60	#秒に変換
###				wGetLag = CLS_OSIF.sTimeLag( str(wARR_RateFollowers[wIndex]['foldate']), inThreshold=wRemoveLimmin )
###				if wGetLag['Result']!=True :
###					wRes['Reason'] = "sTimeLag failed"
###					gVal.OBJ_L.Log( "B", wRes )
###					return wRes
###				if wGetLag['Beyond']==False :
###					###期間内 =自動リムーブ対象外
###					wFLG_UnRemove = True
###			
###			###  ここまでで自動リムーブ対象(False)なら記録する
###			if wFLG_UnRemove==False :
###				wQuery = "update tbl_follower_data set " + \
###							"limited = True, " + \
###							"removed = False, " + \
###							"rc_follower = False, " + \
###							"lastcount = " + wLast_Count + ", " + \
###							"lastdate = '" + str(wLast_Date) + "' " + \
###							"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
###							" and id = '" + str(wARR_RateFollowers[wIndex]['id']) + "' ;"
###				
####			self.OBJ_Parent.STR_Cope['tMyFollowRemove'] += 1
###				gVal.STR_TrafficInfo['autofollowt'] += 1
###			
###			else:
###				###前回もフォロワー かつ フォロー状態に変化がなければスキップ
###				if wARR_RateFollowers[wIndex]['rc_follower']==wFLG_Follower and \
###				   wARR_RateFollowers[wIndex]['removed']==wFLG_UnFollow and \
###				   wFLG_LastCount==False :
###					continue
###				
###				wQuery = "update tbl_follower_data set " + \
###							"rc_follower = " + str(wFLG_Follower) + ", " + \
###							"removed = " + str(wFLG_UnFollow) + ", " + \
###							"lastcount = " + wLast_Count + ", " + \
###							"lastdate = '" + str(wLast_Date) + "' " + \
###							"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
###							" and id = '" + str(wARR_RateFollowers[wIndex]['id']) + "' ;"
###			
###			###フォロー済み 前回フォロワー状態、フォロー日時を記録
###			wResDB = gVal.OBJ_DB.RunQuery( wQuery )
###			wResDB = gVal.OBJ_DB.GetQueryStat()
###			if wResDB['Result']!=True :
###				##失敗
###				wRes['Reason'] = "Run Query is failed(6): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
###				gVal.OBJ_L.Log( "B", wRes )
###				return wRes
###			
###			###  カウント
####		self.OBJ_Parent.STR_Cope['DB_Update'] += 1
###			gVal.STR_TrafficInfo['dbreq'] += 1
###			gVal.STR_TrafficInfo['dbup'] += 1
###		
###		#############################
###		# 正常終了
###		wRes['Result'] = True
###		return wRes
###
###

#####################################################
# フォロワー情報の表示
#####################################################
	def View(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterFollower"
		wRes['Func']  = "View"
		
###		#############################
###		# 集計のリセット
###		self.OBJ_Parent.STR_Cope['MyFollowNum'] = 0
###		self.OBJ_Parent.STR_Cope['FollowerNum'] = 0
###		self.OBJ_Parent.STR_Cope['PieceFollowNum'] = 0
###		self.OBJ_Parent.STR_Cope['NewFollowerNum']  = 0
###		self.OBJ_Parent.STR_Cope['tMyFollowRemove'] = 0
###		self.OBJ_Parent.STR_Cope['MyFollowRemove']  = 0
###		
###		self.OBJ_Parent.STR_Cope['DB_Num']    = 0
###		
		#############################
		# DBのフォロワー一覧取得
		wQuery = "select * from tbl_follower_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed: RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		gVal.STR_TrafficInfo['dbreq'] += 1
		
		#############################
		# 辞書型に整形
		wARR_RateFollowers = {}
		gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateFollowers )
###		self.OBJ_Parent.STR_Cope['DB_Num'] = len(wARR_RateFollowers)
		
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
			
			wStr = wStr + "ユーザ=" + str(wARR_RateFollowers[wIndex]['user_name']) + "(@" + str(wARR_RateFollowers[wIndex]['screen_name']) + ")" + '\n'
			
			wStr = wStr + "登録日=" + str(wARR_RateFollowers[wIndex]['regdate'])
			if wARR_RateFollowers[wIndex]['removed']==True :
				wStr = wStr + " [●非フォロー]"
			else:
				wStr = wStr + " [〇フォロー]  "
			
			if wARR_RateFollowers[wIndex]['rc_follower']==False :
				wStr = wStr + " [●非フォロワー]"
###				if wARR_RateFollowers[wIndex]['removed']==False :
###					# フォロー かつ 非フォロワー = 片フォロー
###					self.OBJ_Parent.STR_Cope['PieceFollowNum'] += 1
			
			else:
				wStr = wStr + " [〇フォロワー]  "
###				self.OBJ_Parent.STR_Cope['FollowerNum'] += 1
###				if wARR_RateFollowers[wIndex]['removed']==False :
###					self.OBJ_Parent.STR_Cope['MyFollowNum'] += 1
			
			if wARR_RateFollowers[wIndex]['limited']==True :
				wStr = wStr + " [★自動リムーブ対象]"
###				self.OBJ_Parent.STR_Cope['tMyFollowRemove'] += 1
			
			wStr = wStr + '\n'
			
			wStr = wStr + "更新日=" + str(wARR_RateFollowers[wIndex]['lastdate']) + "  ツイ数=" + str(wARR_RateFollowers[wIndex]['lastcount'])
			wStr = wStr + '\n'
			wStr = wStr + "--------------------" + '\n'
		
		#############################
		# 統計
		wStr = wStr + "--------------------" + '\n'
###		wStr = wStr + "DB登録数         = " + str(self.OBJ_Parent.STR_Cope['DB_Num']) + '\n'
###		wStr = wStr + '\n'
###		wStr = wStr + "現フォロワー数   = " + str(self.OBJ_Parent.STR_Cope['FollowerNum']) + '\n'
###		wStr = wStr + "相互フォロー数   = " + str(self.OBJ_Parent.STR_Cope['MyFollowNum']) + '\n'
###		wStr = wStr + "片フォロー数     = " + str(self.OBJ_Parent.STR_Cope['PieceFollowNum']) + '\n'
###		wStr = wStr + "自動リムーブ対象 = " + str(self.OBJ_Parent.STR_Cope['tMyFollowRemove']) + '\n'
		wStr = wStr + "現フォロワー数   = " + str(gVal.STR_TrafficInfo['follower']) + '\n'
		wStr = wStr + "片フォロー数     = " + str(gVal.STR_TrafficInfo['piefollow']) + '\n'
		wStr = wStr + "自動リムーブ対象 = " + str(gVal.STR_TrafficInfo['autofollowt']) + '\n'
		
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
	def Run(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterFollower"
		wRes['Func']  = "Run"
		
###		#############################
###		# 集計のリセット
###		self.OBJ_Parent.STR_Cope['FollowerNum']     = 0
###		self.OBJ_Parent.STR_Cope['tMyFollowRemove'] = 0
###		self.OBJ_Parent.STR_Cope['MyFollowRemove']  = 0
###		
###		self.OBJ_Parent.STR_Cope['DB_Update'] = 0
###		
		#############################
		# DBのフォロワー一覧取得(自動リムーブ対象の抜き出し)
		wQuery = "select * from tbl_follower_data where " + \
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
		wARR_RateFollowers = {}
		gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateFollowers )
###		self.OBJ_Parent.STR_Cope['tMyFollowRemove'] = len(wARR_RateFollowers)
		gVal.STR_TrafficInfo['autofollowt'] = len(wARR_RateFollowers)
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " フォロワー監視 実行" + '\n'
		wStr = wStr + "--------------------" + '\n'
		wStr = wStr + "以下のリムーブ対象ユーザをリムーブします......" + '\n'
		CLS_OSIF.sPrn( wStr )
		
		wVAL_ZanNum = len(wARR_RateFollowers)
		wRemoveLimNum = 0
		wResStop = False
		#############################
		# リムーブしていく
		wKeylist = wARR_RateFollowers.keys()
		for wIndex in wKeylist :
			wID = str( wARR_RateFollowers[wIndex]['id'] )
			
			###  リムーブしたユーザを表示
			wStr = "リムーブ処理中= " + str(wARR_RateFollowers[wIndex]['user_name']) + "(@" + str(wARR_RateFollowers[wIndex]['screen_name']) + ")"
			CLS_OSIF.sPrn( wStr )
			
			###  リムーブする
			wRemoveRes = gVal.OBJ_Twitter.RemoveFollow( wID )
			if wRemoveRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error(RemoveFollow): " + wRemoveRes['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			CLS_OSIF.sSleep(5)
			
			###  ミュート解除する
			wRemoveRes = gVal.OBJ_Twitter.RemoveMute( wID )
			if wRemoveRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error(RemoveMute): " + wRemoveRes['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			CLS_OSIF.sSleep(5)
			
			### un_refollowリストへ追加
			wTwitterRes = gVal.OBJ_Twitter.AddUserList( gVal.STR_UserInfo['UrfList'], wID )
			if wTwitterRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error(AddUserList): " + wTwitterRes['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			CLS_OSIF.sSleep(5)
			
			### normalリストから削除する
			wTwitterRes = gVal.OBJ_Twitter.RemoveUserList( gVal.STR_UserInfo['NorList'], wID )
			if wTwitterRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error(RemoveUserList): " + wTwitterRes['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			CLS_OSIF.sSleep(5)
			
			###  リムーブしたユーザを表示
			wStr = "リムーブ成功" + '\n'
			CLS_OSIF.sPrn( wStr )
			
###			self.OBJ_Parent.STR_Cope['MyFollowRemove'] += 1
			gVal.STR_TrafficInfo['autofollow'] += 1
			
			###  limited をOFF、removed をONにする
			wQuery = "update tbl_follower_data set " + \
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
###			self.OBJ_Parent.STR_Cope['DB_Update'] += 1
			gVal.STR_TrafficInfo['dbreq'] += 1
			gVal.STR_TrafficInfo['dbup'] += 1
			
			wRemoveLimNum += 1
			wVAL_ZanNum -= 1
			#############################
			# 処理全て終わり
			if wVAL_ZanNum==0 :
				break
			
			#############################
			# 1回の解除数チェック
###			if gVal.DEF_STR_TLNUM['rRemoveLimNum']<=wRemoveLimNum :
			elif gVal.DEF_STR_TLNUM['rRemoveLimNum']<=wRemoveLimNum :
				###解除数限界ならウェイトする
				CLS_OSIF.sPrn( "Twitter規制回避のため、待機します。" )
				CLS_OSIF.sPrn( "CTRL+Cで中止することもできます。残り処理数= " + str(wVAL_ZanNum) + " 個" )
				
				wResStop = CLS_OSIF.sPrnWAIT( gVal.DEF_STR_TLNUM['removeLimWait'] )
				if wResStop==False :
					CLS_OSIF.sPrn( "処理を中止しました。" + '\n' )
					break	#ウェイト中止
				wRemoveLimNum = 0
			
			#############################
			# 残り処理回数がまだある =5秒ウェイトする
###			elif wVAL_ZanNum>0 :
			else :
				CLS_OSIF.sSleep( 5 )
		
		#############################
		# 統計
		wStr = "--------------------" + '\n'
###		wStr = wStr + "DB更新数              = " + str(self.OBJ_Parent.STR_Cope['DB_Update']) + '\n'
###		wStr = wStr + "リムーブ対象 ユーザ数 = " + str(self.OBJ_Parent.STR_Cope['tMyFollowRemove']) + '\n'
###		wStr = wStr + "リムーブ済み ユーザ数 = " + str(self.OBJ_Parent.STR_Cope['MyFollowRemove']) + '\n'
		wStr = wStr + "リムーブ対象 ユーザ数 = " + str(gVal.STR_TrafficInfo['autofollowt']) + '\n'
		wStr = wStr + "リムーブ済み ユーザ数 = " + str(gVal.STR_TrafficInfo['autofollow']) + '\n'
		
		#############################
		# コンソールに表示
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



