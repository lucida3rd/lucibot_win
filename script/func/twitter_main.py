#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : Twitter監視 メインモジュール
# 
# ::Update= 2021/3/11
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
from traffic import CLS_Traffic
from config import CLS_Config
from gval import gVal
#####################################################
class CLS_TwitterMain():
#####################################################

	STR_KeyUser     = ""
	VAL_KeyUser_Index = -1
	
	ARR_MyFollowID = []
	ARR_FollowerID = []
	ARR_NormalListMenberID = []
	ARR_UnRefollowListMenberID = []
	ARR_OldUserID = []
	
	ARR_newExcUser = {}
	
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
		
		#############################
		# トラヒック情報読み込み
		wResSub = CLS_Traffic.sGet()
		if wResSub['Result']!=True :
			wRes['Reason'] = "Get Traffic failed: reason" + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		wOBJ_Config = CLS_Config()
		#############################
		# 検索モード読み込み
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
		
		#############################
		# 除外Follow候補 読み込み
		wResSub = wOBJ_Config.GetExcFollowID()
		if wResSub['Result']!=True :
			wRes['Reason'] = "GetExcFollowID failed: reason" + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		self.ARR_newExcUser = {}
		wKeylist = gVal.STR_ExcTwitterID_Info.keys()
		for wIndex in wKeylist :
			self.SetnewExcUser(
				gVal.STR_ExcTwitterID_Info[wIndex]['id'],
				gVal.STR_ExcTwitterID_Info[wIndex]['screen_name'],
				gVal.STR_ExcTwitterID_Info[wIndex]['count'],
				gVal.STR_ExcTwitterID_Info[wIndex]['lastdate'],
				gVal.STR_ExcTwitterID_Info[wIndex]['arashi'],
				gVal.STR_ExcTwitterID_Info[wIndex]['reason_id']
			)
		
		#############################
		# 自動いいね読み込み
		wResSub = wOBJ_Config.GetAutoFavo()
		if wResSub['Result']!=True :
			wRes['Reason'] = "GetAutoFavo failed: reason" + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# 周期15分処理
#####################################################
	def Circle15min(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterMain"
		wRes['Func']  = "Circle15min"
		
		#############################
		# 前回チェックから15分経っているか
		wResetAPImin = gVal.DEF_STR_TLNUM['resetAPImin'] * 60	#秒に変換
		wGetLag = CLS_OSIF.sTimeLag( gVal.STR_SystemInfo['APIrect'], inThreshold=wResetAPImin )
		if wGetLag['Result']!=True :
			wRes['Reason'] = "sTimeLag failed"
			return wRes
		
		if wGetLag['Beyond']==False :
			###前回から15分経ってない
			wRes['Result'] = True
			return wRes
		
		### ※前回から15分経ったので処理実行
		
		#############################
		# APIカウントリセット
		gVal.OBJ_Twitter.ResetAPI()
		
		#############################
		# Twitter再接続
		wTwitterRes = gVal.OBJ_Twitter.Connect()
		if wTwitterRes!=True :
			wTwitterStatus = gVal.OBJ_Twitter.GetTwStatus()
			wRes['Reason'] = "Twitterの再接続失敗: reason=" + wTwitterStatus['Reason']
			return wRes
		
		#############################
		# カウント時刻を更新
		gVal.STR_SystemInfo['APIrect'] = str(wGetLag['NowTime'])
		
		wRes['Reason'] = "Twitter規制解除＆再接続"
		gVal.OBJ_L.Log( "R", wRes, "", inViewConsole=True )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# 周期保存
#####################################################
	def CircleSave(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterMain"
		wRes['Func']  = "CircleSave"
		
		wOBJ_Config = CLS_Config()
		#############################
		# 除外Twitter ID 書き込み
		wResSub = wOBJ_Config.SetExcTwitterID( self.ARR_newExcUser )
		if wResSub['Result']!=True :
			wRes['Reason'] = "SetExcTwitterID failed: reason" + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		###再ロード(念のため)
		wResSub = wOBJ_Config.GetExcTwitterID()
		if wResSub['Result']!=True :
			wRes['Reason'] = "GetExcTwitterID failed: reason" + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		#############################
		# 古い除外Follow候補 削除
		wOBJ_Config = CLS_Config()
		wResSub = wOBJ_Config.OldExcFollowID_Erase()
		if wResSub['Result']!=True :
			wRes['Reason'] = "OldExcFollowID_Erase failed: reason" + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		#############################
		# 完了
		wRes['Result'] = True
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
			"update"      : False,
			
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
		# いいね情報の実行
		wResSub = self.OBJ_TwitterFavo.Run()
		if wResSub['Result']!=True :
			wRes['Reason'] = "OBJ_TwitterFavo.Run failed: " + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		#############################
		# フォロワー監視の実行
		wResSub = self.OBJ_TwitterFollower.Run()
		if wResSub['Result']!=True :
			wRes['Reason'] = "OBJ_TwitterFollower.Run failed: " + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		#############################
		# 荒らしユーザCSV出力
		wResSub = self.OBJ_TwitterKeyword.AlloutArashi()
		if wResSub['Result']!=True :
			wRes['Reason'] = "OBJ_TwitterKeyword.OutArashiCSV failed: " + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " 監視情報 結果" + '\n'
		wStr = wStr + "--------------------" + '\n'
		wStr = wStr + str(gVal.STR_TrafficInfo['update']) + '\n'
		wStr = wStr + '\n'
		
		#############################
		# 情報組み立て
		wStr = wStr + "Bot実行回数        : " + str( gVal.STR_TrafficInfo['run'] ) + '\n'
		wStr = wStr + "取得タイムライン数 : " + str( gVal.STR_TrafficInfo['timeline'] ) + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "現いいね数         : " + str( gVal.STR_TrafficInfo['favo'] ) + '\n'
		wStr = wStr + "解除対象 いいね数  : " + str( gVal.STR_TrafficInfo['favoremovet'] ) + '\n'
		wStr = wStr + "解除実行 いいね数  : " + str( gVal.STR_TrafficInfo['favoremove'] ) + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "現フォロー数       : " + str( gVal.STR_TrafficInfo['myfollow'] ) + '\n'
		wStr = wStr + "現フォロワー数     : " + str( gVal.STR_TrafficInfo['follower'] ) + '\n'
		wStr = wStr + "片フォロワー数     : " + str( gVal.STR_TrafficInfo['piefollow'] ) + '\n'
###		wStr = wStr + "新規フォロワー数   : " + str( gVal.STR_TrafficInfo['newfollower'] ) + '\n'
		wStr = wStr + "被リムーブ数       : " + str( gVal.STR_TrafficInfo['selremove'] ) + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "自動リムーブ対象数 : " + str( gVal.STR_TrafficInfo['autofollowt'] ) + '\n'
		wStr = wStr + "自動リムーブ実行数 : " + str( gVal.STR_TrafficInfo['autofollow'] ) + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "自動いいね対象数   : " + str( gVal.STR_TrafficInfo['autofavot'] ) + '\n'
		wStr = wStr + "自動いいね実施数   : " + str( gVal.STR_TrafficInfo['autofavo'] ) + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "荒らし登録者数     : " + str( gVal.STR_TrafficInfo['arashi'] ) + '\n'
		wStr = wStr + "荒らし検出回数     : " + str( gVal.STR_TrafficInfo['arashii'] ) + '\n'
		wStr = wStr + "荒らし解除者数     : " + str( gVal.STR_TrafficInfo['arashir'] ) + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "クエリ要求回数     : " + str( gVal.STR_TrafficInfo['dbreq'] ) + '\n'
		wStr = wStr + "DB挿入回数         : " + str( gVal.STR_TrafficInfo['dbins'] ) + '\n'
		wStr = wStr + "DB更新回数         : " + str( gVal.STR_TrafficInfo['dbup'] ) + '\n'
		wStr = wStr + "DB削除回数         : " + str( gVal.STR_TrafficInfo['dbdel'] ) + '\n'
		wStr = wStr + '\n'
		
		###コンソールに表示
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# キーワードの表示
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
# 自動選出フォロー(手動)
#####################################################
	def AutoChoiceFollow(self):
		wRes = self.OBJ_TwitterFollower.AutoChoiceFollow()
		return wRes



#####################################################
# 指定いいね
#####################################################
	def DesiFavo(self):
		wRes = self.OBJ_TwitterFavo.DesiFavo()
		return wRes



#####################################################
# 自動いいね
#####################################################
	def AutoFavo(self):
		wRes = self.OBJ_TwitterFavo.AutoFavo()
		return wRes



#####################################################
# 無差別いいね
#####################################################
	def CaoFavo(self):
		wRes = self.OBJ_TwitterFavo.CaoFavo()
		return wRes



#####################################################
# いいね情報の表示
#####################################################
	def ViewFavo(self):
		wRes = self.OBJ_TwitterFavo.View()
		return wRes



#####################################################
# フォロワー情報の表示
#####################################################
	def ViewFollower(self):
		wRes = self.OBJ_TwitterFollower.View()
		return wRes



#####################################################
# 個別いいねチェック
#####################################################
	def PointFavoCheck(self):
		wRes = self.OBJ_TwitterFollower.PointFavoCheck()
		return wRes



#####################################################
# ユーザ管理
#####################################################
	def UserAdmin(self):
		wRes = self.OBJ_TwitterAdmin.UserAdmin()
		return wRes



#####################################################
# キーユーザ変更
#####################################################
	def SetKeyuser(self):
		#############################
		# 検索設定モードの起動
		wRes = self.OBJ_TwitterKeyword.SetKeyuser()
		if wRes['Result']!=True :
			return wRes
		
		# ※設定モード終了で戻ってきた
		#############################
		# 検索モードの保存
		wOBJ_Config = CLS_Config()
		wResSub = wOBJ_Config.SetSearchMode_All()
		if wResSub['Result']!=True :
			wRes['Reason'] = "SetKeyuser failed: reason" + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
		return wRes



#####################################################
# 自動いいね変更
#####################################################
	def SetAutoFavo(self):
		#############################
		# 自動いいね変更の起動
		wRes = self.OBJ_TwitterFavo.SetAutoFavo()
		if wRes['Result']!=True :
			return wRes
		
		# ※戻ってきた
		#############################
		# 自動いいね設定の保存
		wOBJ_Config = CLS_Config()
		wResSub = wOBJ_Config.SetAutoFavo()
		if wResSub['Result']!=True :
			wRes['Reason'] = "SaveAutoFavo failed: reason" + CLS_OSIF.sCatErr( wResSub )
			return wRes
		
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
		#############################
		# まだ未発見ならとりま枠を作る
		wIndex = str(inLine['user']['screen_name'])
		if wIndex not in self.ARR_newExcUser :
			self.SetnewExcUser(
				inLine['user']['id'],
				inLine['user']['screen_name']
			)
		else:
			### screen_nameが変わってる場合への対策
			self.ARR_newExcUser[wIndex]['screen_name'] = inLine['user']['screen_name']
			self.ARR_newExcUser[wIndex]['update'] = True
		
		#############################
		# 同じツイートか
		wTweetID = str( inLine['id'] )
		if wTweetID in gVal.STR_ExcTweetID :
			return True	#記録済みとして判定しない,正常扱い
		###新しい更新日として記録
		if self.ARR_newExcUser[wIndex]['lastdate']<inLine['created_at'] :
			self.ARR_newExcUser[wIndex]['lastdate'] = str(inLine['created_at'])
			self.ARR_newExcUser[wIndex]['update'] = True
		
		gVal.STR_ExcTweetID.append( wTweetID )
		
		#############################
		# 除外Twitter IDチェック
		#   既に除外判定されてるID
		if wIndex in gVal.STR_ExcTwitterID :
			###どうせまた荒らしてるんでしょ？のカウンタ
			self.ARR_newExcUser[wIndex]['count'] += 1
			self.ARR_newExcUser[wIndex]['update'] = True
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
				gVal.STR_ExcTwitterID.append( self.ARR_newExcUser[wIndex]['id'] )
			self.ARR_newExcUser[wIndex]['update'] = True
			
			return False	#さよなら
		
		#############################
		# 連続じゃないのでカウントリセット
		self.ARR_newExcUser[wIndex]['count'] = 0
		self.ARR_newExcUser[wIndex]['update'] = True
		
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
		if (questions_gb2312==questions_before ) and ( 
		   (set(questions_before) - set(questions_cp932))!=set([])) :
			return True	#チャイ文
		
		return False	#日本語



#####################################################
# ふぁぼチェック
#####################################################
	def ReciveFavo( self, inID, inARR_FollowerData, inARR_Tweets ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Func']  = "ReciveFavo"
		
		wARR_Update = {
			"flg"		: False,
			"id"		: -1,
			"cnt"		: 0,
			"date"		: None,
			
			"remove"	: False
			}
		
		#############################
		# 該当ユーザのふぁぼ一覧を取得
		wFavoRes = gVal.OBJ_Twitter.GetUserFavolist( inID )
		if wFavoRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetUserFavolist): " + wFavoRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		
		wRemoveNofavoMin = gVal.DEF_STR_TLNUM['removeNofavoMin'] * 60	#秒に変換
		#############################
		# 更新された自分に対するふぁぼがあるか
		for wROW in wFavoRes['Responce'] :
			###自分以外のファボならスルー
			if str(gVal.STR_UserInfo['id'])!=str(wROW['user']['id']) :
				continue
			###最新のファボ＝更新されていない
			###  同じIDなら既ファボとして処理終わり
			if inARR_FollowerData['favo_r_id']==str(wROW['id']) :
				CLS_OSIF.sPrn( "●既ファボ: @" + inARR_FollowerData['screen_name'] + '\n')
			else:
				###最新ファボみつけた
				###  日時の変換
				wTime = CLS_OSIF.sGetTimeformat_Twitter( wROW['created_at'] )
				if wTime['Result']!=True :
					wRes['Reason'] = "sGetTimeformat_Twitter is failed(1): " + str(wROW['created_at'])
					gVal.OBJ_L.Log( "B", wRes )
					continue
				
				###最新より古ければスキップ
				if str(inARR_FollowerData['favo_r_date'])>=str(wTime['TimeDate']) :
					continue
				
				wARR_Update['id']   = str( wROW['id'] )
				wARR_Update['cnt']  = inARR_FollowerData['favo_r_cnt'] + 1
				wARR_Update['date'] = wTime['TimeDate']
				wARR_Update['flg'] = True
			break
		
		### ふぁぼがない場合、リプライ、リツイート、引用リツイートされているかで見る
		if wARR_Update['flg']==False :
			for wTweet in inARR_Tweets :
				### リプライ
				if wTweet['in_reply_to_status_id']!=None :
					if gVal.STR_UserInfo['id']==wTweet['in_reply_to_user_id'] :
						if inARR_FollowerData['favo_r_id']==str( wTweet['id'] ) :
							CLS_OSIF.sPrn( "●既ファボ: @" + inARR_FollowerData['screen_name'] + '\n')
						else:
							###  日時の変換
							wTime = CLS_OSIF.sGetTimeformat_Twitter( wTweet['created_at'] )
							if wTime['Result']!=True :
								wRes['Reason'] = "sGetTimeformat_Twitter is failed(2): " + str(wTweet['created_at'])
								gVal.OBJ_L.Log( "B", wRes )
								continue
							
							wARR_Update['id']   = str( wTweet['id'] )
							wARR_Update['cnt']  = inARR_FollowerData['favo_r_cnt'] + 1
							wARR_Update['date'] = wTime['TimeDate']
							wARR_Update['flg'] = True
						break
				
				### リツイート
				elif "retweeted_status" in wTweet :
					if gVal.STR_UserInfo['id']==wTweet['retweeted_status']['user']['id'] :
						if inARR_FollowerData['favo_r_id']==str( wTweet['id'] ) :
							CLS_OSIF.sPrn( "●既ファボ: @" + inARR_FollowerData['screen_name'] + '\n')
						else:
							###  日時の変換
							wTime = CLS_OSIF.sGetTimeformat_Twitter( wTweet['created_at'] )
							if wTime['Result']!=True :
								wRes['Reason'] = "sGetTimeformat_Twitter is failed(2): " + str(wTweet['created_at'])
								gVal.OBJ_L.Log( "B", wRes )
								continue
							
							wARR_Update['id']   = str( wTweet['id'] )
							wARR_Update['cnt']  = inARR_FollowerData['favo_r_cnt'] + 1
							wARR_Update['date'] = wTime['TimeDate']
							wARR_Update['flg'] = True
						break
				
				### 引用リツイート
				elif "quoted_status" in wTweet :
					if gVal.STR_UserInfo['id']==wTweet['quoted_status']['user']['id'] :
						if inARR_FollowerData['favo_r_id']==str( wTweet['id'] ) :
							CLS_OSIF.sPrn( "●既ファボ: @" + inARR_FollowerData['screen_name'] + '\n')
						else:
							###  日時の変換
							wTime = CLS_OSIF.sGetTimeformat_Twitter( wTweet['created_at'] )
							if wTime['Result']!=True :
								wRes['Reason'] = "sGetTimeformat_Twitter is failed(2): " + str(wTweet['created_at'])
								gVal.OBJ_L.Log( "B", wRes )
								continue
							
							wARR_Update['id']   = str( wTweet['id'] )
							wARR_Update['cnt']  = inARR_FollowerData['favo_r_cnt'] + 1
							wARR_Update['date'] = wTime['TimeDate']
							wARR_Update['flg'] = True
						break
		
		#############################
		# 更新されてない場合、
		# 自動リムーブ対象外かをチェック
		if wARR_Update['flg']==False :
			### フォローしてから一定期間内なら、何もしない
			wGetLag = CLS_OSIF.sTimeLag( str(inARR_FollowerData['foldate']), inThreshold=wRemoveNofavoMin )
			if wGetLag['Result']!=True :
				wRes['Reason'] = "sTimeLag failed(1)"
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			if wGetLag['Beyond']==False :
				###期間内 =対象外
				wRes['Result'] = True
				return wRes
			
			###ファボったことがない場合、何もしない
			if inARR_FollowerData['favoid']==None or inARR_FollowerData['favodate']==None :
				wRes['Result'] = True
				return wRes
			
			###前回のファボから一定期間内なら、何もしない
			wGetLag = CLS_OSIF.sTimeLag( str(inARR_FollowerData['favodate']), inThreshold=wRemoveNofavoMin )
			if wGetLag['Result']!=True :
				wRes['Reason'] = "sTimeLag failed(2)"
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			if wGetLag['Beyond']==False :
				###期間内 =対象外
				wRes['Result'] = True
				return wRes
			
			###ファボられたことがない場合、自動リムーブ対象
			if inARR_FollowerData['favo_r_id']==None or inARR_FollowerData['favo_r_date']==None :
				wARR_Update['remove'] = True
			
			###ファボられたことがある場合
			###  前回から 一定期間外なら自動リムーブ対象
			else:
				wGetLag = CLS_OSIF.sTimeLag( str(inARR_FollowerData['favo_r_date']), inThreshold=wRemoveNofavoMin )
				if wGetLag['Result']!=True :
					wRes['Reason'] = "sTimeLag failed(3)"
					gVal.OBJ_L.Log( "B", wRes )
					return wRes
				if wGetLag['Beyond']==True :
					###期間外 =自動リムーブ対象外
					wARR_Update['remove'] = True
		
		#############################
		# DB更新
		###更新されてる
		if wARR_Update['flg']==True :
			wQuery = "update tbl_follower_data set " + \
						"favo_r_cnt = " + str( wARR_Update['cnt'] ) + ", " + \
						"favo_r_id = '" + str( wARR_Update['id'] ) + "', " + \
						"favo_r_date = '" + str( wARR_Update['date'] ) + "' " + \
						"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
						" and id = '" + str(inID) + "' ;"
			
			CLS_OSIF.sPrn( "〇ファボ検出: @" + inARR_FollowerData['screen_name'] + '\n')
		
		###更新されてない かつ 自動リムーブ候補に設定
		elif wARR_Update['remove']==True :
			wQuery = "update tbl_follower_data set " + \
						"limited = True, " + \
						"removed = False " + \
						"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
						" and id = '" + str(inID) + "' ;"
			
			###※既にリムーブしているユーザを記録＆表示する
			wRes['Reason'] = "ノーアクションのためリムーブ候補に設定: @" + str(inARR_FollowerData['screen_name'])
			gVal.OBJ_L.Log( "R", wRes, "", inViewConsole=True )
		
		if wARR_Update['flg']==True or wARR_Update['remove']==True :
			wResDB = gVal.OBJ_DB.RunQuery( wQuery )
			wResDB = gVal.OBJ_DB.GetQueryStat()
			if wResDB['Result']!=True :
				##失敗
				wRes['Reason'] = "Run Query is failed(20): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			
			###  カウント
			gVal.STR_TrafficInfo['dbreq'] += 1
			gVal.STR_TrafficInfo['dbup'] += 1
		
		wRes['Result'] = True
		return wRes



