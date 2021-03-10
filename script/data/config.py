#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL : https://twitter.com/lucida3hai
# ::Class       : 環境設定変更
# 
# ::Update= 2021/3/11
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
	def SetTwitterAPI( self, inTwitterID, inConf=False, inSave=False ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Config"
		wRes['Func']  = "SetTwitterAPI"
		
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
			# 実行の確認
			if inConf==True :
				wSelect = CLS_OSIF.sInp( "キャンセルしますか？(y)=> " )
				if wSelect=="y" :
					# 完了
					wRes['Result'] = True
					return wRes
			
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
			wRes['Reason'] = "Twitterの接続に失敗しました: reason=" + wResTwitter['Reason']
			return wRes
		
		###結果の確認
		if wResTwitter['Init']!=True :
			wRes['Reason'] = "Twitterが初期化できてません"
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
				"apisecret = '" + wRes['Responce']['APIsecret'] + "', " + \
				"acctoken = '"  + wRes['Responce']['ACCtoken'] + "', " + \
				"accsecret = '" + wRes['Responce']['ACCsecret'] + "' " + \
				"where twitterid = '" + inTwitterID + "' ;"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed: RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
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
	def SetTwitterList( self, inTwitterID, inConf=False, inSave=False ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Config"
		wRes['Func']  = "SetTwitterList"
		
		wRes['Responce'] = {}
###		wRes['Responce'].update({ "norlist" : "(none)", "urflist" : "(none)" })
		wRes['Responce'].update({ "norlist" : "(none)", "urflist" : "(none)", "favolist" : "(none)" })
		
		#############################
		# リスト一覧の取得
		wResTwitter = gVal.OBJ_Twitter.GetLists()
		if wResTwitter['Result']!=True :
			wRes['Reason'] = "GetLists failure reason=" + wResTwitter['Reason']
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
			# 実行の確認
			if inConf==True :
				wSelect = CLS_OSIF.sInp( "キャンセルしますか？(y)=> " )
				if wSelect=="y" :
					# 完了
					wRes['Result'] = True
					return wRes
			
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
			# favolistリストの選択
			wStr = "favolistリストに設定するリスト名を入力してください。(=指定いいね対象ユーザ)"
			CLS_OSIF.sPrn( wStr )
			wSelectFavolist = CLS_OSIF.sInp( "favolist list name ?(name or \\q=Cancel)=> " )
			if wSelectFavolist=="\\q" :
				##キャンセル
				CLS_OSIF.sPrn( "入力がキャンセルされました" + '\n' )
				wRes['Result'] = True
				return wRes
			###名前があるかチェック
			wKeylist = wResTwitter['Responce'].keys()
			wFLG_C_Favolist = False
			for wKey in wKeylist :
				if wResTwitter['Responce'][wKey]['name']==wSelectFavolist :
					wFLG_C_Favolist = True
					break
			if wFLG_C_Favolist==False :
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
		wRes['Responce']['favolist'] = wSelectFavolist
		
		#############################
		# セーブしなければここで完了
		if inSave==False :
			wRes['Result'] = True
			return wRes
		
		#############################
		# DBにセーブ
		wQuery = "update tbl_user_data set " + \
				"norlist = '" + wRes['Responce']['norlist'] + "', " + \
				"urflist = '" + wRes['Responce']['urflist'] + "'," + \
				"favolist = '" + wRes['Responce']['favolist'] + "' " + \
				"where twitterid = '" + inTwitterID + "' ;"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed: RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		wStr = "データベースのユーザ " + inTwitterID + " を更新しました。" + '\n'
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# 検索モード 読み込み
#####################################################
	def GetSearchMode(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Config"
		wRes['Func']  = "GetSearchMode"
		
		#############################
		# DBの検索モード取得
###		wQuery = "select * from tbl_keyword_data where " + \
###					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
###					" and choice = True ;"
		wQuery = "select * from tbl_keyword_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "' " + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		#############################
		# 辞書型に整形
		wARR_RateSearchMode = {}
		gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateSearchMode )
		
		#############################
		# ローカル初期化
		gVal.STR_SearchMode = {}
		
		#############################
		# ローカルに読み込み
		# ※レコードがない場合はこっち =初期状態
		if len(wARR_RateSearchMode)==0 :
			gVal.sStruct_SearchMode()
			gVal.STR_SearchMode[0]['id'] = 0
			gVal.STR_SearchMode[0]['Update'] = True
			
			###完了
			wRes['Result'] = True
			return wRes
		
		#############################
		# ローカルに読み込み
		wIndex = 0
		wKeylist = wARR_RateSearchMode.keys()
		for wIndex in wKeylist :
			###行を挿入
			gVal.sStruct_SearchMode()
			
			gVal.STR_SearchMode[wIndex]['id'] = wARR_RateSearchMode[wIndex]['id']
			gVal.STR_SearchMode[wIndex]['Choice']  = wARR_RateSearchMode[wIndex]['choice']
			gVal.STR_SearchMode[wIndex]['Keyword'] = wARR_RateSearchMode[wIndex]['keyword']
			
			gVal.STR_SearchMode[wIndex]['IncImage'] = wARR_RateSearchMode[wIndex]['incimage']
			gVal.STR_SearchMode[wIndex]['ExcImage'] = wARR_RateSearchMode[wIndex]['excimage']
			gVal.STR_SearchMode[wIndex]['IncVideo'] = wARR_RateSearchMode[wIndex]['incvideo']
			gVal.STR_SearchMode[wIndex]['ExcVideo'] = wARR_RateSearchMode[wIndex]['excvideo']
			gVal.STR_SearchMode[wIndex]['IncLink']  = wARR_RateSearchMode[wIndex]['inclink']
			gVal.STR_SearchMode[wIndex]['ExcLink']  = wARR_RateSearchMode[wIndex]['exclink']
			
			gVal.STR_SearchMode[wIndex]['OFonly'] = wARR_RateSearchMode[wIndex]['ofonly']
			gVal.STR_SearchMode[wIndex]['JPonly'] = wARR_RateSearchMode[wIndex]['jponly']
			gVal.STR_SearchMode[wIndex]['ExcRT']    = wARR_RateSearchMode[wIndex]['excrt']
			gVal.STR_SearchMode[wIndex]['ExcSensi'] = wARR_RateSearchMode[wIndex]['excsensi']
			gVal.STR_SearchMode[wIndex]['Arashi'] = wARR_RateSearchMode[wIndex]['arashi']
			wIndex += 1
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# 検索モード 設定
#####################################################
	def SetSearchMode_All(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Config"
		wRes['Func']  = "SetSearchMode_All"
		
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "PC時間の取得に失敗しました"
			return wRes
		### wTD['TimeDate']
		
		#############################
		# 設定
		wRange = len(gVal.STR_SearchMode)
		for wIndex in range( wRange ) :
			wResSub = self.SetSearchMode( wIndex, wTD['TimeDate'] )
			if wResSub['Result']!=True :
				###失敗
				wRes['Reason'] = CLS_OSIF.sCatErr( wResSub )
				return wRes
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes

	#####################################################
	def SetSearchMode( self, inIndex, inTimeDate ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Config"
		wRes['Func']  = "SetSearchMode"
		
		wRes['Responce'] = False
		#############################
		# 更新フラグ=なし
		if gVal.STR_SearchMode[inIndex]['Update']==False :
			###完了扱いにする
			wRes['Result'] = True
			return wRes
		
		#############################
		# DBの検索モード取得
		wQuery = "select id from tbl_keyword_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					" and id = " + str( gVal.STR_SearchMode[inIndex]['id'] ) + " " + \
					";"
###					" and id = " + str(inIndex) + " " + \

		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		#############################
		# DBになければinsertする
		if len(wResDB['Responce']['Data'])==0 :
			wQuery = "insert into tbl_keyword_data values (" + \
						"'" + gVal.STR_UserInfo['Account'] + "'," + \
						"'" + str(inTimeDate) + "'," + \
						str( gVal.STR_SearchMode[inIndex]['Choice'] ) + "," + \
						str( gVal.STR_SearchMode[inIndex]['id'] ) + "," + \
						"'" + str( gVal.STR_SearchMode[inIndex]['Keyword'] ) + "'," + \
						str( gVal.STR_SearchMode[inIndex]['Count'] ) + "," + \
						str( gVal.STR_SearchMode[inIndex]['IncImage'] ) + "," + \
						str( gVal.STR_SearchMode[inIndex]['ExcImage'] ) + "," + \
						str( gVal.STR_SearchMode[inIndex]['IncVideo'] ) + "," + \
						str( gVal.STR_SearchMode[inIndex]['ExcVideo'] ) + "," + \
						str( gVal.STR_SearchMode[inIndex]['IncLink'] ) + "," + \
						str( gVal.STR_SearchMode[inIndex]['ExcLink'] ) + "," + \
						str( gVal.STR_SearchMode[inIndex]['OFonly'] ) + "," + \
						str( gVal.STR_SearchMode[inIndex]['JPonly'] ) + "," + \
						str( gVal.STR_SearchMode[inIndex]['ExcRT'] ) + "," + \
						str( gVal.STR_SearchMode[inIndex]['ExcSensi'] ) + "," + \
						str( gVal.STR_SearchMode[inIndex]['Arashi'] ) + \
						") ;"
###		
###						str( inIndex ) + "," + \
		
		#############################
		# DBにあれば更新する
		else:
			wQuery = "update tbl_keyword_data set " + \
					"regdate = '" + str(inTimeDate) + "', " + \
					"choice = " + str( gVal.STR_SearchMode[inIndex]['Choice'] ) + ", " + \
					"keyword = '" + str( gVal.STR_SearchMode[inIndex]['Keyword'] ) + "', " + \
					"count = '" + str( gVal.STR_SearchMode[inIndex]['Count'] ) + "', " + \
					"incimage = " + str( gVal.STR_SearchMode[inIndex]['IncImage'] ) + ", " + \
					"excimage = " + str( gVal.STR_SearchMode[inIndex]['ExcImage'] ) + ", " + \
					"incvideo = " + str( gVal.STR_SearchMode[inIndex]['IncVideo'] ) + ", " + \
					"excvideo = " + str( gVal.STR_SearchMode[inIndex]['ExcVideo'] ) + ", " + \
					"inclink = " + str( gVal.STR_SearchMode[inIndex]['IncLink'] ) + ", " + \
					"exclink = " + str( gVal.STR_SearchMode[inIndex]['ExcLink'] ) + ", " + \
					"ofonly = " + str( gVal.STR_SearchMode[inIndex]['OFonly'] ) + ", " + \
					"jponly = " + str( gVal.STR_SearchMode[inIndex]['JPonly'] ) + ", " + \
					"excrt = " + str( gVal.STR_SearchMode[inIndex]['ExcRT'] ) + ", " + \
					"excsensi = " + str( gVal.STR_SearchMode[inIndex]['ExcSensi'] ) + ", " + \
					"arashi = " + str( gVal.STR_SearchMode[inIndex]['Arashi'] ) + " " + \
					"where twitterid = '" + gVal.STR_UserInfo['Account'] + "' " + \
					" and id = " + str( gVal.STR_SearchMode[inIndex]['id'] ) + " ;"
###		
###					" and id = " + str(inIndex) + " ;"
		
		#############################
		# Query実行
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(2): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		#############################
		# 更新フラグ落とす
		gVal.STR_SearchMode[inIndex]['Update'] = False
		
		#############################
		# 完了
		wRes['Responce'] = True
		wRes['Result']   = True
		return wRes



#####################################################
# 除外ユーザ名 読み込み
#####################################################
	def GetExcUserName(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Config"
		wRes['Func']  = "GetExcUserName"
		
		#############################
		# データベースから除外ユーザ名を取得
		wQuery = "select word from tbl_exc_username " + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed: RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		### グローバルに取り込み
		gVal.STR_ExcUserName = []
		gVal.OBJ_DB.ChgList( wResDB['Responce']['Data'], outList=gVal.STR_ExcUserName )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# 除外文字 読み込み
#####################################################
	def GetExcWord(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Config"
		wRes['Func']  = "GetExcWord"
		
		#############################
		# データベースから除外ユーザ名を取得
		wQuery = "select word from tbl_exc_word " + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed: RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		### グローバルに取り込み
		gVal.STR_ExcWord = []
		gVal.OBJ_DB.ChgList( wResDB['Responce']['Data'], outList=gVal.STR_ExcWord )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# 除外Twitter ID 読み込み
#####################################################
	def GetExcTwitterID(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Config"
		wRes['Func']  = "GetExcTwitterID"
		
		#############################
		# データベースから除外Twitter IDを取得
		wQuery = "select * from tbl_exc_twitterid " + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed: RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		### グローバルに取り込み
		gVal.STR_ExcTwitterID_Info = {}
		gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=gVal.STR_ExcTwitterID_Info )
		
		### 除外リストを作成する
		gVal.STR_ExcTwitterID = []		#除外Twitter ID
		gVal.STR_RateExcTwitterID = []	#除外Twitter ID(処理前DB)
		wKeylist = gVal.STR_ExcTwitterID_Info.keys()
		for wIndex in wKeylist :
###			gVal.STR_RateExcTwitterID.append( gVal.STR_ExcTwitterID_Info[wIndex]['screen_name'] )
			gVal.STR_RateExcTwitterID.append( gVal.STR_ExcTwitterID_Info[wIndex]['id'] )
			
			if gVal.STR_ExcTwitterID_Info[wIndex]['arashi']==True :
###				gVal.STR_ExcTwitterID.append( gVal.STR_ExcTwitterID_Info[wIndex]['screen_name'] )
				gVal.STR_ExcTwitterID.append( gVal.STR_ExcTwitterID_Info[wIndex]['id'] )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# 除外Twitter ID 設定
#####################################################
	def SetExcTwitterID( self, inNewList ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Config"
		wRes['Func']  = "SetExcTwitterID"
		
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "PC時間の取得に失敗しました"
			return wRes
		### wTD['TimeDate']
		
		wKeylist = list ( inNewList.keys() )
		for wIndex in wKeylist :
			#############################
			# DBになければinsertする
			if inNewList[wIndex]['id'] not in gVal.STR_RateExcTwitterID :
				wQuery = "insert into tbl_exc_twitterid values (" + \
							"'" + str(wTD['TimeDate']) + "'," + \
							"'" + str( inNewList[wIndex]['id'] ) + "'," + \
							"'" + str( inNewList[wIndex]['screen_name'] ) + "'," + \
							str( inNewList[wIndex]['count'] ) + "," + \
							"'" + str( inNewList[wIndex]['lastdate'] ) + "'," + \
							str( inNewList[wIndex]['arashi'] ) + "," + \
							str( inNewList[wIndex]['reason_id'] ) + " " + \
							") ;"
				inNewList[wIndex]['update'] = False
			
			#############################
			# DBにあれば更新する
			else:
				if inNewList[wIndex]['update']!=True :
					###情報が更新されてなければスキップ
					continue
				
				wQuery = "update tbl_exc_twitterid set " + \
							"id = '" + str( inNewList[wIndex]['id'] ) + "', " + \
							"screen_name = '" + str( inNewList[wIndex]['screen_name'] ) + "', " + \
							"count = " + str( inNewList[wIndex]['count'] ) + ", " + \
							"lastdate = '" + str( inNewList[wIndex]['lastdate'] ) + "', " + \
							"arashi = " + str( inNewList[wIndex]['arashi'] ) + ", " + \
							"reason_id = " + str( inNewList[wIndex]['reason_id'] ) + " " + \
							"where screen_name = '" + inNewList[wIndex]['screen_name'] + "' ;"
				
				inNewList[wIndex]['update'] = False
				
			#############################
			# Query実行
			wResDB = gVal.OBJ_DB.RunQuery( wQuery )
			wResDB = gVal.OBJ_DB.GetQueryStat()
			if wResDB['Result']!=True :
				##失敗
				wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
				return wRes
		
		#############################
		# 保持日数外の情報を削除する
		wLag = gVal.DEF_STR_TLNUM['excTwitterIDdays'] * 24 * 60 * 60
		wLagTime = CLS_OSIF.sTimeLag( inThreshold=wLag, inTimezone=-1 )
		if wLagTime['Result']!=True :
			##失敗
			wRes['Reason'] = "sTimeLag is failed"
			return wRes
		
		wQuery = "delete from tbl_exc_twitterid " + \
					"where lastdate < timestamp '" + str(wLagTime['RateTime']) + "' " + \
					";"
		
		#############################
		# Query実行
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(3): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# Tweet ID 読み込み
#####################################################
	def GetExcTweetID(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Config"
		wRes['Func']  = "GetExcTweetID"
		
		#############################
		# データベースから除外Twitter IDを取得
		wQuery = "select id from tbl_exc_tweetid " + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed: RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		### グローバルに取り込み
		gVal.STR_ExcTweetID = []
		gVal.STR_RateExcTweetID = []
		gVal.OBJ_DB.ChgList( wResDB['Responce']['Data'], outList=gVal.STR_RateExcTweetID )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# Tweet ID 設定
#####################################################
	def SetExcTweetID(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Config"
		wRes['Func']  = "SetExcTweetID"
		
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "PC時間の取得に失敗しました"
			return wRes
		### wTD['TimeDate']
		
		for wNewID in gVal.STR_ExcTweetID :
			#############################
			# DBにあればスキップ
			if wNewID in gVal.STR_RateExcTweetID :
				continue
			
			#############################
			# DBに登録する
			wQuery = "insert into tbl_exc_tweetid values (" + \
						"'" + str(wTD['TimeDate']) + "'," + \
						"'" + str( wNewID ) + "' " + \
						") ;"
			
			#############################
			# Query実行
			wResDB = gVal.OBJ_DB.RunQuery( wQuery )
			wResDB = gVal.OBJ_DB.GetQueryStat()
			if wResDB['Result']!=True :
				##失敗
				wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
				return wRes
		
		#############################
		# 保持日数外の情報を削除する
		wLag = gVal.DEF_STR_TLNUM['excTweetDays'] * 24 * 60 * 60
		wLagTime = CLS_OSIF.sTimeLag( inThreshold=wLag, inTimezone=-1 )
		if wLagTime['Result']!=True :
			##失敗
			wRes['Reason'] = "sTimeLag is failed"
			return wRes
		
		wQuery = "delete from tbl_exc_tweetid " + \
					"where regdate < timestamp '" + str(wLagTime['RateTime']) + "' " + \
					";"
		
		#############################
		# Query実行
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(2): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# 除外Follow候補 読み込み
#####################################################
	def GetExcFollowID(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Config"
		wRes['Func']  = "GetExcFollowID"
		
		#############################
		# データベースから除外Twitter IDを取得
		wQuery = "select id from tbl_exc_followid " + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed: RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		### グローバルに取り込み
		gVal.STR_ExcFollowID = []
		gVal.OBJ_DB.ChgList( wResDB['Responce']['Data'], outList=gVal.STR_ExcFollowID )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# 古い除外Follow候補 削除
#####################################################
	def OldExcFollowID_Erase(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Config"
		wRes['Func']  = "OldExcFollowID_Erase"
		
		#############################
		# 除外日数外の情報を削除する
		wLag = gVal.DEF_STR_TLNUM['excFollowIDdays'] * 24 * 60 * 60
		wLagTime = CLS_OSIF.sTimeLag( inThreshold=wLag, inTimezone=-1 )
		if wLagTime['Result']!=True :
			##失敗
			wRes['Reason'] = "sTimeLag is failed"
			return wRes
		
		wQuery = "delete from tbl_exc_followid " + \
					"where regdate < timestamp '" + str(wLagTime['RateTime']) + "' " + \
					";"
		
		#############################
		# Query実行
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# 自動いいね設定 読み込み
#####################################################
	def GetAutoFavo(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Config"
		wRes['Func']  = "GetAutoFavo"
		
		#############################
		# DBの取得
###		wQuery = "select favorp,favort,favoirt,favotag,favolen from tbl_user_data where " + \
		wQuery = "select * from tbl_user_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "' " + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		#############################
		# 辞書型に整形
		wARR_RateAutoFavo = {}
		gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateAutoFavo )
		wARR_RateAutoFavo = wARR_RateAutoFavo[0]
		
		#############################
		# 読み込み
		gVal.STR_AutoFavo['Rip']  = wARR_RateAutoFavo['favorp']
		gVal.STR_AutoFavo['Ret']  = wARR_RateAutoFavo['favort']
		gVal.STR_AutoFavo['iRet'] = wARR_RateAutoFavo['favoirt']
		gVal.STR_AutoFavo['Tag']  = wARR_RateAutoFavo['favotag']
		gVal.STR_AutoFavo['PieF'] = wARR_RateAutoFavo['favopief']
		gVal.STR_AutoFavo['Len']  = int( wARR_RateAutoFavo['favolen'] )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# 自動いいね 設定
#####################################################
	def SetAutoFavo(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Config"
		wRes['Func']  = "SetAutoFavo"
		
		#############################
		# DBにあれば更新する
		wQuery = "update tbl_user_data set " + \
				"favorp = " + str( gVal.STR_AutoFavo['Rip'] ) + ", " + \
				"favort = " + str( gVal.STR_AutoFavo['Ret'] ) + ", " + \
				"favoirt = " + str( gVal.STR_AutoFavo['iRet'] ) + ", " + \
				"favotag = " + str( gVal.STR_AutoFavo['Tag'] ) + ", " + \
				"favopief = " + str( gVal.STR_AutoFavo['PieF'] ) + ", " + \
				"favolen = " + str( gVal.STR_AutoFavo['Len'] ) + " " + \
				"where twitterid = '" + gVal.STR_UserInfo['Account'] + "' " + \
				";"
		
		#############################
		# Query実行
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		#############################
		# 完了
		wRes['Result']   = True
		return wRes



