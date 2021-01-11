#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : グローバル値
# 
# ::Update= 2021/1/11
#####################################################

#####################################################
class gVal() :

#############################
# ※ユーザ自由変更※
	DEF_BD_HOST         = 'localhost'						#データベースホスト名
	DEF_BD_NAME         = 'lucibot'							#データベース名
	DEF_BD_USER         = 'lucibot'							#データベースユーザ名
	DEF_USERDATA_PATH   = '../lucibot_data/'				#ユーザデータフォルダ
	DEF_TIMEZONE = 9										# 9=日本時間 最終更新日補正用
	DEF_MOJI_ENCODE = 'utf-8'								#文字エンコード

#############################
# システム情報
	#データversion(文字)
	DEF_CONFIG_VER = "1"

	STR_SystemInfo = {
		"Client_Name"	: "るしぼっと Win",
		"ProjectName"	: "",
		"github"		: "",
		"Admin"			: "",
		"TwitterURL"	: "",
		"Update"		: "",
		"Version"		: "",
		
		"PythonVer"		: 0,
		"HostName"		: "",
		
		"APIrect"		: "",
		"RunMode"		: "normal"
			# normal= 通常モード
			# setup = セットアップモード
			# init  = 全初期化モード
	}

#############################
# ユーザ情報
	STR_UserInfo = {
		"Account"	: "",			#Twitterアカウント名
		"NorList"	: "",			#一般ユーザリスト名
		"UrfList"	: "",			#フォロー解除リスト名
		"id"		: "",			#Twitter ID(番号)
		"Traffic"	: False,		#Twitterにトラヒックを報告するか
		
		"UserFolder_path"	: ""	#ユーザフォルダパス
	}

#############################
# 自動いいね設定
	STR_AutoFavo = {
		"Rip"		: False,		#リプライを含める
		"Ret"		: False,		#リツイートを含める
		"iRet"		: False,		#引用リツイートを含める
		"Tag"		: True,			#タグを含める
		
		"Len"		: 8				#対象範囲(時間)
	}

#############################
# 検索モード
	STR_SearchMode = {}
	# [0]..手動用
	# [1]以降..自動用

#############################
# ユーザ管理情報
	STR_UserAdminInfo = {
		"user_name"			: None,		#Twitterユーザ名(日本語)
		"screen_name"		: None,		#Twitterアカウント名(英語)
		"id"        		: -1,
		"statuses_count"	: -1,
		
		"DB_exist"	    : False,
		"DB_r_myfollow"	: False,
		"DB_r_remove"	: False,
		"DB_limited"	: False,
		
		"Protect"	: False,
		"MyFollow"	: False,
		"Follower"	: False,
		
		"MyBlock"	: False,
		"Blocked"	: False,
		
		"NorList"	: False,
		"UnrList"	: False
	}

#############################
# トラヒック情報
	STR_TrafficInfo = {
		"timeline"			: 0,	#取得タイムライン数
		
									#いいね情報
		"favo"				: 0,	#現いいね数
		"favoremovet"		: 0,	#解除対象 いいね数
		"favoremove"		: 0,	#解除実行 いいね数
		
		"myfollow"			: 0,	#現フォロー数
		"follower"			: 0,	#現フォロワー数
		"piefollow"			: 0,	#片フォロー数
		"newfollower"		: 0,	#新規フォロワー数
		"selremove"			: 0,	#被リムーブ数
		
									#自動リムーブ情報
		"autofollowt"		: 0,	#自動リムーブ 対象数
		"autofollow"		: 0,	#自動リムーブ 実行数
		
									#自動いいね情報
		"autofavot"			: 0,	#自動いいね 対象
		"autofavo"			: 0,	#自動いいね 実施数
		
									#荒らし情報
		"arashi"			: 0,	#荒らし登録者数
		"arashii"			: 0,	#荒らし検出回数
		"arashir"			: 0,	#荒らし解除者数
		
									#データベース情報
		"dbreq"				: 0,	#クエリ要求回数
		"dbins"				: 0,	#DB挿入回数
		"dbup"				: 0,	#DB更新回数
		"dbdel"				: 0,	#DB削除回数
		
		"run"				: 0,	#Bot実行回数
		"update"			: None	#トラヒック更新日時
	}



#############################
# 除外ユーザ名・除外文字・除外Twitter ID
	STR_ExcUserName = []			#除外ユーザ名
	STR_ExcWord     = []			#除外ワード
	STR_ExcTwitterID = []			#除外Twitter ID
	STR_RateExcTwitterID = []		#除外Twitter ID(処理前DB)
	STR_ExcTwitterID_Info = {}		#除外Twitter ID(DB詳細)
	STR_ExcFollowID = []			#除外Follow候補

	STR_RateExcTweetID = []			#Tweet ID
	STR_ExcTweetID = []				#新規Tweet ID

#############################
# Timeline調整数
	DEF_STR_TLNUM = {

		"resetAPImin"		: 15,						#APIリセット周期(分)
		"lockLimmin"		: 2,						#排他保持時間

		"favoLimmin"		: 2880,						#いいね解除時間 2日 (60x24)x2=2880(分)
		"favoDBLimmin"		: 20160,					#DBのいいね削除時間 14日 (60x24)x14=20160(分)
		"rFavoLimNum"		: 5,						# 1回のいいね解除数
		"favoLimWait"		: 115,						#いいね解除処理待ち(秒)   900秒/8回(createの場合)

		"AutoFavoCount"		: 20,						#自動いいね タイムライン取得数
		"AutoFavoWait"		: 150,						#自動いいね待機(秒)
		"AutoFavoSkipWait"	: 5,						#自動いいね スキップ待機(秒)
		"AutoFavoRateHour"	: 12,						#自動いいね 前回のいいねからの経過時間(時間)

		"removeLimmin"		: 4320,						#自動リムーブ時間 3日 (60x24)x3=7200(分)
		"rRemoveLimNum"		: 5,						# 1回のリムーブ解除数
		"removeLimWait"		: 100,						#自動リムーブ処理待ち(秒) 900秒/3回(createの場合)

		"searchRoundNum"	: 7,						#1検索の回数(ページング)
		"maxKeywordNum"		: 6,						#最大キーワード数
		"randKeyUserNum"	: 20,						#キーユーザ ランダム選出数
		"randFollowNum"		: 3,						#キーユーザフォロー選出数
														#  ※TwitterAPI(内部)の仕様で4以上を指定しても制限がかかる
		"excFollowIDdays"	: 14,						#除外候補保持日数
		
		"getTwitTLnum"		: 200,						#TwitterのTL取得数(Twitter仕様は最大200)

		"excTwitterID"		: 3,						#荒らし判定回数
		"excTwitterIDdays"	: 14,						#荒らしID保持日数
		"excTweetDays"		: 14,						#Tweet保持日数

		"logShortLen"		: 100,						#ログ表示 ショートモード
		"(dummy)"			: ""
	}

#############################
# ファイルパス
#   ファイルは語尾なし、フォルダは_path
	DEF_DATAPATH = "data/"

	DEF_STR_FILE = {
		"Readme"				: "readme.md",
		"ExcWordArc"			: DEF_DATAPATH + "DEF_ExcWordArc.zip",
		
		"Melt_ExcWordArc_path"	: "DEF_ExcWordArc",
		"Melt_ExcWord"			: "DEF_ExcWordArc/DEF_ExcWord.txt",
		"Melt_ExcUserName"		: "DEF_ExcWordArc/DEF_ExcUserName.txt",
		"(dummy)"				: 0
	}

	DEF_DISPPATH = "script/disp/"

	DEF_STR_DISPFILE = {
		"MainConsole"			: DEF_DISPPATH + "main_console.disp",
		"SearchConsole"			: DEF_DISPPATH + "search_console.disp",
		"KeyuserConsole"		: DEF_DISPPATH + "keyuser_console.disp",
		"UserAdminConsole"		: DEF_DISPPATH + "useradmin_console.disp",
		"AutoFavoConsole"		: DEF_DISPPATH + "autofavo_console.disp",
		
		"(dummy)"				: 0
	}

#############################
# 定数
	DEF_PROF_SUBURL = "/web/accounts/"						#プロフ用サブURL
	DEF_TOOT_SUBURL = "/web/statuses/"						#トゥート用サブURL

	DEF_LOCK_LOOPTIME = 2									#ロック解除待ち
	DEF_LOCK_WAITCNT  = 30									#  待ち時間: DEF_LOCK_LOOPTIME * DEF_LOCK_WAITCNT
	DEF_TEST_MODE     = "bottest"							#テストモード(引数文字)
	DEF_DATA_BOUNDARY = "|,|"



#############################
# 変数
	FLG_Console_Mode = False								#画面出力の有無
	FLG_Test_Mode    = False								#テストモード有無
	
	STR_DomainREM = []										#除外ドメイン
	STR_WordREM   = []										#禁止ワード
	
	OBJ_Twitter = ""										#Twitter
	OBJ_DB      = ""										#ぽすぐれ
	OBJ_L      = ""											#ログ用



#####################################################
# 構造体構築：検索モード
#####################################################
	@classmethod
	def sStruct_SearchMode(cls):
		#############################
		# 行の挿入
		wIndex = len(gVal.STR_SearchMode)
		gVal.STR_SearchMode.update({ wIndex : {} })
		
		gVal.STR_SearchMode[wIndex].update({ "Update"  : False })	#ローカル更新あり
		
		gVal.STR_SearchMode[wIndex].update({ "Choice"  : False })	#選択中
		gVal.STR_SearchMode[wIndex].update({ "id"      : -1 })		#検索キー番号
		gVal.STR_SearchMode[wIndex].update({ "Keyword" : "" })		#検索文字
		gVal.STR_SearchMode[wIndex].update({ "Count"   : 0 })		#ヒットカウンタ
		
		gVal.STR_SearchMode[wIndex].update({ "IncImage" : False })	#検索に画像を含める
		gVal.STR_SearchMode[wIndex].update({ "ExcImage" : False })	#検索は画像を除外
		gVal.STR_SearchMode[wIndex].update({ "IncVideo" : False })	#検索に動画を含める
		gVal.STR_SearchMode[wIndex].update({ "ExcVideo" : False })	#検索は動画を除外
		gVal.STR_SearchMode[wIndex].update({ "IncLink"  : False })	#検索にリンクを含める
		gVal.STR_SearchMode[wIndex].update({ "ExcLink"  : False })	#検索はリンクを除外
		
		gVal.STR_SearchMode[wIndex].update({ "OFonly"   : False })	#検索は公式マークのみ
		gVal.STR_SearchMode[wIndex].update({ "JPonly"   : True })		#検索は日本語のみ
		
		gVal.STR_SearchMode[wIndex].update({ "ExcRT"    : False })	#検索にリツイートを含めない
		gVal.STR_SearchMode[wIndex].update({ "ExcSensi" : True })	#検索にセンシティブな内容を含めない
		gVal.STR_SearchMode[wIndex].update({ "Arashi"   : False })	#荒らし除去をおこなうか
		
		return



#####################################################
# Init
#####################################################
	@classmethod
	def sInit(cls):
		#############################
		# 検索モード
		gVal.STR_SearchMode = {}
		return



#####################################################
# Init
#####################################################
##	def __init__(self):
##		return
##
##

#####################################################
# Delete
#####################################################
##	def __del__(self):
##		return
##
##

