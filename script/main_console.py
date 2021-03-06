#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : メイン処理(コンソール)
# 
# ::Update= 2021/3/6
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
from traffic import CLS_Traffic
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
		
		#############################
		# データクリアモードで実行
		elif gVal.STR_SystemInfo['RunMode']=="clear" :
			wCLS_Setup = CLS_Setup()
			wCLS_Setup.Clear()
			CLS_OSIF.sInp( '\n' + "リターンキーを押して再度コンソールアプリを起動してください。[RT]" )
			return
		
		# ※通常処理継続
		gVal.FLG_Console_Mode = True				#コンソールモード
		cls.OBJ_TwitterMain  = CLS_TwitterMain()	#メインの実体化
		wResIni = cls.OBJ_TwitterMain.Init()		#初期化
		if wResIni['Result']!=True :
			wRes['Reason'] = "Init is failed reason=" + wResIni['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			CLS_BotCtrl.sBotEnd()	#bot停止
			return
		
		#############################
		# コンソールを表示
		while True :
			wCommand = cls().sViewMainConsole()
			
			if wCommand=="" :
				###未入力は再度入力
				continue
			
			if wCommand.find("\\q")>=0 or wCommand=="exit" :
				#############################
				# 終了
				wRes['Reason'] = "コンソール停止"
				gVal.OBJ_L.Log( "R", wRes )
				CLS_BotCtrl.sBotEnd()	#bot停止
				break
				#############################
			
			wResCmd = cls().sRunCommand( wCommand )
			gVal.STR_TrafficInfo['run'] += 1	#Bot実行
			
			#############################
			# トラヒック情報の記録
			wResTraffic = CLS_Traffic.sSet()
			if wResTraffic['Result']!=True :
				wRes['Reason'] = "Set Traffic failed: reason" + CLS_OSIF.sCatErr( wResTraffic )
				gVal.OBJ_L.Log( "B", wRes )
				CLS_BotCtrl.sBotEnd()	#bot停止
				return wRes
			if wResTraffic['Responce']==True :
				CLS_OSIF.sPrn( "トラヒック情報が翌日分に切り替わりました。" )
			
			wResTraffic = CLS_Traffic.sReport()
			if wResTraffic['Result']!=True :
				wRes['Reason'] = "sReport failed: reason" + CLS_OSIF.sCatErr( wResTraffic )
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			
			#############################
			# 待機(入力待ち)
			CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
			
			#############################
			# 開始or前回チェックから15分経ったか
			w15Res = cls.OBJ_TwitterMain.Circle15min()
			if w15Res['Result']!=True :
				wRes['Reason'] = "Circle15min is failed reason=" + w15Res['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				CLS_BotCtrl.sBotEnd()	#bot停止
				return wRes
			
			#############################
			# 保存処理
			wSaveRes = cls.OBJ_TwitterMain.CircleSave()
			if wSaveRes['Result']!=True :
				wRes['Reason'] = "CircleSave is failed reason=" + wSaveRes['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				CLS_BotCtrl.sBotEnd()	#bot停止
				return wRes
		
		return



#####################################################
# メインコンソール画面の表示
#####################################################
	@classmethod
	def sViewMainConsole(cls):
		
		#############################
		# メインコンソール画面
		wResDisp = CLS_MyDisp.sViewDisp( "MainConsole" )
		if wResDisp['Result']==False :
			gVal.OBJ_L.Log( "D", wResDisp )
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
		
	#####################################################
		#############################
		# 監視情報の取得
		if inCommand=="\\g" :
			cls.OBJ_TwitterMain.Run()
		
	#####################################################
		#############################
		# キーユーザフォロー(手動)
		elif inCommand=="\\f" :
			cls.OBJ_TwitterMain.KeyUserFollow()
		
		#############################
		# 自動選出フォロー(手動)
		elif inCommand=="\\af" :
			cls.OBJ_TwitterMain.AutoChoiceFollow()
		
		#############################
		# 指定いいね
		elif inCommand=="\\i" :
			cls.OBJ_TwitterMain.DesiFavo()
		
		#############################
		# 自動いいね(相互フォロー)
		elif inCommand=="\\ia" :
			cls.OBJ_TwitterMain.AutoFavo()
		
		#############################
		# 無差別いいね
		elif inCommand=="\\ics" :
			cls.OBJ_TwitterMain.CaoFavo()
		
	#####################################################
		#############################
		# いいね情報の表示
		elif inCommand=="\\vi" :
			cls.OBJ_TwitterMain.ViewFavo()
		
		#############################
		# フォロワー情報の表示
		elif inCommand=="\\vf" :
			cls.OBJ_TwitterMain.ViewFollower()
		
		#############################
		# 個別いいねチェック
		elif inCommand=="\\ri" :
			cls.OBJ_TwitterMain.PointFavoCheck()
		
	#####################################################
		#############################
		# ユーザ管理
		elif inCommand=="\\u" :
			cls.OBJ_TwitterMain.UserAdmin()
		
	#####################################################
		#############################
		# キーユーザ検索の変更
		elif inCommand=="\\cs" :
			cls.OBJ_TwitterMain.SetKeyuser()
		
		#############################
		# Twitterリストの変更
		elif inCommand=="\\cl" :
			wOBJ_Config = CLS_Config()
			wResList = wOBJ_Config.SetTwitterList( gVal.STR_UserInfo['Account'], True, True )
			if wResList['Result']!=True :
				###失敗
				wRes['Reason'] = "Set Twitter List failed: " + wResList['Reason']
				gVal.OBJ_L.Log( "D", wRes )
		
		#############################
		# Twitter APIの変更
		elif inCommand=="\\ca" :
			wOBJ_Config = CLS_Config()
			wResAPI = wOBJ_Config.SetTwitterAPI( gVal.STR_UserInfo['Account'], True, True )
			if wResAPI['Result']!=True :
				wRes['Reason'] = "Set Twitter API failed: " + wResAPI['Reason']
				gVal.OBJ_L.Log( "D", wRes )
		
		#############################
		# 荒らしユーザ設定
		elif inCommand=="\\cu" :
			cls.OBJ_TwitterMain.ArashiUser()
		
		#############################
		# 自動いいね設定
		elif inCommand=="\\ci" :
			cls.OBJ_TwitterMain.SetAutoFavo()
		
	#####################################################
		#############################
		# ツイート検索
		elif inCommand=="\\s" :
			cls.OBJ_TwitterMain.TweetSearch()
		
#		#############################
#		# 手動トゥートモード
#		elif inCommand=="\\t" :
#			wCLS_work = CLS_Toot()
#			wCLS_work.ManualToot()
		
	#####################################################
		#############################
		# ログの表示(異常ログ)
		elif inCommand=="\\l" :
			gVal.OBJ_L.View( inViewMode="E" )
		
		#############################
		# ログの表示(運用ログ)
		elif inCommand=="\\lr" :
			gVal.OBJ_L.View( inViewMode="R" )
		
		#############################
		# ログの表示(全ログ)
		elif inCommand=="\\la" :
			gVal.OBJ_L.View()
		
		#############################
		# ログクリア
		elif inCommand=="\\lc" :
			gVal.OBJ_L.Clear()
		
		#############################
		# システム情報の表示
		elif inCommand=="\\v" :
			cls().sView_Sysinfo()
		
		#############################
		# トラヒック情報の表示
		elif inCommand=="\\vt" :
			wResTraffic = CLS_Traffic.sView()
			if wResTraffic['Result']!=True :
				gVal.OBJ_L.Log( "B", wResTraffic )
		
	#####################################################
		#############################
		# テスト
		elif inCommand=="\\test" :
##			wTwitterRes = gVal.OBJ_Twitter.SendDM( gVal.STR_UserInfo['id'], "てすと" )
##			if wTwitterRes['Result']!=True :
##				CLS_OSIF.sPrn( "Twitter API Error: " + wTwitterRes['Reason'] )
##			wTwitterRes = gVal.OBJ_Twitter.GetMention()
##			if wTwitterRes['Result']==True :
##				CLS_OSIF.sPrn( str(wTwitterRes['Responce']) )
##			wTwitterRes = gVal.OBJ_Twitter.GetTL( inTLmode="user" )
##			if wTwitterRes['Result']==True :
##				CLS_OSIF.sPrn( str(wTwitterRes['Responce']) )
###			wTwitterRes = gVal.OBJ_Twitter.GetTweetStat2( inID="1349021137309757446" )
###			if wTwitterRes['Result']==True :
###				CLS_OSIF.sPrn( str(wTwitterRes['Responce']) )
###			else:
###				CLS_OSIF.sPrn( "Twitter API Error: " + wTwitterRes['Reason'] )

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
			wARR_NormalListMenberID = []
			for wROW in wListsRes['Responce'] :
				wARR_NormalListMenberID.append( str(wROW['id']) )
			print( str(wARR_NormalListMenberID) )

		
	#####################################################
		#############################
		# ないコマンド
		else :
			wRes['Reason'] = "存在しないコマンド :" + str(inCommand)
			gVal.OBJ_L.Log( "D", wRes )
			return False
		
		return True



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



