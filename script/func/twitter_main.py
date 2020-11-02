#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : Twitter監視 メインモジュール
# 
# ::Update= 2020/11/2
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
from twitter_admin import CLS_TwitterAdmin
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
		
		"ArashiNum"			: 0,	#荒らし登録者数
		"ArashiOnNum"		: 0,	#荒らし者数
		
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
	
	ARR_newExcUser = {}
###	ARR_ExcTwiitID = []
	
	STR_newFollower = {}
	VAL_newFollower = 0
	
	OBJ_TwitterFavo = ""
	OBJ_TwitterFollower = ""
	OBJ_TwitterKeyword = ""

	DEF_STR_ARASHI_REASON_ID = {
		0	: "Not Arashi",
		10	: "Hash Tag",
		11	: "Hash and URL",
		20	: "China User Name",
		21	: "China Word",
		99	: "Manual Designation"
	}



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
		self.OBJ_TwitterAdmin    = CLS_TwitterAdmin( parentObj=self )
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
		# Twitterから自ユーザ情報を取得する
		wUserinfoRes = gVal.OBJ_Twitter.GetMyUserinfo()
		if wUserinfoRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetUserinfo): " + wUserinfoRes['Reason']
			return wRes
		gVal.STR_UserInfo['id'] = wUserinfoRes['Responce']['id']
		
		wOBJ_Config = CLS_Config()
		#############################
		# 検索モード読み込み
###		wOBJ_Config = CLS_Config()
		wResSub = wOBJ_Config.GetSearchMode()
		if wResSub['Result']!=True :
			wRes['Reason'] = "GetSearchMode failed: reason" + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		#############################
		# 除外ユーザ名読み込み
		wResSub = wOBJ_Config.GetExcUserName()
		if wResSub['Result']!=True :
			wRes['Reason'] = "GetExcUserName failed: reason" + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		#############################
		# 除外文字読み込み
		wResSub = wOBJ_Config.GetExcWord()
		if wResSub['Result']!=True :
			wRes['Reason'] = "GetExcWord failed: reason" + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		#############################
		# 除外Twitter ID読み込み
		wResSub = wOBJ_Config.GetExcTwitterID()
		if wResSub['Result']!=True :
			wRes['Reason'] = "GetExcTwitterID failed: reason" + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
###		self.ARR_ExcTwiitID = []
		self.ARR_newExcUser = {}
		wKeylist = gVal.STR_ExcTwitterID_Info.keys()
		for wIndex in wKeylist :
###			wCell = {
###				"id"          : str(gVal.STR_ExcTwitterID_Info[wIndex]['id']),
###				"screen_name" : gVal.STR_ExcTwitterID_Info[wIndex]['screen_name'],
###				"count"       : gVal.STR_ExcTwitterID_Info[wIndex]['count'],
###				"lastdate"    : gVal.STR_ExcTwitterID_Info[wIndex]['lastdate']
###				}
###			self.ARR_newExcUser.update({ str(gVal.STR_ExcTwitterID_Info[wIndex]['id']) : wCell })
			self.SetnewExcUser(
				gVal.STR_ExcTwitterID_Info[wIndex]['id'],
				gVal.STR_ExcTwitterID_Info[wIndex]['screen_name'],
				gVal.STR_ExcTwitterID_Info[wIndex]['count'],
				gVal.STR_ExcTwitterID_Info[wIndex]['lastdate'],
				gVal.STR_ExcTwitterID_Info[wIndex]['arashi'],
				gVal.STR_ExcTwitterID_Info[wIndex]['reason_id']
			)
		
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
###		wOBJ_Config = CLS_Config()
###		wResSub = wOBJ_Config.SetSearchMode_All()
		wResSub = self.SaveSearchMode()
		if wResSub['Result']!=True :
			wRes['Reason'] = "SetSearchMode_All failed: reason" + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		#############################
		# 除外Twitter ID 書き込み
###		wResSub = wOBJ_Config.SetExcTwitterID( self.ARR_newExcUser )
		wResSub = self.SaveExcTwitterID()
		if wResSub['Result']!=True :
			wRes['Reason'] = "SetExcTwitterID failed: reason" + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# 検索モード保存
#####################################################
	def SaveSearchMode(self):
		wOBJ_Config = CLS_Config()
		wRes = wOBJ_Config.SetSearchMode_All()
		return wRes



#####################################################
# 除外Twitter ID保存
#####################################################
	def SaveExcTwitterID(self):
		wOBJ_Config = CLS_Config()
		wRes = wOBJ_Config.SetExcTwitterID( self.ARR_newExcUser )
		if wRes['Result']!=True :
			return wRes
		
		###再ロード(念のため)
		wRes = wOBJ_Config.GetExcTwitterID()
		return wRes



#####################################################
# 新規除外ユーザ 設定
#####################################################
	def SetnewExcUser( self, inID, inScreenName, inCount=0, inLastDate="1901-01-01 00:00:00", inArashi=False, inReasonID=0 ):
		wCell = {
			"id"          : str(inID),
			"screen_name" : inScreenName,
			"count"       : inCount,
			"lastdate"    : str(inLastDate),
			"arashi"      : inArashi,
			"reason_id"   : inReasonID
		}
		self.ARR_newExcUser.update({ str(inScreenName) : wCell })
		return



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
		
		self.STR_Cope['ArashiNum']  = 0
		self.STR_Cope['ArashiOnNum']  = 0
		
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
		# 画面クリア(=通常モード時)
		if gVal.FLG_Test_Mode==False :
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
		wStr = wStr + "荒らし登録者数 = " + str(self.STR_Cope['ArashiNum']) + '\n'
		wStr = wStr + "荒らし者数     = " + str(self.STR_Cope['ArashiOnNum']) + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "DB登録数 = " + str(self.STR_Cope['DB_Num']) + '\n'
		wStr = wStr + "DB挿入   = " + str(self.STR_Cope['DB_Insert']) + '\n'
		wStr = wStr + "DB更新   = " + str(self.STR_Cope['DB_Update']) + '\n'
		wStr = wStr + "DB削除   = " + str(self.STR_Cope['DB_Delete']) + '\n'
		
		###コンソールに表示
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# キーワードの表示
###		wStr = '\n'
###		wStr = wStr + " キーワードごとのヒット数" + '\n'
###		wStr = wStr + "--------------------" + '\n'
###		wKeylist = self.STR_Keywords.keys()
###		for wWord in wKeylist :
###			wStr = wStr + wWord + " = " + str(self.STR_Keywords[wWord]) + '\n'
		wRange = len(gVal.STR_SearchMode)
		if wRange>1 :
			wStr = '\n'
			wStr = wStr + " キーワードごとのヒット数" + '\n'
			wStr = wStr + "--------------------" + '\n'
			wRange = len(gVal.STR_SearchMode)
			for wIndex in range( wRange ) :
				if gVal.STR_SearchMode[wIndex]['id']==0 :
					continue	#id=0は手動用
				
				###前方に半角スペース埋め
				wLen = 10 - len( str(gVal.STR_SearchMode[wIndex]['Count']) )
				wBlank = " " * wLen
				wStr = wStr + wBlank + str(gVal.STR_SearchMode[wIndex]['Count']) + "  " + gVal.STR_SearchMode[wIndex]['Keyword'] + '\n'
			
			###コンソールに表示
			CLS_OSIF.sPrn( wStr )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# キーユーザフォロー(手動)
#####################################################
	def KeyUserFollow(self):
		wRes = self.OBJ_TwitterKeyword.KeyUserFollow()
		return wRes



#####################################################
# キーユーザCSV出力
#####################################################
	def KeyUserCSV(self):
		wRes = self.OBJ_TwitterKeyword.OutCSV()
		return wRes



#####################################################
# 荒らしユーザCSV出力
#####################################################
	def ArashiCSV(self):
		wRes = self.OBJ_TwitterKeyword.OutArashiCSV()
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
# フォロワー監視の実行
#####################################################
	def RunFollower(self):
		wRes = self.OBJ_TwitterFollower.Run()
		return wRes



#####################################################
# キーユーザ変更
#####################################################
	def SetKeyuser(self):
		wRes = self.OBJ_TwitterKeyword.SetKeyuser()
		return wRes



#####################################################
# ユーザ復活
#####################################################
	def UserRevival(self):
		wRes = self.OBJ_TwitterAdmin.UserRevival()
		return wRes



#####################################################
# 荒らしユーザ設定
#####################################################
	def ArashiUser(self):
		wRes = self.OBJ_TwitterAdmin.ArashiUser()
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



#####################################################
# 荒らしチェック
#####################################################
	def CheckTrolls( self, inLine ):
##		#############################
##		# Indexの検索
##		wKeylist = list( self.ARR_newExcUser.keys() )
##		wFLG_Ditect = False
##		for wKey in wKeylist :
##			if self.ARR_newExcUser[wKey]['screen_name']==inLine['user']['screen_name'] :
##				wIndex = self.ARR_newExcUser[wKey]['screen_name']
##				wFLG_Ditect = True
##				break
##		
##		###まだ未発見ならとりま枠を作る
##		if wFLG_Ditect==False :
###			wCell = {
###				"id"          : str(inLine['user']['id']),
###				"screen_name" : inLine['user']['screen_name'],
###				"count"       : 0,
###				"lastdate"    : "1901-01-01 00:00:00"
###				}
###			wIndex = str(inLine['user']['id'])
###			self.ARR_newExcUser.update({ str(inLine['user']['id']) : wCell })
		
		#############################
		# まだ未発見ならとりま枠を作る
		wIndex = str(inLine['user']['screen_name'])
		if wIndex not in self.ARR_newExcUser :
			self.SetnewExcUser(
				inLine['user']['id'],
				inLine['user']['screen_name']
			)
		
###		#############################
###		# 同じツイートか(日時で判定)
###		if self.ARR_newExcUser[wIndex]['lastdate']==str(inLine['created_at']) :
###			return True	#記録済みとして判定しない,正常扱い
		
		#############################
		# 同じツイートか
		wTweetID = str( inLine['id'] )
###		if wTweetID in self.ARR_ExcTwiitID :
		if wTweetID in gVal.STR_ExcTweetID :
			return True	#記録済みとして判定しない,正常扱い
		###新しい更新日として記録
		self.ARR_newExcUser[wIndex]['lastdate'] = str(inLine['created_at'])
###		self.ARR_ExcTwiitID.append( wTweetID )
		gVal.STR_ExcTweetID.append( wTweetID )
		
		#############################
		# 除外Twitter IDチェック
		#   既に除外判定されてるID
###		for wID in gVal.STR_ExcTwitterID :
###			if inLine['user']['screen_name']==wID :
###				###どうせまた荒らしてるんでしょ？のカウンタ
###				self.ARR_newExcUser[wIndex]['count'] += 1
###				return False	#除外、さよなら
###		
		if wIndex in gVal.STR_ExcTwitterID :
			###どうせまた荒らしてるんでしょ？のカウンタ
			self.ARR_newExcUser[wIndex]['count'] += 1
			return False	#除外、さよなら
		
		#############################
		# ツイートからタグ・URLを除去する
		wCHR_Text = CLS_OSIF.sDel_HTML( str(inLine['text']) )
		wCHR_Text = CLS_OSIF.sDel_HashTag( wCHR_Text )
		wCHR_Text = CLS_OSIF.sDel_URL( wCHR_Text )
		wCHR_Text = wCHR_Text.replace( " ", "" )
		
		wFLG_Trolls = False
		wReasonID = 0
		#############################
		# 荒らし判定
		
		###ハッシュタグを4つ以上使ってる
		if CLS_OSIF.sGetCount_HashTag( inLine['text'] )>=4 :
			wReasonID = 10
			wFLG_Trolls = True
		
		###タグ・URLのみのツイート
		elif len(wCHR_Text)==0 :
			wReasonID = 11
			wFLG_Trolls = True
		
		###ユーザ名にチャイ文を含んでる
		elif self.__check_ChinaWord( inLine['user']['name'] )==True :
			wReasonID = 20
			wFLG_Trolls = True
		
		###ツイートにチャイ文を含んでる
		elif self.__check_ChinaWord( inLine['text'] )==True :
			wReasonID = 21
			wFLG_Trolls = True
		
		#############################
		# 荒らしカウント
		if wFLG_Trolls==True :
			self.ARR_newExcUser[wIndex]['count'] += 1
			
			#############################
			# 荒らし確定
			if gVal.DEF_STR_TLNUM['excTwitterID']<=self.ARR_newExcUser[wIndex]['count'] :
				self.ARR_newExcUser[wIndex]['arashi'] = True
				self.ARR_newExcUser[wIndex]['reason_id'] = wReasonID
				
				###除外リスト入り
				gVal.STR_ExcTwitterID.append( self.ARR_newExcUser[wIndex]['screen_name'] )
			
			return False	#さよなら
		
		#############################
		# 連続じゃないのでカウントリセット
		self.ARR_newExcUser[wIndex]['count'] = 0
		
		return True

	#####################################################
	# チャイ文判定
	def __check_ChinaWord( self, inText ):
	### SJISに変換して文字数が減れば簡体字があるので中国語
	###   参考ロジック：
	###     https://showyou.hatenablog.com/entry/20110131/1296490644
	###     https://qiita.com/ry_2718/items/47c21792d7bbd3fe33b9
		wOrgLen = len( inText )
		wHenLen = len( inText.encode('sjis','ignore').decode('sjis') )
		if wOrgLen==wHenLen :
			return False #日本語
		
		questions_before = [s for s in inText]
		questions_gb2312 = [s for s in \
			inText.encode('gb2312','ignore').decode('gb2312')]
		questions_cp932 = [s for s in \
			inText.encode('cp932','ignore').decode('cp932')]
###		if questions_gb2312==questions_before :
###			return True	#チャイ文
###		
###		wLen = len(questions_before) - len(questions_cp932)
###		if wLen!=0 :
		if (questions_gb2312==questions_before ) and ( 
		   (set(questions_before) - set(questions_cp932))!=set([])) :
			return True	#チャイ文
		
		return False	#日本語



