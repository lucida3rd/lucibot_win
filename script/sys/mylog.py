#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : ログ処理
# 
# ::Update= 2020/10/9
#####################################################
# Private Function:
#   __write( self, inLogFile, inDate, inMsg ):
#
# Instance Function:
#   __init__( self, inPath ):
#   Log( cls, inLevel, inMsg, inView=False ):
#
# Class Function(static):
#   (none)
#
#####################################################
# 書式:
#	A:	gVal.OBJ_L.Log( "A", "Class", "Func", "Reason" )	致命的エラー: プログラム停止 ロジックエラーなどソフト側の問題
#	B:	gVal.OBJ_L.Log( "B", "Class", "Func", "Reason" )	外部のエラー: プログラム停止か実行不可 外部モジュールやハードの問題
#	C:	gVal.OBJ_L.Log( "C", "Class", "Func", "Reason" )	内部的エラー: プログラムは停止しないが、実行に影響があるレベル
#	D:	gVal.OBJ_L.Log( "D", "Class", "Func", "Reason" )	潜在的エラー: ユーザ入力など予想外 or 後に問題を起こす可能性がある
#	R:	gVal.OBJ_L.Log( "R", "Class", "Func", "Reason" )	実行記録
#	T:	gVal.OBJ_L.Log( "T", "Class", "Func", "Reason" )	テスト用ログ
#
#####################################################

from osif import CLS_OSIF
from filectrl import CLS_File
from gval import gVal
#####################################################
class CLS_Mylog():
#####################################################

#############################
# ログレベル 日本語ローカライズ
#   参考:A～Cは Cコンパイラのレベル2～4レベル基準
	DEF_STR_LEVEL = {
		"A"			: "致命的エラー: プログラム停止 ロジックエラーなどソフト側の問題",
		"B"			: "外部のエラー: プログラム停止か実行不可 外部モジュールやハードの問題",
		"C"			: "内部的エラー: プログラムは停止しないが、実行に影響があるレベル",
		"D"			: "潜在的エラー: ユーザ入力など予想外 or 後に問題を起こす可能性がある",
		
		"R"			: "実行記録",
		"T"			: "テスト用ログ",
		
		"U"			: "ログレベルのセットミス",
		"(dummy)"	: ""
	}

#############################
# ログ表示モード
	DEF_STR_VIEW_LEVEL = {
		"A"			: "全ログ",
		"R"			: "運用ログ",
		"E"			: "異常ログ",
		"(dummy)"	: ""
	}

	DEF_VIEW_CONSOLE = True		#デフォルトのコンソール表示
	DEF_OUT_FILE     = False	#デフォルトのファイル出力



#####################################################
# ロギング
#####################################################
	def Log( self, inLevel=None, inLogClass=None, inLogFunc=None, inReason=None, inARR_Data=[], inViewConsole=DEF_VIEW_CONSOLE, inOutFile=DEF_OUT_FILE ):
		#############################
		# ログ文字セット
		wSTR_Log = {
			"LogClass" : None,
			"LogFunc"  : None,
			"Reason"   : None }
		
		#############################
		# ログレベルのチェック
		wLevel = inLevel
		if wLevel==None or wLevel=="" :
			wLevel = "U"
		###大文字変換
		try:
			wLevel = wLevel.upper()
		except ValueError as err :
			wLevel = "U"
		###定義チェック
		if wLevel not in self.DEF_STR_LEVEL :
			wLevel = "U"
		
		#############################
		# ログクラスのチェック
		wLogClass = inLogClass
		if wLogClass==None or wLogClass=="" :
			wLogClass = "(none)"
		wSTR_Log['LogClass'] = wLogClass
		
		#############################
		# ログファンクのチェック
		wLogFunc = inLogFunc
		if wLogFunc==None or wLogFunc=="" :
			wLogFunc = "(none)"
		wSTR_Log['LogFunc'] = wLogFunc
		
		#############################
		# 理由のチェック
		wReason = inReason
		if wReason==None or wReason=="" :
			wReason = "(none)"
		### ' を　'' に置き換える
		wReason = wReason.replace( "'", "''" )
		wSTR_Log['Reason'] = wReason
		
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		### wTD['TimeDate']
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			CLS_OSIF.sPrn( "CLS_Mylog: Log: PC時間の取得に失敗しました" )
			wCHR_TimeDate = "1901-01-01 00:00:00"
			
			###いちおデータベースにも記録する
			wQuery = "insert into tbl_log_data values (" + \
						"'" + gVal.STR_UserInfo['Account'] + "'," + \
						"'B'," + \
						"'CLS_Mylog'," + \
						"'Log'," + \
						"'CLS_OSIF.sGetTime is failed'," + \
						"'" + wCHR_TimeDate + "'" + \
						") ;"
			
			wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
			wDBRes = gVal.OBJ_DB.GetQueryStat()
			if wDBRes['Result']!=True :
				##失敗
				wStr = "CLS_Mylog: Log: Run Query is failed(sGetTime)" + wDBRes['Reason']
				CLS_OSIF.sPrn( wStr )
		
		else:
			wCHR_TimeDate = str(wTD['TimeDate'])
		
		#############################
		# データベースに記録する
		wQuery = "insert into tbl_log_data values (" + \
					"'" + gVal.STR_UserInfo['Account'] + "'," + \
					"'" + wLevel + "'," + \
					"'" + wSTR_Log['LogClass'] + "'," + \
					"'" + wSTR_Log['LogFunc'] + "'," + \
					"'" + wSTR_Log['Reason'] + "'," + \
					"'" + wCHR_TimeDate + "'" + \
					") ;"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wStr = "CLS_Mylog: Log: Run Query is failed" + wDBRes['Reason']
			CLS_OSIF.sPrn( wStr )
			##以後の記録処理は継続する
		
		#############################
		# ログの組み立て
		wOutLog = wLevel + ": "
		wOutLog = wOutLog + wSTR_Log['LogClass'] + ": "
		wOutLog = wOutLog + wSTR_Log['LogFunc'] + ": "
		wOutLog = wOutLog + wSTR_Log['Reason']
		
		#############################
		# データの組み立て
		wData = []
		if len(inARR_Data)>0 :
			###ブランク文字
			wBlank = " " * len( wCHR_TimeDate )
			###データのセット
			for wLine in inARR_Data :
				wIncLine = wBlank + ' ' + wLine + '\n'
				wData.append( wIncLine )
		
		#############################
		# コンソールに表示する
		# = システムログに出る
		if inViewConsole==True and \
		   wLevel!="R" :
			CLS_OSIF.sPrn( wOutLog )
			for wLineData in wData :
				CLS_OSIF.sPrn( wLineData )
		
		#############################
		# ファイル書き出し
		if inOutFile==True :
			wFileRes = self.__writeFile( wCHR_TimeDate, wOutLog, wData )
		
		return wOutLog



#####################################################
# ファイルへの書き出し
#####################################################
	def __writeFile( self, inTimeDate, inLog, inARR_Data=[] ):
		#############################
		# ユーザフォルダの存在チェック
		if CLS_File.sExist( gVal.DEF_USERDATA_PATH )!=True :
			###フォルダがなければ諦める
			return False
		
		#############################
		# ログフォルダの作成
		wLogPath = gVal.DEF_USERDATA_PATH + "log"
		if CLS_File.sExist( wLogPath )!=True :
			###まだ未生成なら作成する
			if CLS_File.sMkdir( wLogPath )!=True :
				###作れなければ諦める
				return False
		
		#############################
		# ファイル名、フルパスの生成
		wFilePath = inTimeDate.split(" ")
		wFilePath_Date = wFilePath[0]
		wFilePath_Date = wFilePath_Date.replace( "-", "" )
		wFilePath_Time = wFilePath[1]
		wFilePath_Time = wFilePath_Time.replace( ":", "" )
		
		wFilePath = wFilePath_Date + "_" + wFilePath_Time + ".log"
		wLogPath = wLogPath + "/" + wFilePath
		
		wSetLine = []
		#############################
		# 1行目
		wLine = inTimeDate + ' ' + inLog + '\n'
		wSetLine.append( wLine )
		
		#############################
		# 2行目以降
		if len(inARR_Data)>0 :
			for wLineData in inARR_Data :
				wSetLine.append( wLineData )
		
		#############################
		# ファイル追加書き込み
		wRes = CLS_File.sAddFile( wLogPath, wSetLine, inExist=False )
		if wRes!=True :
			###失敗
			return False
		
		return True



#####################################################
# ログの表示
#####################################################
	def View( self, inShortMode=True, inViewMode="A" ):
		#############################
		# 運用モード
		wViewMode = inViewMode.upper()
		if inViewMode not in self.DEF_STR_VIEW_LEVEL :
			wViewMode = "A"
		###大文字変換
		try:
			wViewMode = wViewMode.upper()
		except ValueError as err :
			wViewMode = "A"
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " ログの表示" + '\n'
		wStr = wStr + "--------------------" + '\n'
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# ログ取得
		### wViewMode=R 運用ログ
		if wViewMode=="R" :
			wQuery = "select * from tbl_log_data where " + \
						"twitterid = '" + gVal.STR_UserInfo['Account'] + "' and " + \
						"level = 'R' " + \
						"order by lupdate DESC ;"
		
		### wViewMode=E 異常ログ
		elif wViewMode=="E" :
			wQuery = "select * from tbl_log_data where " + \
						"twitterid = '" + gVal.STR_UserInfo['Account'] + "' and " + \
						"not level = 'R' " + \
						"order by lupdate DESC ;"
		
		### wViewMode=A 全ログ
		else:
			wQuery = "select * from tbl_log_data where " + \
						"twitterid = '" + gVal.STR_UserInfo['Account'] + "' " + \
						"order by lupdate DESC ;"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wStr = "CLS_Mylog: View: Run Query is failed: " + wDBRes['Reason'] + " query=" + wDBRes['Query']
			CLS_OSIF.sPrn( wStr )
			return False
		
		#############################
		# 辞書型に整形
		wARR_Log = {}
		gVal.OBJ_DB.ChgDict( wDBRes['Responce']['Collum'], wDBRes['Responce']['Data'], outDict=wARR_Log )
		
		#############################
		# ログ表示長のセット
		wOutLen = len(wARR_Log)
		if wOutLen==0 :
			wStr = "ログがありません。処理を中止します。" + '\n'
			CLS_OSIF.sPrn( wStr )
			return True
		
		if inShortMode==True :
			wOutLen = gVal.DEF_STR_TLNUM['logShortLen']
		
		#############################
		# ログ表示
		wKeylist = wARR_Log.keys()
		wIndex = 0
		for wKey in wKeylist :
			wTD    = str(wARR_Log[wKey]['lupdate'])
			wBlank = " " * len( wTD ) + " "
			
			wLine = wTD + " " + wARR_Log[wKey]['level'] + " "
			wLine = wLine + "[" + wARR_Log[wKey]['log_class'] + "] "
			wLine = wLine + "[" + wARR_Log[wKey]['log_func'] + "]"
			CLS_OSIF.sPrn( wLine )
			
			wLine = wBlank + wARR_Log[wKey]['reason']
			CLS_OSIF.sPrn( wLine )
			
			wIndex += 1
			if wOutLen<=wIndex :
				break
		
		return True

#############################
#	twitterid   TEXT  NOT NULL
#	level       CHAR(1) DEFAULT '-'
#	log_class   TEXT  NOT NULL
#	log_func    TEXT  NOT NULL
#	reason      TEXT  NOT NULL
#	lupdate     TIMESTAMP
#############################



#####################################################
# ログクリア
#####################################################
	def Clear(self):
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			CLS_OSIF.sPrn( "CLS_Mylog: Clear: PC時間の取得に失敗しました" )
			return False
		wTimeDate = str(wTD['TimeDate'])
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " ログ退避中" + '\n'
		wStr = wStr + "--------------------" + '\n'
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 実行の確認
		wStr = "データベースのログを全てファイルに退避したあと、全てクリアします。" + '\n'
		CLS_OSIF.sPrn( wStr )
		wSelect = CLS_OSIF.sInp( "よろしいですか？(y/N)=> " )
		if wSelect!="y" :
			##キャンセル
			CLS_OSIF.sPrn( "中止しました。" )
			return True
		
		#############################
		# 全ログ取得
		wQuery = "select * from tbl_log_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "' " + \
					"order by lupdate ;"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wStr = "CLS_Mylog: Clear: Run Query is failed: " + wDBRes['Reason'] + " query=" + wDBRes['Query']
			CLS_OSIF.sPrn( wStr )
			return False
		
		#############################
		# 辞書型に整形
		wARR_Log = {}
		gVal.OBJ_DB.ChgDict( wDBRes['Responce']['Collum'], wDBRes['Responce']['Data'], outDict=wARR_Log )
		
		#############################
		# ログ表示長のセット
		wOutLen = len(wARR_Log)
		if wOutLen==0 :
			wStr = "ログがありません。処理を中止します。" + '\n'
			CLS_OSIF.sPrn( wStr )
			return True
		
		wARR_Output = []
		#############################
		# 出力組み立て
		wKeylist = wARR_Log.keys()
		for wKey in wKeylist :
			wTD    = str(wARR_Log[wKey]['lupdate'])
			wBlank = " " * len( wTD ) + " "
			
			wLine = wTD + "," + wARR_Log[wKey]['level'] + ","
			wLine = wLine + wARR_Log[wKey]['log_class'] + ","
			wLine = wLine + wARR_Log[wKey]['log_func'] + ","
			wLine = wLine + wARR_Log[wKey]['reason'] + "," + '\n'
			wARR_Output.append( wLine )
		
		#############################
		# ログ出力
		self.__writeLogFile( wTimeDate, inARR_Data=wARR_Output )
		
		#############################
		# ログ消去
		wQuery = "delete from tbl_log_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "' " + \
					";"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wStr = "CLS_Mylog: Clear: Run Query is failed: " + wDBRes['Reason'] + " query=" + wDBRes['Query']
			CLS_OSIF.sPrn( wStr )
			return False
		
		#############################
		# 結果表示
		wStr = "データベースのログを全てクリアしました。" + '\n'
		CLS_OSIF.sPrn( wStr )
		return True



#####################################################
# ログ退避 書き出し
#####################################################
	def __writeLogFile( self, inTimeDate, inARR_Data=[] ):
		#############################
		# ユーザフォルダの存在チェック
		if CLS_File.sExist( gVal.DEF_USERDATA_PATH )!=True :
			###フォルダがなければ諦める
			return False
		
		#############################
		# ログフォルダの作成
		wLogPath = gVal.DEF_USERDATA_PATH + "log"
		if CLS_File.sExist( wLogPath )!=True :
			###まだ未生成なら作成する
			if CLS_File.sMkdir( wLogPath )!=True :
				###作れなければ諦める
				return False
		
		#############################
		# ファイル名、フルパスの生成
		wFilePath = inTimeDate.split(" ")
		wFilePath_Date = wFilePath[0]
		wFilePath_Date = wFilePath_Date.split("-")
		
		wFilePath = wFilePath_Date[0] + wFilePath_Date[1] + ".csv"
		wLogPath = wLogPath + "/" + wFilePath
		
		#############################
		# ファイル追加書き込み
		wRes = CLS_File.sAddFile( wLogPath, inARR_Data, inExist=False )
		if wRes!=True :
			###失敗
			return False
		
		wStr = "ログをファイルに退避しました: " + wFilePath
		CLS_OSIF.sPrn( wStr )
		
		return True



