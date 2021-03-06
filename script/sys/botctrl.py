#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : bot制御(共通)
# 
# ::Update= 2021/1/15
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
from gval import gVal
#####################################################
class CLS_BotCtrl():
#####################################################

#####################################################
# Botテスト
#####################################################
	@classmethod
	def sBotTest(cls):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_BotCtrl"
		wRes['Func']  = "sBotTest"
		
		#############################
		# 引数取得
		wArg = CLS_OSIF.sGetArg()
		if len(wArg)==4 :	#テストモード : bottest か
			if wArg[3]==gVal.DEF_TEST_MODE :
				gVal.FLG_Test_Mode = True
		
		elif len(wArg)==2 :	#モード
			###セットアップモード
			###全初期化モード
			###データ追加モード
			###データクリアモード
			if wArg[1]!="setup" and \
			   wArg[1]!="init" and \
			   wArg[1]!="add" and \
			   wArg[1]!="clear" :
				wRes['Reason'] = "存在しないモードです"
				CLS_OSIF.sErr( wRes )
				return False
			
			gVal.STR_SystemInfo['RunMode'] = wArg[1]
			return True
		
		elif len(wArg)!=3 :	#引数が足りない
			wRes['Reason'] = "CLS_BotCtrl: sBotTest: 引数が足りません= " + str( wArg )
			CLS_OSIF.sErr( wRes )
			return False
		
		gVal.STR_UserInfo['Account'] = wArg[1]	#ユーザ名
		wPassword                    = wArg[2]	#パスワード
		gVal.STR_SystemInfo['RunMode'] = "Normal"
		
		#############################
		# DBに接続
		gVal.OBJ_DB = CLS_PostgreSQL_Use()
		wResDBconn = gVal.OBJ_DB.Create( gVal.DEF_BD_HOST, gVal.DEF_BD_NAME, gVal.DEF_BD_USER, wPassword )
		wResDB = gVal.OBJ_DB.GetDbStatus()
		if wResDBconn!=True :
			wRes['Reason'] = "DBの接続に失敗しました: reason=" + wResDB['Reason']
			CLS_OSIF.sErr( wRes )
			return False
		
		###結果の確認
		if wResDB['Init']!=True :
			wRes['Reason'] = "DBが初期化できてません"
			CLS_OSIF.sErr( wRes )
			return False
		
		wFLG_UserRegisted = False
		#############################
		# DBの状態チェック
		wResDB = gVal.OBJ_DB.RunTblExist( "tbl_user_data" )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##クエリ失敗
			wRes['Reason'] = "DBの状態チェック失敗: RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			CLS_OSIF.sErr( wRes )
			gVal.OBJ_DB.Close()
			return False
		if wResDB['Responce']!=True :
			##テーブルがない= 初期化してない
			wRes['Reason'] = "初期化されていません"
			CLS_OSIF.sErr( wRes )
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
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			gVal.OBJ_L.Log( "B", wRes )
			gVal.OBJ_DB.Close()
			return False
		
		#############################
		# ユーザ登録の確認
		if len(wResDB['Responce']['Data'])==0 :
			wRes['Reason'] = "ユーザが登録されていません =" + gVal.STR_UserInfo['Account']
			gVal.OBJ_L.Log( "D", wRes )
			gVal.OBJ_DB.Close()
			return False
		
		wChgDict = {}
		if gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wChgDict )!=True :
			##ないケースかも
			wRes['Reason'] = "恐らくDBに未登録: ChgDict is failed"
			gVal.OBJ_L.Log( "C", wRes )
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
		gVal.STR_UserInfo['FavoList'] = wChgDict[0]['favolist']
		
		#############################
		# 排他開始
		wLock = cls.sLock()
		if wLock['Result']!=True :
			wRes['Reason'] = "排他取得失敗: " + wLock['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			gVal.OBJ_DB.Close()
			return
		elif wLock['Responce']!=None :
			wRes['Reason'] = "排他中"
			gVal.OBJ_L.Log( "R", wRes )
			
			CLS_OSIF.sPrn( "処理待機中です。CTRL+Cで中止することもできます。" )
			CLS_OSIF.sPrn( wLock['Reason'] + '\n' )
			
			wResStop = CLS_OSIF.sPrnWAIT( wLock['Responce'] )
			if wResStop==False :
				###ウェイト中止
				CLS_OSIF.sPrn( '\n' + "待機を中止しました。プログラムを停止しました。" )
				gVal.OBJ_DB.Close()
				return
		
		#############################
		# Twitterに接続
		gVal.OBJ_Twitter = CLS_Twitter_Use()
		wResTwitter_Create = gVal.OBJ_Twitter.Create( gVal.STR_UserInfo['Account'], wAPIkey, wAPIsecret, wACCtoken, wACCsecret )
		wResTwitter = gVal.OBJ_Twitter.GetTwStatus()
		if wResTwitter_Create!=True :
			wRes['Reason'] = "Twitterの接続失敗: reason=" + wResTwitter['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			cls.sBotEnd()	#bot終了
			return False
		
		###結果の確認
		if wResTwitter['Init']!=True :
			wRes['Reason'] = "Twitter初期化失敗"
			gVal.OBJ_L.Log( "B", wRes )
			cls.sBotEnd()	#bot終了
			return False
		
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "PC時間取得失敗"
			gVal.OBJ_L.Log( "B", wRes )
			cls.sBotEnd()	#bot終了
			return
		### wTD['TimeDate']
		gVal.STR_SystemInfo['APIrect'] = str(wTD['TimeDate'])
		
		#############################
		# るしぼっとVersion
		wReadme = []
		if CLS_File.sReadFile( gVal.DEF_STR_FILE['Readme'], outLine=wReadme )!=True :
			wRes['Reason'] = "Readme.mdファイルが見つかりません: path=" + gVal.DEF_STR_FILE['Readme']
			gVal.OBJ_L.Log( "D", wRes )
			cls.sBotEnd()	#bot終了
			return False
		
		if len(wReadme)<=1 :
			wRes['Reason'] = "Readme.mdファイルが空です: path=" + gVal.DEF_STR_FILE['Readme']
			gVal.OBJ_L.Log( "D", wRes )
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
		wRes['Reason'] = "実行"
		gVal.OBJ_L.Log( "R", wRes )
		
		#############################
		# テスト終了
		return True



#####################################################
# Bot終了
#####################################################
	@classmethod
	def sBotEnd(cls):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_BotCtrl"
		wRes['Func']  = "sBotEnd"
		
		#############################
		# 排他解除
		wRes = cls.sUnlock()
		if wRes['Result']!=True :
			wRes['Reason'] = "排他取得失敗: " + wRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
		
		#############################
		# DB終了
		gVal.OBJ_DB.Close()
		return True



#####################################################
# 排他制御
#####################################################
	@classmethod
	def sLock(cls):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_BotCtrl"
		wRes['Func']  = "sLock"
		
		#############################
		# テーブルがある
		wQuery = "select * from tbl_user_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		#############################
		# ユーザ登録の確認
		if len(wResDB['Responce']['Data'])==0 :
			wRes['Reason'] = "Not Regist User"
			return wRes
		
		wChgDict = {}
		if gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wChgDict )!=True :
			##ないケースかも
			wRes['Reason'] = "ChgDict failed"
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
				wRes['Reason'] = "sTimeLag failed"
				return wRes
			if wGetLag['Beyond']==True :
				#反応時間外
				cls.sUnlock()	#一度解除する
				
				#ログに記録する
				wRes['Reason'] = "排他解除"
				gVal.OBJ_L.Log( "R", wRes )
				wRes['Reason'] = None
			
			else :
				wAtSec = wReaRIPmin - wGetLag['RateSec']
				wAtSec = CLS_OSIF.sGetFloor( wAtSec )	#小数点切り捨て
				wRes['Reason'] = "処理終了まであと " + str(wAtSec) + " 秒です"
				wRes['Responce'] = wAtSec
				wRes['Result']   = True
				return wRes
		
		#※排他がかかってない
		#############################
		# 排他する
		
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "PC時間の取得に失敗しました"
			return wRes
		### wTD['TimeDate']
		
		wQuery = "update tbl_user_data set " + \
				"locked = True, " + \
				"lupdate = '" + str(wTD['TimeDate']) + "'" + \
				"where twitterid = '" + gVal.STR_UserInfo['Account'] + "' ;"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(2): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		wRes['Result']   = True
		return wRes	#排他あり



#####################################################
# 排他延長
#####################################################
	@classmethod
	def sExtLock(cls):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_BotCtrl"
		wRes['Func']  = "sExtLock"
		
		#############################
		# テーブルがある
		wQuery = "select * from tbl_user_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		#############################
		# ユーザ登録の確認
		if len(wResDB['Responce']['Data'])==0 :
			wRes['Reason'] = "Not Regist User"
			return wRes
		
		wChgDict = {}
		if gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wChgDict )!=True :
			##ないケースかも
			wRes['Reason'] = "ChgDict failed"
			return wRes
		
		#############################
		# ロックの取得
		wLocked  = wChgDict[0]['locked']
		wLUpdate = wChgDict[0]['lupdate']
		if wLocked!=True :
			### 排他がかかってない
			wRes['Reason'] = "Do not lock"
			return wRes
		
		#############################
		# 排他の延長 = 今の操作時間に更新する
		
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "PC時間の取得に失敗しました"
			return wRes
		### wTD['TimeDate']
		
		wQuery = "update tbl_user_data set " + \
				"lupdate = '" + str(wTD['TimeDate']) + "'" + \
				"where twitterid = '" + gVal.STR_UserInfo['Account'] + "' ;"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(2): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		wRes['Result']   = True
		return wRes



#####################################################
# 排他情報の取得
#####################################################
	@classmethod
	def sGetLock(cls):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_BotCtrl"
		wRes['Func']  = "sGetLock"
		
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
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed: RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		#############################
		# ユーザ登録の確認
		if len(wResDB['Responce']['Data'])==0 :
			wRes['Reason'] = "Not Regist User"
			return wRes
		
		wChgDict = {}
		if gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wChgDict )!=True :
			##ないケースかも
			wRes['Reason'] = "ChgDict failed"
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
				wRes['Reason'] = "sTimeLag failed"
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
	def sUnlock(cls):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_BotCtrl"
		wRes['Func']  = "sUnlock"
		
		#############################
		# 排他解除する
		wQuery = "update tbl_user_data set " + \
				"locked = False " + \
				"where twitterid = '" + gVal.STR_UserInfo['Account'] + "' ;"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed: RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		wRes['Result']   = True
		return wRes	#排他なし



