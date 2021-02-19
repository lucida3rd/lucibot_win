#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : Twitter監視 フォロワー監視系
# 
# ::Update= 2021/2/16
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
			
			###自動リムーブ対象外 で 既にリムーブ済みだった
			else:
				if wARR_RateFollowers[wIndex]['rc_myfollow']==False and \
				   wARR_RateFollowers[wIndex]['removed']==False :
					wQuery = "update tbl_follower_data set " + \
								"removed = True " + \
								"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
								" and id = '" + str(wARR_RateFollowers[wIndex]['id']) + "' ;"
					
					###※既にリムーブしているユーザを記録＆表示する
					wRes['Reason'] = "既にリムーブ済みのユーザ: @" + str(wARR_RateFollowers[wIndex]['screen_name'])
					gVal.OBJ_L.Log( "R", wRes, "", inViewConsole=True )
			
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



