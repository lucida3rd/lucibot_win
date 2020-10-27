#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : Twitter監視 管理系
# 
# ::Update= 2020/10/27
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
			if wARR_RateFollowers[wIndex]['user_name']==wTwitterID :
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



