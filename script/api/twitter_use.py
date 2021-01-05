#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL : https://twitter.com/lucida3hai
# ::Class       : ついったーユーズ
# 
# ::Update= 2021/1/4
#####################################################
# Private Function:
#   __initTwStatus(self):
#   __Get_Resp(self):
#   __twConnect(self):
#   __TwitterPing(self):
#   __set_API( self, inName, inMAX, outStatus ):
#   __set_APIcolum( self, outStatus ):
#   __set_APIcount( self, inName ):
#   __get_APIrect( self, inName ):
#
# Instance Function:
#   __init__(self):
#   GetTwStatus(self):
#   GetUsername(self):
#   Create( self, inTwitterID, inAPIkey, inAPIsecret, inACCtoken, inACCsecret, inGetNum=200 ):
#   ResetAPI( self, inName ):
#
# ◇Twitter接続・切断
#   Connect(self):
#   
# ◇タイムライン制御系
#   Tweet( self, inTweet ):
#   GetTL( self, inTLmode="home", inListID=None, inFLG_Rep=True, inFLG_Rts=False ):
#   GetSearch( self, inKeyword=None, inRoundNum=1 ):
#   GetMyUserinfo(self):
#   GetUserinfo( self, inID ):
#   GetFollowInfo( self, inSrcID, inDstID ):
#   GetMyFollowList(self):
#   GetFollowerList(self):
#   CreateFollow( self, inID ):
#   RemoveFollow( self, inID ):
#   GetMuteIDs(self):
#   CreateMute( self, inID ):
#   RemoveMute( self, inID ):
#   GetFavolist(self):
#   CreateFavo( self, inID ):
#   RemoveFavo( self, inID ):
#   GetLists(self):
#   GetListMember( self, inListName ):
#   AddUserList( self, inListName, inUserID ):
#   RemoveUserList( self, inListName, inUserID ):
#   GetTrends(self):
#
# Class Function(static):
#   (none)
#
#####################################################
# 参考：
#   twitter api rate
#     https://developer.twitter.com/en/docs/basics/rate-limits
#
#####################################################
import time
import json
import subprocess as sp
from requests_oauthlib import OAuth1Session

#####################################################
class CLS_Twitter_Use():
#####################################################
	Twitter_use = ''						#Twitterモジュール実体
###	IniStatus = ""
	TwStatus = ""
	##	"Init"     : False
	##	"Reason"   : None
	##	"Responce" : None

	STR_TWITTERdata = {
		"TwitterID"		: "",				#Twitter ID
		"APIkey"		: "",				#API key
		"APIsecret"		: "",				#API secret key
		"ACCtoken"		: "",				#Access token
		"ACCsecret"		: ""				#Access token secret
	}
	
	VAL_TwitNum       = 200
	VAL_TwitListNum   = 5000
	VAL_TwitSearchNum = 100

	DEF_TWITTER_HOSTNAME = "twitter.com"	#Twitterホスト名
	DEF_MOJI_ENCODE      = 'utf-8'			#ファイル文字エンコード
	DEF_TWITTER_PING_COUNT   = "2"			#Ping回数 (文字型)
##	DEF_TWITTER_PING_TIMEOUT = "1000"		#Pingタイムアウト秒 (文字型)

	#トレンド地域ID
#	DEF_WOEID = "1"				#グローバル
	DEF_WOEID = "23424856"		#日本
		# idにはWOEID Lookupの地域IDを入れる
		#   http://woeid.rosselliot.co.nz/
		#   なんだけどエラー？で取得できない。なんやこれ...


	STR_TWITTER_STATUS_CODE = {
		"200"	: "OK",
		"304"	: "Not Modified",
		"400"	: "Bad Request",
		"401"	: "Unauthorized",
		"403"	: "Forbidden",
		"404"	: "Not Found",
		"406"	: "Not Acceptable",
		"410"	: "Gone",
		"420"	: "Enhance Your Calm",
		"422"	: "Unprocessable Entity",
		"429"	: "Too Many Requests",
		"500"	: "Internal Server Error",
		"502"	: "Bad Gateway",
		"503"	: "Service Unavailable",
		"504"	: "Gateway timeout"
	}
	### http://westplain.sakuraweb.com/translate/twitter/API-Overview/Error-Codes-and-Responses.cgi

	ARR_TwitterList = {}	#Twitterリスト
	# id    リストid
	# name  リスト名

	ARR_MuteList = []	#ミュートIDs(リスト)

	CHR_TimeDate = "1901-01-01 00:00:00"
	DEF_VAL_SLEEP = 3		#Twitter処理遅延（秒）



#####################################################
# Twitter状態取得
#####################################################
	def GetTwStatus(self):
		return self.TwStatus	#返すだけ



#####################################################
# ユーザ名取得
#####################################################
	def GetUsername(self):
		if self.STR_TWITTERdata['TwitterID']=='' :
			return ""
		
		wUser = self.STR_TWITTERdata['TwitterID'] + "@" + self.DEF_TWITTER_HOSTNAME
		return wUser



#####################################################
# Twitter状態取得
#####################################################
	def __initTwStatus(self):
		self.TwStatus = {
			"Init"     : False,
			"Reason"   : None,
			"Responce" : None,
			"APIrect"  : None
		}
		
		#############################
		# API規制値
		#   ※アプリでの規制値は 15分 * 80% で計算する
		self.TwStatus['APIrect'] = {}
		###	POST														# リクエストとTwitter規制値
		self.__set_API( "status",      20, self.TwStatus['APIrect'] )	# POST: 3h/300 (ツイートとリツイは共通)
		self.__set_API( "favorites",    8, self.TwStatus['APIrect'] )	# POST: 24h/1000
		self.__set_API( "friendships",  3, self.TwStatus['APIrect'] )	# POST: 24h/400
		self.__set_API( "muted",       20, self.TwStatus['APIrect'] )	# POST: 3h/300
		
		###	GET
		self.__set_API( "home_timeline",  12, self.TwStatus['APIrect'] )# GET: 15m/15
		self.__set_API( "user_timeline", 720, self.TwStatus['APIrect'] )# GET: 15m/900
		self.__set_API( "lists_status",  720, self.TwStatus['APIrect'] )# GET: 15m/900
		self.__set_API( "search_tweets", 144, self.TwStatus['APIrect'] )# GET: 15m/180
		self.__set_API( "friends_list",   12, self.TwStatus['APIrect'] )# GET: 15m/15
		self.__set_API( "friends_show",   12, self.TwStatus['APIrect'] )# GET: 15m/15
		self.__set_API( "followers_list", 12, self.TwStatus['APIrect'] )# GET: 15m/15
		self.__set_API( "favorites_list", 60, self.TwStatus['APIrect'] )# GET: 15m/75
		self.__set_API( "lists_list",     12, self.TwStatus['APIrect'] )# GET: 15m/15
		self.__set_API( "lists_members", 720, self.TwStatus['APIrect'] )# GET: 15m/900
		self.__set_API( "trends_place",   60, self.TwStatus['APIrect'] )# GET: 15m/75
		self.__set_API( "users_show",    900, self.TwStatus['APIrect'] )# GET: 15m/900
		self.__set_API( "mute_list",      12, self.TwStatus['APIrect'] )# GET: 15m/15
		return

	#####################################################
	def __set_API( self, inName, inMAX, outStatus ):
		pStatus = outStatus
		pStatus.update({ inName : {} })
		self.__set_APIcolum( inMAX, pStatus[inName] )
		return

	#####################################################
	def __set_APIcolum( self, inMAX, outStatus ):
		pStatus = outStatus
		pStatus.update({ "num"    :  0 })
		pStatus.update({ "max"    : inMAX })
		pStatus.update({ "rect"   : False })
		return



#####################################################
# API規制値カウント
#####################################################
	def __set_APIcount( self, inName ):
		if self.TwStatus['APIrect'][inName]['rect']==True :
			return	#規制中はカウントしない
		
		self.TwStatus['APIrect'][inName]['num'] += 1
		if self.TwStatus['APIrect'][inName]['max']<=self.TwStatus['APIrect'][inName]['num'] :
			self.TwStatus['APIrect'][inName]['rect'] = True	#規制
		return

	#####################################################
	def __get_APIrect( self, inName ):
		if self.TwStatus['APIrect'][inName]['rect']==True :
			return False	#規制中
		return True			#規制なし

	#####################################################
	### ※外部の時間差が分かる処理から呼び出してリセットすること
	def ResetAPI(self):
		wKeylist = self.TwStatus['APIrect'].keys()
		for wKey in wKeylist :
			self.TwStatus['APIrect'][wKey]['num']  = 0
			self.TwStatus['APIrect'][wKey]['rect'] = False
		return



#####################################################
# レスポンス取得
#####################################################

##		#############################
##		# 応答形式の取得
##		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
##		wRes = self.__Get_Resp()
##		wRes['Func'] = "Function"

	def __Get_Resp(self):
		wRes = {
			"Result"   : False,
			"Class"    : "CLS_Twitter_Use",
			"Func"     : None,
			"Reason"   : None,
			"Responce" : None }
		
		return wRes



#####################################################
# 初期化
#####################################################
	def __init__(self):
		return



#####################################################
# 接続情報の作成
#####################################################
	def Create( self, inTwitterID, inAPIkey, inAPIsecret, inACCtoken, inACCsecret, inGetNum=200 ):
		#############################
		# Twitter状態 全初期化
		self.__initTwStatus()
		
		#############################
		# 接続情報の仮セット
		self.STR_TWITTERdata['TwitterID'] = inTwitterID
		self.STR_TWITTERdata['APIkey']    = inAPIkey
		self.STR_TWITTERdata['APIsecret'] = inAPIsecret
		self.STR_TWITTERdata['ACCtoken']  = inACCtoken
		self.STR_TWITTERdata['ACCsecret'] = inACCsecret
		
		self.VAL_TwitNum = inGetNum
		
		#############################
		# Twitter接続テスト
		if self.__twConnect()!=True :
			return False	#失敗
		
		#############################
		# 遅延
		time.sleep( self.DEF_VAL_SLEEP )
		
		#############################
		# 初期化完了
		self.TwStatus['Init'] = True
		return True



#####################################################
# 接続
#####################################################
	def Connect(self):
		#############################
		# 初期化状態の確認
		if self.TwStatus['Init']!=True :
			self.TwStatus['Reason'] = "CLS_Twitter_Use: Connect: TwStatusが初期化されていません"
			return False
		
		#############################
		# Twitter接続
		if self.__twConnect()!=True :
			return False
		
		#############################
		# 遅延
		time.sleep( self.DEF_VAL_SLEEP )
		
		return True

	#####################################################
	def __twConnect(self):

		#############################
		# 通信テスト
		if self.__TwitterPing()!=True :
			self.TwStatus['Reason'] = "CLS_Twitter_Use: __twConnect: Twitter host no responce"
			return False
		
		#############################
		# Twitterクラスの生成
		try:
			self.Twitter_use = OAuth1Session(
				self.STR_TWITTERdata["APIkey"],
				self.STR_TWITTERdata["APIsecret"],
				self.STR_TWITTERdata["ACCtoken"],
				self.STR_TWITTERdata["ACCsecret"]
			)
		except ValueError as err :
			self.IniStatus['Reason'] = "CLS_Twitter_Use: __twConnect: Twitter error: " + str(err)
			return False
		
		return True



#####################################################
# twitterサーバのPing確認
#####################################################
	def __TwitterPing(self):
##		wStatus, wResult = sp.getstatusoutput( "ping -c " + str(inCount) + " " + str( self.DEF_TWITTER_HOSTNAME ) )
##		wPingComm = "ping -c " + self.DEF_TWITTER_PING_COUNT + " -w " + self.DEF_TWITTER_PING_TIMEOUT + " " + self.DEF_TWITTER_HOSTNAME
##		wPingComm = "ping -c " + self.DEF_TWITTER_PING_COUNT + " " + self.DEF_TWITTER_HOSTNAME
		wPingComm = "ping -n " + self.DEF_TWITTER_PING_COUNT + " " + self.DEF_TWITTER_HOSTNAME
		wStatus, wResult = sp.getstatusoutput( wPingComm )
		if wStatus==0 :
			return True	# Link UP
		
		return False	# Link Down



#####################################################
# ついーと処理
#####################################################
	def Tweet( self, inTweet ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "Tweet"
		
		#############################
		# API規制チェック
		if self.__get_APIrect( "status" )!=True :
			wRes['Reason'] = "Twitter規制中(アプリ内)"
			return wRes
		
		#############################
		# 入力チェック
		if inTweet=='' :
			wRes['Reason'] = "Twitter内容がない"
			return wRes
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/statuses/update.json"
		
		#############################
		# パラメータの生成
		wParams = { "status" : inTweet }
		
		#############################
		# APIカウント
		self.__set_APIcount( "status" )
		
		#############################
		# ついーと
		try:
			wTweetRes = self.Twitter_use.post( wAPI, params=wParams )
		except ValueError as err :
			wRes['Reason'] = "Twitter error: " + err
			return wRes
		
		#############################
		# 遅延
		time.sleep( self.DEF_VAL_SLEEP )
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wRes['Reason'] = "Twitter responce failed: " + str(wTweetRes.status_code)
			return wRes
		
		wRes['Result'] = True
		return wRes



#####################################################
# タイムライン読み込み処理
#####################################################
###	def GetTL( self, inTLmode="home", inListID=None, inFLG_Rep=True, inFLG_Rts=False ):
	def GetTL( self, inTLmode="home", inFLG_Rep=True, inFLG_Rts=False, inScreenName=STR_TWITTERdata['TwitterID'], inCount=VAL_TwitNum, inListID=None ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "GetTL"
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# APIの指定
		if inTLmode=="home" :
			wAPI = "https://api.twitter.com/1.1/statuses/home_timeline.json"
			wAPIname = "home_timeline"
		elif inTLmode=="user" :
			wAPI = "https://api.twitter.com/1.1/statuses/user_timeline.json"
			wAPIname = "user_timeline"
		elif inTLmode=="list" and isinstance(inListID, int)==True :
			wAPI = "https://api.twitter.com/1.1/lists/statuses.json"
			wAPIname = "lists_status"
		else :
			wRes['Reason'] = "inTLmode is invalid: " + str(inTLmode)
			return wRes
		
		#############################
		# API規制チェック
		if self.__get_APIrect( wAPIname )!=True :
			wRes['Reason'] = "Twitter規制中(アプリ内)"
			return wRes
		
		#############################
		# パラメータの生成
		if inTLmode=="list" :
			wParams = {
				"count"           : inCount,
				"screen_name"     : inScreenName,
				"exclude_replies" : inFLG_Rep,
				"include_rts"     : inFLG_Rts,
				"list_id"         : inListID
			}
		else :
			wParams = {
				"count"           : inCount,
				"screen_name"     : inScreenName,
				"exclude_replies" : inFLG_Rep,
				"include_rts"     : inFLG_Rts
			}
			## exclude_replies  : リプライを除外する True=除外
			## include_rts      : リツイートを含める True=含める
		
		#############################
		# APIカウント
		self.__set_APIcount( wAPIname )
		
		#############################
		# タイムライン読み込み
		try:
			wTweetRes = self.Twitter_use.get( wAPI, params=wParams )
		except ValueError as err :
			wRes['Reason'] = "Twitter error: " + err
			return wRes
		
		#############################
		# 遅延
		time.sleep( self.DEF_VAL_SLEEP )
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wRes['Reason'] = "Twitter responce failed: " + str(wTweetRes.status_code)
			return wRes
		
		#############################
		# TLを取得
		wRes['Responce'] = json.loads( wTweetRes.text )
		
		#############################
		# 正常
		wRes['Result'] = True
		return wRes



#####################################################
# 検索 読み込み処理
#####################################################
	def GetSearch( self, inKeyword=None, inRoundNum=1 ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "GetSearch"
		
		#############################
		# API規制チェック
		if self.__get_APIrect( "search_tweets" )!=True :
			wRes['Reason'] = "Twitter規制中(アプリ内)"
			return wRes
		
		#############################
		# 入力チェック
		if inKeyword=='' or inKeyword==None :
			wRes['Reason'] = "検索キーがない"
			return wRes
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/search/tweets.json"
		
		#############################
		# パラメータの生成
		wParams = {
			"count"           : self.VAL_TwitSearchNum,
			"q"               : inKeyword
		}
		
		#############################
		# タイムライン読み込み
		wARR_TL = []
		wRound  = 0
		try:
			while True :
				#############################
				# APIカウント
				self.__set_APIcount( "search_tweets" )
				
				wTweetRes = self.Twitter_use.get( wAPI, params=wParams )
				wTimeline = json.loads( wTweetRes.text )
				
				###要素チェック
				if 'statuses' not in wTimeline :
					break
				
				###情報抜き出し
				if len(wTimeline['statuses'])>0 :
					for wLine in wTimeline['statuses'] :
						wARR_TL.append( wLine )
				
				#############################
				# API規制チェック
				if self.__get_APIrect( "search_tweets" )!=True :
					break
				###ページング処理
				wRound += 1
				if inRoundNum<=wRound :
					break
				wIndex = len(wTimeline['statuses']) - 1
				wParams['max_id'] = wTimeline['statuses'][wIndex]['id']
				
				#############################
				# 遅延
				time.sleep( self.DEF_VAL_SLEEP )
			
		except ValueError as err :
			wRes['Reason'] = "Twitter error: " + err
			return wRes
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wCHR_StatusCode = str(wTweetRes.status_code)
			if wCHR_StatusCode in self.STR_TWITTER_STATUS_CODE :
				###定義コードがあるなら文字出力する
				wCHR_StatusCode = self.STR_TWITTER_STATUS_CODE[wCHR_StatusCode]
			else :
				wCHR_StatusCode = "unknown code"
			
			###直前エラーならデコードする
			if 'errors' in wTimeline :
				wCHR_StatusCode = wCHR_StatusCode + ": Error Code=" + str(wTimeline['errors'][0]['code']) + ":" + str(wTimeline['errors'][0]['message'])
			
			wRes['Reason'] = "Twitter responce failed: Status Code=" + str(wTweetRes.status_code) + ":" + wCHR_StatusCode
			return wRes
		
		#############################
		# TLを取得
		wRes['Responce'] = wARR_TL
		
		#############################
		# 正常
		wRes['Result'] = True
		return wRes



#####################################################
# 自ユーザ情報取得処理
#####################################################
	def GetMyUserinfo(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "GetMyUserinfo"
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/users/show.json"
		
		#############################
		# API規制チェック
		if self.__get_APIrect( "users_show" )!=True :
			wRes['Reason'] = "Twitter規制中(アプリ内)"
			return wRes
		
		#############################
		# パラメータの生成
		wParams = { "screen_name" : self.STR_TWITTERdata['TwitterID'] }
		
		#############################
		# 実行
		try:
			wTweetRes = self.Twitter_use.get( wAPI, params=wParams )
		except ValueError as err :
			wRes['Reason'] = "Twitter error: " + err
			return wRes
		
		#############################
		# 遅延
		time.sleep( self.DEF_VAL_SLEEP )
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wRes['Reason'] = "Twitter responce failed: " + str(wTweetRes.status_code)
			return wRes
		
		#############################
		# TLを取得
		wRes['Responce'] = json.loads( wTweetRes.text )
		
		wRes['Result'] = True
		return wRes



#####################################################
# ユーザ情報取得処理
#####################################################
	def GetUserinfo( self, inID=-1, inScreenName=None ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "GetUserinfo"
		
		#############################
		# 入力チェック
		if inID==-1 and inScreenName==None :
			wRes['Reason'] = "Input is Undefined"
			return wRes
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/users/show.json"
		
		#############################
		# API規制チェック
		if self.__get_APIrect( "users_show" )!=True :
			wRes['Reason'] = "Twitter規制中(アプリ内)"
			return wRes
		
		#############################
		# パラメータの生成
		if inID>=0 :
			wParams = { "user_id" : inID }
		else :
			wParams = { "screen_name" : inScreenName }
		
		#############################
		# 実行
		try:
			wTweetRes = self.Twitter_use.get( wAPI, params=wParams )
		except ValueError as err :
			wRes['Reason'] = "Twitter error: " + err
			return wRes
		
		#############################
		# 遅延
		time.sleep( self.DEF_VAL_SLEEP )
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wRes['Reason'] = "Twitter responce failed: " + str(wTweetRes.status_code)
			return wRes
		
		#############################
		# TLを取得
		wRes['Responce'] = json.loads( wTweetRes.text )
		
		wRes['Result'] = True
		return wRes



#####################################################
# フォロー関係取得処理
#####################################################
	def GetFollowInfo( self, inSrcID, inDstID ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "GetFollowInfo"
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/friendships/show.json"
		
		#############################
		# API規制チェック
		if self.__get_APIrect( "friends_show" )!=True :
			wRes['Reason'] = "Twitter規制中(アプリ内)"
			return wRes
		
		#############################
		# パラメータの生成
		wParams = {
			"source_id"		: inSrcID,
			"target_id"		: inDstID
		}
		
		#############################
		# 実行
		try:
			wTweetRes = self.Twitter_use.get( wAPI, params=wParams )
		except ValueError as err :
			wRes['Reason'] = "Twitter error: " + err
			return wRes
		
		#############################
		# 遅延
		time.sleep( self.DEF_VAL_SLEEP )
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wRes['Reason'] = "Twitter responce failed: " + str(wTweetRes.status_code)
			return wRes
		
		#############################
		# TLを取得
		wRes['Responce'] = json.loads( wTweetRes.text )
		
		wRes['Result'] = True
		return wRes



#####################################################
# フォロー一覧読み込み処理
#####################################################
	def GetMyFollowList(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "GetMyFollowList"
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/friends/list.json"
		
		#############################
		# API規制チェック
		if self.__get_APIrect( "friends_list" )!=True :
			wRes['Reason'] = "Twitter規制中(アプリ内)"
			return wRes
		
		#############################
		# パラメータの生成
		wParams = {
			"count"			: self.VAL_TwitNum,
			"cursor"		: "-1",
			"skip_status"	: "True"
##			"screen_name"	: "..."
		}
		
		#############################
		# タイムライン読み込み
		wARR_TL = []
		wFLG_Limit = False
		try:
			while True :
				#############################
				# APIカウント
				self.__set_APIcount( "friends_list" )
				
				wTweetRes = self.Twitter_use.get( wAPI, params=wParams )
				wUsers = json.loads( wTweetRes.text )
				
				###要素チェック
				if 'next_cursor_str' not in wUsers :
					break
				if 'users' not in wUsers :
					break
				
				###情報抜き出し
				if len(wUsers['users'])>0 :
					for wLine in wUsers['users'] :
						wARR_TL.append( wLine )
				
				#############################
				# API規制チェック
				if self.__get_APIrect( "friends_list" )!=True :
					break
				###ページング処理
				if wParams['cursor']==wUsers['next_cursor_str'] :
					break
				if wUsers['next_cursor_str']=="0" :
					break
				wParams['cursor'] = wUsers['next_cursor_str']
				
				#############################
				# 遅延
				time.sleep( self.DEF_VAL_SLEEP )
			
		except ValueError as err :
			wRes['Reason'] = "Twitter error: " + err
			return wRes
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wCHR_StatusCode = str(wTweetRes.status_code)
			if wCHR_StatusCode in self.STR_TWITTER_STATUS_CODE :
				###定義コードがあるなら文字出力する
				wCHR_StatusCode = self.STR_TWITTER_STATUS_CODE[wCHR_StatusCode]
			else :
				wCHR_StatusCode = "unknown code"
			
			###直前エラーならデコードする
			if 'errors' in wUsers :
				wCHR_StatusCode = wCHR_StatusCode + ": Error Code=" + str(wUsers['errors'][0]['code']) + ":" + str(wUsers['errors'][0]['message'])
			
			wRes['Reason'] = "Twitter responce failed: Status Code=" + str(wTweetRes.status_code) + ":" + wCHR_StatusCode
			return wRes
		
		#############################
		# TLを取得
		wRes['Responce'] = wARR_TL
		
		#############################
		# 正常
		wRes['Result'] = True
		return wRes



#####################################################
# フォロワー一覧読み込み処理
#####################################################
	def GetFollowerList(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "GetFollowerList"
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/followers/list.json"
		
		#############################
		# API規制チェック
		if self.__get_APIrect( "followers_list" )!=True :
			wRes['Reason'] = "Twitter規制中(アプリ内)"
			return wRes
		
		#############################
		# パラメータの生成
		wParams = {
			"count"			: self.VAL_TwitNum,
			"cursor"		: "-1",
			"skip_status"	: "True"
##			"screen_name"	: "..."
		}
		
		#############################
		# タイムライン読み込み
		wARR_TL = []
		wFLG_Limit = False
		try:
			while True :
				#############################
				# APIカウント
				self.__set_APIcount( "followers_list" )
				
				wTweetRes = self.Twitter_use.get( wAPI, params=wParams )
				wUsers = json.loads( wTweetRes.text )
				
				###要素チェック
				if 'next_cursor_str' not in wUsers :
					break
				if 'users' not in wUsers :
					break
				
				###情報抜き出し
				if len(wUsers['users'])>0 :
					for wLine in wUsers['users'] :
						wARR_TL.append( wLine )
				
				#############################
				# API規制チェック
				if self.__get_APIrect( "followers_list" )!=True :
					break
				###ページング処理
				if wParams['cursor']==wUsers['next_cursor_str'] :
					break
				if wUsers['next_cursor_str']=="0" :
					break
				wParams['cursor'] = wUsers['next_cursor_str']
				
				#############################
				# 遅延
				time.sleep( self.DEF_VAL_SLEEP )
			
		except ValueError as err :
			wRes['Reason'] = "Twitter error: " + err
			return wRes
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wCHR_StatusCode = str(wTweetRes.status_code)
			if wCHR_StatusCode in self.STR_TWITTER_STATUS_CODE :
				###定義コードがあるなら文字出力する
				wCHR_StatusCode = self.STR_TWITTER_STATUS_CODE[wCHR_StatusCode]
			else :
				wCHR_StatusCode = "unknown code"
			
			###直前エラーならデコードする
			if 'errors' in wUsers :
				wCHR_StatusCode = wCHR_StatusCode + ": Error Code=" + str(wUsers['errors'][0]['code']) + ":" + str(wUsers['errors'][0]['message'])
			
			wRes['Reason'] = "Twitter responce failed: Status Code=" + str(wTweetRes.status_code) + ":" + wCHR_StatusCode
			return wRes
		
		#############################
		# TLを取得
		wRes['Responce'] = wARR_TL
		
		#############################
		# 正常
		wRes['Result'] = True
		return wRes



#####################################################
# フォロー処理
#####################################################
	def CreateFollow( self, inID ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "CreateFollow"
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/friendships/create.json"
		
		#############################
		# API規制チェック
		if self.__get_APIrect( "friendships" )!=True :
			wRes['Reason'] = "Twitter規制中(アプリ内)"
			return wRes
		
		#############################
		# パラメータの生成
		wParams = { "id" : inID }
		
		#############################
		# 実行
		try:
			wTweetRes = self.Twitter_use.post( wAPI, params=wParams )
		except ValueError as err :
			wRes['Reason'] = "Twitter error: " + err
			return wRes
		
		#############################
		# 遅延
		time.sleep( self.DEF_VAL_SLEEP )
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wRes['Reason'] = "Twitter responce failed: " + str(wTweetRes.status_code)
			return wRes
		
		wRes['Result'] = True
		return wRes



#####################################################
# フォロー解除処理
#####################################################
	def RemoveFollow( self, inID ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "RemoveFollow"
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/friendships/destroy.json"
		
		#############################
		# パラメータの生成
		wParams = { "id" : inID }
		
		#############################
		# 実行
		try:
			wTweetRes = self.Twitter_use.post( wAPI, params=wParams )
		except ValueError as err :
			wRes['Reason'] = "Twitter error: " + err
			return wRes
		
		#############################
		# 遅延
		time.sleep( self.DEF_VAL_SLEEP )
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wRes['Reason'] = "Twitter responce failed: " + str(wTweetRes.status_code)
			return wRes
		
		wRes['Result'] = True
		return wRes



#####################################################
# ミュートIDs
#####################################################
	def GetMuteIDs(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "GetMuteIDs"
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/mutes/users/ids.json"
		
		#############################
		# API規制チェック
		if self.__get_APIrect( "mute_list" )!=True :
			wRes['Reason'] = "Twitter規制中(アプリ内)"
			return wRes
		
		#############################
		# パラメータの生成
		wParams = { "cursor"		: "-1"
		}
		
		#############################
		# タイムライン読み込み
		wARR_TL = []
		wFLG_Limit = False
		try:
			while True :
				#############################
				# APIカウント
				self.__set_APIcount( "mute_list" )
				
				wTweetRes = self.Twitter_use.get( wAPI, params=wParams )
				wIDs = json.loads( wTweetRes.text )
				
				###要素チェック
				if 'next_cursor_str' not in wIDs :
					break
				if 'users' not in wIDs :
					break
				
				###情報抜き出し
				if len(wIDs['ids'])>0 :
					for wLine in wIDs['ids'] :
						wARR_TL.append( wLine )
				
				#############################
				# API規制チェック
				if self.__get_APIrect( "mute_list" )!=True :
					break
				###ページング処理
				if wParams['cursor']==wIDs['next_cursor_str'] :
					break
				if wIDs['next_cursor_str']=="0" :
					break
				wParams['cursor'] = wIDs['next_cursor_str']
				
				#############################
				# 遅延
				time.sleep( self.DEF_VAL_SLEEP )
			
		except ValueError as err :
			wRes['Reason'] = "Twitter error: " + err
			return wRes
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wCHR_StatusCode = str(wTweetRes.status_code)
			if wCHR_StatusCode in self.STR_TWITTER_STATUS_CODE :
				###定義コードがあるなら文字出力する
				wCHR_StatusCode = self.STR_TWITTER_STATUS_CODE[wCHR_StatusCode]
			else :
				wCHR_StatusCode = "unknown code"
			
			###直前エラーならデコードする
			if 'errors' in wUsers :
				wCHR_StatusCode = wCHR_StatusCode + ": Error Code=" + str(wUsers['errors'][0]['code']) + ":" + str(wUsers['errors'][0]['message'])
			
			wRes['Reason'] = "Twitter responce failed: Status Code=" + str(wTweetRes.status_code) + ":" + wCHR_StatusCode
			return wRes
		
		#############################
		# TLを取得
		self.ARR_MuteList = wARR_TL
		wRes['Responce']  = wARR_TL
		
		#############################
		# 正常
		wRes['Result'] = True
		return wRes



#####################################################
# ミュート処理
#####################################################
	def CreateMute( self, inID ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "CreateMute"
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# ミュート一覧が空ならまず取得しにいく
		if len(self.ARR_MuteList)==0 :
			wResList = self.GetMuteIDs()
			if wResList['Result']!=True :
				wRes['Reason'] = "GetLists failed: " + str(wResList['Reason'])
				return wRes
		
		#############################
		# ミュート一覧にあったら終了
		if inID in self.ARR_MuteList :
			wRes['Responce'] = False
			wRes['Result']   = True
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/mutes/users/create.json"
		
		#############################
		# API規制チェック
		if self.__get_APIrect( "muted" )!=True :
			wRes['Reason'] = "Twitter規制中(アプリ内)"
			return wRes
		
		#############################
		# パラメータの生成
		wParams = { "id" : inID }
		
		#############################
		# 実行
		try:
			wTweetRes = self.Twitter_use.post( wAPI, params=wParams )
		except ValueError as err :
			wRes['Reason'] = "Twitter error: " + err
			return wRes
		
		#############################
		# 遅延
		time.sleep( self.DEF_VAL_SLEEP )
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wRes['Reason'] = "Twitter responce failed: " + str(wTweetRes.status_code)
			return wRes
		
		wRes['Responce'] = True
		wRes['Result']   = True
		return wRes



#####################################################
# ミュート解除処理
#####################################################
	def RemoveMute( self, inID ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "RemoveFollow"
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# ミュート一覧が空ならまず取得しにいく
		if len(self.ARR_MuteList)==0 :
			wResList = self.GetMuteIDs()
			if wResList['Result']!=True :
				wRes['Reason'] = "GetLists failed: " + str(wResList['Reason'])
				return wRes
		
		#############################
		# ミュート一覧になかったら終了
		if inID not in self.ARR_MuteList :
			wRes['Responce'] = False
			wRes['Result']   = True
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/mutes/users/destroy.json"
		
		#############################
		# パラメータの生成
		wParams = { "id" : inID }
		
		#############################
		# 実行
		try:
			wTweetRes = self.Twitter_use.post( wAPI, params=wParams )
		except ValueError as err :
			wRes['Reason'] = "Twitter error: " + err
			return wRes
		
		#############################
		# 遅延
		time.sleep( self.DEF_VAL_SLEEP )
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wRes['Reason'] = "Twitter responce failed: " + str(wTweetRes.status_code)
			return wRes
		
		wRes['Responce'] = True
		wRes['Result']   = True
		return wRes



#####################################################
# いいね一覧読み込み処理
#####################################################
	def GetFavolist(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "GetFavolist"
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/favorites/list.json"
		
		#############################
		# API規制チェック
		if self.__get_APIrect( "favorites_list" )!=True :
			wRes['Reason'] = "Twitter規制中(アプリ内)"
			return wRes
		
		#############################
		# パラメータの生成
		wParams = {
			"count"			: self.VAL_TwitNum,
			"cursor"		: "-1",
			"skip_status"	: "True"
##			"screen_name"	: "..."
		}
		
		#############################
		# タイムライン読み込み
		wARR_TL = []
		wFLG_Limit = False
		try:
			while True :
				#############################
				# APIカウント
				self.__set_APIcount( "favorites_list" )
				
				wTweetRes = self.Twitter_use.get( wAPI, params=wParams )
				wTL = json.loads( wTweetRes.text )
				
				###情報抜き出し
				if len(wTL)>0 :
					for wLine in wTL :
						wARR_TL.append( wLine )
				
				#############################
				# API規制チェック
				if self.__get_APIrect( "favorites_list" )!=True :
					break
				###ページング処理
				if 'next_cursor_str' not in wTL :
					break
				if wParams['cursor']==wTL['next_cursor_str'] :
					break
				if wTL['next_cursor_str']=="0" :
					break
				wParams['cursor'] = wUsers['next_cursor_str']
				
				#############################
				# 遅延
				time.sleep( self.DEF_VAL_SLEEP )
			
		except ValueError as err :
			wRes['Reason'] = "Twitter error: " + err
			return wRes
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wCHR_StatusCode = str(wTweetRes.status_code)
			if wCHR_StatusCode in self.STR_TWITTER_STATUS_CODE :
				###定義コードがあるなら文字出力する
				wCHR_StatusCode = self.STR_TWITTER_STATUS_CODE[wCHR_StatusCode]
			else :
				wCHR_StatusCode = "unknown code"
			
			###直前エラーならデコードする
			if 'errors' in wUsers :
				wCHR_StatusCode = wCHR_StatusCode + ": Error Code=" + str(wUsers['errors'][0]['code']) + ":" + str(wUsers['errors'][0]['message'])
			
			wRes['Reason'] = "Twitter responce failed: Status Code=" + str(wTweetRes.status_code) + ":" + wCHR_StatusCode
			return wRes
		
		#############################
		# TLを取得
		wRes['Responce'] = wARR_TL
		
		#############################
		# 正常
		wRes['Result'] = True
		return wRes



#####################################################
# いいね処理
#####################################################
	def CreateFavo( self, inID ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "CreateFavo"
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/favorites/create.json"
		
		#############################
		# API規制チェック
		if self.__get_APIrect( "favorites" )!=True :
			wRes['Reason'] = "Twitter規制中(アプリ内)"
			return wRes
		
		#############################
		# パラメータの生成
		wParams = { "id" : inID }
		
		#############################
		# 実行
		try:
			wTweetRes = self.Twitter_use.post( wAPI, params=wParams )
		except ValueError as err :
			wRes['Reason'] = "Twitter error: " + err
			return wRes
		
		#############################
		# 遅延
		time.sleep( self.DEF_VAL_SLEEP )
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wRes['Reason'] = "Twitter responce failed: " + str(wTweetRes.status_code)
			return wRes
		
		wRes['Result'] = True
		return wRes



#####################################################
# いいね解除処理
#####################################################
	def RemoveFavo( self, inID ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "RemoveFavo"
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/favorites/destroy.json"
		
		#############################
		# パラメータの生成
		wParams = { "id" : inID }
		
		#############################
		# 実行
		try:
			wTweetRes = self.Twitter_use.post( wAPI, params=wParams )
		except ValueError as err :
			wRes['Reason'] = "Twitter error: " + err
			return wRes
		
		#############################
		# 遅延
		time.sleep( self.DEF_VAL_SLEEP )
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wRes['Reason'] = "Twitter responce failed: " + str(wTweetRes.status_code)
			return wRes
		
		wRes['Result'] = True
		return wRes



#####################################################
# リスト一覧の取得
#####################################################
	def GetLists(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "GetLists"
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + str(wResIni['Reason'])
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/lists/list.json"
		
		#############################
		# API規制チェック
		if self.__get_APIrect( "lists_list" )!=True :
			wRes['Reason'] = "Twitter規制中(アプリ内)"
			return wRes
		
		#############################
		# パラメータの生成
		wParams = {
			"screen_name" : self.STR_TWITTERdata['TwitterID']
		}
		
		#############################
		# APIカウント
		self.__set_APIcount( "lists_list" )
		
		#############################
		# タイムライン読み込み
		try:
			wTweetRes = self.Twitter_use.get( wAPI, params=wParams )
		except ValueError as err :
			wRes['Reason'] = "Twitter error: " + err
			return wRes
		
		#############################
		# 遅延
		time.sleep( self.DEF_VAL_SLEEP )
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wRes['Reason'] = "Twitter responce failed: " + str(wTweetRes.status_code)
			return wRes
		
		#############################
		# リストを取得
		wTweetList = json.loads( wTweetRes.text )
		
		#############################
		# Twitterリストの作成
		self.ARR_TwitterList = {}	#Twitterリスト
		wIndex = 0
		for wROW in wTweetList :
			#自分のリストではない
			if wROW['user']['name']!=self.STR_TWITTERdata['TwitterID'] :
				continue
			
			wCell = {}
			wCell.update({ "id"   : wROW['id'] })
			wCell.update({ "name" : wROW['name'] })
			self.ARR_TwitterList.update({ wIndex : wCell })
			wIndex += 1
		
		#############################
		# 一覧を返す
		wRes['Responce'] = self.ARR_TwitterList
		
		#############################
		# 正常
		wRes['Result'] = True
		return wRes



#####################################################
# リスト登録者一覧の取得
#####################################################
	def GetListMember( self, inListName ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "GetListMember"
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + str(wResIni['Reason'])
			return wRes
		
		#############################
		# リスト一覧が空ならまず取得しにいく
		if len(self.ARR_TwitterList)==0 :
			wResList = self.GetLists()
			if wResList['Result']!=True :
				wRes['Reason'] = "GetLists failed: " + str(wResList['Reason'])
				return wRes
		
		#############################
		# リスト名のIDを取得
		wListID = -1
		wKeylist = self.ARR_TwitterList.keys()
		for wKey in wKeylist :
			if self.ARR_TwitterList[wKey]['name']==inListName :
				###リスト発見 =idを取得する
				wListID = self.ARR_TwitterList[wKey]['id']
				break
		
		if wListID==-1 :
			wRes['Reason'] = "List is not found: " + inListName
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/lists/members.json"
		
		#############################
		# API規制チェック
		if self.__get_APIrect( "lists_members" )!=True :
			wRes['Reason'] = "Twitter規制中(アプリ内)"
			return wRes
		
		#############################
		# パラメータの生成
		wParams = { "list_id"		: wListID,
					"count"			: self.VAL_TwitListNum,
					"cursor"		: "-1",
					"skip_status"	: "True"
##					"screen_name"	: "..."
		}
		
		#############################
		# タイムライン読み込み
		wARR_TL = []
		wFLG_Limit = False
		try:
			while True :
				#############################
				# APIカウント
				self.__set_APIcount( "lists_members" )
				
				wTweetRes = self.Twitter_use.get( wAPI, params=wParams )
				wUsers = json.loads( wTweetRes.text )
				
				###要素チェック
				if 'next_cursor_str' not in wUsers :
					break
				if 'users' not in wUsers :
					break
				
				###情報抜き出し
				if len(wUsers['users'])>0 :
					for wLine in wUsers['users'] :
						wARR_TL.append( wLine )
				
				#############################
				# API規制チェック
				if self.__get_APIrect( "lists_members" )!=True :
					break
				###ページング処理
				if wParams['cursor']==wUsers['next_cursor_str'] :
					break
				if wUsers['next_cursor_str']=="0" :
					break
				wParams['cursor'] = wUsers['next_cursor_str']
				
				#############################
				# 遅延
				time.sleep( self.DEF_VAL_SLEEP )
			
		except ValueError as err :
			wRes['Reason'] = "Twitter error: " + err
			return wRes
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wCHR_StatusCode = str(wTweetRes.status_code)
			if wCHR_StatusCode in self.STR_TWITTER_STATUS_CODE :
				###定義コードがあるなら文字出力する
				wCHR_StatusCode = self.STR_TWITTER_STATUS_CODE[wCHR_StatusCode]
			else :
				wCHR_StatusCode = "unknown code"
			
			###直前エラーならデコードする
			if 'errors' in wUsers :
				wCHR_StatusCode = wCHR_StatusCode + ": Error Code=" + str(wUsers['errors'][0]['code']) + ":" + str(wUsers['errors'][0]['message'])
			
			wRes['Reason'] = "Twitter responce failed: Status Code=" + str(wTweetRes.status_code) + ":" + wCHR_StatusCode
			return wRes
		
		#############################
		# TLを取得
		wRes['Responce'] = wARR_TL
		
		#############################
		# 正常
		wRes['Result'] = True
		return wRes



#####################################################
# リストへ追加処理
#####################################################
	def AddUserList( self, inListName, inUserID ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "AddUserList"
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# リスト一覧が空ならまず取得しにいく
		if len(self.ARR_TwitterList)==0 :
			wResList = self.GetLists()
			if wResList['Result']!=True :
				wRes['Reason'] = "GetLists failed: " + str(wResList['Reason'])
				return wRes
		
		#############################
		# リスト名のIDを取得
		wListID = -1
		wKeylist = self.ARR_TwitterList.keys()
		for wKey in wKeylist :
			if self.ARR_TwitterList[wKey]['name']==inListName :
				###リスト発見 =idを取得する
				wListID = self.ARR_TwitterList[wKey]['id']
				break
		
		if wListID==-1 :
			wRes['Reason'] = "List is not found: " + inListName
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/lists/members/create.json"
		
		#############################
		# パラメータの生成
		wParams = { "list_id" : wListID,
					"user_id" : inUserID
		}
		
		#############################
		# 実行
		try:
			wTweetRes = self.Twitter_use.post( wAPI, params=wParams )
		except ValueError as err :
			wRes['Reason'] = "Twitter error: " + err
			return wRes
		
		#############################
		# 遅延
		time.sleep( self.DEF_VAL_SLEEP )
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wRes['Reason'] = "Twitter responce failed: " + str(wTweetRes.status_code)
			return wRes
		
		wRes['Result'] = True
		return wRes



#####################################################
# リストから削除処理
#####################################################
	def RemoveUserList( self, inListName, inUserID ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "RemoveUserList"
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# リスト一覧が空ならまず取得しにいく
		if len(self.ARR_TwitterList)==0 :
			wResList = self.GetLists()
			if wResList['Result']!=True :
				wRes['Reason'] = "GetLists failed: " + str(wResList['Reason'])
				return wRes
		
		#############################
		# リスト名のIDを取得
		wListID = -1
		wKeylist = self.ARR_TwitterList.keys()
		for wKey in wKeylist :
			if self.ARR_TwitterList[wKey]['name']==inListName :
				###リスト発見 =idを取得する
				wListID = self.ARR_TwitterList[wKey]['id']
				break
		
		if wListID==-1 :
			wRes['Reason'] = "List is not found: " + inListName
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/lists/members/destroy.json"
		
		#############################
		# パラメータの生成
		wParams = { "list_id" : wListID,
					"user_id" : inUserID
		}
		
		#############################
		# 実行
		try:
			wTweetRes = self.Twitter_use.post( wAPI, params=wParams )
		except ValueError as err :
			wRes['Reason'] = "Twitter error: " + err
			return wRes
		
		#############################
		# 遅延
		time.sleep( self.DEF_VAL_SLEEP )
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wRes['Reason'] = "Twitter responce failed: " + str(wTweetRes.status_code)
			return wRes
		
		wRes['Result'] = True
		return wRes



#####################################################
# トレンド読み込み処理
#####################################################
	def GetTrends(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = self.__Get_Resp()
		wRes['Func'] = "GetTrends"
		
		#############################
		# Twitter状態のチェック
		wResIni = self.GetTwStatus()
		if wResIni['Init']!=True :
			wRes['Reason'] = "Twitter connect error: " + wResIni['Reason']
			return wRes
		
		#############################
		# APIの指定
		wAPI = "https://api.twitter.com/1.1/trends/place.json"
		
		#############################
		# API規制チェック
		if self.__get_APIrect( "trends_place" )!=True :
			wRes['Reason'] = "Twitter規制中(アプリ内)"
			return wRes
		
		#############################
		# パラメータの生成
		wParams = {
			"id" : self.DEF_WOEID
		}
		
		#############################
		# APIカウント
		self.__set_APIcount( "trends_place" )
		
		#############################
		# タイムライン読み込み
		try:
			wTweetRes = self.Twitter_use.get( wAPI, params=wParams )
		except ValueError as err :
			wRes['Reason'] = "GetTL: Twitter error: " + err
			return wRes
		
		#############################
		# 遅延
		time.sleep( self.DEF_VAL_SLEEP )
		
		#############################
		# 結果
		if wTweetRes.status_code != 200 :
			wRes['Reason'] = "Twitter responce failed: " + str(wTweetRes.status_code)
			return wRes
		
		#############################
		# TLを取得
		wRes['Responce'] = json.loads( wTweetRes.text )
		
		#############################
		# 正常
		wRes['Result'] = True
		return wRes



