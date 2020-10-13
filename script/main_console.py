#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : メイン処理(コンソール)
# 
# ::Update= 2020/10/14
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   (none)
#
# Class Function(static):
#   sRun(cls):
#   sViewMainConsole(cls):
#   sRunCommand( cls, inCommand ):
#   sView_Sysinfo(cls):
#
#####################################################

from osif import CLS_OSIF
from filectrl import CLS_File
from setup import CLS_Setup
from botctrl import CLS_BotCtrl
from mydisp import CLS_MyDisp
from config import CLS_Config
from twitter_main import CLS_TwitterMain
from gval import gVal
#####################################################
class CLS_Main_Console() :
#####################################################
	#使用クラス実体化
	OBJ_TwitterMain = ""

#####################################################
# 実行
#####################################################
	@classmethod
	def sRun(cls):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Main_Console"
		wRes['Func']  = "sRun"
		
		#############################
		# botテスト、引数ロード
		#   テスト項目
		#     1.引数ロード
		#     2.データベースの取得
		#     3.ログの取得
		#     4.排他
		#     5.Twitterの取得
		#     6.Readme情報の取得
		#     7.Python情報の取得
		#     8.TESTログ記録
		wResTest = CLS_BotCtrl.sBotTest()
		if wResTest!=True :
			return	#問題あり
		
		#############################
		# セットアップモードで実行
		if gVal.STR_SystemInfo['RunMode']=="setup" :
			wCLS_Setup = CLS_Setup()
			wCLS_Setup.Setup()
			CLS_OSIF.sInp( '\n' + "リターンキーを押して再度コンソールアプリを起動してください。[RT]" )
			return
		
		#############################
		# 初期化モードで実行
		elif gVal.STR_SystemInfo['RunMode']=="init" :
			wCLS_Setup = CLS_Setup()
			wCLS_Setup.AllInit()
			CLS_OSIF.sInp( '\n' + "リターンキーを押して再度コンソールアプリを起動してください。[RT]" )
			return
		
		#############################
		# データ追加モードで実行
		elif gVal.STR_SystemInfo['RunMode']=="add" :
			wCLS_Setup = CLS_Setup()
			wCLS_Setup.Add()
			CLS_OSIF.sInp( '\n' + "リターンキーを押して再度コンソールアプリを起動してください。[RT]" )
			return
		
		# ※通常処理継続
		gVal.FLG_Console_Mode = True				#コンソールモード
		cls.OBJ_TwitterMain  = CLS_TwitterMain()	#メインの実体化
		#############################
		# コンソールを表示
		while True :
			wCommand = cls().sViewMainConsole()
			
			if wCommand.find("\\q")>=0 or wCommand=="exit" :
				###終了
###				CLS_OSIF.sPrn( "コンソールを停止します。" + '\n' )
###				gVal.OBJ_L.Log( "R", "CLS_Main_Console", "sRun", "コンソール停止" )
				wRes['Reason'] = "コンソール停止"
				gVal.OBJ_L.Log( "R", wRes )
				CLS_BotCtrl.sBotEnd()	#bot停止
				break
			
			wResCmd = cls().sRunCommand( wCommand )
			if wResCmd==True :
				CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
			
			#############################
			# 開始or前回チェックから15分経ったか
			wFLG_Err = False
			wResetAPImin = gVal.DEF_STR_TLNUM['resetAPImin'] * 60	#秒に変換
			wGetLag = CLS_OSIF.sTimeLag( gVal.STR_SystemInfo['APIrect'], inThreshold=wResetAPImin )
			if wGetLag['Result']!=True :
				wRes['Reason'] = "sTimeLag failed"
				gVal.OBJ_L.Log( "B", wRes )
				wFLG_Err = True
			
			if wGetLag['Beyond']==True or \
			   wFLG_Err==True :
				###前回から15分経ってるので更新
				gVal.OBJ_Twitter.ResetAPI()
				gVal.STR_SystemInfo['APIrect'] = str(wGetLag['NowTime'])
				wRes['Reason'] = "TwitterAPI規制解除"
				gVal.OBJ_L.Log( "R", wRes )
			
		return



#####################################################
# メインコンソール画面の表示
#####################################################
	@classmethod
	def sViewMainConsole(cls):
		
		#############################
		# メインコンソール画面
###		wRes = cls().sViewDisp( "MainConsole" )
###		if wRes==False :
###			return "q"	#失敗=強制終了
		wResDisp = CLS_MyDisp.sViewDisp( "MainConsole" )
		if wResDisp['Result']==False :
			gVal.OBJ_L.Log( "D", wResDisp )
###			return "q"	#失敗=強制終了
			return "\\q"	#失敗=強制終了
		
		wCommand = CLS_OSIF.sInp( "コマンド？=> " )
		return wCommand



#####################################################
# 実行
#####################################################
	@classmethod
	def sRunCommand( cls, inCommand ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Main_Console"
		wRes['Func']  = "sRunCommand"
		
		wCLS_work = ""
		wFlg = False
		
	#####################################################
		#############################
		# 監視情報の取得
		if inCommand=="\\g" :
			cls.OBJ_TwitterMain.Run()
			wFlg = True
		
	#####################################################
		#############################
		# キーユーザCSV出力
		if inCommand=="\\k" :
			cls.OBJ_TwitterMain.KeyUserCSV()
			wFlg = True
		
	#####################################################
		#############################
		# いいね情報の表示
		if inCommand=="\\vi" :
			cls.OBJ_TwitterMain.ViewFavo()
			wFlg = True
		
		#############################
		# いいね監視の実行
		if inCommand=="\\ri" :
			cls.OBJ_TwitterMain.RunFavo()
			wFlg = True
		
		#############################
		# フォロワー情報の表示
		if inCommand=="\\vf" :
			cls.OBJ_TwitterMain.ViewFollower()
			wFlg = True
		



	#####################################################
		#############################
		# Twitterリストの変更
		elif inCommand=="\\cl" :
			wOBJ_Config = CLS_Config()
			wResList = wOBJ_Config.SetTwitterList( gVal.STR_UserInfo['Account'], True, True )
			if wResList['Result']!=True :
				###失敗
				wRes['Reason'] = "Set Twitter List failed: " + wResList['Reason']
				gVal.OBJ_L.Log( "D", wRes )
			
			wFlg = True
		
		#############################
		# Twitter APIの変更
		elif inCommand=="\\ca" :
			wOBJ_Config = CLS_Config()
			wResAPI = wOBJ_Config.SetTwitterAPI( gVal.STR_UserInfo['Account'], True, True )
			if wResAPI['Result']!=True :
				wRes['Reason'] = "Set Twitter API failed: " + wResAPI['Reason']
				gVal.OBJ_L.Log( "D", wRes )
			
			wFlg = True
		
	#####################################################
		#############################
		# ツイート検索
		elif inCommand=="\\s" :
			cls.OBJ_TwitterMain.TweetSearch()
			wFlg = True
		
		#############################
		# 手動トゥートモード
#		elif inCommand=="\\t" :
#			wCLS_work = CLS_Toot()
#			wCLS_work.ManualToot()
#			wFlg = True
		
	#####################################################
		#############################
		# ログの表示(異常ログ)
		if inCommand=="\\l" :
			gVal.OBJ_L.View( inViewMode="E" )
			wFlg = True
		
		#############################
		# ログの表示(運用ログ)
		if inCommand=="\\lr" :
			gVal.OBJ_L.View( inViewMode="R" )
			wFlg = True
		
		#############################
		# ログの表示(全ログ)
		if inCommand=="\\la" :
			gVal.OBJ_L.View()
			wFlg = True
		
		#############################
		# ログクリア
		if inCommand=="\\lc" :
			gVal.OBJ_L.Clear()
			wFlg = True
		
		#############################
		# システム情報の表示
		if inCommand=="\\v" :
			cls().sView_Sysinfo()
			wFlg = True
		
	#####################################################
		#############################
		# ないコマンド
		if wFlg!=True :
###			gVal.OBJ_L.Log( "D", "CLS_Main_Console", "sRunCommand", "存在しないコマンド :" + str(inCommand) )
			wRes['Reason'] = "存在しないコマンド :" + str(inCommand)
			gVal.OBJ_L.Log( "D", wRes )
		
		return wFlg



#####################################################
# ディスプレイ表示
#####################################################
#	@classmethod
#	def sViewDisp( cls, inDisp ):
#		#############################
#		# 応答形式の取得
#		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
#		wRes = CLS_OSIF.sGet_Resp()
#		wRes['Class'] = "CLS_Main_Console"
#		wRes['Func']  = "sViewDisp"
#		
#		#############################
#		# ディスプレイファイルの確認
#		wKeylist = gVal.DEF_STR_DISPFILE.keys()
#		if inDisp not in wKeylist :
#			###キーがない(指定ミス)
#			wRes['Reason'] = "Display key is not found: inDisp= " + inDisp
#			gVal.OBJ_L.Log( "C", wRes )
#			return False
#		
#		if CLS_File.sExist( gVal.DEF_STR_DISPFILE[inDisp] )!=True :
#			###ファイルがない...(消した？)
#			wRes['Reason'] = "Displayファイルがない: file=" + gVal.DEF_STR_DISPFILE[inDisp]
#			gVal.OBJ_L.Log( "D", wRes )
#			return False
#		
#		#############################
#		# 画面クリア
#		CLS_OSIF.sDispClr()
#		
#		#############################
#		# 中身表示
#		wDispFile = []
#		if CLS_File.sReadFile( gVal.DEF_STR_DISPFILE[inDisp], outLine=wDispFile )!=True :
#			wRes['Reason'] = "Displayファイルがない(sReadFile): file=" + gVal.DEF_STR_DISPFILE[inDisp]
#			gVal.OBJ_L.Log( "D", wRes )
#			return False
#		
#		if len(wDispFile)<=1 :
#			wRes['Reason'] = "Displayファイルが空: file=" + gVal.DEF_STR_DISPFILE[inDisp]
#			gVal.OBJ_L.Log( "D", wRes )
#			return False
#		
#		wStr = "--------------------" + '\n'
#		wStr = wStr + "るしぼっとCONSOLE" + '\n'
#		wStr = wStr + "--------------------" + '\n'
#		wStr = wStr + "Twitter ID : " + gVal.STR_UserInfo['Account'] + '\n'
#		wStr = wStr + '\n'
#		for wLine in wDispFile :
#			wStr = wStr + "    " + wLine + '\n'
#		
#		CLS_OSIF.sPrn( wStr )
#		return True
#
#

#####################################################
# システム情報の表示
#####################################################
	@classmethod
	def sView_Sysinfo(cls):
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " システム情報" + '\n'
		wStr = wStr + "--------------------" + '\n'
		
		#############################
		# 時間の取得
		wRes = CLS_OSIF.sGetTime()
		if wRes['Result']==True :
			wStr = wStr + wRes['TimeDate'] + '\n'
		
		#############################
		# 情報組み立て
		wStr = wStr + "Client Name = " + gVal.STR_SystemInfo['Client_Name'] + '\n'
		wStr = wStr + "Project Name= " + gVal.STR_SystemInfo['ProjectName'] + '\n'
		wStr = wStr + "github      = " + gVal.STR_SystemInfo['github'] + '\n'
		wStr = wStr + "Admin       = " + gVal.STR_SystemInfo['Admin'] + '\n'
		wStr = wStr + "Twitter URL = " + gVal.STR_SystemInfo['TwitterURL'] + '\n'
		wStr = wStr + "Update      = " + gVal.STR_SystemInfo['Update'] + '\n'
		wStr = wStr + "Version     = " + gVal.STR_SystemInfo['Version'] + '\n'
		
		wStr = wStr + "Python      = " + str( gVal.STR_SystemInfo['PythonVer'] )  + '\n'
		wStr = wStr + "HostName    = " + gVal.STR_SystemInfo['HostName'] + '\n'
		
		#############################
		# コンソールに表示
		CLS_OSIF.sPrn( wStr )
		return



