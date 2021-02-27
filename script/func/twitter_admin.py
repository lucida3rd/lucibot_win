#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : Twitter監視 管理系
# 
# ::Update= 2021/2/20
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   __init__( self, parentObj=None ):
#   UserRevival(self):
#
# Class Function(static):
#   (none)
#
#####################################################

from osif import CLS_OSIF
from htmlif import CLS_HTMLIF
from mydisp import CLS_MyDisp
from gval import gVal
#####################################################
class CLS_TwitterAdmin():
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
		wRes['Class'] = "CLS_TwitterAdmin"
		wRes['Func']  = "__init__"
		
		if parentObj==None :
			###親クラス実体の未設定
			wRes['Reason'] = "You have not set the parent class entity for parentObj"
			gVal.OBJ_L.Log( "A", wRes )
			return
		
		self.OBJ_Parent = parentObj
		return



#####################################################
# ユーザ管理
#####################################################
	def UserAdmin(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterAdmin"
		wRes['Func']  = "UserAdmin"
		
		#############################
		# コンソールを表示
		while True :
			
			gVal.STR_UserAdminInfo['screen_name'] = None
			gVal.STR_UserAdminInfo['id']          = -1
			
			#############################
			# 画面クリア
			CLS_OSIF.sDispClr()
			
			#############################
			# ヘッダ表示
			wStr = "--------------------" + '\n'
			wStr = wStr + " ユーザ管理" + '\n'
			wStr = wStr + "--------------------" + '\n'
			wStr = wStr + "管理をおこないたいユーザのTwitter ID(@なし)を入力してください。" + '\n'
			wStr = wStr + "中止する場合は \q を入力してください" + '\n'
			CLS_OSIF.sPrn( wStr )
			
			#############################
			# 実行の確認
			wTwitterID = CLS_OSIF.sInp( "Twitter ID(@なし)？(\\q=中止)=> " )
			if wTwitterID=="\\q" :
				##キャンセル
###				CLS_OSIF.sPrn( "処理を中止しました。" )
				wRes['Result'] = True
				return wRes
			
			#############################
			# 処理中表示
			CLS_OSIF.sPrn( "確認しています。しばらくお待ちください......" )
			
			#############################
			# ユーザ情報を取得する
###			wUserinfoRes = gVal.OBJ_Twitter.GetUserinfo( inScreenName=wTwitterID )
###			if wUserinfoRes['Result']!=True :
###				wRes['Reason'] = "Twitter API Error(GetUserinfo): " + wUserinfoRes['Reason']
###				gVal.OBJ_L.Log( "B", wRes )
###				break
###			
			wUserinfoRes = self.GetUserInfo( wTwitterID )
			if wUserinfoRes['Result']!=True :
				wRes['Reason'] = "GetUserInfo is failed: " + wUserinfoRes['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				break
			
			if wUserinfoRes['Responce']==False :
				CLS_OSIF.sPrn( "そのユーザは存在しません。" + '\n' )
				CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
				continue
			
			gVal.STR_UserAdminInfo['screen_name'] = wTwitterID
			gVal.STR_UserAdminInfo['user_name']   = wUserinfoRes['Responce']['user_name']
			gVal.STR_UserAdminInfo['id']          = wUserinfoRes['Responce']['id']
			gVal.STR_UserAdminInfo['statuses_count'] = wUserinfoRes['Responce']['statuses_count']
			
			gVal.STR_UserAdminInfo['DB_exist']      = wUserinfoRes['Responce']['DB_exist']
			gVal.STR_UserAdminInfo['DB_r_myfollow'] = wUserinfoRes['Responce']['DB_r_myfollow']
			gVal.STR_UserAdminInfo['DB_r_remove']   = wUserinfoRes['Responce']['DB_r_remove']
			gVal.STR_UserAdminInfo['DB_limited']    = wUserinfoRes['Responce']['DB_limited']
			
			gVal.STR_UserAdminInfo['DB_favo_date']   = wUserinfoRes['Responce']['DB_favo_date']
			gVal.STR_UserAdminInfo['DB_favo_cnt']    = wUserinfoRes['Responce']['DB_favo_cnt']
			gVal.STR_UserAdminInfo['DB_favo_r_date'] = wUserinfoRes['Responce']['DB_favo_r_date']
			gVal.STR_UserAdminInfo['DB_favo_r_cnt']  = wUserinfoRes['Responce']['DB_favo_r_cnt']
			
			gVal.STR_UserAdminInfo['Protect']  = wUserinfoRes['Responce']['Protect']
			gVal.STR_UserAdminInfo['MyFollow'] = wUserinfoRes['Responce']['MyFollow']
			gVal.STR_UserAdminInfo['Follower'] = wUserinfoRes['Responce']['Follower']
			gVal.STR_UserAdminInfo['MyBlock']  = wUserinfoRes['Responce']['MyBlock']
			gVal.STR_UserAdminInfo['Blocked']  = wUserinfoRes['Responce']['Blocked']
			gVal.STR_UserAdminInfo['NorList']  = wUserinfoRes['Responce']['NorList']
			gVal.STR_UserAdminInfo['UnrList']  = wUserinfoRes['Responce']['UnrList']
			
			#############################
			# 管理の本画面を表示する
			while True :
				wWord = self.__view_UserAdmin()
				
				if wWord=="\\q" :
					###終了
					break
				if wWord=="" :
					###未入力は再度入力
					continue
				
				wResSearch = self.__run_UserAdmin( wWord )
###				CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
				if wResSearch['Result']!=True :
					### 処理失敗
					continue
		
		wRes['Result'] = True
		return wRes

	#####################################################
	# ユーザ管理 画面表示
	#####################################################
###	def __view_UserAdmin( self, inIndex ):
	def __view_UserAdmin(self):
		wResDisp = CLS_MyDisp.sViewDisp( "UserAdminConsole", -1 )
		if wResDisp['Result']==False :
			gVal.OBJ_L.Log( "D", wResDisp )
			return "\\q"	#失敗=強制終了
		
		wWord = CLS_OSIF.sInp( "コマンド？=> " )
		return wWord

	#####################################################
	# ユーザ管理 実行
	#####################################################
###	def __run_UserAdmin( self, inIndex, inWord ):
	def __run_UserAdmin( self, inWord ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterAdmin"
		wRes['Func']  = "__run_UserAdmin"
		
		#############################
		# コマンド：フォローする
		if inWord=="\\f" :
			wRes = self.__run_Follow()
			CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
		
		#############################
		# コマンド：リムーブする
		elif inWord=="\\rm" :
			wRes = self.__run_Remove()
			CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
		
		#############################
		# コマンド：関係リセット
		elif inWord=="\\rma" :
			wRes = self.__run_Remove( inDBClear=True )
			CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
		
		#############################
		# コマンド：ブラウザで表示
		elif inWord=="\\v" :
			wRes = self.__view_Profile()
		
		#############################
		# 不明なコマンド
		else :
			CLS_OSIF.sPrn( "不明なコマンドです" + '\n' )
			CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
		
###		#############################
###		# 正常終了
###		wRes['Result'] = True
		return wRes



#####################################################
# フォロー実行
#####################################################
	def __run_Follow(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterAdmin"
		wRes['Func']  = "__run_Follow"
		
		#############################
		# フォローできるか確認する
		
		#############################
		# 既にフォロー済みか
		if gVal.STR_UserAdminInfo['MyFollow']==True :
			CLS_OSIF.sPrn( "既にフォロー済みです" + '\n' )
			return wRes
		
		#############################
		# 鍵アカウント
		if gVal.STR_UserAdminInfo['Protect']==True :
			CLS_OSIF.sPrn( "鍵アカウントのためフォローできません" + '\n' )
			return wRes
		
		#############################
		# ブロック or 被ブロック
		if gVal.STR_UserAdminInfo['MyBlock']==True :
			CLS_OSIF.sPrn( "ブロックしているためフォローできません" + '\n' )
			return wRes
		if gVal.STR_UserAdminInfo['Blocked']==True :
			CLS_OSIF.sPrn( "ブロックされているためフォローできません" + '\n' )
			return wRes
		
		wFLG_r_remove = False
		if gVal.STR_UserAdminInfo['DB_exist']==True :
			#############################
			# フォローしていないが、過去にフォローしたことがある
			if gVal.STR_UserAdminInfo['DB_r_myfollow']==True :
				CLS_OSIF.sPrn( "過去に一度フォローしたことがありますが、フォローしますか？" )
				wResGet = CLS_OSIF.sInp( "(y=Yes / other=No)=> " )
				if wResGet!="y" :
					return wRes
###				wFLG_r_remove = True
			
			#############################
			# 過去にリムーブされたことがある
			if gVal.STR_UserAdminInfo['DB_r_remove']==True :
				CLS_OSIF.sPrn( "過去に一度リムーブされたことがあります。フォローしますか？" )
				wResGet = CLS_OSIF.sInp( "(y=Yes / other=No)=> " )
				if wResGet!="y" :
					return wRes
				wFLG_r_remove = True
		
		#############################
		# アンフォローリストに登録されている
		if gVal.STR_UserAdminInfo['UnrList']==True and wFLG_r_remove==False :
			CLS_OSIF.sPrn( "アンフォローリストに登録しています。フォローしますか？" )
			wResGet = CLS_OSIF.sInp( "(y=Yes / other=No)=> " )
			if wResGet!="y" :
				return wRes
		
		# ※ここまででフォロー確定
		CLS_OSIF.sPrn( "フォロー処理をおこなってます。しばらくお待ちください......" )
		
		#############################
		# フォローする
		wTwitterRes = gVal.OBJ_Twitter.CreateFollow( gVal.STR_UserAdminInfo['id'] )
		if wTwitterRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(CreateFollow): " + wTwitterRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		
		#############################
		# normalリストへ追加
		if gVal.STR_UserAdminInfo['NorList']==False :
			wTwitterRes = gVal.OBJ_Twitter.AddUserList( gVal.STR_UserInfo['NorList'], gVal.STR_UserAdminInfo['id'] )
			if wTwitterRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error(AddUserList): " + wTwitterRes['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
		
		#############################
		# un_refollowリストから削除
		if gVal.STR_UserAdminInfo['UnrList']==True :
			wTwitterRes = gVal.OBJ_Twitter.RemoveUserList( gVal.STR_UserInfo['UrfList'], gVal.STR_UserAdminInfo['id'] )
			if wTwitterRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error(RemoveUserList): " + wTwitterRes['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
		
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
		# DBに記録する
		if gVal.STR_UserAdminInfo['DB_exist']==True :
			###DBに記録あり
			wQuery = "update tbl_follower_data set " + \
						"r_myfollow = True, " + \
						"rc_myfollow = True, " + \
						"rc_follower = " + str(gVal.STR_UserAdminInfo['Follower']) + ", " + \
						"lastcount = " + gVal.STR_UserAdminInfo['statuses_count'] + ", " + \
						"foldate = '" + str(wTD['TimeDate']) + "' " + \
						"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
						" and id = '" + gVal.STR_UserAdminInfo['id'] + "' ;"
			gVal.STR_TrafficInfo['dbup'] += 1
		
		else:
			###DBに記録なし
###			wFLG_r_remove = False
###			if gVal.STR_UserAdminInfo['Follower']==True :
###				wFLG_r_remove = True
			wQuery = "insert into tbl_follower_data values (" + \
						"'" + gVal.STR_UserInfo['Account'] + "'," + \
						"'" + str(wTD['TimeDate']) + "'," + \
						"True," + \
						str( wFLG_r_remove ) + "," + \
						"True," + \
						str(gVal.STR_UserAdminInfo['Follower']) + "," + \
						"'" + str(wTD['TimeDate']) + "'," + \
						"False," + \
						"False," + \
						"'" + gVal.STR_UserAdminInfo['id'] + "'," + \
						"'" + gVal.STR_UserAdminInfo['user_name'] + "'," + \
						"'" + gVal.STR_UserAdminInfo['screen_name'] + "'," + \
						gVal.STR_UserAdminInfo['statuses_count'] + "," + \
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
		# 情報反映
		gVal.STR_UserAdminInfo['DB_exist']      = True
		gVal.STR_UserAdminInfo['DB_r_myfollow'] = True
###		gVal.STR_UserAdminInfo['DB_r_remove']   = False
		gVal.STR_UserAdminInfo['DB_limited']    = False
###		gVal.STR_UserAdminInfo['Protect']       = True
		gVal.STR_UserAdminInfo['MyFollow']      = True
###		gVal.STR_UserAdminInfo['Follower']      = False
###		gVal.STR_UserAdminInfo['MyBlock']       = False
###		gVal.STR_UserAdminInfo['Blocked']       = False
		gVal.STR_UserAdminInfo['NorList']       = True
		gVal.STR_UserAdminInfo['UnrList']       = False
		
		#############################
		# 正常終了
		CLS_OSIF.sPrn( "フォローが正常終了しました" )
		wRes['Result'] = True
		return wRes



#####################################################
# リムーブ実行
#####################################################
	def __run_Remove( self, inDBClear=False ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterAdmin"
		wRes['Func']  = "__run_Remove"
		
		#############################
		# フォロー中か
		if gVal.STR_UserAdminInfo['MyFollow']!=True :
			CLS_OSIF.sPrn( "そのユーザはフォローしてません" + '\n' )
			return wRes
		
		CLS_OSIF.sPrn( "リムーブ処理をおこなってます。しばらくお待ちください......" )
		#############################
		# リムーブする
		wTwitterRes = gVal.OBJ_Twitter.RemoveFollow( gVal.STR_UserAdminInfo['id'] )
		if wTwitterRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(RemoveFollow): " + wTwitterRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		
		#############################
		# normalリストから削除
		if gVal.STR_UserAdminInfo['NorList']==True :
			wTwitterRes = gVal.OBJ_Twitter.RemoveUserList( gVal.STR_UserInfo['NorList'], gVal.STR_UserAdminInfo['id'] )
			if wTwitterRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error(RemoveUserList): " + wTwitterRes['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
		
		#############################
		# un_refollowリストに追加
		if gVal.STR_UserAdminInfo['UnrList']==False :
			wTwitterRes = gVal.OBJ_Twitter.AddUserList( gVal.STR_UserInfo['UrfList'], gVal.STR_UserAdminInfo['id'] )
			if wTwitterRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error(AddUserList): " + wTwitterRes['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
		
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
		# 関係解除= DB削除
		if inDBClear==True :
			if gVal.STR_UserAdminInfo['DB_exist']==True :
				wQuery = "delete from tbl_follower_data " + \
							"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
							" and id = '" + str(gVal.STR_UserAdminInfo['id']) + "' ;"
		
		#############################
		# DBに記録する
		else:
			if gVal.STR_UserAdminInfo['DB_exist']==True :
				###DBに記録あり
				wQuery = "update tbl_follower_data set " + \
							"rc_myfollow = False, " + \
							"rc_follower = " + str(gVal.STR_UserAdminInfo['Follower']) + ", " + \
							"lastcount = " + gVal.STR_UserAdminInfo['statuses_count'] + ", " + \
							"foldate = '" + str(wTD['TimeDate']) + "' " + \
							"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
							" and id = '" + gVal.STR_UserAdminInfo['id'] + "' ;"
				gVal.STR_TrafficInfo['dbup'] += 1
			
			else:
				###DBに記録なし
###				wFLG_r_remove = False
###				if gVal.STR_UserAdminInfo['Follower']==True :
###					wFLG_r_remove = True
				wQuery = "insert into tbl_follower_data values (" + \
							"'" + gVal.STR_UserInfo['Account'] + "'," + \
							"'" + str(wTD['TimeDate']) + "'," + \
							"False," + \
							"False," + \
							"False," + \
							str(gVal.STR_UserAdminInfo['Follower']) + "," + \
							"'" + str(wTD['TimeDate']) + "'," + \
							"False," + \
							"False," + \
							"'" + gVal.STR_UserAdminInfo['id'] + "'," + \
							"'" + gVal.STR_UserAdminInfo['user_name'] + "'," + \
							"'" + gVal.STR_UserAdminInfo['screen_name'] + "'," + \
							gVal.STR_UserAdminInfo['statuses_count'] + "," + \
							"'" + str(wTD['TimeDate']) + "'," + \
							"''," + \
							"''," + \
							"'1900-01-01 00:00:00'," + \
							"0, 0, 0," + \
							"''," + \
							"'1900-01-01 00:00:00' " + \
							") ;"
###							str( wFLG_r_remove ) + "," + \
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
		# 情報反映
		if inDBClear==True :
			gVal.STR_UserAdminInfo['DB_exist']      = False
			gVal.STR_UserAdminInfo['DB_r_myfollow'] = False
			gVal.STR_UserAdminInfo['DB_r_remove']   = False
			gVal.STR_UserAdminInfo['DB_limited']    = False
		else:
###			gVal.STR_UserAdminInfo['DB_exist']      = False
###			gVal.STR_UserAdminInfo['DB_r_myfollow'] = False
###			gVal.STR_UserAdminInfo['DB_r_remove']   = True
			gVal.STR_UserAdminInfo['DB_limited']    = False
		
###		gVal.STR_UserAdminInfo['Protect']       = True
		gVal.STR_UserAdminInfo['MyFollow']      = False
###		gVal.STR_UserAdminInfo['Follower']      = False
###		gVal.STR_UserAdminInfo['MyBlock']       = False
###		gVal.STR_UserAdminInfo['Blocked']       = False
		gVal.STR_UserAdminInfo['NorList']       = False
		gVal.STR_UserAdminInfo['UnrList']       = True
		
		#############################
		# 正常終了
		CLS_OSIF.sPrn( "リムーブが正常終了しました" )
		wRes['Result'] = True
		return wRes



#####################################################
# ブラウザ表示
#####################################################
	def __view_Profile(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterAdmin"
		wRes['Func']  = "__view_Profile"
		
		#############################
		# ブラウザ表示
		wURL = "https://twitter.com/" + gVal.STR_UserAdminInfo['screen_name']
		CLS_HTMLIF.sOpenURL( wURL )
		
		#############################
		# 正常終了
		wRes['Result'] = True
		return wRes



#####################################################
# ユーザ情報取得
#####################################################
	def GetUserInfo( self, inScreenName ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterAdmin"
		wRes['Func']  = "GetUserInfo"
		
		#############################
		# 取得した情報の入れ場所確保
		wRelation = {
				"id"		: -1,
				"user_name"	: None,
				"statuses_count" : -1,
				
				"DB_r_myfollow"	: False,
				"DB_r_remove"	: False,
				"DB_limited"	: False,
				"DB_favo_date"	: None,
				"DB_favo_cnt"	: 0,
				"DB_favo_r_date"	: None,
				"DB_favo_r_cnt"		: 0,
				"DB_exist"		: False,
				
				"Protect"	: False,
				"MyFollow"	: False,
				"Follower"	: False,
				
				"MyBlock"	: False,
				"Blocked"	: False,
				
				"NorList"	: False,
				"UnrList"	: False
			}
		
		#############################
		# DBのフォロワー一覧取得
		wQuery = "select * from tbl_follower_data where " + \
					"screen_name = '" + inScreenName + "'" + \
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
		# DB情報を取得
		if len(wARR_RateFollowers)==1 :
			wRelation['DB_r_myfollow'] = wARR_RateFollowers[0]['r_myfollow']
			wRelation['DB_r_remove']   = wARR_RateFollowers[0]['r_remove']
			wRelation['DB_limited']    = wARR_RateFollowers[0]['limited']
			
			if wARR_RateFollowers[0]['favoid']!=None :
				wRelation['DB_favo_date']    = wARR_RateFollowers[0]['favodate']
				wRelation['DB_favo_cnt']     = wARR_RateFollowers[0]['favo_cnt']
			else:
				wRelation['DB_favo_date']    = None
				wRelation['DB_favo_cnt']     = 0
			
			if wARR_RateFollowers[0]['favo_r_id']!=None :
				wRelation['DB_favo_r_date']  = wARR_RateFollowers[0]['favo_r_date']
				wRelation['DB_favo_r_cnt']   = wARR_RateFollowers[0]['favo_r_cnt']
			else:
				wRelation['DB_favo_r_date']  = None
				wRelation['DB_favo_r_cnt']   = 0
			
			wRelation['DB_exist']      = True
		else :
			wRelation['DB_r_myfollow'] = False
			wRelation['DB_r_remove']   = False
			wRelation['DB_limited']    = False
			wRelation['DB_favo_date']    = None
			wRelation['DB_favo_cnt']     = 0
			wRelation['DB_favo_r_date']  = None
			wRelation['DB_favo_r_cnt']   = 0
			wRelation['DB_exist']      = False
		
		#############################
		# Twitterからユーザ情報を取得する
###		wUserinfoRes = gVal.OBJ_Twitter.GetUserinfo( wID )
		wUserinfoRes = gVal.OBJ_Twitter.GetUserinfo( inScreenName=inScreenName )
		if wUserinfoRes['Result']!=True :
			### 404エラーか
			if CLS_OSIF.sRe_Search( "404", wUserinfoRes['Reason'] )!=False :
				### ユーザが存在しない
				wRes['Responce'] = False
				wRes['Result'] = True
				return wRes
			
			wRes['Reason'] = "Twitter API Error(GetUserinfo): " + wUserinfoRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		wRelation['Protect'] = wUserinfoRes['Responce']['protected']
		wID = str( wUserinfoRes['Responce']['id'] )
		wRelation['id']        = wID
		wRelation['user_name'] = str( wUserinfoRes['Responce']['name'] )
		wRelation['statuses_count'] = str(wUserinfoRes['Responce']['statuses_count'])
		
		### Twitterからフォロー関係を取得する
		wUserinfoRes = gVal.OBJ_Twitter.GetFollowInfo( gVal.STR_UserInfo['id'], wID )
		if wUserinfoRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetUserinfo): " + wUserinfoRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		wRelation['MyFollow'] = wUserinfoRes['Responce']['relationship']['source']['following']
		wRelation['Follower'] = wUserinfoRes['Responce']['relationship']['source']['followed_by']
		wRelation['MyBlock']  = wUserinfoRes['Responce']['relationship']['source']['blocking']
		wRelation['Blocked']  = wUserinfoRes['Responce']['relationship']['source']['blocked_by']
		
		#############################
		# normalの登録状態を確認
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
		wFLG_Detect = False
		for wROW in wListsRes['Responce'] :
			if str(wROW['id'])==wID :
				wFLG_Detect = True
				break
		wRelation['NorList'] = wFLG_Detect
		
		#############################
		# un_refollowlの登録状態を確認
		wListsRes = gVal.OBJ_Twitter.GetListMember( gVal.STR_UserInfo['UrfList'] )
		if wListsRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetListMember:UrfList): " + wListsRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		wFLG_Detect = False
		for wROW in wListsRes['Responce'] :
			if str(wROW['id'])==wID :
				wFLG_Detect = True
				break
		wRelation['UnrList'] = wFLG_Detect
		
		#############################
		# 正常
		wRes['Responce'] = wRelation
		wRes['Result'] = True
		return wRes



#####################################################
# 荒らしユーザ管理
#####################################################
	def ArashiUser(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterAdmin"
		wRes['Func']  = "ArashiUser"
		
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
		# 除外Twitter ID確認
		if len( self.OBJ_Parent.ARR_newExcUser )==0 :
			##キャンセル
			CLS_OSIF.sPrn( "学習不足のため実行できません。監視情報取得、ツイート検索などを実行してください。" )
			wRes['Result'] = True
			return wRes
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " 荒らしユーザ設定" + '\n'
		wStr = wStr + "--------------------" + '\n'
		
		wStr = wStr + "荒らしユーザの設定変更をします。" + '\n'
		wStr = wStr + "変更をおこなうTwitter ID(@なし)を入力してください。" + '\n'
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 実行の確認
		wTwitterID = CLS_OSIF.sInp( "Twitter ID(@なし)？(\\q=中止)=> " )
		if wTwitterID=="\\q" :
			##キャンセル
			CLS_OSIF.sPrn( "処理を中止しました。" )
			wRes['Result'] = True
			return wRes
		
		#############################
		# 処理中表示
		CLS_OSIF.sPrn( "確認しています。しばらくお待ちください......" )
		
		#############################
		# IDがDBに存在するか
		wFLG_UserFind = False
		if wTwitterID in self.OBJ_Parent.ARR_newExcUser :
			wFLG_UserFind = True
		else:
			#############################
			# DBに存在しない場合、Twitter IDが実在するか
			wUserinfoRes = gVal.OBJ_Twitter.GetUserinfo( inScreenName=wTwitterID )
			if wUserinfoRes['Result']!=True :
				CLS_OSIF.sPrn( "指定のIDはTwitter上で確認できないか、凍結されています。" )
				wRes['Result'] = True
				return wRes
				## IDが存在しない場合 :404
				## IDが凍結されている場合:403
		
		#############################
		# IDがDBに存在しない場合
		#   事前に荒らし設定しておくか
		if wFLG_UserFind==False :
			wStr = "データベースに登録されていないユーザです。事前に荒らし設定しておくこともできます。" + '\n'
			wStr = wStr + '\n'
			wStr = wStr + "理由の指定＞" + '\n'
			wKeylist = list( self.OBJ_Parent.DEF_STR_ARASHI_REASON_ID.keys() )
			for wReasonID in self.OBJ_Parent.DEF_STR_ARASHI_REASON_ID :
				if wReasonID==0 :
					continue
				wStr = wStr + str(wReasonID) + " : " + self.OBJ_Parent.DEF_STR_ARASHI_REASON_ID[wReasonID] + '\n'
			
			CLS_OSIF.sPrn( wStr )
			wSelect = CLS_OSIF.sInp( "有効な荒らし理由を指定？(一覧にない理由=キャンセル)=> " )
			wResInt = CLS_OSIF.sChgInt( wSelect )
			if wResInt['Result']!=True :
				CLS_OSIF.sPrn( "設定を中止します。" )
				wRes['Result'] = True
				return True
			wSelect = wResInt['Value']
			if ( wSelect not in self.OBJ_Parent.DEF_STR_ARASHI_REASON_ID ) or \
			   ( wSelect==0 ) :
				CLS_OSIF.sPrn( "設定を中止します。" )
				wRes['Result'] = True
				return True
			
			###リストに追加する(DBの保存は)
			self.OBJ_Parent.SetnewExcUser(
					inID         = wUserinfoRes['Responce']['id'],
					inScreenName = wTwitterID,
					inCount      = gVal.DEF_STR_TLNUM['excTwitterID'],
					inLastDate   = wTD['TimeDate'],
					inArashi     = True,
					inReasonID   = wSelect
				)
		
		#############################
		# IDがDBに存在する場合
		# 荒らし設定の変更
		else:
			#############################
			# 選択肢の表示と入力
			if self.OBJ_Parent.ARR_newExcUser[wTwitterID]['arashi']==True :
				###荒らし設定の場合
				wCHR_Reason = self.OBJ_Parent.DEF_STR_ARASHI_REASON_ID[self.OBJ_Parent.ARR_newExcUser[wTwitterID]['reason_id']]
				wStr = "指定のIDは荒らし設定されているユーザです。" + '\n'
				wStr = wStr + "  Screen Name = " + self.OBJ_Parent.ARR_newExcUser[wTwitterID]['screen_name'] + '\n'
				wStr = wStr + "  Last date   = " + str(self.OBJ_Parent.ARR_newExcUser[wTwitterID]['lastdate']) + '\n'
				wStr = wStr + "  荒らし回数  = " + str(self.OBJ_Parent.ARR_newExcUser[wTwitterID]['count']) + '\n'
				wStr = wStr + "  理由        = " + wCHR_Reason + '\n'
				wStr = wStr + '\n'
				wStr = wStr + "理由の指定＞" + '\n'
				wKeylist = list( self.OBJ_Parent.DEF_STR_ARASHI_REASON_ID.keys() )
				for wReasonID in self.OBJ_Parent.DEF_STR_ARASHI_REASON_ID :
					if wReasonID==0 :
						continue
					wStr = wStr + str(wReasonID) + " : " + self.OBJ_Parent.DEF_STR_ARASHI_REASON_ID[wReasonID] + '\n'
				wStr = wStr + "0  : 荒らし解除" + '\n'
			
			else:
				###荒らしでない場合
				wStr = "指定のIDは荒らし設定されていません。" + '\n'
				wStr = wStr + '\n'
				wStr = wStr + "理由の指定＞" + '\n'
				wKeylist = list( self.OBJ_Parent.DEF_STR_ARASHI_REASON_ID.keys() )
				for wReasonID in self.OBJ_Parent.DEF_STR_ARASHI_REASON_ID :
					if wReasonID==0 :
						continue
					wStr = wStr + str(wReasonID) + " : " + self.OBJ_Parent.DEF_STR_ARASHI_REASON_ID[wReasonID] + '\n'
			
			CLS_OSIF.sPrn( wStr )
			wSelect = CLS_OSIF.sInp( "有効な荒らし理由を指定？(一覧にない理由=キャンセル)=> " )
			wResInt = CLS_OSIF.sChgInt( wSelect )
			if wResInt['Result']!=True :
				CLS_OSIF.sPrn( "設定を中止します。" )
				wRes['Result'] = True
				return True
			wSelect = wResInt['Value']
			if wSelect not in self.OBJ_Parent.DEF_STR_ARASHI_REASON_ID :
				CLS_OSIF.sPrn( "設定を中止します。" )
				wRes['Result'] = True
				return True
			
			#############################
			# 荒らしの場合
			if self.OBJ_Parent.ARR_newExcUser[wTwitterID]['arashi']==True :
				#############################
				# 0 = 解除の場合
				if wSelect==0 :
					self.OBJ_Parent.ARR_newExcUser[wTwitterID]['lastdate'] = wTD['TimeDate']
					self.OBJ_Parent.ARR_newExcUser[wTwitterID]['count']     = 0
					self.OBJ_Parent.ARR_newExcUser[wTwitterID]['reason_id'] = 0
					self.OBJ_Parent.ARR_newExcUser[wTwitterID]['arashi'] = False
				#############################
				# 設定変更の場合
				else :
					if self.OBJ_Parent.ARR_newExcUser[wTwitterID]['reason_id']==wSelect :
						CLS_OSIF.sPrn( "同じ理由を設定できません。" )
						wRes['Result'] = True
						return True
					
					self.OBJ_Parent.ARR_newExcUser[wTwitterID]['lastdate'] = wTD['TimeDate']
					self.OBJ_Parent.ARR_newExcUser[wTwitterID]['reason_id'] = wSelect
			
			#############################
			# 荒らしではない→荒らし設定
			else:
				if wSelect==0 :
					CLS_OSIF.sPrn( "設定を中止します。" )
					wRes['Result'] = True
					return True
				
				self.OBJ_Parent.ARR_newExcUser[wTwitterID]['lastdate'] = wTD['TimeDate']
				self.OBJ_Parent.ARR_newExcUser[wTwitterID]['count']     = gVal.DEF_STR_TLNUM['excTwitterID']	#最低値を設定
				self.OBJ_Parent.ARR_newExcUser[wTwitterID]['reason_id'] = wSelect
				self.OBJ_Parent.ARR_newExcUser[wTwitterID]['arashi'] = True
		
		#############################
		# DBに保存する
		wResSub = self.OBJ_Parent.SaveExcTwitterID()
		if wResSub['Result']!=True :
			wRes['Reason'] = "SetExcTwitterID failed: reason" + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		#############################
		# 正常終了
		CLS_OSIF.sPrn( '\n' + "設定変更しました。" )
		wRes['Result'] = True
		return wRes



