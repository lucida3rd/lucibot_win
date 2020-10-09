#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : メイン処理(コンソール)
# 
# ::Update= 2020/10/9
#####################################################
# Private Function:
#   __getLucibotVer(cls):
#   __getSystemInfo(cls):
#
# Instance Function:
#   (none)
#
# Class Function(static):
#   sRun(cls):
#   sViewMainConsole(cls):
#   sRunCommand( cls, inCommand ):
#   sViewDisp( cls, inDisp ):
#   sView_Sysinfo(cls):
#
#####################################################

from osif import CLS_OSIF
from filectrl import CLS_File
from setup import CLS_Setup
from botctrl import CLS_BotCtrl
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
		wRes = CLS_BotCtrl.sBotTest()
		if wRes!=True :
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
				gVal.OBJ_L.Log( "R", "CLS_Main_Console", "sRun", "コンソール停止" )
				CLS_BotCtrl.sBotEnd()	#bot停止
				break
			
			wRes = cls().sRunCommand( wCommand )
			if wRes==True :
				CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
		
		return



#####################################################
# メインコンソール画面の表示
#####################################################
	@classmethod
	def sViewMainConsole(cls):
		
		#############################
		# メインコンソール画面
		wRes = cls().sViewDisp( "MainConsole" )
		if wRes==False :
			return "q"	#失敗=強制終了
		
		wCommand = CLS_OSIF.sInp( "コマンド？=> " )
		return wCommand



#####################################################
# 実行
#####################################################
	@classmethod
	def sRunCommand( cls, inCommand ):

		wCLS_work = ""
		wFlg = False
		
	#####################################################
		#############################
		# システム情報の表示
		if inCommand=="\\v" :
			cls().sView_Sysinfo()
			wFlg = True
		
		#############################
		# 監視情報の取得
		if inCommand=="\\g" :
			cls.OBJ_TwitterMain.Run()
			wFlg = True
		
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
		# 手動トゥートモード
#		elif inCommand=="\\t" :
#			wCLS_work = CLS_Toot()
#			wCLS_work.ManualToot()
#			wFlg = True
		
		#############################
		# ログの表示(全ログ)
		if inCommand=="\\l" :
			gVal.OBJ_L.View()
			wFlg = True
		
		#############################
		# ログの表示(運用ログ)
		if inCommand=="\\lr" :
			gVal.OBJ_L.View( inViewMode="R" )
			wFlg = True
		
		#############################
		# ログの表示(異常ログ)
		if inCommand=="\\le" :
			gVal.OBJ_L.View( inViewMode="E" )
			wFlg = True
		
		#############################
		# ログクリア
		if inCommand=="\\lc" :
			gVal.OBJ_L.Clear()
			wFlg = True
		
	#####################################################
		#############################
		# ないコマンド
		if wFlg!=True :
			gVal.OBJ_L.Log( "D", "CLS_Main_Console", "sRunCommand", "存在しないコマンド :" + str(inCommand) )
		
		return wFlg



#####################################################
# ディスプレイ表示
#####################################################
	@classmethod
	def sViewDisp( cls, inDisp ):
		#############################
		# ディスプレイファイルの確認
		wKeylist = gVal.DEF_STR_DISPFILE.keys()
		if inDisp not in wKeylist :
			###キーがない(指定ミス)
###			CLS_OSIF.sPrn( "CLS_Main_Console: __viewDisp: Display key is not found: inDisp= " + inDisp )
			gVal.OBJ_L.Log( "C", "CLS_Main_Console", "sViewDisp", "Display key is not found: inDisp= " + inDisp )
			return False
		
		if CLS_File.sExist( gVal.DEF_STR_DISPFILE[inDisp] )!=True :
			###ファイルがない...(消した？)
###			CLS_OSIF.sPrn( "CLS_Main_Console: __viewDisp: Display file is not found: " + gVal.DEF_STR_DISPFILE[inDisp] )
			gVal.OBJ_L.Log( "D", "CLS_Main_Console", "sViewDisp", "Displayファイルがない: file=" + gVal.DEF_STR_DISPFILE[inDisp] )
			return False
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# 中身表示
		wDispFile = []
		if CLS_File.sReadFile( gVal.DEF_STR_DISPFILE[inDisp], outLine=wDispFile )!=True :
###			CLS_OSIF.sPrn( "CLS_Main_Console: __viewDisp: Dispファイルが見つかりません: path=" + gVal.DEF_STR_DISPFILE[inDisp] )
			gVal.OBJ_L.Log( "D", "CLS_Main_Console", "sViewDisp", "Displayファイルがない(sReadFile): file=" + gVal.DEF_STR_DISPFILE[inDisp] )
			return False
		
		if len(wDispFile)<=1 :
###			CLS_OSIF.sPrn( "CLS_Main_Console: __viewDisp: Dispファイルが空です: path=" + gVal.DEF_STR_DISPFILE[inDisp] )
			gVal.OBJ_L.Log( "D", "CLS_Main_Console", "sViewDisp", "Displayファイルが空: file=" + gVal.DEF_STR_DISPFILE[inDisp] )
			return False
		
		wStr = "--------------------" + '\n'
		wStr = wStr + "るしぼっとCONSOLE" + '\n'
		wStr = wStr + "--------------------" + '\n'
		wStr = wStr + "Twitter ID : " + gVal.STR_UserInfo['Account'] + '\n'
		wStr = wStr + '\n'
		for wLine in wDispFile :
			wStr = wStr + "    " + wLine + '\n'
		
		CLS_OSIF.sPrn( wStr )
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



#####################################################
# いいね監視の実行
#####################################################
	@classmethod
	def sRun_FavoAdmin(cls):
		
		#############################
		# いいね監視の実行
		wCLS_work = CLS_Twitter_Ctrl( parentObj=cls )
		wCLS_work.Get_RunFavoAdmin()
		wSTR_Cope = wCLS_work.GetCope()
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " いいね監視結果" + '\n'
		wStr = wStr + "--------------------" + '\n'
		
		#############################
		# 情報組み立て
		wStr = wStr + "現いいね数   = " + str(wSTR_Cope['FavoNum']) + '\n'
		wStr = wStr + "解除いいね数 = " + str(wSTR_Cope['FavoRemove']) + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "DB登録数 = " + str(wSTR_Cope['DB_Num']) + '\n'
		wStr = wStr + "DB挿入   = " + str(wSTR_Cope['DB_Insert']) + '\n'
		wStr = wStr + "DB更新   = " + str(wSTR_Cope['DB_Update']) + '\n'
		wStr = wStr + "DB削除   = " + str(wSTR_Cope['DB_Delete']) + '\n'
		
		#############################
		# コンソールに表示
		CLS_OSIF.sPrn( wStr )
		return



#####################################################
# フォロワー監視の実行
#####################################################
	@classmethod
	def sRun_FollowerAdmin(cls):
		
		#############################
		# フォロワー監視の実行
		wCLS_work = CLS_Twitter_Ctrl( parentObj=cls )
		wRes = wCLS_work.Get_Run_FollowerAdmin()
		if wRes['Result']!=True :
			CLS_OSIF.sPrn( wRes['Reason'] )
			return
		
		wSTR_Cope = wCLS_work.GetCope()
		wSTR_NewFollower = wCLS_work.GetNewFollower()
		
		#############################
		# 画面クリア
##		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " フォロワー監視結果" + '\n'
		wStr = wStr + "--------------------" + '\n'
		
		#############################
		# 情報組み立て
		wStr = wStr + "現フォロワー数   = " + str(wSTR_Cope['FollowerNum']) + '\n'
		wStr = wStr + "新規フォロワー数 = " + str(wSTR_Cope['NewFollowerNum']) + '\n'
		wStr = wStr + "自動リムーブ数   = " + str(wSTR_Cope['MyFollowRemove']) + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "DB登録数 = " + str(wSTR_Cope['DB_Num']) + '\n'
		wStr = wStr + "DB挿入   = " + str(wSTR_Cope['DB_Insert']) + '\n'
		wStr = wStr + "DB更新   = " + str(wSTR_Cope['DB_Update']) + '\n'
		wStr = wStr + "DB削除   = " + str(wSTR_Cope['DB_Delete']) + '\n'
		
		#############################
		# コンソールに表示
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 新規フォロワーCSV出力
		if len(wSTR_NewFollower)>0 :
			wRes = cls.sSaveCSV_NewFollower( wSTR_NewFollower )
			if wRes!="" :
				wStr = "--------------------" + '\n'
				wStr = "CSVファイルを出力しました: " + wRes + '\n'
				CLS_OSIF.sPrn( wStr )
		
		return

	#####################################################
	@classmethod
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



