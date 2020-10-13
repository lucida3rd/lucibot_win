#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : グローバル値
# 
# ::Update= 2020/10/13
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
		
		"UserFolder_path"	: ""	#ユーザフォルダパス
	}

#############################
# 検索モード
	STR_SearchMode = {
		"IncImage"	: False,		#検索に画像を含める
		"ExcImage"	: False,		#検索は画像を除外
		"IncVideo"	: False,		#検索に動画を含める
		"ExcVideo"	: False,		#検索は動画を除外
		"IncLink"	: False,		#検索にリンクを含める
		"ExcLink"	: False,		#検索はリンクを除外
		"OFonly"	: False,		#検索は公式マークのみ
		"JPonly"	: True,			#検索は日本語のみ
		
		"ExcRT"		: False,		#検索にリツイートを含めない
		"ExcSensi"	: True			#検索にセンシティブな内容を含めない
	}

#############################
# 除外ユーザ名
	STR_ExcUserName = [
		"高額",
		"攻略",
		"速報",
		"bot",
		"(**********)"
	]

#############################
# 除外文字
	STR_ExcWord = [
		"高額",
		"(**********)"
	]

#############################
# Timeline調整数
	DEF_STR_TLNUM = {

		"resetAPImin"		: 15,						#APIリセット周期(分)
		"lockLimmin"		: 2,						#排他保持時間

###		"favoLimmin"		: 4320,						#いいね解除時間 3日 (60x24)x3=4320(分)
		"favoLimmin"		: 2880,						#いいね解除時間 2日 (60x24)x2=2880(分)
		"favoDBLimmin"		: 20160,					#DBのいいね削除時間 14日 (60x24)x14=20160(分)
		"rFavoLimNum"		: 5,						# 1回のいいね解除数
		"favoLimWait"		: 185,						#いいね解除処理待ち(秒)   900秒

###		"removeLimmin"		: 4320,						#自動リムーブ時間 3日 (60x24)x3=4320(分)
		"removeLimmin"		: 7200,						#自動リムーブ時間 5日 (60x24)x5=7200(分)
		"rRemoveLimNum"		: 5,						# 1回のリムーブ解除数
		"removeLimWait"		: 185,						#自動リムーブ処理待ち(秒)   900秒

#		"searchRoundNum"	: 7,						#1検索の回数(ページング)
		"searchRoundNum"	: 1,						#1検索の回数(ページング)
		"maxKeywordNum"		: 6,						#最大キーワード数
		"randKeyUserNum"	: 20,						#キーユーザ ランダム選出数

		"getTwitTLnum"		: 200,						#TwitterのTL取得数(Twitter仕様は最大200)

		"logShortLen"		: 100,						#ログ表示 ショートモード
		"(dummy)"			: ""
	}

#############################
# ファイルパス
#   ファイルは語尾なし、フォルダは_path
	DEF_STR_FILE = {
		"Readme"				: "readme.md",
		"(dummy)"				: 0
	}

	DEF_DISPPATH = "script/disp/"

	DEF_STR_DISPFILE = {
		"MainConsole"			: DEF_DISPPATH + "main_console.disp",
		"SearchConsole"			: DEF_DISPPATH + "search_console.disp",
		
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
# Init
#####################################################
##	def __init__(self):
##		self.STR_SystemInfo = {
##			"BotName"		: "",
##			"HostName"		: ""
##		}
##		return



