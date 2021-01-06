#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL : https://twitter.com/lucida3hai
# ::Class       : セットアップ
# 
# ::Update= 2021/1/6
#####################################################
# Private Function:
#   __initDB( self, inDBobj ):
#   __allDrop( self, inDBobj ):
#
# ◇テーブル作成系
#   __create_TBL_USER_DATA( self, inOBJ_DB, inTBLname="tbl_user_data" ):
#   __create_TBL_LOG_DATA( self, inOBJ_DB, inTBLname="tbl_log_data" ):
#   __create_TBL_FAVO_DATA( self, inOBJ_DB, inTBLname="tbl_favo_data" ):
#   __create_TBL_FOLLOWER_DATA( self, inOBJ_DB, inTBLname="tbl_follower_data" ):
#
# Instance Function:
#   __init__(self):
#   Setup( self, inPassWD=None ):
#   AllInit(self):
#
# Class Function(static):
#   (none)
#
#####################################################
from postgresql_use import CLS_PostgreSQL_Use
from twitter_use import CLS_Twitter_Use

from osif import CLS_OSIF
from filectrl import CLS_File
from config import CLS_Config
from gval import gVal
#####################################################
class CLS_Setup():
#####################################################

#####################################################
# 初期化
#####################################################
	def __init__(self):
		return



#####################################################
# セットアップ
#####################################################
###	def Setup(self):
	def Setup( self, inPassWD=None ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Setup"
		wRes['Func']  = "Setup"
		
		CLS_OSIF.sPrn( "Lucibotをセットアップモードで起動しました" + '\n' )
		
		#############################
		# ユーザフォルダの存在チェック
		if CLS_File.sExist( gVal.DEF_USERDATA_PATH )!=True :
			## フォルダがなければ作成する
			if CLS_File.sMkdir( gVal.DEF_USERDATA_PATH )!=True :
				wRes['Reason'] = "フォルダの作成に失敗しました: path=" + gVal.DEF_USERDATA_PATH
				CLS_OSIF.sErr( wRes )
				return False
		
		#############################
		# DBに接続
		wPassword = inPassWD
		
		###パスワードが未設定なら入力を要求する
		if wPassword==None :
			wStr = "データベースに接続します。データベースのパスワードを入力してください。" + '\n'
			wStr = wStr + "  Hostname=" + gVal.DEF_BD_HOST + " Database=" + gVal.DEF_BD_NAME + " Username=" + gVal.DEF_BD_USER
			CLS_OSIF.sPrn( wStr )
			
			###入力受け付け
			wPassword = CLS_OSIF.sGpp( "Password: " )
		
		###テスト
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
		
		wStr = "データベースへ正常に接続しました。" + '\n'
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# TwitterIDの入力
		wStr = "Lucibotで使うユーザ登録をおこないます。" + '\n'
		wStr = wStr + "ここではTwitter IDと、Twitter Devで取得したキーを登録していきます。" + '\n'
		wStr = wStr + "Twitter IDを入力してください。"
		CLS_OSIF.sPrn( wStr )
		wTwitterAccount = CLS_OSIF.sInp( "Twitter ID？=> " )
		
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
			##DB初期化
			self.__initDB( gVal.OBJ_DB )
			CLS_OSIF.sPrn( "データベースを初期化しました" + '\n' )
		else :
			##テーブルがある
			##ユーザ登録の確認 and 抽出
			wQuery = "select * from tbl_user_data where " + \
						"twitterid = '" + wTwitterAccount + "'" + \
						";"
			
			wResDB = gVal.OBJ_DB.RunQuery( wQuery )
			wResDB = gVal.OBJ_DB.GetQueryStat()
			if wResDB['Result']!=True :
				##失敗
				wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
				CLS_OSIF.sErr( wRes )
				gVal.OBJ_DB.Close()
				return False
			
			##登録あり
			if len(wResDB['Responce']['Data'])==1 :
				wFLG_UserRegisted = True	#ユーザあり
				wStr = "ユーザ " + wTwitterAccount + " は既に登録されています。キーの変更をおこないますか？" + '\n'
				CLS_OSIF.sPrn( wStr )
				wSelect = CLS_OSIF.sInp( "変更する？(y/N)=> " )
				if wSelect!="y" :
					###キャンセル
					gVal.OBJ_DB.Close()
					return True
		
		#############################
		# Twitterキーの入力と接続テスト
		gVal.OBJ_Twitter = CLS_Twitter_Use()
		wOBJ_Config = CLS_Config()
		wResAPI = wOBJ_Config.SetTwitterAPI( wTwitterAccount )
		if wResAPI['Result']!=True :
			###失敗
			wRes['Reason'] = "Set Twitter API failed: " + wResAPI['Reason']
			CLS_OSIF.sErr( wRes )
			gVal.OBJ_DB.Close()
			return False
		
		#############################
		# Twitterリストの設定
		wResList = wOBJ_Config.SetTwitterList( wTwitterAccount )
		if wResList['Result']!=True :
			###失敗
			wRes['Reason'] = "Set Twitter List failed: " + wResList['Reason']
			CLS_OSIF.sErr( wRes )
			gVal.OBJ_DB.Close()
			return False
		
		#############################
		# 登録してなければデータベースに登録する
		if wFLG_UserRegisted==False :
			wQuery = "insert into tbl_user_data values (" + \
						"'" + wTwitterAccount + "'," + \
						"'" + wResAPI['Responce']['APIkey'] + "'," + \
						"'" + wResAPI['Responce']['APIsecret'] + "'," + \
						"'" + wResAPI['Responce']['ACCtoken'] + "'," + \
						"'" + wResAPI['Responce']['ACCsecret'] + "'," + \
						"False," + \
						"'1901-01-01 00:00:00'," + \
						"'" + wResList['Responce']['norlist'] + "'," + \
						"'" + wResList['Responce']['urflist'] + "' " + \
						") ;"
			
			wResDB = gVal.OBJ_DB.RunQuery( wQuery )
			wResDB = gVal.OBJ_DB.GetQueryStat()
			if wResDB['Result']!=True :
				##失敗
				wRes['Reason'] = "Run Query is failed(2): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
				CLS_OSIF.sErr( wRes )
				gVal.OBJ_DB.Close()
				return False
			
			wStr = "データベースにユーザ " + wTwitterAccount + " を登録しました。" + '\n'
			CLS_OSIF.sPrn( wStr )
		#############################
		# 登録されていればキーを更新する
		else:
			wQuery = "update tbl_user_data set " + \
					"apikey = '"    + wResAPI['Responce']['APIkey'] + "', " + \
					"apisecret = '" + wResAPI['Responce']['APIsecret'] + "', " + \
					"acctoken = '"  + wResAPI['Responce']['ACCtoken'] + "', " + \
					"accsecret = '" + wResAPI['Responce']['ACCsecret'] + "', " + \
					"locked = False, " + \
					"lupdate = '1901-01-01 00:00:00', " + \
					"norlist = '" + wResList['Responce']['norlist'] + "', " + \
					"urflist = '" + wResList['Responce']['urflist'] + "' " + \
					"where twitterid = '" + wTwitterAccount + "' ;"
			
			wResDB = gVal.OBJ_DB.RunQuery( wQuery )
			wResDB = gVal.OBJ_DB.GetQueryStat()
			if wResDB['Result']!=True :
				##失敗
				wRes['Reason'] = "Run Query is failed(3): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
				CLS_OSIF.sErr( wRes )
				gVal.OBJ_DB.Close()
				return False
			
			wStr = "データベースのユーザ " + wTwitterAccount + " を更新しました。" + '\n'
			CLS_OSIF.sPrn( wStr )
		
		#############################
		# 終わり
		gVal.OBJ_DB.Close()
		return True



#####################################################
# 全初期化
#   作業ファイルとDBを全て初期化する
#####################################################
	def AllInit(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Setup"
		wRes['Func']  = "AllInit"
		
		#############################
		# 実行の確認
		wStr = "データベースと全ての作業ファイルをクリアします。" + '\n'
		CLS_OSIF.sPrn( wStr )
		wSelect = CLS_OSIF.sInp( "よろしいですか？(y/N)=> " )
		if wSelect!="y" :
			##キャンセル
			return True
		
		#############################
		# ユーザフォルダの存在チェック
		if CLS_File.sExist( gVal.DEF_USERDATA_PATH )!=True :
			## フォルダがなければ作成する
			if CLS_File.sMkdir( gVal.DEF_USERDATA_PATH )!=True :
				wRes['Reason'] = "フォルダの作成に失敗しました: path=" + gVal.DEF_USERDATA_PATH
				CLS_OSIF.sErr( wRes )
				return False
		
		#############################
		# DBに接続 (接続情報の作成)
		wStr = "データベースに接続します。データベースのパスワードを入力してください。" + '\n'
		wStr = wStr + "  Hostname=" + gVal.DEF_BD_HOST + " Database=" + gVal.DEF_BD_NAME + " Username=" + gVal.DEF_BD_USER
		CLS_OSIF.sPrn( wStr )
		
		###入力受け付け
		wPassword = CLS_OSIF.sGpp( "Password: " )
		
		###接続
		gVal.OBJ_DB = CLS_PostgreSQL_Use()
		wResDBconn = gVal.OBJ_DB.Create( gVal.DEF_BD_HOST, gVal.DEF_BD_NAME, gVal.DEF_BD_USER, wPassword )
		wResDBconn = gVal.OBJ_DB.Connect()
		wResDB = gVal.OBJ_DB.GetDbStatus()
		if wResDBconn!=True :
			wRes['Reason'] = "DBの接続に失敗しました: reason=" + wResDB['Reason']
			CLS_OSIF.sErr( wRes )
			gVal.OBJ_DB.Close()
			return False
		
		###結果の確認
		if wResDB['Init']!=True :
			wRes['Reason'] = "DBが初期化できてません"
			CLS_OSIF.sErr( wRes )
			gVal.OBJ_DB.Close()
			return False
		
		#############################
		# DB初期化
		self.__initDB( gVal.OBJ_DB )
		CLS_OSIF.sPrn( "データベースを初期化しました" + '\n' )
		
		#############################
		# 終わり
		gVal.OBJ_DB.Close()
		CLS_OSIF.sPrn( "全初期化が正常終了しました。" )
		
		#############################
		# セットアップの確認
		wStr = "続いてセットアップを続行しますか。" + '\n'
		CLS_OSIF.sPrn( wStr )
		wSelect = CLS_OSIF.sInp( "セットアップする？(y/N)=> " )
		if wSelect!="y" :
			##キャンセル
			return True
		
		###入力の手間を省くため、パスワードを引き継ぐ
		self.Setup( inPassWD=wPassword )
		self.Add( inPassWD=wPassword )
		return True



#####################################################
# データ追加モード
#####################################################
	def Add( self, inPassWD=None, inDBInit=False ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Setup"
		wRes['Func']  = "Add"
		
		CLS_OSIF.sPrn( "追加データをデータベースに追加します" + '\n' )
		
		#############################
		# ユーザフォルダの存在チェック
		if CLS_File.sExist( gVal.DEF_USERDATA_PATH )!=True :
			## フォルダがないと失敗扱い
			wRes['Reason'] = "ユーザフォルダがありません: path=" + gVal.DEF_USERDATA_PATH
			CLS_OSIF.sErr( wRes )
			return False
		
		#############################
		# デフォルトの除外ユーザ・文字の読み出し
		# ・除外ファイルの解凍
		# ・読み出し
		# ・解凍の削除
		
		###デフォルト除外文字ファイルの解凍
		wExcWordArc_Path = gVal.DEF_STR_FILE['ExcWordArc']											#アーカイブ
		wMelt_ExcWordArc_Path = gVal.DEF_USERDATA_PATH + gVal.DEF_STR_FILE['Melt_ExcWordArc_path']	#アーカイブ解凍先
		if CLS_File.sArciveMelt( inSrcPath=wExcWordArc_Path, inDstPath=gVal.DEF_USERDATA_PATH )!=True :
			wRes['Reason'] = "デフォルト除外文字ファイルの解凍に失敗しました: srcpath=" + wExcWordArc_Path + " dstpath=" + wMelt_ExcWordArc_Path
			CLS_OSIF.sErr( wRes )
			return False
		
		###ローカルに読み出し
		wFilePath = gVal.DEF_USERDATA_PATH + gVal.DEF_STR_FILE['Melt_ExcUserName']
		wARR_ExcUserName = []
		if CLS_File.sReadFile( wFilePath, outLine=wARR_ExcUserName )!=True :
			wRes['Reason'] = "解凍ファイルが見つかりません: path=" + wFilePath
			CLS_OSIF.sErr( wRes )
			return False
		
		wFilePath = gVal.DEF_USERDATA_PATH + gVal.DEF_STR_FILE['Melt_ExcWord']
		wARR_ExcWord = []
		if CLS_File.sReadFile( wFilePath, outLine=wARR_ExcWord )!=True :
			wRes['Reason'] = "解凍ファイルが見つかりません: path=" + wFilePath
			CLS_OSIF.sErr( wRes )
			return False
		
		###解凍したフォルダ削除
		if CLS_File.sRmtree( wMelt_ExcWordArc_Path )!=True :
			wRes['Reason'] = "解凍フォルダの削除に失敗しました: path=" + wMelt_ExcWordArc_Path
			CLS_OSIF.sErr( wRes )
			return False
		
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "PC時間の取得に失敗しました"
			CLS_OSIF.sErr( wRes )
			return False
		### wTD['TimeDate']
		
		#############################
		# DBに接続 (接続情報の作成)
		wPassword = inPassWD
		
		###パスワードが未設定なら入力を要求する
		if wPassword==None :
			wStr = "データベースに接続します。データベースのパスワードを入力してください。" + '\n'
			wStr = wStr + "  Hostname=" + gVal.DEF_BD_HOST + " Database=" + gVal.DEF_BD_NAME + " Username=" + gVal.DEF_BD_USER
			CLS_OSIF.sPrn( wStr )
			
			###入力受け付け
			wPassword = CLS_OSIF.sGpp( "Password: " )
		
		###接続
		gVal.OBJ_DB = CLS_PostgreSQL_Use()
		wResDBconn = gVal.OBJ_DB.Create( gVal.DEF_BD_HOST, gVal.DEF_BD_NAME, gVal.DEF_BD_USER, wPassword )
		wResDBconn = gVal.OBJ_DB.Connect()
		wResDB = gVal.OBJ_DB.GetDbStatus()
		if wResDBconn!=True :
			wRes['Reason'] = "DBの接続に失敗しました: reason=" + wResDB['Reason']
			CLS_OSIF.sErr( wRes )
			gVal.OBJ_DB.Close()
			return False
		
		###結果の確認
		if wResDB['Init']!=True :
			wRes['Reason'] = "DBが初期化できてません"
			CLS_OSIF.sErr( wRes )
			gVal.OBJ_DB.Close()
			return False
		
		#############################
		# データベースを初期化する
		# ※初期化しないほうが便利
		if inDBInit==True :
			self.__create_TBL_EXC_USERNAME( gVal.OBJ_DB )
			self.__create_TBL_EXC_WORD( gVal.OBJ_DB )
		
		#############################
		# データベースから除外ユーザ名を取得
		wQuery = "select word from tbl_exc_username " + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			CLS_OSIF.sErr( wRes )
			gVal.OBJ_DB.Close()
			return False
		
		### リスト型に整形
		wARR_RateWord = []
		gVal.OBJ_DB.ChgList( wResDB['Responce']['Data'], outList=wARR_RateWord )
		
		gVal.STR_ExcUserName = []
		#############################
		# アーカイブの除外ユーザ名を検索
		#   データベースになければ登録する
		# 除外ユーザ名を登録する
		wFLG_newAdd = False
		for wWord in wARR_ExcUserName :
			if wWord in wARR_RateWord :
				###既登録
				gVal.STR_ExcUserName.append( wWord )
				continue
			
			wFLG_newAdd = True
			wWord = wWord.replace( "'", "''" )
			wQuery = "insert into tbl_exc_username values (" + \
						"'" + str(wTD['TimeDate']) + "'," + \
						"True," + \
						"'" + wWord + "'" + \
						") ;"
			
			wResDB = gVal.OBJ_DB.RunQuery( wQuery )
			wResDB = gVal.OBJ_DB.GetQueryStat()
			if wResDB['Result']!=True :
				##失敗
				wRes['Reason'] = "Run Query is failed(2): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
				CLS_OSIF.sErr( wRes )
				gVal.OBJ_DB.Close()
				return False
			
			###追加
			gVal.STR_ExcUserName.append( wWord )
			CLS_OSIF.sPrn( "除外ユーザ名が追加されました: " + wWord )
		
		if wFLG_newAdd==False :
			CLS_OSIF.sPrn( "新規の除外ユーザ名はありませんでした" )
		
		#############################
		# データベースから除外文字を取得
		wQuery = "select word from tbl_exc_word " + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(3): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			CLS_OSIF.sErr( wRes )
			gVal.OBJ_DB.Close()
			return False
		
		### リスト型に整形
		wARR_RateWord = []
		gVal.OBJ_DB.ChgList( wResDB['Responce']['Data'], outList=wARR_RateWord )
		
		gVal.STR_ExcWord = []
		#############################
		# アーカイブの除外文字を検索
		#   データベースになければ登録する
		# 除外文字を登録する
		wFLG_newAdd = False
		for wWord in wARR_ExcWord :
			if wWord in wARR_RateWord :
				###既登録
				gVal.STR_ExcWord.append( wWord )
				continue
			
			wFLG_newAdd = True
			wWord = wWord.replace( "'", "''" )
			wQuery = "insert into tbl_exc_word values (" + \
						"'" + str(wTD['TimeDate']) + "'," + \
						"True," + \
						"'" + wWord + "'" + \
						") ;"
			
			wResDB = gVal.OBJ_DB.RunQuery( wQuery )
			wResDB = gVal.OBJ_DB.GetQueryStat()
			if wResDB['Result']!=True :
				##失敗
				wRes['Reason'] = "Run Query is failed(4): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
				CLS_OSIF.sErr( wRes )
				gVal.OBJ_DB.Close()
				return False
			
			###追加
			gVal.STR_ExcWord.append( wWord )
			CLS_OSIF.sPrn( "除外文字が追加されました: " + wWord )
		
		if wFLG_newAdd==False :
			CLS_OSIF.sPrn( "新規の除外文字はありませんでした" )
		
		#############################
		# DBを閉じる
		gVal.OBJ_DB.Close()
		
		#############################
		# 正常終了
		CLS_OSIF.sPrn( "データの追加が正常終了しました。" )
		return True



#####################################################
# クリア
#   一部のDBを初期化する
#####################################################
	def Clear(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_Setup"
		wRes['Func']  = "Clear"
		
		#############################
		# 実行の確認
		wStr = "ログと、キーユーザ検索データ用のデータベースをクリアします。" + '\n'
		CLS_OSIF.sPrn( wStr )
		wSelect = CLS_OSIF.sInp( "よろしいですか？(y/N)=> " )
		if wSelect!="y" :
			##キャンセル
			return True
		
		#############################
		# DBに接続 (接続情報の作成)
		wStr = "データベースに接続します。データベースのパスワードを入力してください。" + '\n'
		wStr = wStr + "  Hostname=" + gVal.DEF_BD_HOST + " Database=" + gVal.DEF_BD_NAME + " Username=" + gVal.DEF_BD_USER
		CLS_OSIF.sPrn( wStr )
		
		###入力受け付け
		wPassword = CLS_OSIF.sGpp( "Password: " )
		
		###接続
		gVal.OBJ_DB = CLS_PostgreSQL_Use()
		wResDBconn = gVal.OBJ_DB.Create( gVal.DEF_BD_HOST, gVal.DEF_BD_NAME, gVal.DEF_BD_USER, wPassword )
		wResDBconn = gVal.OBJ_DB.Connect()
		wResDB = gVal.OBJ_DB.GetDbStatus()
		if wResDBconn!=True :
			wRes['Reason'] = "DBの接続に失敗しました: reason=" + wResDB['Reason']
			CLS_OSIF.sErr( wRes )
			gVal.OBJ_DB.Close()
			return False
		
		###結果の確認
		if wResDB['Init']!=True :
			wRes['Reason'] = "DBが初期化できてません"
			CLS_OSIF.sErr( wRes )
			gVal.OBJ_DB.Close()
			return False
		
##		#############################
##		# DB初期化
##		
##		#############################
##		# DB初期化：tbl_log_data
##		wStr = "tbl_log_data（ログデータ） " + '\n'
##		wStr = wStr + "をクリアしますか？(y/N)=> "
##		wSelect = CLS_OSIF.sInp( wStr )
##		if wSelect!="y" :
##			self.__create_TBL_LOG_DATA( inDBobj )
##			CLS_OSIF.sPrn( "クリアしました。" + '\n' )
##		
##		#############################
##		# DB初期化：tbl_keyword_data
##		wStr = "tbl_keyword_data（キーユーザ検索用データ） " + '\n'
##		wStr = wStr + "をクリアしますか？(y/N)=> "
##		wSelect = CLS_OSIF.sInp( wStr )
##		if wSelect!="y" :
##			self.__create_TBL_KEYWORD_DATA( inDBobj )
##			CLS_OSIF.sPrn( "クリアしました。" + '\n' )
##		
##		#############################
##		# DB初期化：tbl_favo_data
##		wStr = "tbl_favo_data（いいね保存用データ） " + '\n'
##		wStr = wStr + "をクリアしますか？(y/N)=> "
##		wSelect = CLS_OSIF.sInp( wStr )
##		if wSelect!="y" :
##			self.__create_TBL_FAVO_DATA( inDBobj )
##			CLS_OSIF.sPrn( "クリアしました。" + '\n' )
##		
##		#############################
##		# DB初期化：tbl_follower_data
##		wStr = "tbl_follower_data（フォロー・フォロワー管理用データ） " + '\n'
##		wStr = wStr + "をクリアしますか？(y/N)=> "
##		wSelect = CLS_OSIF.sInp( wStr )
##		if wSelect!="y" :
##			self.__create_TBL_FOLLOWER_DATA( inDBobj )
##			CLS_OSIF.sPrn( "クリアしました。" + '\n' )
##		
		#############################
		# DB初期化
		self.__create_TBL_LOG_DATA( gVal.OBJ_DB )
		self.__create_TBL_KEYWORD_DATA( gVal.OBJ_DB )
		self.__create_TBL_EXC_FOLLOWID( gVal.OBJ_DB )
		self.__create_TBL_EXC_TWITTERID( gVal.OBJ_DB )
		self.__create_TBL_EXC_TWEETID( gVal.OBJ_DB )
		
		#############################
		# 終わり
		gVal.OBJ_DB.Close()
		CLS_OSIF.sPrn( "クリアが正常終了しました。" )
		
		return True



#####################################################
# データベースの初期化
#####################################################
	def __initDB( self, inDBobj ):
		self.__create_TBL_USER_DATA( inDBobj )
		self.__create_TBL_LOG_DATA( inDBobj )
		self.__create_TBL_FAVO_DATA( inDBobj )
		self.__create_TBL_FOLLOWER_DATA( inDBobj )
		self.__create_TBL_KEYWORD_DATA( inDBobj )
		self.__create_TBL_EXC_FOLLOWID( inDBobj )
		self.__create_TBL_EXC_USERNAME( inDBobj )
		self.__create_TBL_EXC_WORD( inDBobj )
		self.__create_TBL_EXC_TWITTERID( inDBobj )
		self.__create_TBL_EXC_TWEETID( inDBobj )
		return True

	#####################################################
	def __allDrop( self, inDBobj ):
		wQuery = "drop table if exists tbl_user_data ;"
		inOBJ_DB.RunQuery( wQuery )
		wQuery = "drop table if exists tbl_log_data ;"
		inOBJ_DB.RunQuery( wQuery )
		wQuery = "drop table if exists tbl_favo_data ;"
		inOBJ_DB.RunQuery( wQuery )
		wQuery = "drop table if exists tbl_follower_data ;"
		inOBJ_DB.RunQuery( wQuery )
		wQuery = "drop table if exists tbl_keyword_data ;"
		inOBJ_DB.RunQuery( wQuery )
		wQuery = "drop table if exists tbl_exc_followid ;"
		inOBJ_DB.RunQuery( wQuery )
		wQuery = "drop table if exists tbl_exc_username ;"
		inOBJ_DB.RunQuery( wQuery )
		wQuery = "drop table if exists tbl_exc_word ;"
		inOBJ_DB.RunQuery( wQuery )
		wQuery = "drop table if exists tbl_exc_twitterid ;"
		inOBJ_DB.RunQuery( wQuery )
		wQuery = "drop table if exists tbl_exc_tweetid ;"
		inOBJ_DB.RunQuery( wQuery )
		return True



#####################################################
# テーブル作成: TBL_USER_DATA
#####################################################
	def __create_TBL_USER_DATA( self, inOBJ_DB, inTBLname="tbl_user_data" ):
		#############################
		# テーブルのドロップ
		wQuery = "drop table if exists " + inTBLname + ";"
		inOBJ_DB.RunQuery( wQuery )
		
		#############################
		# テーブル枠の作成
		wQuery = "create table " + inTBLname + "(" + \
					"twitterid   TEXT  NOT NULL," + \
					"apikey      TEXT  NOT NULL," + \
					"apisecret   TEXT  NOT NULL," + \
					"acctoken    TEXT  NOT NULL," + \
					"accsecret   TEXT  NOT NULL," + \
					"locked      BOOL  DEFAULT false," + \
					"lupdate     TIMESTAMP," + \
					"norlist     TEXT  DEFAULT '(none)'," + \
					"urflist     TEXT  DEFAULT '(none)'," + \
					"favorp      BOOL  DEFAULT false," + \
					"favort      BOOL  DEFAULT false," + \
					"favoirt     BOOL  DEFAULT false," + \
					"favotag     BOOL  DEFAULT true," + \
					"favolen     INTEGER DEFAULT 8," + \
					" PRIMARY KEY ( twitterid ) ) ;"
		
##					"twitterid   記録したユーザ(Twitter ID)
##					"apikey      Twitter Devで取ったAPI key
##					"apisecret   Twitter Devで取ったAPI secret
##					"acctoken    Twitter Devで取ったAccess Token Key
##					"accsecret   Twitter Devで取ったAccess Token secret
##					"locked      
##					"lupdate     
##					"norlist     normalリスト名
##					"urflist     un_refollowリスト名
		inOBJ_DB.RunQuery( wQuery )
		return



#####################################################
# テーブル作成: TBL_LOG_DATA
#####################################################
	def __create_TBL_LOG_DATA( self, inOBJ_DB, inTBLname="tbl_log_data" ):
		#############################
		# テーブルのドロップ
		wQuery = "drop table if exists " + inTBLname + ";"
		inOBJ_DB.RunQuery( wQuery )
		
		#############################
		# テーブル枠の作成
		wQuery = "create table " + inTBLname + "(" + \
					"twitterid   TEXT  NOT NULL," + \
					"level       CHAR(1) DEFAULT '-'," + \
					"log_class   TEXT  NOT NULL," + \
					"log_func    TEXT  NOT NULL," + \
					"reason      TEXT  NOT NULL," + \
					"lupdate     TIMESTAMP" + \
					" ) ;"
		
##					"twitterid   記録したユーザ(Twitter ID)
##					"level       ログレベル
##					"reason      理由
##					"lupdate     記録日時
		inOBJ_DB.RunQuery( wQuery )
		return



#####################################################
# テーブル作成: TBL_FAVO_DATA
#####################################################
	def __create_TBL_FAVO_DATA( self, inOBJ_DB, inTBLname="tbl_favo_data" ):
		#############################
		# テーブルのドロップ
		wQuery = "drop table if exists " + inTBLname + ";"
		inOBJ_DB.RunQuery( wQuery )
		
		#############################
		# テーブル枠の作成
		wQuery = "create table " + inTBLname + "(" + \
					"twitterid   TEXT  NOT NULL," + \
					"regdate     TIMESTAMP," + \
					"limited     BOOL  DEFAULT false," + \
					"removed     BOOL  DEFAULT false," + \
					"id          TEXT  NOT NULL," + \
					"user_name   TEXT  NOT NULL," + \
					"screen_name TEXT  NOT NULL," + \
					"text        TEXT  NOT NULL," + \
					"created_at  TIMESTAMP" + \
					" ) ;"
		
##					"twitterid   記録したユーザ(Twitter ID)
##					"regdate     DB登録日時
##					"limited     ファボ期限切れ =ファボ解除対象
##					"removed     ファボ解除済み
##					"id          ツイート ID
##					"user_name   ツイート ユーザ名
##					"screen_name ツイート スクリーン名
##					"text        ツイート 内容
##					"created_at  ツイート 日時
		inOBJ_DB.RunQuery( wQuery )
		return



#####################################################
# テーブル作成: TBL_FOLLOWER_DATA
#####################################################
	def __create_TBL_FOLLOWER_DATA( self, inOBJ_DB, inTBLname="tbl_follower_data" ):
		#############################
		# テーブルのドロップ
		wQuery = "drop table if exists " + inTBLname + ";"
		inOBJ_DB.RunQuery( wQuery )
		
		#############################
		# テーブル枠の作成
		wQuery = "create table " + inTBLname + "(" + \
					"twitterid   TEXT  NOT NULL," + \
					"regdate     TIMESTAMP," + \
					"r_myfollow  BOOL  DEFAULT false," + \
					"r_remove    BOOL  DEFAULT false," + \
					"rc_follower BOOL  DEFAULT false," + \
					"foldate     TIMESTAMP," + \
					"limited     BOOL  DEFAULT false," + \
					"removed     BOOL  DEFAULT false," + \
					"id          TEXT  NOT NULL," + \
					"user_name   TEXT  NOT NULL," + \
					"screen_name TEXT  NOT NULL," + \
					"lastcount   INTEGER," + \
					"lastdate    TIMESTAMP," + \
					"reason      TEXT," + \
					"favoid      TEXT," + \
					"favodate     TIMESTAMP," + \
					" ) ;"
		
##					"twitterid   記録したユーザ(Twitter ID)
##					"regdate     DB登録日時
##					"r_myfollow  1度でもフォローしたことがある
##					"r_remove    1度でもリムーブされたことがある
##					"rc_follower 前のチェックでフォローされてた
##					"foldate     フォローした日
##					"limited     リムーブ期限切れ or 自動リムーブ解除対象
##					"removed     リムーブ済み
##					"id          ツイート ID
##					"user_name   ツイート ユーザ名
##					"screen_name ツイート スクリーン名
		
		inOBJ_DB.RunQuery( wQuery )
		return



#####################################################
# テーブル作成: TBL_KEYWORD_DATA
#####################################################
	def __create_TBL_KEYWORD_DATA( self, inOBJ_DB, inTBLname="tbl_keyword_data" ):
		#############################
		# テーブルのドロップ
		wQuery = "drop table if exists " + inTBLname + ";"
		inOBJ_DB.RunQuery( wQuery )
		
		#############################
		# テーブル枠の作成
		wQuery = "create table " + inTBLname + "(" + \
					"twitterid   TEXT  NOT NULL," + \
					"regdate     TIMESTAMP," + \
					"choice      BOOL  DEFAULT false," + \
					"id          INTEGER NOT NULL," + \
					"keyword     TEXT  NOT NULL," + \
					"count       INTEGER NOT NULL," + \
					"incimage    BOOL  DEFAULT false," + \
					"excimage    BOOL  DEFAULT false," + \
					"incvideo    BOOL  DEFAULT false," + \
					"excvideo    BOOL  DEFAULT false," + \
					"inclink     BOOL  DEFAULT false," + \
					"exclink     BOOL  DEFAULT false," + \
					"ofonly      BOOL  DEFAULT false," + \
					"jponly      BOOL  DEFAULT true," + \
					"excrt       BOOL  DEFAULT false," + \
					"excsensi    BOOL  DEFAULT true," + \
					"arashi      BOOL  DEFAULT false" + \
					" ) ;"
		
##					"twitterid   記録したユーザ(Twitter ID)
##					"regdate     DB登録日時
##					"choice      選択中
##					"id          検索キー番号
##					"keyword     検索キーワード
		
		inOBJ_DB.RunQuery( wQuery )
		return



#####################################################
# テーブル作成: TBL_EXC_FOLLOWID
#####################################################
	def __create_TBL_EXC_FOLLOWID( self, inOBJ_DB, inTBLname="tbl_exc_followid" ):
		#############################
		# テーブルのドロップ
		wQuery = "drop table if exists " + inTBLname + ";"
		inOBJ_DB.RunQuery( wQuery )
		
		#############################
		# テーブル枠の作成
		wQuery = "create table " + inTBLname + "(" + \
					"regdate     TIMESTAMP," + \
					"id          TEXT  NOT NULL, " + \
					" PRIMARY KEY ( id ) ) ;"
		
##					"regdate     DB登録日時
##					"id          Tweet ID
		
		inOBJ_DB.RunQuery( wQuery )
		return



#####################################################
# テーブル作成: TBL_EXC_USERNAME
#####################################################
	def __create_TBL_EXC_USERNAME( self, inOBJ_DB, inTBLname="tbl_exc_username" ):
		#############################
		# テーブルのドロップ
		wQuery = "drop table if exists " + inTBLname + ";"
		inOBJ_DB.RunQuery( wQuery )
		
		#############################
		# テーブル枠の作成
		wQuery = "create table " + inTBLname + "(" + \
					"regdate     TIMESTAMP," + \
					"choice      BOOL  DEFAULT true," + \
					"word        TEXT  NOT NULL, " + \
					" PRIMARY KEY ( word ) ) ;"
		
##					"regdate     DB登録日時
##					"keyword     検索キーワード
		
		inOBJ_DB.RunQuery( wQuery )
		return



#####################################################
# テーブル作成: TBL_EXC_WORD
#####################################################
	def __create_TBL_EXC_WORD( self, inOBJ_DB, inTBLname="tbl_exc_word" ):
		#############################
		# テーブルのドロップ
		wQuery = "drop table if exists " + inTBLname + ";"
		inOBJ_DB.RunQuery( wQuery )
		
		#############################
		# テーブル枠の作成
		wQuery = "create table " + inTBLname + "(" + \
					"regdate     TIMESTAMP," + \
					"choice      BOOL  DEFAULT true," + \
					"word        TEXT  NOT NULL, " + \
					" PRIMARY KEY ( word ) ) ;"
		
##					"regdate     DB登録日時
##					"keyword     検索キーワード
		
		inOBJ_DB.RunQuery( wQuery )
		return



#####################################################
# テーブル作成: TBL_EXC_TWITTERID
#####################################################
	def __create_TBL_EXC_TWITTERID( self, inOBJ_DB, inTBLname="tbl_exc_twitterid" ):
		#############################
		# テーブルのドロップ
		wQuery = "drop table if exists " + inTBLname + ";"
		inOBJ_DB.RunQuery( wQuery )
		
		#############################
		# テーブル枠の作成
		wQuery = "create table " + inTBLname + "(" + \
					"regdate     TIMESTAMP," + \
					"id          TEXT  NOT NULL, " + \
					"screen_name TEXT  NOT NULL, " + \
					"count       INTEGER NOT NULL," + \
					"lastdate    TIMESTAMP," + \
					"arashi      BOOL  DEFAULT true," + \
					"reason_id   INTEGER NOT NULL," + \
					" PRIMARY KEY ( id ) ) ;"
		
##					"regdate     DB登録日時
##					"id          Twitter ID
##					"screen_name Twitter ID(英語)
##					"count       荒らした回数カウンタ
##					"lastdate    最後の判定ツイート日時
##					"arashi      荒らしか
##					"reason_id   荒らし理由番号(荒らし判定時)
		
		inOBJ_DB.RunQuery( wQuery )
		return



#####################################################
# テーブル作成: TBL_EXC_TWEETID
#####################################################
	def __create_TBL_EXC_TWEETID( self, inOBJ_DB, inTBLname="tbl_exc_tweetid" ):
		#############################
		# テーブルのドロップ
		wQuery = "drop table if exists " + inTBLname + ";"
		inOBJ_DB.RunQuery( wQuery )
		
		#############################
		# テーブル枠の作成
		wQuery = "create table " + inTBLname + "(" + \
					"regdate     TIMESTAMP," + \
					"id          TEXT  NOT NULL, " + \
					" PRIMARY KEY ( id ) ) ;"
		
##					"regdate     DB登録日時
##					"id          Tweet ID
		
		inOBJ_DB.RunQuery( wQuery )
		return



