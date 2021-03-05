#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : Twitter監視 フォロワー監視系
# 
# ::Update= 2021/3/5
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

from htmlif import CLS_HTMLIF
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
					
					###※新規フォロー
					wRes['Reason'] = "既にフォローしているユーザ: @" + str(wARR_RateFollowers[wIndex]['screen_name'])
					gVal.OBJ_L.Log( "R", wRes, "", inViewConsole=True )
				
				###記録上リムーブされたことがない かつ リムーブ =初リムーブ
				elif wARR_RateFollowers[wIndex]['r_remove']==False and \
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
					
					###※リムーブされた(新規)
					wRes['Reason'] = "リムーブされたユーザ: @" + str(wARR_RateFollowers[wIndex]['screen_name'])
					gVal.OBJ_L.Log( "R", wRes, "", inViewConsole=True )
				
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
								"user_name = '" + wARR_ObjUser[wObjectUserID]['user_name'] + "', " + \
								"screen_name = '" + wARR_ObjUser[wObjectUserID]['screen_name'] + "', " + \
								"lastcount = " + wARR_ObjUser[wObjectUserID]['statuses_count'] + ", " + \
								"lastdate = '" + str(wTD['TimeDate']) + "' " + \
								"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
								" and id = '" + str( wObjectUserID ) + "' ;"
				
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
							"'1900-01-01 00:00:00'," + \
							"0, 0, 0," + \
							"''," + \
							"'1900-01-01 00:00:00' " + \
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
				
				###※フォローされた(新規)
				if wARR_ObjUser[wObjectUserID]['Follower']==True :
					wRes['Reason'] = "新規フォロワーのユーザ: @" + str(wARR_ObjUser[wObjectUserID]['screen_name'])
					gVal.OBJ_L.Log( "R", wRes, "", inViewConsole=True )
		
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
			
			###フォロワー
			if str(wARR_RateFollowers[wIndex]['id']) in self.OBJ_Parent.ARR_FollowerID :
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
			
			###自動リムーブ対象外 で フォローしてたけど既にリムーブ済みだった
			else:
###				if wARR_RateFollowers[wIndex]['rc_myfollow']==False and \
				if wARR_RateFollowers[wIndex]['r_myfollow']==True and \
				   wARR_RateFollowers[wIndex]['rc_myfollow']==False and \
				   wARR_RateFollowers[wIndex]['removed']==False :
					wQuery = "update tbl_follower_data set " + \
								"removed = True " + \
								"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
								" and id = '" + str(wARR_RateFollowers[wIndex]['id']) + "' ;"
					
					###※既にリムーブしているユーザを記録＆表示する
					wRes['Reason'] = "既にリムーブ済みのユーザ: @" + str(wARR_RateFollowers[wIndex]['screen_name'])
					gVal.OBJ_L.Log( "R", wRes, "", inViewConsole=True )
###				else:
###					###ふぁぼったのに一定期間ノーリアクションなら自動リムーブする
###					# 以下の条件に全てあてはまる場合
###					# ・フォロー者
###					# ・Normalリストユーザ
###					# ・フォローしてから 90日超え
###					# ・ファボったことがある場合
###					#   ・前回のファボから 90日以内
###					#   ・ふぁぼられたことがある場合、前回から 90日超えている
###					#   ・ふぁぼられたことがない場合は自動リムーブ
###					
###					###フォローしてない場合、対象外
###					if str(wARR_RateFollowers[wIndex]['id']) not in self.OBJ_Parent.ARR_MyFollowID :
###						continue
###					###normalリスト以外は対象外
###					if str(wARR_RateFollowers[wIndex]['id']) not in self.OBJ_Parent.ARR_NormalListMenberID :
###						continue
###					###ファボったことがない
###					if wARR_RateFollowers[wIndex]['favoid']==None or wARR_RateFollowers[wIndex]['favodate']==None :
###						continue
###					
###					wRemoveNofavoMin = gVal.DEF_STR_TLNUM['removeNofavoMin'] * 60	#秒に変換
###					###フォローしてからの時間が範囲内
###					wGetLag = CLS_OSIF.sTimeLag( str(wARR_RateFollowers[wIndex]['foldate']), inThreshold=wRemoveNofavoMin )
###					if wGetLag['Result']!=True :
###						wRes['Reason'] = "sTimeLag failed"
###						gVal.OBJ_L.Log( "B", wRes )
###						return wRes
###					if wGetLag['Beyond']==False :
###						###期間内 =自動リムーブ対象外
###						continue
###					
###					###ファボってからの時間が範囲外
###					wGetLag = CLS_OSIF.sTimeLag( str(wARR_RateFollowers[wIndex]['favodate']), inThreshold=wRemoveNofavoMin )
###					if wGetLag['Result']!=True :
###						wRes['Reason'] = "sTimeLag failed"
###						gVal.OBJ_L.Log( "B", wRes )
###						return wRes
###					if wGetLag['Beyond']==True :
###						###期間外 =自動リムーブ対象外
###						continue
###					
###					###ファボられたことがある
###					if wARR_RateFollowers[wIndex]['favo_r_id']!=None and wARR_RateFollowers[wIndex]['favo_r_date']!=None :
###						###前回のファボからの時間が範囲内
###						wGetLag = CLS_OSIF.sTimeLag( str(wARR_RateFollowers[wIndex]['favo_r_date']), inThreshold=wRemoveNofavoMin )
###						if wGetLag['Result']!=True :
###							wRes['Reason'] = "sTimeLag failed"
###							gVal.OBJ_L.Log( "B", wRes )
###							return wRes
###						if wGetLag['Beyond']==False :
###							###期間内 =自動リムーブ対象外
###							continue
###					
###					### ここまでで自動リムーブ確定
###					wQuery = "update tbl_follower_data set " + \
###								"limited = True, " + \
###								"removed = False " + \
###								"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
###								" and id = '" + str(wARR_RateFollowers[wIndex]['id']) + "' ;"
###					gVal.STR_TrafficInfo['autofollowt'] += 1
###					
###					###※既にリムーブしているユーザを記録＆表示する
###					wRes['Reason'] = "ノーアクションのためリムーブ候補に設定: @" + str(wARR_RateFollowers[wIndex]['screen_name'])
###					gVal.OBJ_L.Log( "R", wRes, "", inViewConsole=True )
###			
			###その他 スキップ
				else:
					continue
			
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
			
			else:
				wStr = wStr + " [〇フォロワー]  "
			
			if wARR_RateFollowers[wIndex]['limited']==True :
				wStr = wStr + " [★自動リムーブ対象]"
			
			wStr = wStr + '\n'
			
			wStr = wStr + "更新日=" + str(wARR_RateFollowers[wIndex]['lastdate']) + "  ツイ数=" + str(wARR_RateFollowers[wIndex]['lastcount'])
			wStr = wStr + '\n'
			wStr = wStr + "--------------------" + '\n'
		
		#############################
		# 統計
		wStr = wStr + "--------------------" + '\n'
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
		# フォロー一覧 取得
		wMyFollowRes = gVal.OBJ_Twitter.GetMyFollowList()
		if wMyFollowRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetMyFollowList): " + wMyFollowRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		wARR_MyFollowID = []
		for wROW in wMyFollowRes['Responce'] :
			wARR_MyFollowID.append( str(wROW['id']) )
		
		#############################
		# normal登録者 取得(idだけ)
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
		wARR_NormalListMenberID = []
		for wROW in wListsRes['Responce'] :
			wARR_NormalListMenberID.append( str(wROW['id']) )
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " フォロワー監視 実行" + '\n'
		wStr = wStr + "--------------------" + '\n'
		wStr = wStr + "ノーリアクション リムーブチェック実行中......" + '\n'
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# DBのフォロワー一覧取得(自動リムーブでない情報を抽出)
		wQuery = "select * from tbl_follower_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "' and " + \
					"limited = False " + \
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
		
		wVAL_ZanNum = len(wARR_RateFollowers)
		wRemoveLimNum = 0
		wResStop = False
		wKeylist = wARR_RateFollowers.keys()
		#############################
		# ノーリアクションチェック
		for wIndex in wKeylist :
			###カウント
			wRemoveLimNum += 1
			wVAL_ZanNum -= 1
			
			###ユーザIDを抽出
			wID = str( wARR_RateFollowers[wIndex]['id'] )
			
			###フォロー者でないならスキップ
			if wID not in wARR_MyFollowID :
				continue
			###normalリストでないならスキップ
			if wID not in wARR_NormalListMenberID :
				continue
			
			###ユーザの直近のツイートを取得
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
			# わたしをふぁぼったかチェック
			wReciveFavoRes = self.OBJ_Parent.ReciveFavo( wID, wARR_RateFollowers[wIndex], wTweetRes['Responce'] )
			if wReciveFavoRes['Result']!=True :
				##失敗
				continue
			
			#############################
			# 処理全て終わり
			if wVAL_ZanNum==0 :
				break
			
			#############################
			# 1回の解除数チェック
			elif gVal.DEF_STR_TLNUM['rRemoveNofavoNum']<=wRemoveLimNum :
				###解除数限界ならウェイトする
				CLS_OSIF.sPrn( "Twitter規制回避のため、待機します。" )
				CLS_OSIF.sPrn( "CTRL+Cで中止することもできます。残り処理数= " + str(wVAL_ZanNum) + " 個" )
				
				wResStop = CLS_OSIF.sPrnWAIT( gVal.DEF_STR_TLNUM['removeLimWait'] )
				if wResStop==False :
					CLS_OSIF.sPrn( "処理を中止しました。" + '\n' )
					break	#ウェイト中止
				
				#############################
				# 15分周期処理
				w15Res = self.OBJ_Parent.Circle15min()
				if w15Res['Result']!=True :
					wRes['Reason'] = "Circle15min is failed reason=" + w15Res['Reason']
					gVal.OBJ_L.Log( "B", wRes )
					return wRes
				
				wRemoveLimNum = 0
			
			#############################
			# 残り処理回数がまだある =5秒ウェイトする
			else :
				CLS_OSIF.sSleep( 5 )
		
		#############################
		
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
		gVal.STR_TrafficInfo['autofollowt'] = len(wARR_RateFollowers)
		
###		#############################
###		# 画面クリア
###		CLS_OSIF.sDispClr()
###		
		#############################
		# ヘッダ表示
###		wStr = "--------------------" + '\n'
###		wStr = wStr + " フォロワー監視 実行" + '\n'
###		wStr = wStr + "--------------------" + '\n'
###		wStr = wStr + "以下のリムーブ対象ユーザをリムーブします......" + '\n'
		wStr = '\n' + "以下のリムーブ対象ユーザをリムーブします......" + '\n'
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
			elif gVal.DEF_STR_TLNUM['rRemoveLimNum']<=wRemoveLimNum :
				###解除数限界ならウェイトする
				CLS_OSIF.sPrn( "Twitter規制回避のため、待機します。" )
				CLS_OSIF.sPrn( "CTRL+Cで中止することもできます。残り処理数= " + str(wVAL_ZanNum) + " 個" )
				
				wResStop = CLS_OSIF.sPrnWAIT( gVal.DEF_STR_TLNUM['removeLimWait'] )
				if wResStop==False :
					CLS_OSIF.sPrn( "処理を中止しました。" + '\n' )
					break	#ウェイト中止
				
				#############################
				# 15分周期処理
				w15Res = self.OBJ_Parent.Circle15min()
				if w15Res['Result']!=True :
					wRes['Reason'] = "Circle15min is failed reason=" + w15Res['Reason']
					gVal.OBJ_L.Log( "B", wRes )
					return wRes
				
				wRemoveLimNum = 0
			
			#############################
			# 残り処理回数がまだある =5秒ウェイトする
			else :
				CLS_OSIF.sSleep( 5 )
		
		#############################
		# ミュート解除の実行
		# 対象：
		#   フォロー者ではない、かつ 一度フォローしている、かつ ミュート中
		CLS_OSIF.sPrn( '\n' + "続いてミュート解除を実行します。対象ユーザを検索中......." + '\n' )
		#############################
		# ミュート解除対象のIDを抜き出し
		wQuery = "select * from tbl_follower_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "' and " + \
					"r_myfollow = True " + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(2): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		gVal.STR_TrafficInfo['dbreq'] += 1
		
		#############################
		# リスト型に整形
		wARR_RateMyFollows = []
		gVal.OBJ_DB.ChgList( wResDB['Responce']['Data'], outList=wARR_RateMyFollows )
		
		#############################
		# フォロー一覧 取得
		wMyFollowRes = gVal.OBJ_Twitter.GetMyFollowList()
		if wMyFollowRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetMyFollowList): " + wMyFollowRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		
		#############################
		# ミュート一覧 取得
		wMuteRes = gVal.OBJ_Twitter.GetMuteIDs()
		if wMuteRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetMuteIDs): " + wMuteRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		
		#############################
		# 対象の作成
		wARR_MuteRemoveID = []
		if len(wMuteRes['Responce'])>=1 :
			wARR_MuteIDs = []
			for wROW in wMuteRes['Responce']:
				wROW_id = str(wROW)
				wARR_MuteIDs.append( wROW_id )
			
			wARR_MyFollowID = []
			for wROW in wMyFollowRes['Responce'] :
				wROW_id = str(wROW['id'])
				wARR_MyFollowID.append( wROW_id )
			
			### DBベースで検索
			for wROW in wARR_RateMyFollows :
				wROW_id = str(wROW)
				
				###現フォロー者なら対象外
				if wROW_id in wARR_MyFollowID :
					continue
				###ミュート一覧になければ対象外
				if wROW_id not in wARR_MuteIDs :
					continue
				
				wARR_MuteRemoveID.append( wROW_id )
			gVal.STR_TrafficInfo['muteremovet'] = len( wARR_MuteRemoveID )
		
		if len( wARR_MuteRemoveID )==0 :
			CLS_OSIF.sPrn( "ミュート解除対象はありませんでした。" + '\n' )
		else:
			#############################
			# ミュート解除していく
			gVal.STR_TrafficInfo['muteremove'] = 0
			wStr = "ミュート解除対象数: " + str(len( wARR_MuteRemoveID )) + '\n'
			wStr = wStr + "ミュート解除中......." + '\n'
			CLS_OSIF.sPrn( wStr )
			
			for wID in wARR_MuteRemoveID :
				###  ミュート解除する
				wRemoveRes = gVal.OBJ_Twitter.RemoveMute( wID )
				if wRemoveRes['Result']!=True :
					wRes['Reason'] = "Twitter API Error(RemoveMute): " + wRemoveRes['Reason']
					gVal.OBJ_L.Log( "B", wRes )
					return wRes
				###  ミュート一覧にないID=ミュート解除してない 場合は待機スキップ
				if wRemoveRes['Responce']==False :
					continue
				gVal.STR_TrafficInfo['muteremove'] += 1
				CLS_OSIF.sSleep(5)
		
		#############################
		# 統計
		wStr = "--------------------" + '\n'
		wStr = wStr + "リムーブ対象 ユーザ数 = " + str(gVal.STR_TrafficInfo['autofollowt']) + '\n'
		wStr = wStr + "リムーブ済み ユーザ数 = " + str(gVal.STR_TrafficInfo['autofollow']) + '\n'
		wStr = wStr + "ミュート解除 対象数   = " + str(gVal.STR_TrafficInfo['muteremovet']) + '\n'
		wStr = wStr + "ミュート解除 実行数   = " + str(gVal.STR_TrafficInfo['muteremove']) + '\n'
		
		#############################
		# コンソールに表示
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# 自動選出フォロー(手動)
#####################################################
	def AutoChoiceFollow(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterFollower"
		wRes['Func']  = "AutoChoiceFollow"
		
		CLS_OSIF.sPrn( "処理中......" )
		#############################
		# DBのフォロワー一覧取得(一度でもフォローしたことがある)
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
		wARR_Followers = []
		gVal.OBJ_DB.ChgList( wResDB['Responce']['Data'], outList=wARR_Followers )
		
		#############################
		# 登録者がいなければ処理しない
		if len(wARR_Followers)==0 :
			##失敗
			wRes['Reason'] = "DB登録にユーザが登録されていません。"
			gVal.OBJ_L.Log( "D", wRes )
			return wRes
		
		#############################
		# un_refollowl登録者のIDを取得する
		wARR_unReFollow = []
		wListsRes = gVal.OBJ_Twitter.GetListMember( gVal.STR_UserInfo['UrfList'] )
		if wListsRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetListMember:UrfList): " + wListsRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		for wROW in wListsRes['Responce'] :
			if str(wROW['id']) not in wARR_Followers :
				wARR_unReFollow.append( str(wROW['id']) )
		
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "PC時間の取得に失敗しました"
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		### wTD['TimeDate']
		
		wKeyUserNum = len( wARR_Followers )
		#############################
		# 画面クリア(=通常モード時)
		if gVal.FLG_Test_Mode==False :
			CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " 自動選出フォロー(手動)" + '\n'
		wStr = wStr + "--------------------" + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "選出された " + str(wKeyUserNum) + " 人のキーユーザのうち 1 人フォローできます。"
		wStr = wStr + "なおAPIが規制されやすいので、次回の実行までは 15分以上 時間をあけてください。"
		CLS_OSIF.sPrn( wStr )
		
		CLS_OSIF.sPrn( "ユーザを選出中......" )
		#############################
		# DB登録ユーザからランダムに選出する
		wARR_ChoicedID = []
		wARR_Rand   = []
		wCount      = -1
		while True:
			wRandID = None
			wCount += 1
			#############################
			# DBユーザの情報がない =処理終わり
			if wKeyUserNum<wCount :
				break
			
			#############################
			# DB登録ユーザからランダムにID選出
			wRand = CLS_OSIF.sGetRand( wKeyUserNum )
			if wRand in wARR_Rand :
				###既に選出されたランダム値(ID) =やり直し
				continue
			wARR_Rand.append( wRand )
			wRandID = str(wARR_Followers[wRand])
			
			CLS_OSIF.sPrn( "元フォロー情報取得中......" )
			#############################
			# フォロー者が1人以上か
			wUserInfoRes = gVal.OBJ_Twitter.GetUserinfo( inID=wRandID )
			if wUserInfoRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error(GetUserinfo:1): " + wUserInfoRes['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				continue
			
			### フォロー者20人未満はやり直し
			if wUserInfoRes['Responce']['friends_count']<=20 :
				continue
			### フォロー者よりフォロワーのが多ければやり直し
			if wUserInfoRes['Responce']['friends_count']<wUserInfoRes['Responce']['followers_count'] :
				continue
			### 公式マークは除外する仕様とする（有名人の知り合いは有名人が多い）
			if wUserInfoRes['Responce']['verified']==True :
				continue
			
			wScreenName = wUserInfoRes['Responce']['screen_name']
			CLS_OSIF.sPrn( "元フォロー者ID一覧取得中......: 情報元ユーザ @" + wScreenName )
			#############################
			# 選出ユーザのフォロー者ID一覧を取得する
			wFollowIDListRes = gVal.OBJ_Twitter.GetFollowIDList( wRandID )
			if wFollowIDListRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error(GetFollowIDList): " + wFollowIDListRes['Reason'] + ": " + wScreenName
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			###フォロー者がいない？(ありえなくね？) =対象外
			if len(wFollowIDListRes['Responce'])==0 :
				continue
			
			#############################
			# ユーザIDを選出する
			wARR_RandFollow   = []
			wFollowIDList_Num = len(wFollowIDListRes['Responce'])
			wFollowIDList_Cnt = -1
			while True:
				wFollowIDList_Cnt += 1
				if wFollowIDList_Num<wFollowIDList_Cnt :
					wRandID = None
					break
				
				#############################
				# フォロー者からユーザIDをランダム選出する
				wRand_2 = CLS_OSIF.sGetRand( wFollowIDList_Num )
				if wRand_2 in wARR_RandFollow :
					###既に選出されたランダム値(ID) =やり直し
					continue
				wARR_RandFollow.append( wRand_2 )
				wRandID = str(wFollowIDListRes['Responce'][wRand_2])
				if wRandID in wARR_ChoicedID :
					###既に選出されたID =やり直し
					continue
				wARR_ChoicedID.append( wRandID )
				
				###既にフォロー者ならやり直し
				if wRandID in wARR_Followers :
					continue
				###除外リストユーザならやり直し
				if wRandID in wARR_unReFollow :
					continue
				###候補から除外されていたらやり直し
				if wRandID in gVal.STR_ExcFollowID :
					continue
				
				CLS_OSIF.sPrn( "候補フォロー情報取得中......: 情報元ユーザ @" + wScreenName )
				#############################
				# ユーザ情報を取得する
				wUserInfoRes = gVal.OBJ_Twitter.GetUserinfo( inID=wRandID )
				if wUserInfoRes['Result']!=True :
					wRes['Reason'] = "Twitter API Error(GetUserinfo:2): " + wUserInfoRes['Reason']
					gVal.OBJ_L.Log( "B", wRes )
					continue
				
				###この機能では鍵垢は除外する仕様とする
				if wUserInfoRes['Responce']['protected']==True :
					continue
				
				###この機能では公式マークは除外する仕様とする
				if wUserInfoRes['Responce']['verified']==True :
					continue
				
				#############################
				# ユーザの直近のツイートが期間内か（アクティブに活動中か）
				#   リツイートのみは除外
				wTweetRes = gVal.OBJ_Twitter.GetTL( inTLmode="user", inFLG_Rep=False, inFLG_Rts=False,
					 inScreenName=wUserInfoRes['Responce']['screen_name'], inCount=gVal.DEF_STR_TLNUM['AutoFavoCount'] )
				if wTweetRes['Result']!=True :
					wRes['Reason'] = "Twitter API Error(GetTL): " + wTweetRes['Reason']
					gVal.OBJ_L.Log( "B", wRes )
					continue
				if len(wTweetRes['Responce'])==0 :
					continue
				gVal.STR_TrafficInfo['timeline'] += len(wTweetRes['Responce'])
				
				wFLG_Active = False
				for wTweet in wTweetRes['Responce'] :
					### リツイートは除外
					if "retweeted_status" in wTweet :
						continue
					### 引用リツイートは除外
					elif "quoted_status" in wTweet :
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
					
					### アクティブツイート検出
					wFLG_Active = True
					break
				
				###アクティブでないので除外
				if wFLG_Active==False :
					continue
				
###				#############################
###				#※候補確定
###				break
###			
###			if wRandID==None :
###				###候補が確定してなければ、やり直し
###				continue
###			
				wUserInfo = wUserInfoRes['Responce']
				#※候補あり
				#############################
				# 候補の表示
				wStr = '\n' + "--------------------" + '\n'
				wStr = wStr + "フォロー候補= " + str(wUserInfo['name']) + "(@" + str(wUserInfo['screen_name']) + ")" + '\n'
				wStr = wStr + '\n' + str(wUserInfo['description']) + '\n'
				wStr = wStr + '\n' + "対処コマンド：" + '\n'
				wStr = wStr + "    y=フォロー / q=選定中止 / v=ブラウザで表示" + '\n'
				CLS_OSIF.sPrn( wStr )
				
				while True:
					wStr = "対処コマンドを指定してください=> "
					wSelect = CLS_OSIF.sInp( wStr )
					if wSelect=="y" :
						### フォローする =確定 ループ抜ける
						break
					
					elif wSelect=="q" :
						###選出中止
						CLS_OSIF.sPrn( "選出を終了しました。" + '\n' )
						wRes['Result'] = True
						return wRes
					
					elif wSelect=="v" :
						###ブラウザで表示
						wURL = "https://twitter.com/" + str(wUserInfo['screen_name'])
						CLS_HTMLIF.sOpenURL( wURL )
						continue
					
					elif wSelect=="n" :
						###次から候補から外す
						wQuery = "insert into tbl_exc_followid values (" + \
									"'" + str(wTD['TimeDate']) + "'," + \
									"" + str( wRandID ) + " " + \
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
						
						gVal.STR_ExcFollowID.append( wRandID )
						wRandID = None
						break
					
					else :
						wRandID = None
						break
				
				if wRandID!=None :
					break
			
			if wRandID!=None :
				## ※フォロー確定
				break
		
		#############################
		# 候補がいなければ処理しない
		if wRandID==None :
			CLS_OSIF.sPrn( "ユーザが選出されませんでした。" )
			wRes['Result'] = True
			return wRes
		
		CLS_OSIF.sPrn( "フォロー処理中......" )
		#############################
		# 候補をフォローする
		wTwitterRes = gVal.OBJ_Twitter.CreateFollow( wRandID )
		if wTwitterRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(CreateFollow): " + wTwitterRes['Reason']
			return wRes
		
		#############################
		# normalリストへ追加
		wTwitterRes = gVal.OBJ_Twitter.AddUserList( gVal.STR_UserInfo['NorList'], wRandID )
		if wTwitterRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(AddUserList): " + wTwitterRes['Reason']
			return wRes
		
		#############################
		# DBに記録する(新規)
		wName = str(wUserInfo['name']).replace( "'", "''" )
		wQuery = "insert into tbl_follower_data values (" + \
					"'" + gVal.STR_UserInfo['Account'] + "'," + \
					"'" + str(wTD['TimeDate']) + "'," + \
					"True," + \
					"False," + \
					"True," + \
					"False," + \
					"'" + str(wTD['TimeDate']) + "'," + \
					"False," + \
					"False," + \
					"'" + str( wRandID ) + "'," + \
					"'" + wName + "'," + \
					"'" + str(wUserInfo['screen_name']) + "'," + \
					str(wUserInfo['statuses_count']) + "," + \
					"'" + str(wTD['TimeDate']) + "'," + \
					"''," + \
					"''," + \
					"'1900-01-01 00:00:00'," + \
					"0, 0, 0," + \
					"''," + \
					"'1900-01-01 00:00:00' " + \
					") ;"
		gVal.STR_TrafficInfo['dbins'] += 1
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(4): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		gVal.STR_TrafficInfo['dbreq'] += 1
		
		#############################
		# 正常終了
		CLS_OSIF.sPrn( '\n' + "フォローが正常に完了しました。" )
		wRes['Result'] = True
		return wRes



