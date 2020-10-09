#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : Twitter監視 いいね監視系
# 
# ::Update= 2020/10/9
#####################################################
# Private Function:
#   __checkTwitterPatt( self, inROW ):
#   __getTwitterPatt(self):
#
# Instance Function:
#   __init__(self):
#   GetCope(self):
#   GetNewFollower(self):
#   Run(self):

#   __get_FavoInfo(self):
#   ViewFavo(self):

#   Get_RunFavoAdmin(self):
#   Get_Run_FollowerAdmin(self):
#
# Class Function(static):
#   (none)
#
#####################################################

from osif import CLS_OSIF
from gval import gVal
#####################################################
class CLS_TwitterFavo():
#####################################################
	OBJ_Parent = ""				#親クラス実体

#####################################################
# Init
#####################################################
	def __init__( self, parentObj=None ):
		if parentObj==None :
			###親クラス実体の未設定
			gVal.OBJ_L.Log( "A", "CLS_TwitterFavo", "__init__", "You have not set the parent class entity for parentObj" )
			return
		
		self.OBJ_Parent = parentObj
		return



#####################################################
# いいね情報の取得
#####################################################
	def Get(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# DBのいいね一覧取得
		wQuery = "select * from tbl_favo_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_TwitterMain: __get_FavoInfo: Run Query is failed(1): " + wDBRes['Reason'] + " query=" + wDBRes['Query']
			return wRes
		
		#############################
		# 辞書型に整形
		wARR_RateFavoID = {}
		gVal.OBJ_DB.ChgDict( wDBRes['Responce']['Collum'], wDBRes['Responce']['Data'], outDict=wARR_RateFavoID )
		self.OBJ_Parent.STR_Cope['DB_Num'] += len(wARR_RateFavoID)
		
		#############################
		# 取得
		wTwitterRes = gVal.OBJ_Twitter.GetFavolist()
		if wTwitterRes['Result']!=True :
			wRes['Reason'] = "CLS_TwitterMain: __get_FavoInfo: Twitter API Error: " + wTwitterRes['Reason']
			return wRes
		self.OBJ_Parent.STR_Cope['FavoNum'] = len(wTwitterRes['Responce'])
		
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "CLS_TwitterMain: __get_FavoInfo: PC時間の取得に失敗しました"
			return
		### wTD['TimeDate']
		
		#############################
		# Twitterのいいね一覧を取得
		#   DBに記録されていなければ、記録する
		#   DBに記録されている かつ期間外なら limited をONにする
		wARR_FavoID = []
		for wROW in wTwitterRes['Responce'] :
			wARR_FavoID.append( str(wROW['id']) )	#Favo IDだけ記録
			
			wTime = CLS_OSIF.sGetTimeformat_Twitter( wROW['created_at'] )
			if wTime['Result']!=True :
				wRes['Reason'] = "CLS_TwitterMain: __get_FavoInfo: sGetTimeformat_Twitter is failed: " + str(wROW['created_at'])
				return wRes
			
			###記録を探す
			wFLG_Ditect = False
			wKeylist = wARR_RateFavoID.keys()
			for wIndex in wKeylist :
				if str(wARR_RateFavoID[wIndex]['id'])==str(wROW['id']) :
					wFLG_Ditect = True	#DB記録あり
					break
			
			if wFLG_Ditect==True :
				###DBに記録されている
				
				###  既にリムーブor期間外ならばスキップ
				if wARR_RateFavoID[wIndex]['removed']==True or \
				   wARR_RateFavoID[wIndex]['limited']==True :
					continue
				
				###  いいね期間外かを求める (変換＆差)
				wFavoLimmin = gVal.DEF_STR_TLNUM['favoLimmin'] * 60	#秒に変換
				wGetLag = CLS_OSIF.sTimeLag( str(wARR_RateFavoID[wIndex]['regdate']), inThreshold=wFavoLimmin )
				if wGetLag['Result']!=True :
					wRes['Reason'] = "CLS_TwitterMain: __get_FavoInfo: sTimeLag failed"
					return wRes
				if wGetLag['Beyond']==True :
					###いいね期間外
					###  limited をONにする
					wQuery = "update tbl_favo_data set " + \
								"limited = True " + \
								"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
								" and id = '" + str(wROW['id']) + "' ;"
					
					wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
					wDBRes = gVal.OBJ_DB.GetQueryStat()
					if wDBRes['Result']!=True :
						##失敗
						wRes['Reason'] = "CLS_TwitterMain: __get_FavoInfo: Run Query is failed(2): " + wDBRes['Reason']
						return wRes
					
					###  カウント
					self.OBJ_Parent.STR_Cope['DB_Update'] += 1
			
			else:
				###DBに記録されていない
				###  記録する
				wText = str(wROW['text'])
				wText = wText.replace( "'", "''" )
				
				wQuery = "insert into tbl_favo_data values (" + \
							"'" + gVal.STR_UserInfo['Account'] + "'," + \
							"'" + str(wTD['TimeDate']) + "'," + \
							"False," + \
							"False," + \
							"'" + str(wROW['id']) + "'," + \
							"'" + str(wROW['user']['name']) + "'," + \
							"'" + str(wROW['user']['screen_name']) + "'," + \
							"'" + wText + "'," + \
							"'" + str(wTime['TimeDate']) + "'" + \
							") ;"
				
				wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
				wDBRes = gVal.OBJ_DB.GetQueryStat()
				if wDBRes['Result']!=True :
					##失敗
					wRes['Reason'] = "CLS_TwitterMain: __get_FavoInfo: Run Query is failed(3): " + wDBRes['Reason']
					return wRes
				
				self.OBJ_Parent.STR_Cope['DB_Insert'] += 1
		
		#############################
		# DBに記録があるのに、Twitterのいいね一覧にない情報
		#   リムーブ済みでなければ、リムーブ済みにする
		# 保存期間を過ぎた情報
		#   DBから削除する
		wKeylist = wARR_RateFavoID.keys()
		for wIndex in wKeylist :
			### DBに記録があるのに、Twitterのいいね一覧にない
			###   リムーブ済みにする
			if wARR_RateFavoID[wIndex]['id'] not in wARR_FavoID :
				###まだリムーブ済みではない
				if wARR_RateFavoID[wIndex]['removed']==False :
					wQuery = "update tbl_favo_data set " + \
								"removed = True " + \
								"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
								" and id = '" + str(wARR_RateFavoID[wIndex]['id']) + "' ;"
					
					wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
					wDBRes = gVal.OBJ_DB.GetQueryStat()
					if wDBRes['Result']!=True :
						##失敗
						wRes['Reason'] = "CLS_TwitterMain: __get_FavoInfo: Run Query is failed(4): " + wDBRes['Reason']
						return wRes
					
					self.OBJ_Parent.STR_Cope['FavoRemove'] += 1
					self.OBJ_Parent.STR_Cope['DB_Update'] += 1
				
				continue
			
			### Twitterのいいね一覧にある
			else:
				###リムーブ済み
				if wARR_RateFavoID[wIndex]['removed']==True :
					self.OBJ_Parent.STR_Cope['FavoRemove'] += 1
				###期間外
				elif wARR_RateFavoID[wIndex]['limited']==True :
					self.OBJ_Parent.STR_Cope['tFavoRemove'] += 1
			
			###保存期間外かを求める (変換＆差)
			wFavoLimmin = gVal.DEF_STR_TLNUM['favoDBLimmin'] * 60	#秒に変換
			wGetLag = CLS_OSIF.sTimeLag( str(wARR_RateFavoID[wIndex]['regdate']), inThreshold=wFavoLimmin )
			if wGetLag['Result']!=True :
				wRes['Reason'] = "CLS_TwitterMain: __get_FavoInfo: sTimeLag failed(2)"
				return wRes
			if wGetLag['Beyond']==True :
				###期間外
				###  削除する
				wQuery = "delete from tbl_favo_data " + \
							"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
							" and id = '" + str(wARR_RateFavoID[wIndex]['id']) + "' ;"
				
				wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
				wDBRes = gVal.OBJ_DB.GetQueryStat()
				if wDBRes['Result']!=True :
					##失敗
					wRes['Reason'] = "CLS_TwitterMain: __get_FavoInfo: Run Query is failed(5): " + wDBRes['Reason']
					return wRes
				
				self.OBJ_Parent.STR_Cope['DB_Delete'] += 1
		
		#############################
		# 正常終了
		wRes['Result'] = True
		return wRes



#####################################################
# いいね情報の表示
#####################################################
	def View(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
		#############################
		# 集計のリセット
		self.OBJ_Parent.STR_Cope['FavoNum'] = 0
		self.OBJ_Parent.STR_Cope['tFavoRemove'] = 0
		self.OBJ_Parent.STR_Cope['FavoRemove']  = 0
		
		self.OBJ_Parent.STR_Cope['DB_Num']    = 0
		
		#############################
		# DBのいいね一覧取得
		wQuery = "select * from tbl_favo_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					";"
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_TwitterMain: ViewFavo: Run Query is failed(1): " + wDBRes['Reason'] + " query=" + wDBRes['Query']
			return wRes
		
		#############################
		# 辞書型に整形
		wARR_RateFavoID = {}
		gVal.OBJ_DB.ChgDict( wDBRes['Responce']['Collum'], wDBRes['Responce']['Data'], outDict=wARR_RateFavoID )
		self.OBJ_Parent.STR_Cope['DB_Num'] = len(wARR_RateFavoID)
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " 保持中のいいね情報" + '\n'
		wStr = wStr + "--------------------" + '\n'
		
		#############################
		# 情報組み立て
		wKeylist = wARR_RateFavoID.keys()
		for wIndex in wKeylist :
			if wARR_RateFavoID[wIndex]['twitterid']!=gVal.STR_UserInfo['Account'] :
				continue	#自分以外の情報はスキップ
			
			wStr = wStr + str(wARR_RateFavoID[wIndex]['text']) + '\n'
			wStr = wStr + "ツイ日=" + str(wARR_RateFavoID[wIndex]['created_at'])
			wStr = wStr + "  ユーザ=" + str(wARR_RateFavoID[wIndex]['screen_name']) + "(@" + str(wARR_RateFavoID[wIndex]['user_name']) + ")" + '\n'
			wStr = wStr + "登録日=" + str(wARR_RateFavoID[wIndex]['regdate'])
			if wARR_RateFavoID[wIndex]['removed']==True :
				wStr = wStr + " [☆いいね解除済み]"
				self.OBJ_Parent.STR_Cope['FavoRemove'] += 1
			elif wARR_RateFavoID[wIndex]['limited']==True :
				wStr = wStr + " [★いいね解除対象]"
				self.OBJ_Parent.STR_Cope['tFavoRemove'] += 1
			wStr = wStr + '\n'
			wStr = wStr + "--------------------" + '\n'
		
		#############################
		# 統計
		wStr = wStr + "--------------------" + '\n'
###		wStr = wStr + "現いいね数        = " + str(self.OBJ_Parent.STR_Cope['FavoNum']) + '\n'
		wStr = wStr + "DB登録数          = " + str(self.OBJ_Parent.STR_Cope['DB_Num']) + '\n'
		wStr = wStr + "解除対象 いいね数 = " + str(self.OBJ_Parent.STR_Cope['tFavoRemove']) + '\n'
		wStr = wStr + "解除済み いいね数 = " + str(self.OBJ_Parent.STR_Cope['FavoRemove']) + '\n'
###		wStr = wStr + '\n'
###		wStr = wStr + "DB登録数 = " + str(self.OBJ_Parent.STR_Cope['DB_Num']) + '\n'
		
		#############################
		# コンソールに表示
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 完了
		wRes['Result'] = True
		return wRes



#####################################################
# いいね監視の実行
#####################################################
	def Run(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		
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
		
		wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
		wDBRes = gVal.OBJ_DB.GetQueryStat()
		if wDBRes['Result']!=True :
			##失敗
			wRes['Reason'] = "CLS_TwitterMain: Run_FavoRemove: Run Query is failed(1): " + wDBRes['Reason'] + " query=" + wDBRes['Query']
			return wRes
		
		#############################
		# 辞書型に整形
		wARR_RateFavoID = {}
		gVal.OBJ_DB.ChgDict( wDBRes['Responce']['Collum'], wDBRes['Responce']['Data'], outDict=wARR_RateFavoID )
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
				wRes['Reason'] = "CLS_TwitterMain: Run_FavoRemove: Twitter API Error: " + wRemoveRes['Reason']
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
			
			wDBRes = gVal.OBJ_DB.RunQuery( wQuery )
			wDBRes = gVal.OBJ_DB.GetQueryStat()
			if wDBRes['Result']!=True :
				##失敗
				wRes['Reason'] = "CLS_TwitterMain: Run_FavoRemove: Run Query is failed(2): " + wDBRes['Reason']
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



