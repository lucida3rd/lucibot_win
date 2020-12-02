#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : Twitter監視 管理系
# 
# ::Update= 2020/11/2
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
			CLS_OSIF.sPrn( "処理を中止しました。" )
			wRes['Result'] = True
			return wRes
		
		#############################
		# 処理中表示
		CLS_OSIF.sPrn( "確認しています。しばらくお待ちください......" )
		
		#############################
		# Twitterからユーザ情報を取得する
		wUserinfoRes = gVal.OBJ_Twitter.GetUserinfo( inScreenName=wTwitterID )
		if wUserinfoRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetUserinfo): " + wUserinfoRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		













#####################################################
# ユーザ復活
#####################################################
	def UserRevival(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterAdmin"
		wRes['Func']  = "UserRevival"
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " ユーザ復活" + '\n'
		wStr = wStr + "--------------------" + '\n'
		
		wStr = wStr + "自動リムーブ済みのユーザのフォローを復活します。" + '\n'
		wStr = wStr + "復活するTwitter ID(@なし)を入力してください。" + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "  条件：" + '\n'
		wStr = wStr + "    ・過去フォローしていたが、既にリムーブ済み" + '\n'
		wStr = wStr + "    ・現在フォローされている(フォロワー)こと" + '\n'
		wStr = wStr + "    ・un_refollowリストに入っている" + '\n'
		wStr = wStr + "    ・鍵アカウントでなないこと" + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "中止する場合は \q を入力してください" + '\n'
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
		CLS_OSIF.sPrn( "復活できるか確認しています。しばらくお待ちください......" )
		
		#############################
		# DBのフォロワー一覧取得
		#   ※1度でもフォロー・リムーブした、現在フォロワー、自動リムーブ対象ではない、リムーブ済み
		wQuery = "select * from tbl_follower_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "' and " + \
					"r_myfollow = True and " + \
					"r_remove = True and " + \
					"rc_follower = True and " + \
					"limited = False and " + \
					"removed = True " + \
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
		# 検索
		wKeylist = wARR_RateFollowers.keys()
		wFLG_Detect = False
		for wIndex in wKeylist :
			if wARR_RateFollowers[wIndex]['screen_name']==wTwitterID :
				wID = wARR_RateFollowers[wIndex]['id']
				wFLG_Detect = True
				break
		if wFLG_Detect!=True :
			### DBにないユーザ
			CLS_OSIF.sPrn( "復活できないユーザでした。" )
			wRes['Result'] = True
			return wRes
		
		#############################
		# normal、un_refollowlの登録状態を確認
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
		if wFLG_Detect==True :
			CLS_OSIF.sPrn( "nornalリストから外してください。" )
			wRes['Result'] = True
			return wRes
		
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
		if wFLG_Detect==False :
			CLS_OSIF.sPrn( "un_refollowリストに未登録のため復活できません。" )
			wRes['Result'] = True
			return wRes
		
		#############################
		# 相手との関係性情報(Twitter上)
		wRelation = {
				"Protect"	: False,
				"MyFollow"	: False,
				"Follower"	: False
			}
		
		### Twitterからユーザ情報を取得する
		wUserinfoRes = gVal.OBJ_Twitter.GetUserinfo( wID )
		if wUserinfoRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetUserinfo): " + wUserinfoRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		wRelation['Protect'] = wUserinfoRes['Responce']['protected']
		
		### Twitterからフォロー関係を取得する
		wUserinfoRes = gVal.OBJ_Twitter.GetFollowInfo( gVal.STR_UserInfo['id'], wID )
		if wUserinfoRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetUserinfo): " + wUserinfoRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		wRelation['MyFollow'] = wUserinfoRes['Responce']['relationship']['source']['following']
		wRelation['Follower'] = wUserinfoRes['Responce']['relationship']['source']['followed_by']
		
		#############################
		# Twitter状態での判定
		if wRelation['Protect']==True :
			CLS_OSIF.sPrn( "対象が鍵アカウントのため復活できません。" )
			wRes['Result'] = True
			return wRes
		
		if wRelation['MyFollow']==True :
			###実は既にフォローしていた
			
			###リムーブフラグを落としておく
			wQuery = "update tbl_follower_data set " + \
						"r_remove = False, " + \
						"removed = False " + \
						"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
						" and id = '" + str( wID ) + "' ;"
			
			wResDB = gVal.OBJ_DB.RunQuery( wQuery )
			wResDB = gVal.OBJ_DB.GetQueryStat()
			if wResDB['Result']!=True :
				##失敗
				wRes['Reason'] = "Run Query is failed(2): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			
			CLS_OSIF.sPrn( "既にフォローしています。" )
			wRes['Result'] = True
			return wRes
		
		if wRelation['Follower']==False :
			###実はフォロワーではなかった
			
			###前回フォロワーフラグを落としておく
			wQuery = "update tbl_follower_data set " + \
						"rc_follower = False " + \
						"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
						" and id = '" + str( wID ) + "' ;"
			
			wResDB = gVal.OBJ_DB.RunQuery( wQuery )
			wResDB = gVal.OBJ_DB.GetQueryStat()
			if wResDB['Result']!=True :
				##失敗
				wRes['Reason'] = "Run Query is failed(3): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			
			CLS_OSIF.sPrn( "フォローされていないため復活できません。" )
			wRes['Result'] = True
			return wRes
		
		# ※ここまでで復活可能
		CLS_OSIF.sPrn( '\n' + "復活処理をしています。しばらくお待ちください......" )
		
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
		# フォローする
		wTwitterRes = gVal.OBJ_Twitter.CreateFollow( wID )
		if wTwitterRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(CreateFollow): " + wTwitterRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		CLS_OSIF.sSleep(5)
		
		#############################
		# normalリストへ追加
		wTwitterRes = gVal.OBJ_Twitter.AddUserList( gVal.STR_UserInfo['NorList'], wID )
		if wTwitterRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(AddUserList): " + wTwitterRes['Reason']
			return wRes
		CLS_OSIF.sSleep(5)
		
		#############################
		# un_refollowリストから削除する
		wTwitterRes = gVal.OBJ_Twitter.RemoveUserList( gVal.STR_UserInfo['UrfList'], wID )
		if wTwitterRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(RemoveUserList): " + wTwitterRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		
		#############################
		# DBに記録する
		wQuery = "update tbl_follower_data set " + \
					"r_remove = False, " + \
					"foldate = '" + str(wTD['TimeDate']) + "', " + \
					"removed = False " + \
					"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					" and id = '" + str( wID ) + "' ;"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(4): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		
		#############################
		# 正常終了
		CLS_OSIF.sPrn( '\n' + "正常にフォロー関係を復活しました。念のためTwitterの状態を確認してください。" )
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



