#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL : https://twitter.com/lucida3hai
# ::Class       : 環境設定変更
# 
# ::Update= 2020/10/3
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   __init__(self):
#
# Class Function(static):
#   SetTwitterAPI( self, inTwitterID, inSave=True ):
#   SetTwitterList( self, inTwitterID, inSave=True ):
#
#####################################################

from osif import CLS_OSIF
from gval import gVal
#####################################################
class CLS_Config() :
#####################################################

#####################################################
# Init
#####################################################
	def __init__(self):
		return



#####################################################
# Twitter API設定
#####################################################
	def SetTwitterAPI( self, inTwitterID, inSave=True ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		wRes['Responce'] = {}
		wRes['Responce'].update({
			"APIkey"    : "(none)",
			"APIsecret" : "(none)",
			"ACCtoken"  : "(none)",
			"ACCsecret" : "(none)"
		})
		
		CLS_OSIF.sPrn( "Twitter APIキーの設定をおこないます。" )
		CLS_OSIF.sPrn( "---------------------------------------" )
		while True :
			###初期化
			wRes['Responce']['APIkey']    = "(none)"
			wRes['Responce']['APIsecret'] = "(none)"
			wRes['Responce']['ACCtoken']  = "(none)"
			wRes['Responce']['ACCsecret'] = "(none)"
			
			#############################
			# 入力
			wStr = "Twitter Devで取得した API key を入力してください。"
			CLS_OSIF.sPrn( wStr )
			wKey = CLS_OSIF.sGpp( "API key？=> " )
			if wKey=="" :
				CLS_OSIF.sPrn( "キーが未入力です" + '\n' )
				continue
			wRes['Responce']['APIkey'] = wKey
			
			wStr = "Twitter Devで取得した API secret key を入力してください。"
			CLS_OSIF.sPrn( wStr )
			wKey = CLS_OSIF.sGpp( "API secret key？=> " )
			if wKey=="" :
				CLS_OSIF.sPrn( "キーが未入力です" + '\n' )
				continue
			wRes['Responce']['APIsecret'] = wKey
			
			wStr = "Twitter Devで取得した Access token を入力してください。"
			CLS_OSIF.sPrn( wStr )
			wKey = CLS_OSIF.sGpp( "Access token？=> " )
			if wKey=="" :
				CLS_OSIF.sPrn( "キーが未入力です" + '\n' )
				continue
			wRes['Responce']['ACCtoken'] = wKey
			
			wStr = "Twitter Devで取得した Access token secret を入力してください。"
			CLS_OSIF.sPrn( wStr )
			wKey = CLS_OSIF.sGpp( "Access token secret？=> " )
			if wKey=="" :
				CLS_OSIF.sPrn( "キーが未入力です" + '\n' )
				continue
			wRes['Responce']['ACCsecret'] = wKey
			
			###ここまでで入力は完了した
			break
		
		#############################
		# Twitterに接続
		###テスト
		wResTwitter_Create = gVal.OBJ_Twitter.Create(
					inTwitterID,
					wRes['Responce']['APIkey'],
					wRes['Responce']['APIsecret'],
					wRes['Responce']['ACCtoken'],
					wRes['Responce']['ACCsecret']
				)
		wResTwitter = gVal.OBJ_Twitter.GetTwStatus()
		if wResTwitter_Create!=True :
			wRes['Reason'] = "CLS_Config: SetTwitterAPI: Twitterの接続に失敗しました: 理由=" + wResTwitter['Reason']
			CLS_OSIF.sPrn( wRes['Reason'] )
			return wRes
		
		###結果の確認
		if wResTwitter['Init']!=True :
			wRes['Reason'] = "CLS_Config: SetTwitterAPI: Twitterが初期化できてません"
			CLS_OSIF.sPrn( wRes['Reason'] )
			return wRes
		
		wStr = "Twitterへ正常に接続しました。" + '\n'
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# セーブしなければここで完了
		if inSave==False :
			wRes['Result'] = True
			return wRes
		
		#############################
		# DBにセーブ
		wQuery = "update tbl_user_data set " + \
				"apikey = '"    + wRes['Responce']['APIkey'] + "', " + \
				"apisecret = '" + wRes['Responce']['APIsecret'] + "' " + \
				"acctoken = '"  + wRes['Responce']['ACCtoken'] + "' " + \
				"accsecret = '" + wRes['Responce']['ACCsecret'] + " " + \
				"where twitterid = '" + inTwitterID + "' ;"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_Setup: SetTwitterAPI: Run Query is failed: " + wDBRes['Reason']
			CLS_OSIF.sPrn( wRes['Reason'] )
			return wRes
		
		wStr = "データベースのユーザ " + inTwitterID + " を更新しました。" + '\n'
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# Twitterリスト設定
#####################################################
	def SetTwitterList( self, inTwitterID, inSave=True ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		wRes['Responce'] = {}
		wRes['Responce'].update({ "norlist" : "(none)", "urflist" : "(none)" })
		
		#############################
		# リスト一覧の取得
		wResTwitter = gVal.OBJ_Twitter.GetLists()
		if wResTwitter['Result']!=True :
			wRes['Reason'] = "CLS_Setup: SetTwitterList: GetLists failure reason=" + wResTwitter['Reason']
			CLS_OSIF.sPrn( wRes['Reason'] )
			return wRes
		
		if len(wResTwitter['Responce'])==0 :
			CLS_OSIF.sPrn( "設定できるTwitterリストがありません。" )
			wRes['Result'] = True
			return wRes
		
		#############################
		# リスト一覧の出力
		CLS_OSIF.sPrn( "Twitterリストの設定をおこないます。" )
		CLS_OSIF.sPrn( "--- Twitterリスト一覧 ---" )
		wKeylist = wResTwitter['Responce'].keys()
		for wKey in wKeylist :
			CLS_OSIF.sPrn( wResTwitter['Responce'][wKey]['name'] )
		CLS_OSIF.sPrn( "-------------------------" )
		
		#############################
		# 入力
		while True :
			#############################
			# normalリストの選択
			wStr = "normalリストに設定するリスト名を入力してください。(=自動リムーブ監視対象のユーザ)"
			CLS_OSIF.sPrn( wStr )
			wSelectNormal = CLS_OSIF.sInp( "normal list name ?(name or \\q=Cancel)=> " )
			if wSelectNormal=="\\q" :
				##キャンセル
				CLS_OSIF.sPrn( "入力がキャンセルされました" + '\n' )
				wRes['Result'] = True
				return wRes
			###名前があるかチェック
			wKeylist = wResTwitter['Responce'].keys()
			wFLG_C_Normal = False
			for wKey in wKeylist :
				if wResTwitter['Responce'][wKey]['name']==wSelectNormal :
					wFLG_C_Normal = True
					break
			if wFLG_C_Normal==False :
				CLS_OSIF.sPrn( "リストにない名前です" )
				continue
			
			#############################
			# un_refollowリストの選択
			wStr = "un_refollowリストに設定するリスト名を入力してください。(=自動リムーブ済みユーザ)"
			CLS_OSIF.sPrn( wStr )
			wSelectUnrefollow = CLS_OSIF.sInp( "un_refollow list name ?(name or \\q=Cancel)=> " )
			if wSelectUnrefollow=="\\q" :
				##キャンセル
				CLS_OSIF.sPrn( "入力がキャンセルされました" + '\n' )
				wRes['Result'] = True
				return wRes
			###名前があるかチェック
			wKeylist = wResTwitter['Responce'].keys()
			wFLG_C_Unrefollow = False
			for wKey in wKeylist :
				if wResTwitter['Responce'][wKey]['name']==wSelectUnrefollow :
					wFLG_C_Unrefollow = True
					break
			if wFLG_C_Unrefollow==False :
				CLS_OSIF.sPrn( "リストにない名前です" )
				continue
			
			#############################
			# 最終チェック
			if wSelectNormal==wSelectUnrefollow :
				CLS_OSIF.sPrn( "同じリストは登録できません" )
				continue
			
			if wFLG_C_Normal==True and wFLG_C_Unrefollow==True :
				break	#2個選んだら終わる
		
		#############################
		# 完了
		wRes['Responce']['norlist'] = wSelectNormal
		wRes['Responce']['urflist'] = wSelectUnrefollow
		
		#############################
		# セーブしなければここで完了
		if inSave==False :
			wRes['Result'] = True
			return wRes
		
		#############################
		# DBにセーブ
		wQuery = "update tbl_user_data set " + \
				"norlist = '" + wRes['Responce']['norlist'] + "', " + \
				"urflist = '" + wRes['Responce']['urflist'] + "' " + \
				"where twitterid = '" + inTwitterID + "' ;"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_Setup: Setup: Run Query is failed: " + wDBRes['Reason']
			CLS_OSIF.sPrn( wRes['Reason'] )
			return wRes
		
		wStr = "データベースのユーザ " + inTwitterID + " を更新しました。" + '\n'
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



