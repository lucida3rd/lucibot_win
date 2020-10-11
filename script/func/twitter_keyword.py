#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : Twitter監視 キーワード抽出
# 
# ::Update= 2020/10/12
#####################################################
# Private Function:
#   __out_CSV( self, inPath, inARR_List ):
#
# Instance Function:
#   __init__( self, parentObj=None ):
#   Get(self):
#   OutCSV(self):
#
# Class Function(static):
#   (none)
#
#####################################################

from osif import CLS_OSIF
from filectrl import CLS_File
from gval import gVal
#####################################################
class CLS_TwitterKeyword():
#####################################################
	OBJ_Parent = ""				#親クラス実体

#####################################################
# Init
#####################################################
	def __init__( self, parentObj=None ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterKeyword"
		wRes['Func']  = "__init__"
		
		if parentObj==None :
			###親クラス実体の未設定
			wRes['Reason'] = "You have not set the parent class entity for parentObj"
			gVal.OBJ_L.Log( "A", wRes )
			return
		
		self.OBJ_Parent = parentObj
		return



#####################################################
# キーユーザの取得
#####################################################
	def Get(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterKeyword"
		wRes['Func']  = "Get"
		
		#############################
		# 取得開始の表示
		CLS_OSIF.sPrn( "タイムラインサーチ中。しばらくお待ちください......" )
		
		#############################
		# ★検索キーの取得（仮処理）★
		self.OBJ_Parent.STR_Keywords = {
			"マインクラフト OR マイクラ OR minecraft"	: 0,
			"#ARK"										: 0,
			"アズレン OR アズールレーン"				: 0,
			"#ETS2 OR Euro Truck"						: 0,
			"#ATS OR American Truck"					: 0,
			"ホロライブ OR Hololive"					: 0
		}
		self.OBJ_Parent.FLG_Search_JP    = True		#検索は日本語のみ
		self.OBJ_Parent.FLG_Search_IncRt = False	#検索にリツイートを含める
		
		#############################
		self.OBJ_Parent.STR_KeyUser = {}
		#############################
		# 取得
		wKeylist = self.OBJ_Parent.STR_Keywords.keys()
		for wWord in wKeylist :
			CLS_OSIF.sPrn( "取得中... 検索語=" + wWord )
			
			wTwitterRes = gVal.OBJ_Twitter.GetSearch( inKeyword=wWord, inRoundNum=gVal.DEF_STR_TLNUM['searchRoundNum'] )
			if wTwitterRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error: " + wTwitterRes['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			self.OBJ_Parent.STR_Cope['TimelineNum'] += len(wTwitterRes['Responce'])
			
			#############################
			# 必要な情報だけ抜き出す
			for wLine in wTwitterRes['Responce'] :
				###検索は日本語のみの場合、
				###  日本語以外はスキップする
				if self.OBJ_Parent.FLG_Search_JP==True :
					if str(wLine['lang'])!="ja" :
						continue
				###検索にリツイートを含めない場合、
				###  リツイートはスキップする
				if self.OBJ_Parent.FLG_Search_IncRt==False :
					if "retweeted_status" in wLine :
						continue
				###既に同じユーザを抽出した
				if str(wLine['user']['id']) in self.OBJ_Parent.STR_KeyUser :
					continue
				###既にフォローしているユーザ
				if str(wLine['user']['id']) in self.OBJ_Parent.ARR_MyFollowID :
					continue
				###一度でもフォロー・リムーブしたことあるユーザ
				if str(wLine['user']['id']) in self.OBJ_Parent.ARR_OldUserID :
					continue
				###アンフォローリストに登録しているユーザ
				if str(wLine['user']['id']) in self.OBJ_Parent.ARR_UnRefollowListMenberID :
					continue
				
				wSTR_Cell = {}
				wSTR_Cell.update({ "id"          : str(wLine['user']['id']) })
				wSTR_Cell.update({ "user_name"   : str(wLine['user']['name']) })
				wSTR_Cell.update({ "screen_name" : str(wLine['user']['screen_name']) })
				wSTR_Cell.update({ "hit_word"    : wWord })
				self.OBJ_Parent.STR_KeyUser.update({ str(wLine['user']['id']) : wSTR_Cell })
				self.OBJ_Parent.STR_Keywords[wWord] += 1
				
				###リツイート元
				if "retweeted_status" in wLine :
					###既に同じユーザを抽出した
					if str(wLine['retweeted_status']['user']['id']) in self.OBJ_Parent.STR_KeyUser :
						continue
					###既にフォローしているユーザ
					if str(wLine['retweeted_status']['user']['id']) in self.OBJ_Parent.ARR_MyFollowID :
						continue
					###一度でもフォロー・リムーブしたことあるユーザ
					if str(wLine['retweeted_status']['user']['id']) in self.OBJ_Parent.ARR_OldUserID :
						continue
					###アンフォローリストに登録しているユーザ
					if str(wLine['retweeted_status']['user']['id']) in self.OBJ_Parent.ARR_UnRefollowListMenberID :
						continue
					
					wSTR_Cell = {}
					wSTR_Cell.update({ "id"          : str(wLine['retweeted_status']['user']['id']) })
					wSTR_Cell.update({ "user_name"   : str(wLine['retweeted_status']['user']['name']) })
					wSTR_Cell.update({ "screen_name" : str(wLine['retweeted_status']['user']['screen_name']) })
					wSTR_Cell.update({ "hit_word"    : wWord })
					self.OBJ_Parent.STR_KeyUser.update({ str(wLine['retweeted_status']['user']['id']) : wSTR_Cell })
					self.OBJ_Parent.STR_Keywords[wWord] += 1
		
		#############################
		# キーユーザ数
		self.OBJ_Parent.STR_Cope['KeyUserNum'] += len(self.OBJ_Parent.STR_KeyUser)
		
		#############################
		# 正常終了
		wRes['Result'] = True
		return wRes



#####################################################
# キーユーザCSV出力
#####################################################
	def OutCSV(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterKeyword"
		wRes['Func']  = "OutCSV"
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " キーユーザCSV出力" + '\n'
		wStr = wStr + "--------------------" + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "出力するキーユーザを選出しています。しばらくお待ちください......" + '\n'
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# キーユーザからランダムに選出する
		wARR_RandID = []
		wKeylist = list( self.OBJ_Parent.STR_KeyUser.keys() )
		wKeyNum  = len( wKeylist )
		wCount   = 0
		wRetry   = 0
		while True:
			if gVal.DEF_STR_TLNUM['randKeyUserNum']<=wCount :
				break	#選出数上限
			
			wRand = CLS_OSIF.sGetRand( wKeyNum )
			wKey  = wKeylist[wRand]
			wID = self.OBJ_Parent.STR_KeyUser[wKey]['id']
			if wID in wARR_RandID :
				if wRetry<=5 :
					###リトライする
					wRetry += 1
				else:
					###リトライ回数超えたら、その回は未選出にする
					wCount += 1
					wRetry = 0
				continue	#既に選出されたID
			
			wARR_RandID.append( wID )
			wCount += 1
			wRetry = 0
		
		#############################
		# CSV書き込み
		
		# ファイル名の設定
		wCHR_File_path = gVal.DEF_USERDATA_PATH + "keyusers_" + str(gVal.STR_UserInfo['Account']) + ".csv"
		
		if self.__out_CSV( wCHR_File_path, wARR_RandID )!=True :
			###失敗
			wRes['Reason'] = "sWriteFile is failed: " + wCHR_File_path
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		
		#############################
		# 取得開始の表示
		CLS_OSIF.sPrn( "キーユーザをCSVに出力しました: " + wCHR_File_path + '\n' )
		
		#############################
		# 正常終了
		wRes['Result'] = True
		return wRes

	#####################################################
	def __out_CSV( self, inPath, inARR_List ):
		#############################
		# 書き込みデータを作成
		wSetLine = []
		
		#############################
		# ヘッダ部
		wLine = "user_name, screen_name, hit_word, url, " + '\n'
		wSetLine.append(wLine)
		
		#############################
		# データ部
		for wKey in inARR_List :
			wLine = ""
			wLine = wLine + self.OBJ_Parent.STR_KeyUser[wKey]['user_name'] + ", "
			wLine = wLine + self.OBJ_Parent.STR_KeyUser[wKey]['screen_name'] + ", "
			wLine = wLine + self.OBJ_Parent.STR_KeyUser[wKey]['hit_word'] + ", "
			wLine = wLine + "https://twitter.com/" + self.OBJ_Parent.STR_KeyUser[wKey]['screen_name'] + ", " + '\n'
			wSetLine.append(wLine)
		
		#############################
		# ファイル上書き書き込み
		if CLS_File.sWriteFile( inPath, wSetLine, inExist=False )!=True :
			return False	#失敗
		
		return True










#####################################################
# タイムラインの表示
#####################################################
#	def View(self):
#		#############################
#		# 応答形式の取得
#		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
#		wRes = CLS_OSIF.sGet_Resp()
#		wRes['Class'] = "CLS_TwitterKeyword"
#		wRes['Func']  = "View"
#		
#		#############################
#		# 集計のリセット
###		self.OBJ_Parent.STR_Cope['TimelineNum'] = 0
###		self.OBJ_Parent.STR_Cope['KeywordNum']  = 0
###		self.OBJ_Parent.STR_Cope['KeywordHit']  = 0
###		
###		self.OBJ_Parent.STR_Cope['DB_Num']    = 0
#		
#		#############################
#		# 画面クリア
#		CLS_OSIF.sDispClr()
#		
#		#############################
#		# ヘッダ表示
#		wStr = "--------------------" + '\n'
#		wStr = wStr + " キーユーザの表示" + '\n'
#		wStr = wStr + "--------------------" + '\n'
#		
#		#############################
#		# 情報組み立て
#		wKeylist = self.OBJ_Parent.STR_KeyUser.keys()
#		for wKey in wKeylist :
#			wStr = wStr + "ユーザ=" + self.OBJ_Parent.STR_KeyUser[wKey]['screen_name'] + "(@" + self.OBJ_Parent.STR_KeyUser[wKey]['user_name'] + ")" + '\n'
#			wStr = wStr + "Hitワード=" + self.OBJ_Parent.STR_KeyUser[wKey]['hit_word'] + '\n'
#			wStr = wStr + "--------------------" + '\n'
#		
#		#############################
#		# 統計
#		wStr = wStr + "--------------------" + '\n'
#####		wStr = wStr + "DB登録数          = " + str(self.OBJ_Parent.STR_Cope['DB_Num']) + '\n'
#		wStr = wStr + "タイムライン数    = " + str(self.OBJ_Parent.STR_Cope['TimelineNum']) + '\n'
#		wStr = wStr + "キーユーザ数      = " + str(self.OBJ_Parent.STR_Cope['KeyUserNum']) + '\n'
#		wStr = wStr + '\n'
#		
#		wKeylist = self.OBJ_Parent.STR_Keywords.keys()
#		for wWord in wKeylist :
#			wStr = wStr + wWord + " = " + str(self.OBJ_Parent.STR_Keywords[wWord]) + '\n'
#		
#		#############################
#		# コンソールに表示
#		CLS_OSIF.sPrn( wStr )
#		
#		#############################
#		# 完了
#		wRes['Result'] = True
#		return wRes
#
#

#####################################################
# タイムラインの表示
#####################################################
#	def View(self):
#		#############################
#		# 応答形式の取得
#		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
#		wRes = CLS_OSIF.sGet_Resp()
#		wRes['Class'] = "CLS_TwitterKeyword"
#		wRes['Func']  = "View"
#		
#		#############################
#		# 集計のリセット
###		self.OBJ_Parent.STR_Cope['TimelineNum'] = 0
###		self.OBJ_Parent.STR_Cope['KeywordNum']  = 0
###		self.OBJ_Parent.STR_Cope['KeywordHit']  = 0
###		
###		self.OBJ_Parent.STR_Cope['DB_Num']    = 0
#		
#		#############################
#		# 画面クリア
#		CLS_OSIF.sDispClr()
#		
#		#############################
#		# ヘッダ表示
#		wStr = "--------------------" + '\n'
#		wStr = wStr + " 保持中のタイムライン" + '\n'
#		wStr = wStr + "--------------------" + '\n'
#		
#		#############################
#		# 情報組み立て
#		for wLine in self.OBJ_Parent.STR_Timeline :
####			wStr = wStr + str(wLine) + '\n'
#
#			wFLG_Retweet = False
#			if "retweeted_status" in wLine :
#				wFLG_Retweet = True
#			else:
#				###準ツイート
#				self.OBJ_Parent.STR_Cope['OrTweetNum'] += 1
#			
#
###			if "created_at" not in wLine :
###				print("xxxx1")
###				continue
#
#			wTime = CLS_OSIF.sGetTimeformat_Twitter( wLine['created_at'] )
#			if wTime['Result']!=True :
#				wRes['Reason'] = "sGetTimeformat_Twitter is failed: " + str(wLine['created_at'])
#				gVal.OBJ_L.Log( "B", wRes )
#				return wRes
#			
#			wStr = wStr + str(wLine['text']) + '\n'
#			wStr = wStr + "ツイ日=" + str(wTime['TimeDate'])
#			wStr = wStr + "  ユーザ=" + str(wLine['user']['screen_name']) + "(@" + str(wLine['user']['name']) + ")" + '\n'
#			if wFLG_Retweet==True :
#				wStr = wStr + "[Ｒ]リツイート" + '\n'
#			else:
#				wStr = wStr + "[〇]純ツイート" + '\n'
#			
#			wStr = wStr + "--------------------" + '\n'
#			
#			###リツイート元
#			if wFLG_Retweet==True :
#				wTime = CLS_OSIF.sGetTimeformat_Twitter( wLine['retweeted_status']['created_at'] )
#				if wTime['Result']!=True :
#					wRes['Reason'] = "sGetTimeformat_Twitter is failed: " + str(wLine['retweeted_status']['created_at'])
#					gVal.OBJ_L.Log( "B", wRes )
#					return wRes
#				
#				wStr = wStr + str(wLine['retweeted_status']['text']) + '\n'
#				wStr = wStr + "ツイ日=" + str(wTime['TimeDate'])
#				wStr = wStr + "  ユーザ=" + str(wLine['retweeted_status']['user']['screen_name']) + "(@" + str(wLine['retweeted_status']['user']['name']) + ")" + '\n'
#				wStr = wStr + "[★]リツイート元" + '\n'
#				
#				wStr = wStr + "--------------------" + '\n'
#
#		
#		#############################
#		# 統計
#		wStr = wStr + "--------------------" + '\n'
####		wStr = wStr + "DB登録数          = " + str(self.OBJ_Parent.STR_Cope['DB_Num']) + '\n'
#		wStr = wStr + "タイムライン数    = " + str(self.OBJ_Parent.STR_Cope['TimelineNum']) + '\n'
#		wStr = wStr + "純ツイート数      = " + str(self.OBJ_Parent.STR_Cope['OrTweetNum']) + '\n'
#		
#		#############################
#		# コンソールに表示
#		CLS_OSIF.sPrn( wStr )
#		
#		#############################
#		# 完了
#		wRes['Result'] = True
#		return wRes
#
#

#####################################################
# いいね監視の実行
#####################################################
	def Run(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterFavo"
		wRes['Func']  = "Run"
		
		#############################
		# 集計のリセット
		self.OBJ_Parent.STR_Cope['tFavoRemove'] = 0
		self.OBJ_Parent.STR_Cope['FavoRemove']  = 0
		
		self.OBJ_Parent.STR_Cope['DB_Update'] = 0
		
		#############################
		# DBのいいね一覧取得 (いいね解除対象の抜き出し)
		wQuery = "select * from tbl_favo_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "' and " + \
					"limited = True and " + \
					"removed = False " + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		
		#############################
		# 辞書型に整形
		wARR_RateFavoID = {}
		gVal.OBJ_DB.ChgDict( wResDB['Responce']['Collum'], wResDB['Responce']['Data'], outDict=wARR_RateFavoID )
		self.OBJ_Parent.STR_Cope['tFavoRemove'] = len(wARR_RateFavoID)
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " いいね監視 実行" + '\n'
		wStr = wStr + "--------------------" + '\n'
		
		wVAL_ZanNum = len(wARR_RateFavoID)
		wFavoLimNum = 0
		wResStop = False
		#############################
		# いいね解除していく
		wKeylist = wARR_RateFavoID.keys()
		for wIndex in wKeylist :
			wID = str( wARR_RateFavoID[wIndex]['id'] )
			
			###  いいねを外す
			wRemoveRes = gVal.OBJ_Twitter.RemoveFavo( wID )
			if wRemoveRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error: " + wRemoveRes['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			
			###  解除したいいねを表示
			wStr = str(wARR_RateFavoID[wIndex]['text']) + '\n'
			wStr = wStr + "ツイ日=" + str(wARR_RateFavoID[wIndex]['created_at'])
			wStr = wStr + "  ユーザ=" + str(wARR_RateFavoID[wIndex]['screen_name']) + "(@" + str(wARR_RateFavoID[wIndex]['user_name']) + ")" + '\n'
			wStr = wStr + "登録日=" + str(wARR_RateFavoID[wIndex]['regdate'])
			wStr = wStr + " [☆いいね解除済み]"
			wStr = wStr + '\n'
			wStr = wStr + "--------------------" + '\n'
			CLS_OSIF.sPrn( wStr )
			
			self.OBJ_Parent.STR_Cope['FavoRemove'] += 1
			
			###  limited をOFF、removed をONにする
			wQuery = "update tbl_favo_data set " + \
						"limited = False, " + \
						"removed = True " + \
						"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
						" and id = '" + wID + "' ;"
			
			wResDB = gVal.OBJ_DB.RunQuery( wQuery )
			wResDB = gVal.OBJ_DB.GetQueryStat()
			if wResDB['Result']!=True :
				##失敗
				wRes['Reason'] = "Run Query is failed(2): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			
			###  カウント
			self.OBJ_Parent.STR_Cope['DB_Update'] += 1
			
			wFavoLimNum += 1
			wVAL_ZanNum -= 1
			#############################
			# 1回の解除数チェック
			if gVal.DEF_STR_TLNUM['rFavoLimNum']<=wFavoLimNum :
				###解除数限界ならウェイトする
				CLS_OSIF.sPrn( "Twitter規制回避のため、待機します。" )
				CLS_OSIF.sPrn( "CTRL+Cで中止することもできます。残り処理数= " + str(wVAL_ZanNum) + " 個" )
				
				wResStop = self.__wait_FavoRemove( gVal.DEF_STR_TLNUM['favoLimWait'] )
				if wResStop==False :
					CLS_OSIF.sPrn( "処理を中止しました。" + '\n' )
					break	#ウェイト中止
				wFavoLimNum = 0
		
		#############################
		# 統計
		wStr = "--------------------" + '\n'
		wStr = wStr + "DB更新数          = " + str(self.OBJ_Parent.STR_Cope['DB_Update']) + '\n'
		wStr = wStr + "解除対象 いいね数 = " + str(self.OBJ_Parent.STR_Cope['tFavoRemove']) + '\n'
		wStr = wStr + "解除済み いいね数 = " + str(self.OBJ_Parent.STR_Cope['FavoRemove']) + '\n'
		
		#############################
		# コンソールに表示
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes

	#####################################################
	def __wait_FavoRemove( self, inCount ):
		wCount = inCount
		try:
			while True:
				if wCount==0 :
					break
				
				#############################
				# 1行にカウントを表示
				# ctrl+cでウェイト中止
				wStr = "残り待機時間 " + str(self.VAL_WaitCount) + " 秒"
				CLS_OSIF.sPrnER( wStr )
				CLS_OSIF.sSleep(1)
				wCount -= 1
		
		except KeyboardInterrupt:
			return False 	#ウェイト中止
		
		return True			#ウェイト完了



