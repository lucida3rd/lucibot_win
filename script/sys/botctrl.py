#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : bot制御(共通)
# 
# ::Update= 2020/10/9
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   (none)
#
# Class Function(static):
#   sBotTest(cls):
#   sBotEnd(cls):
#   sLock(cls):
#   sExtLock(cls):
#   sGetLock(cls):
#   sUnlock(cls):
#
#####################################################
from postgresql_use import CLS_PostgreSQL_Use
from twitter_use import CLS_Twitter_Use
from mylog import CLS_Mylog

from osif import CLS_OSIF
from filectrl import CLS_File
from userdata import CLS_UserData
from gval import gVal
#####################################################
class CLS_BotCtrl():
#####################################################

#####################################################
# Botテスト
#####################################################
	@classmethod
###	def sBotTest( cls, parentObj ):
	def sBotTest(cls):
		#############################
		# 引数取得
		wArg = CLS_OSIF.sGetArg()
		if len(wArg)==4 :	#テストモードか
			if wArg[3]==gVal.DEF_TEST_MODE :
				gVal.FLG_Test_Mode = True
		
		elif len(wArg)==2 :	#モード
			###セットアップモード
			###全初期化モード
			if wArg[1]!="setup" and \
			   wArg[1]!="init" :
				CLS_OSIF.sPrn( "CLS_BotCtrl: sBotTest: 存在しないモードです" )
				return False
			
			gVal.STR_SystemInfo['RunMode'] = wArg[1]
			return True
		
		elif len(wArg)!=3 :	#引数が足りない
			wStr = "CLS_BotCtrl: sBotTest: 引数が足りません= " + str( wArg )
			CLS_OSIF.sPrn( wStr  )	#メールに頼る
			return False
		
		gVal.STR_UserInfo['Account'] = wArg[1]	#ユーザ名
		wPassword                    = wArg[2]	#パスワード
		gVal.STR_SystemInfo['RunMode'] = "Normal"
		
		#############################
		# DBに接続
		gVal.OBJ_DB = CLS_PostgreSQL_Use()
		wRes = gVal.OBJ_DB.Create( gVal.DEF_BD_HOST, gVal.DEF_BD_NAME, gVal.DEF_BD_USER, wPassword )
		wResDB = gVal.OBJ_DB.GetDbStatus()
		if wRes!=True :
			CLS_OSIF.sPrn( "CLS_BotCtrl: sBotTest: DBの接続に失敗しました: 理由=" + wResDB['Reason'] )
			return False
		
		###結果の確認
		if wResDB['Init']!=True :
			CLS_OSIF.sPrn( "CLS_BotCtrl: sBotTest: DBが初期化できてません" )
			return False
		
		wFLG_UserRegisted = False
		#############################
		# DBの状態チェック
		wDBRes = gVal.OBJ_DB.RunTblExist( "tbl_user_data" )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##クエリ失敗
			CLS_OSIF.sPrn( "CLS_BotCtrl: sBotTest: DBの状態チェック失敗: " + wDBRes['Reason'] )
			gVal.OBJ_DB.Close()
			return False
		if wDBRes['Responce']!=True :
			##テーブルがない= 初期化してない
			CLS_OSIF.sPrn( "CLS_BotCtrl: sBotTest: 初期化されていません" )
			gVal.OBJ_DB.Close()
			return False
		
		#############################
		# ログオブジェクトの生成
		gVal.OBJ_L = CLS_Mylog()
		
		#############################
		# テーブルがある
		wQuery = "select * from tbl_user_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
###			wStr = "CLS_BotCtrl: sBotTest: Run Query is failed(1): " + wDBRes['Reason'] + " query=" + wDBRes['Query']
###			CLS_OSIF.sPrn( wStr )
			gVal.OBJ_L.Log( "B", "CLS_BotCtrl", "sBotTest", "Run Query is failed(1): " + wDBRes['Reason'] + " query=" + wDBRes['Query'] )
			gVal.OBJ_DB.Close()
			return False
		
		#############################
		# ユーザ登録の確認
		if len(wDBRes['Responce']['Data'])==0 :
###			CLS_OSIF.sPrn( "CLS_BotCtrl: sBotTest: ユーザが登録されていません" )
			gVal.OBJ_L.Log( "D", "CLS_BotCtrl", "sBotTest", "ユーザが登録されていません =" + gVal.STR_UserInfo['Account'] )
			gVal.OBJ_DB.Close()
			return False
		
		wChgDict = {}
		if gVal.OBJ_DB.ChgDict( wDBRes['Responce']['Collum'], wDBRes['Responce']['Data'], outDict=wChgDict )!=True :
			##ないケースかも
###			wStr = "CLS_BotCtrl: sBotTest: ChgList is failed(1)"
###			CLS_OSIF.sPrn( wStr )
			gVal.OBJ_L.Log( "C", "CLS_BotCtrl", "sBotTest", "恐らくDBに未登録: ChgList is failed" )
			gVal.OBJ_DB.Close()
			return False
		
		#############################
		# ユーザ登録の抽出
		wAPIkey    = wChgDict[0]['apikey']
		wAPIsecret = wChgDict[0]['apisecret']
		wACCtoken  = wChgDict[0]['acctoken']
		wACCsecret = wChgDict[0]['accsecret']
		
		gVal.STR_UserInfo['NorList'] = wChgDict[0]['norlist']
		gVal.STR_UserInfo['UrfList'] = wChgDict[0]['urflist']
		
		#############################
		# 排他開始
###		wLock = cls.sLock( parentObj=parentObj )
		wLock = cls.sLock()
		if wLock['Result']!=True :
###			CLS_OSIF.sPrn( "CLS_BotCtrl: sBotTest: 排他取得失敗(1): " + wLock['Reason'] + '\n' )
			gVal.OBJ_L.Log( "B", "CLS_BotCtrl", "sBotTest", "排他取得失敗(1): " + wLock['Reason'] )
			gVal.OBJ_DB.Close()
			return
		elif wLock['Responce']==True :
			gVal.OBJ_L.Log( "R", "CLS_BotCtrl", "sBotTest", "排他中" )
			CLS_OSIF.sPrn( "処理中です。しばらくお待ちください。" )
			CLS_OSIF.sPrn( wLock['Reason'] )
			gVal.OBJ_DB.Close()
			return
		
		#############################
		# Twitterに接続
		gVal.OBJ_Twitter = CLS_Twitter_Use()
		wResTwitter_Create = gVal.OBJ_Twitter.Create( gVal.STR_UserInfo['Account'], wAPIkey, wAPIsecret, wACCtoken, wACCsecret )
		wResTwitter = gVal.OBJ_Twitter.GetTwStatus()
		if wResTwitter_Create!=True :
###			CLS_OSIF.sPrn( "CLS_BotCtrl: sBotTest: Twitterの接続に失敗しました: 理由=" + wResTwitter['Reason'] )
			gVal.OBJ_L.Log( "B", "CLS_BotCtrl", "sBotTest", "Twitterの接続失敗: reason=" + wResTwitter['Reason'] )
			cls.sBotEnd()	#bot終了
			return False
		
		###結果の確認
		if wResTwitter['Init']!=True :
###			CLS_OSIF.sPrn( "CLS_BotCtrl: sBotTest: Twitterが初期化できてません" )
			gVal.OBJ_L.Log( "B", "CLS_BotCtrl", "sBotTest", "Twitter初期化失敗" )
			cls.sBotEnd()	#bot終了
			return False
		
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
###			CLS_OSIF.sPrn( "CLS_BotCtrl: sBotTest: PC時間の取得に失敗しました" )
			gVal.OBJ_L.Log( "B", "CLS_BotCtrl", "sBotTest", "PC時間取得失敗" )
			cls.sBotEnd()	#bot終了
			return
		### wTD['TimeDate']
		
		#############################
		# るしぼっとVersion
		wReadme = []
		if CLS_File.sReadFile( gVal.DEF_STR_FILE['Readme'], outLine=wReadme )!=True :
###			CLS_OSIF.sPrn( "CLS_BotCtrl: sBotTest: Readme.mdファイルが見つかりません: path=" + gVal.DEF_STR_FILE['Readme'] )
			gVal.OBJ_L.Log( "B", "CLS_BotCtrl", "sBotTest", "Readme.mdファイルが見つかりません: path=" + gVal.DEF_STR_FILE['Readme'] )
			cls.sBotEnd()	#bot終了
			return False
		
		if len(wReadme)<=1 :
###			CLS_OSIF.sPrn( "CLS_BotCtrl: sBotTest: Readme.mdファイルが空です: path=" + gVal.DEF_STR_FILE['Readme'] )
			gVal.OBJ_L.Log( "B", "CLS_BotCtrl", "sBotTest", "Readme.mdファイルが空です: path=" + gVal.DEF_STR_FILE['Readme'] )
			cls.sBotEnd()	#bot終了
			return False
		
		for wLine in wReadme :
			#############################
			# 分解+要素数の確認
			wLine = wLine.strip()
			wGetLine = wLine.split("= ")
			if len(wGetLine) != 2 :
				continue
			
			wGetLine[0] = wGetLine[0].replace("::", "")
			#############################
			# キーがあるか確認
			if wGetLine[0] not in gVal.STR_SystemInfo :
				continue
			
			#############################
			# キーを設定
			gVal.STR_SystemInfo[wGetLine[0]] = wGetLine[1]
		
		#############################
		# システム情報の取得
		wCLS_work = CLS_OSIF()
		gVal.STR_SystemInfo['PythonVer'] = wCLS_work.Get_PythonVer()
		gVal.STR_SystemInfo['HostName']  = wCLS_work.Get_HostName()
		
		#############################
		# ログに記録する
##		wQuery = "insert into tbl_log_data values (" + \
##					"'" + gVal.STR_UserInfo['Account'] + "'," + \
##					"'t'," + \
##					"'TEST=OK'," + \
##					"'" + str(wTD['TimeDate']) + "'" + \
##					") ;"
##		
##		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
##		wDBRes = gVal.OBJ_DB.GetQueryStat()
##		if wDBRes['Result']!=True :
##			##失敗
##			wStr = "CLS_BotCtrl: sBotTest: Run Query is failed(2): " + wDBRes['Reason']
##			CLS_OSIF.sPrn( wStr )
##			cls.sBotEnd()	#bot終了
##			return False
		gVal.OBJ_L.Log( "R", "CLS_BotCtrl", "sBotTest", "実行" )
		
		#############################
		# テスト終了
		return True



#####################################################
# Bot終了
#####################################################
	@classmethod
	def sBotEnd(cls):
		#############################
		# 排他解除
		wRes = cls.sUnlock()
		if wRes['Result']!=True :
###			CLS_OSIF.sPrn( "CLS_BotCtrl: sBotEnd: 排他取得失敗: " + wRes['Reason'] + '\n' )
			gVal.OBJ_L.Log( "B", "CLS_BotCtrl", "sBotEnd", "排他取得失敗: " + wRes['Reason'] )
		
		#############################
		# DB終了
		gVal.OBJ_DB.Close()
		return True



#####################################################
# 排他制御
#####################################################
	@classmethod
###	def sLock( cls, parentObj ):
	def sLock(cls):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# テーブルがある
		wQuery = "select * from tbl_user_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_BotCtrl: sLock: Run Query is failed(1): " + wDBRes['Reason'] + " query=" + wDBRes['Query']
			return wRes
		
		#############################
		# ユーザ登録の確認
		if len(wDBRes['Responce']['Data'])==0 :
			wRes['Reason'] = "CLS_BotCtrl: sLock: Not Regist User"
			return wRes
		
		wChgDict = {}
		if gVal.OBJ_DB.ChgDict( wDBRes['Responce']['Collum'], wDBRes['Responce']['Data'], outDict=wChgDict )!=True :
			##ないケースかも
			wRes['Reason'] = "CLS_BotCtrl: sLock: ChgDict failed(2)"
			return wRes
		
		#############################
		# ロックの取得
		wLocked  = wChgDict[0]['locked']
		wLUpdate = wChgDict[0]['lupdate']
		if wLocked==True :
			### 排他済み
			
			# ロック保持時間外かを求める (変換＆差)
			wReaRIPmin = gVal.DEF_STR_TLNUM['lockLimmin'] * 60	#秒に変換
			wGetLag = CLS_OSIF.sTimeLag( str(wLUpdate), inThreshold=wReaRIPmin )
			if wGetLag['Result']!=True :
				wRes['Reason'] = "CLS_BotCtrl: sLock: sTimeLag failed"
				return wRes
			if wGetLag['Beyond']==True :
				#反応時間外
				cls.sUnlock()	#一度解除する
				
				#ログに記録する
###				wQuery = "insert into tbl_log_data values (" + \
###							"'" + gVal.STR_UserInfo['Account'] + "'," + \
###							"'t'," + \
###							"'排他解除'," + \
###							"'" + str(wGetLag['NowTime']) + "'" + \
###							") ;"
###				
###				wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
###				wDBRes = gVal.OBJ_DB.GetQueryStat()
###				if wDBRes['Result']!=True :
###					##失敗
###					wRes['Reason'] = "CLS_BotCtrl: Run Query is failed(2): " + wDBRes['Reason']
###					return wRes
				gVal.OBJ_L.Log( "R", "CLS_BotCtrl", "sLock", "排他解除" )
			
			else :
				wAtSec = wReaRIPmin - wGetLag['RateSec']
				wAtSec = CLS_OSIF.sGetFloor( wAtSec )	#小数点切り捨て
				wRes['Reason'] = "処理終了まであと " + str(wAtSec) + " 秒です"
				wRes['Responce'] = True
				wRes['Result']   = True
				return wRes
		
		#※排他がかかってない
		#############################
		# 排他する
		
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "CLS_BotCtrl: sLock: PC時間の取得に失敗しました"
			return wRes
		### wTD['TimeDate']
		
		wQuery = "update tbl_user_data set " + \
				"locked = True, " + \
				"lupdate = '" + str(wTD['TimeDate']) + "'" + \
				"where twitterid = '" + gVal.STR_UserInfo['Account'] + "' ;"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_BotCtrl: sLock: Run Query is failed(3): " + wDBRes['Reason']
			return wRes
		
		wRes['Result']   = True
		return wRes	#排他あり



#####################################################
# 排他延長
#####################################################
	@classmethod
###	def sExtLock( cls, parentObj ):
	def sExtLock(cls):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# テーブルがある
		wQuery = "select * from tbl_user_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_BotCtrl: sExtLock: Run Query is failed(1): " + wDBRes['Reason'] + " query=" + wDBRes['Query']
			return wRes
		
		#############################
		# ユーザ登録の確認
		if len(wDBRes['Responce']['Data'])==0 :
			wRes['Reason'] = "CLS_BotCtrl: sExtLock: Not Regist User"
			return wRes
		
		wChgDict = {}
		if gVal.OBJ_DB.ChgDict( wDBRes['Responce']['Collum'], wDBRes['Responce']['Data'], outDict=wChgDict )!=True :
			##ないケースかも
			wRes['Reason'] = "CLS_BotCtrl: sExtLock: ChgDict failed(2)"
			return wRes
		
		#############################
		# ロックの取得
		wLocked  = wChgDict[0]['locked']
		wLUpdate = wChgDict[0]['lupdate']
		if wLocked!=True :
			### 排他がかかってない
			wRes['Reason'] = "CLS_BotCtrl: sExtLock: Do not lock"
			return wRes
		
		#############################
		# 排他の延長 = 今の操作時間に更新する
		
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "CLS_BotCtrl: sExtLock: PC時間の取得に失敗しました"
			return wRes
		### wTD['TimeDate']
		
		wQuery = "update tbl_user_data set " + \
				"lupdate = '" + str(wTD['TimeDate']) + "'" + \
				"where twitterid = '" + gVal.STR_UserInfo['Account'] + "' ;"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_BotCtrl: sExtLock: Run Query is failed(3): " + wDBRes['Reason']
			return wRes
		
		wRes['Result']   = True
		return wRes



#####################################################
# 排他情報の取得
#####################################################
	@classmethod
###	def sGetLock( cls, parentObj ):
	def sGetLock(cls):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		wRes['Responce'] = {}
		wRes['Responce'].update({
			"Locked"    : False,
			"Beyond"    : False
		})
		
		#############################
		# テーブルがある
		wQuery = "select * from tbl_user_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_BotCtrl: sGetLock: Run Query is failed(1): " + wDBRes['Reason'] + " query=" + wDBRes['Query']
			return wRes
		
		#############################
		# ユーザ登録の確認
		if len(wDBRes['Responce']['Data'])==0 :
			wRes['Reason'] = "CLS_BotCtrl: sGetLock: Not Regist User"
			return wRes
		
		wChgDict = {}
		if gVal.OBJ_DB.ChgDict( wDBRes['Responce']['Collum'], wDBRes['Responce']['Data'], outDict=wChgDict )!=True :
			##ないケースかも
			wRes['Reason'] = "CLS_BotCtrl: sGetLock: ChgDict failed(2)"
			return wRes
		
		#############################
		# ロックの取得
		wLocked  = wChgDict[0]['locked']
		wLUpdate = wChgDict[0]['lupdate']
		if wLocked==True :
			### 排他がかかってる
			
			# ロック保持時間外かを求める (変換＆差)
			wReaRIPmin = gVal.DEF_STR_TLNUM['lockLimmin'] * 60	#秒に変換
			wGetLag = CLS_OSIF.sTimeLag( str(wLUpdate), inThreshold=wReaRIPmin )
			if wGetLag['Result']!=True :
				wRes['Reason'] = "CLS_BotCtrl: sGetLock: sTimeLag failed"
				return wRes
			if wGetLag['Beyond']==True :
				###解除可能
				wRes['Reason'] = "解除可能です"
			
			else :
				wAtSec = wReaRIPmin - wGetLag['RateSec']
				wAtSec = CLS_OSIF.sGetFloor( wAtSec )	#小数点切り捨て
				wRes['Reason'] = "処理終了まであと " + str(wAtSec) + " 秒です"
			
			#############################
			# ロック=ON, 排他解除 可or否
			wRes['Responce']['Beyond'] = wGetLag['Beyond']
		
		###else:
			#############################
			# ロック=OFF
		
		#############################
		# ロック状態 ON or OFF, 正常終了
		wRes['Responce']['Locked'] = wLocked
		wRes['Result'] = True
		return wRes



#####################################################
# 排他解除
#####################################################
	@classmethod
###	def sUnlock( cls, parentObj ):
	def sUnlock(cls):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# 排他解除する
		wQuery = "update tbl_user_data set " + \
				"locked = False " + \
				"where twitterid = '" + gVal.STR_UserInfo['Account'] + "' ;"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_BotCtrl: sUnlock: Run Query is failed(1): " + wDBRes['Reason']
			return wRes
		
		wRes['Responce'] = False
		wRes['Result']   = True
		return wRes	#排他なし



