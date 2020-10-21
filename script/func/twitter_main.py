#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : Twitter監視 メインモジュール
# 
# ::Update= 2020/10/14
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   __init__(self):
#   Init(self):
#   GetCope(self):
#   GetNewFollower(self):
#   Run(self):
#   ViewFavo(self):
#   RunFavo(self):
#   ViewFollower(self):
#
# Class Function(static):
#   (none)
#
#####################################################
from twitter_favo import CLS_TwitterFavo
from twitter_follower import CLS_TwitterFollower
from twitter_keyword import CLS_TwitterKeyword
###import threading
###import sys, time

from osif import CLS_OSIF
###from filectrl import CLS_File
from config import CLS_Config
from gval import gVal
#####################################################
class CLS_TwitterMain():
#####################################################

	STR_Cope = {				#処理カウンタ
		"TimelineNum"		: 0,	#タイムライン数
		"KeyUserNum"		: 0,	#キーユーザ数
		
		"FavoNum"			: 0,	#現いいね数
		"tFavoRemove"		: 0,	#解除対象 いいね数
		"FavoRemove"		: 0,	#解除実行 いいね数
		
		"MyFollowNum"		: 0,	#現フォロー数
		"FollowerNum"		: 0,	#現フォロワー数
		"PieceFollowNum"	: 0,	#片フォロー数
		"NewFollowerNum"	: 0,	#新規フォロワー数
		"tMyFollowRemove"	: 0,	#自動リムーブ 対象数
		"MyFollowRemove"	: 0,	#自動リムーブ 実行数
		
		"DB_Num"			: 0,	#DB登録数
		"DB_Insert"			: 0,	#DB挿入
		"DB_Update"			: 0,	#DB更新
		"DB_Delete"			: 0,	#DB削除
		
		"dummy"				: 0		#(未使用)
	}

###	VAL_WaitCount = 0

	STR_KeyUser     = ""
###	STR_Keywords    = ""
	
###	FLG_Search_JP    = True			#検索は日本語のみ
###	FLG_Search_IncRt = False		#検索にリツイートを含める
	
	ARR_MyFollowID = []
	ARR_FollowerID = []
	ARR_NormalListMenberID = []
	ARR_UnRefollowListMenberID = []
	ARR_OldUserID = []
	
	STR_newFollower = {}
	VAL_newFollower = 0
	
	OBJ_TwitterFavo = ""
	OBJ_TwitterFollower = ""
	OBJ_TwitterKeyword = ""



#####################################################
# 集計取得
#####################################################
	def GetCope(self):
		return self.STR_Cope	#返すだけ



#####################################################
# 新規フォロワー取得
#####################################################
	def GetNewFollower(self):
		return self.STR_newFollower	#返すだけ



#####################################################
# Init
#####################################################
	def __init__(self):
		self.OBJ_TwitterFavo     = CLS_TwitterFavo( parentObj=self )
		self.OBJ_TwitterFollower = CLS_TwitterFollower( parentObj=self )
		self.OBJ_TwitterKeyword  = CLS_TwitterKeyword( parentObj=self )
		return



#####################################################
# 初期化
#####################################################
	def Init(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterMain"
		wRes['Func']  = "Init"
		
		#############################
		# 検索モード読み込み
		wOBJ_Config = CLS_Config()
		wResSub = wOBJ_Config.GetSearchMode()
		if wResSub['Result']!=True :
			wRes['Reason'] = "GetSearchMode failed: reason" + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# 終了
#####################################################
	def End(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterMain"
		wRes['Func']  = "End"
		
		#############################
		# 検索モード保存
		wOBJ_Config = CLS_Config()
		wResSub = wOBJ_Config.SetSearchMode_All()
		if wResSub['Result']!=True :
			wRes['Reason'] = "SetSearchMode_All failed: reason" + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# 監視情報の取得 実行
#####################################################
	def Run(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterMain"
		wRes['Func']  = "Run"
		
		#############################
		# 集計のリセット
		self.STR_Cope['TimelineNum'] = 0
		self.STR_Cope['KeyUserNum']  = 0
		
		self.STR_Cope['FavoNum'] = 0
		self.STR_Cope['tFavoRemove'] = 0
		self.STR_Cope['FavoRemove']  = 0
		
		self.STR_Cope['MyFollowNum'] = 0
		self.STR_Cope['FollowerNum'] = 0
		self.STR_Cope['PieceFollowNum'] = 0
		self.STR_Cope['NewFollowerNum']  = 0
		self.STR_Cope['tMyFollowRemove'] = 0
		self.STR_Cope['MyFollowRemove']  = 0
		
		self.STR_Cope['DB_Num']    = 0
		self.STR_Cope['DB_Insert'] = 0
		self.STR_Cope['DB_Update'] = 0
		self.STR_Cope['DB_Delete'] = 0
		
		#############################
		# いいね情報の取得
		wResSub = self.OBJ_TwitterFavo.Get()
		if wResSub['Result']!=True :
			wRes['Reason'] = "OBJ_TwitterFavo.Get failed: " + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		#############################
		# フォロワー情報の取得
		wResSub = self.OBJ_TwitterFollower.Get()
		if wResSub['Result']!=True :
			wRes['Reason'] = "OBJ_TwitterFollower.Get failed: " + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		#############################
		# キーユーザの取得
		wResSub = self.OBJ_TwitterKeyword.Get()
		if wResSub['Result']!=True :
			wRes['Reason'] = "OBJ_TwitterKeyword.Get failed: " + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " 監視情報 結果" + '\n'
		wStr = wStr + "--------------------" + '\n'
		
		#############################
		# 情報組み立て
		wStr = wStr + "タイムライン数    = " + str(self.STR_Cope['TimelineNum']) + '\n'
		wStr = wStr + "キーユーザ数      = " + str(self.STR_Cope['KeyUserNum']) + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "現いいね数        = " + str(self.STR_Cope['FavoNum']) + '\n'
		wStr = wStr + "解除対象 いいね数 = " + str(self.STR_Cope['tFavoRemove']) + '\n'
		wStr = wStr + "解除済み いいね数 = " + str(self.STR_Cope['FavoRemove']) + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "現フォロー数        = " + str(self.STR_Cope['MyFollowNum']) + '\n'
		wStr = wStr + "現フォロワー数      = " + str(self.STR_Cope['FollowerNum']) + '\n'
		wStr = wStr + "片フォロー数        = " + str(self.STR_Cope['PieceFollowNum']) + '\n'
		wStr = wStr + "新規フォロワー数    = " + str(self.STR_Cope['NewFollowerNum']) + '\n'
		wStr = wStr + "自動リムーブ 対象数 = " + str(self.STR_Cope['tMyFollowRemove']) + '\n'
		wStr = wStr + "自動リムーブ 実行数 = " + str(self.STR_Cope['MyFollowRemove']) + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "DB登録数 = " + str(self.STR_Cope['DB_Num']) + '\n'
		wStr = wStr + "DB挿入   = " + str(self.STR_Cope['DB_Insert']) + '\n'
		wStr = wStr + "DB更新   = " + str(self.STR_Cope['DB_Update']) + '\n'
		wStr = wStr + "DB削除   = " + str(self.STR_Cope['DB_Delete']) + '\n'
		
		wStr = wStr + '\n'
		wStr = wStr + " キーワードごとのヒット数" + '\n'
		wStr = wStr + "--------------------" + '\n'
		wKeylist = self.STR_Keywords.keys()
		for wWord in wKeylist :
			wStr = wStr + wWord + " = " + str(self.STR_Keywords[wWord]) + '\n'
		
		#############################
		# コンソールに表示
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# キーユーザCSV出力
#####################################################
	def KeyUserCSV(self):
		wRes = self.OBJ_TwitterKeyword.OutCSV()
		return wRes



#####################################################
# いいね情報の表示
#####################################################
	def ViewFavo(self):
		wRes = self.OBJ_TwitterFavo.View()
		return wRes



#####################################################
# いいね監視の実行
#####################################################
	def RunFavo(self):
		wRes = self.OBJ_TwitterFavo.Run()
		return wRes



#####################################################
# フォロワー情報の表示
#####################################################
	def ViewFollower(self):
		wRes = self.OBJ_TwitterFollower.View()
		return wRes



#####################################################
# キーユーザ変更
#####################################################
	def SetKeyuser(self):
		wRes = self.OBJ_TwitterKeyword.SetKeyuser()
		return wRes



#####################################################
# ツイート検索
#####################################################
	def TweetSearch(self):
		wRes = self.OBJ_TwitterKeyword.TweetSearch()
		return wRes



#####################################################
# 除外ユーザ名 チェック
#####################################################
	def CheckExcUserName( self, inUserName ):
		for wLine in gVal.STR_ExcUserName :
			if inUserName.find( wLine )>=0 :
				return False
		return True



#####################################################
# 除外文字 チェック
#####################################################
	def CheckExcWord( self, inWord ):
		for wLine in gVal.STR_ExcWord :
			if inWord.find( wLine )>=0 :
				return False
		return True



