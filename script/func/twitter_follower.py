#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : Twitter監視 フォロワー監視系
# 
# ::Update= 2020/10/10
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
		self.OBJ_Parent.STR_Cope['MyFollowNum'] = len(wARR_MyFollowID)
		
		#############################
		# フォロワー一覧 取得
		wFollowerRes = gVal.OBJ_Twitter.GetFollowerList()
		if wFollowerRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetFollowerList): " + wFollowerRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		wARR_FollowerID = []
		for wROW in wFollowerRes['Responce'] :
			wARR_FollowerID.append( str(wROW['id']) )
		self.OBJ_Parent.STR_Cope['FollowerNum'] = len(wARR_FollowerID)
		
		#############################
		# normal登録者 取得(idだけ)
		wListsRes = gVal.OBJ_Twitter.GetLists()
		if wListsRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetLists): " + wListsRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		wListsRes = gVal.OBJ_Twitter.GetListMember( gVal.STR_UserInfo['NorList'] )
		if wListsRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetListMember): " + wListsRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		wARR_NormalListMenberID = []
		for wROW in wListsRes['Responce'] :
			wARR_NormalListMenberID.append( str(wROW['id']) )
		
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
				wResDB = gVal.OBJ_DB.RunQuery( wQuery )
				wResDB = gVal.OBJ_DB.GetQueryStat()
				if wResDB['Result']!=True :
					##失敗
					wRes['Reason'] = "Run Query is failed(2): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
					gVal.OBJ_L.Log( "B", wRes )
					return wRes
				
				###  カウント
				self.OBJ_Parent.STR_Cope['DB_Update'] += 1
			
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
				
				wResDB = gVal.OBJ_DB.RunQuery( wQuery )
				wResDB = gVal.OBJ_DB.GetQueryStat()
				if wResDB['Result']!=True :
					##失敗
					wRes['Reason'] = "Run Query is failed(3): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
					gVal.OBJ_L.Log( "B", wRes )
					return wRes
				
				self.OBJ_Parent.STR_Cope['DB_Insert'] += 1
		
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
		
		#############################
		# 辞書型に整形
		wARR_RateFollowers = {}
		gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateFollowers )
		self.OBJ_Parent.STR_Cope['DB_Num'] += len(wARR_RateFollowers)
		
		#############################
		# 自動リムーブ対象を設定する
		#   ・フォロー者 かつ アンフォロワー
		#   ・一度もリムーブしたことがない
		#   ・normalリスト
		#   ・フォローしてから一定期間過ぎた
		# 自動リムーブ対象で、既にアンフォロワーならリムーブ済みにする
		
##		wFLG_UnRemove = False	#自動リムーブ対象外か
##		wFLG_UnFollow = False	#フォロー状態
##		wFLG_Follower = False	#フォロワー状態
		wKeylist = wARR_RateFollowers.keys()
		for wIndex in wKeylist :
			wFLG_UnRemove = False	#自動リムーブ対象外か
			wFLG_UnFollow = False	#フォロー状態
			wFLG_Follower = False	#フォロワー状態
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
					wRes['Reason'] = "key is not found"
					gVal.OBJ_L.Log( "C", wRes )
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
					wRes['Reason'] = "sTimeLag failed"
					gVal.OBJ_L.Log( "B", wRes )
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
				
				self.OBJ_Parent.STR_Cope['tMyFollowRemove'] += 1
			
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
			wResDB = gVal.OBJ_DB.RunQuery( wQuery )
			wResDB = gVal.OBJ_DB.GetQueryStat()
			if wResDB['Result']!=True :
				##失敗
				wRes['Reason'] = "Run Query is failed(5): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			
			###  カウント
			self.OBJ_Parent.STR_Cope['DB_Update'] += 1
		
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
		# 集計のリセット
		self.OBJ_Parent.STR_Cope['MyFollowNum'] = 0
		self.OBJ_Parent.STR_Cope['FollowerNum'] = 0
		self.OBJ_Parent.STR_Cope['NewFollowerNum']  = 0
		self.OBJ_Parent.STR_Cope['tMyFollowRemove'] = 0
		self.OBJ_Parent.STR_Cope['MyFollowRemove']  = 0
		
		self.OBJ_Parent.STR_Cope['DB_Num']    = 0
		
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
		
		#############################
		# 辞書型に整形
		wARR_RateFollowers = {}
		gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateFollowers )
		self.OBJ_Parent.STR_Cope['DB_Num'] = len(wARR_RateFollowers)
		
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
##				self.OBJ_Parent.STR_Cope['MyFollowRemove'] += 1
			else:
				wStr = wStr + " [〇フォロー]  "
			
			if wARR_RateFollowers[wIndex]['rc_follower']==False :
				wStr = wStr + " [●非フォロワー]"
			else:
				wStr = wStr + " [〇フォロワー]  "
				self.OBJ_Parent.STR_Cope['FollowerNum'] += 1
				if wARR_RateFollowers[wIndex]['removed']==False :
					self.OBJ_Parent.STR_Cope['MyFollowNum'] += 1
			
			if wARR_RateFollowers[wIndex]['limited']==True :
				wStr = wStr + " [★いいね解除対象]"
				self.OBJ_Parent.STR_Cope['tFavoRemove'] += 1
			
			wStr = wStr + '\n'
			
			wStr = wStr + "更新日=" + str(wARR_RateFollowers[wIndex]['lastdate']) + "  ツイ数=" + str(wARR_RateFollowers[wIndex]['lastcount'])
			wStr = wStr + '\n'
			wStr = wStr + "--------------------" + '\n'
		
		#############################
		# 統計
		wStr = wStr + "--------------------" + '\n'
		wStr = wStr + "DB登録数         = " + str(self.OBJ_Parent.STR_Cope['DB_Num']) + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "現フォロワー数   = " + str(self.OBJ_Parent.STR_Cope['FollowerNum']) + '\n'
		wStr = wStr + "相互フォロー数   = " + str(self.OBJ_Parent.STR_Cope['MyFollowNum']) + '\n'
		wStr = wStr + "自動リムーブ対象 = " + str(self.OBJ_Parent.STR_Cope['tMyFollowRemove']) + '\n'
		
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
	def sSaveCSV_NewFollower( cls, inNewFollower ):
		#############################
		# 書き込みデータを作成
		wSetLine = []
		wKeylist = inNewFollower.keys()
		
		wLine = "user_name, screen_name, url, " + '\n'
		wSetLine.append(wLine)
		for iKey in wKeylist :
			wLine = ""
			wLine = wLine + str(inNewFollower[iKey]['user_name']) + ", "
			wLine = wLine + str(inNewFollower[iKey]['screen_name']) + ", "
			wLine = wLine + "https://twitter.com/" + str(inNewFollower[iKey]['user_name']) + ", "
			wSetLine.append(wLine)
		
		#############################
		# ファイル名の設定
		wFile_path = gVal.DEF_USERDATA_PATH + str(gVal.STR_UserInfo['Account']) + ".csv"
		
		#############################
		# ファイル上書き書き込み
		if CLS_File.sWriteFile( wFile_path, wSetLine, inExist=False )!=True :
			return ""	#失敗
		
		return wFile_path








#####################################################
# フォロワー監視の実行
#####################################################
	def Run(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# 集計のリセット
		self.OBJ_Parent.STR_Cope['FollowerNum']    = 0
		self.OBJ_Parent.STR_Cope['NewFollowerNum'] = 0
		self.OBJ_Parent.STR_Cope['MyFollowRemove'] = 0
		self.OBJ_Parent.STR_Cope['DB_Num']    = 0
		self.OBJ_Parent.STR_Cope['DB_Insert'] = 0
		self.OBJ_Parent.STR_Cope['DB_Update'] = 0
		self.OBJ_Parent.STR_Cope['DB_Delete'] = 0
		
		#############################
		# DBのフォロワー一覧取得(id, created_at)
		wQuery = "select * from tbl_follower_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wResDB = self.Obj_Parent.OBJ_DB.RunQuery( wQuery )
		wResDB = self.Obj_Parent.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_Twitter_Ctrl: Get_Run_FollowerAdmin: Run Query is failed(1): " + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		#############################
		# 辞書型に整形
		wARR_RateFollowers = {}
		self.Obj_Parent.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateFollowers )
###		self.OBJ_Parent.STR_Cope['DB_Num'] = len(wARR_Followers)
		
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
		self.OBJ_Parent.STR_Cope['FollowerNum'] = len(wFollowerRes['Responce'])
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
				
				wResDB = self.Obj_Parent.OBJ_DB.RunQuery( wQuery )
				wResDB = self.Obj_Parent.OBJ_DB.GetQueryStat()
				if wResDB['Result']!=True :
					##失敗
					wRes['Reason'] = "CLS_Twitter_Ctrl: Get_RunFavoAdmin: Run Query is failed(2): " + wResDB['Reason']
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
				
				wResDB = self.Obj_Parent.OBJ_DB.RunQuery( wQuery )
				wResDB = self.Obj_Parent.OBJ_DB.GetQueryStat()
				if wResDB['Result']!=True :
					##失敗
					wRes['Reason'] = "CLS_Twitter_Ctrl: Get_RunFavoAdmin: Run Query is failed(3): " + wResDB['Reason']
					return wRes
				
				self.OBJ_Parent.STR_Cope['DB_Insert'] += 1
			
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
					self.OBJ_Parent.STR_Cope['NewFollowerNum'] += 1
		
		#############################
		# DBのフォロワー一覧 再取得
		wQuery = "select * from tbl_follower_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wResDB = self.Obj_Parent.OBJ_DB.RunQuery( wQuery )
		wResDB = self.Obj_Parent.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_Twitter_Ctrl: Get_Run_FollowerAdmin: Run Query is failed(4): " + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		#############################
		# 辞書型に整形
		wARR_RateFollowers = {}
		self.Obj_Parent.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateFollowers )
		self.OBJ_Parent.STR_Cope['DB_Num'] = len(wARR_RateFollowers)
		
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
				self.OBJ_Parent.STR_Cope['MyFollowRemove'] += 1
				wVAL_rRemoveLimNum += 1
			
			###DBに記録する
			###  自動リムーブ
			if wFLG_AutoRemove==True :
				wQuery = "update tbl_follower_data set " + \
							"r_remove = True," + \
							"remdate = '" + str(wTD['TimeDate']) + "' " + \
							"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
							" and id = '" + str(wROW['id']) + "' ;"
				
				wResDB = self.Obj_Parent.OBJ_DB.RunQuery( wQuery )
				wResDB = self.Obj_Parent.OBJ_DB.GetQueryStat()
				if wResDB['Result']!=True :
					##失敗
					wRes['Reason'] = "CLS_Twitter_Ctrl: Get_RunFavoAdmin: Run Query is failed(11): " + wResDB['Reason']
					return wRes
				
				###  カウント
				self.OBJ_Parent.STR_Cope['DB_Update'] += 1
			
			###  フォロワー状態が更新された
			elif wSTR_wk_RateFollower['rc_follower']!=wFLG_Follower :
				wQuery = "update tbl_follower_data set " + \
							"rc_follower = " + str(wFLG_Follower) + " " + \
							"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
							" and id = '" + str(wROW['id']) + "' ;"
				
				wResDB = self.Obj_Parent.OBJ_DB.RunQuery( wQuery )
				wResDB = self.Obj_Parent.OBJ_DB.GetQueryStat()
				if wResDB['Result']!=True :
					##失敗
					wRes['Reason'] = "CLS_Twitter_Ctrl: Get_RunFavoAdmin: Run Query is failed(12): " + wResDB['Reason']
					return wRes
				
				###  カウント
				self.OBJ_Parent.STR_Cope['DB_Update'] += 1
		
		wRes['Result'] = True
		return wRes



