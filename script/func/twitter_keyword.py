#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : Twitter監視 キーワード抽出
# 
# ::Update= 2020/11/1
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
from htmlif import CLS_HTMLIF
from filectrl import CLS_File
from mydisp import CLS_MyDisp
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
		self.OBJ_Parent.STR_KeyUser = {}
		#############################
		# 取得
		wRange = len( gVal.STR_SearchMode )
		for wIndex in range( wRange ) :
			#############################
			# 選択中でない、もしくは手動モードのキー は除外
			if gVal.STR_SearchMode[wIndex]['Choice']==False or \
			   gVal.STR_SearchMode[wIndex]['id']==0 :
				continue
			
			#############################
			# コマンド付加
			wResCmd = self.IncSearchMode( wIndex, gVal.STR_SearchMode[wIndex]['Keyword'] )
			if wResCmd['Result']!=True :
				###やらかし
				wResCmd['Reason'] = "IncSearchModeのやらかし: reason=" + wResCmd['Reason']
				gVal.OBJ_L.Log( "A", wResCmd )
				CLS_OSIF.sPrn( "プログラムミスのためこの用語はスキップされます 検索語=" + gVal.STR_SearchMode[wIndex]['Keyword'] )
				continue
			wCommand = wResCmd['Responce']
			
			CLS_OSIF.sPrn( "取得中... 検索語=" + wCommand )
			
			wTwitterRes = gVal.OBJ_Twitter.GetSearch( inKeyword=wCommand, inRoundNum=gVal.DEF_STR_TLNUM['searchRoundNum'] )
			if wTwitterRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error: " + wTwitterRes['Reason']
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			self.OBJ_Parent.STR_Cope['TimelineNum'] += len(wTwitterRes['Responce'])
			
			#############################
			# 必要な情報だけ抜き出す
			for wLine in wTwitterRes['Responce'] :
				###検索にリツイートを含めない場合、
				###  リツイートはスキップする
				if gVal.STR_SearchMode[wIndex]['ExcRT']==True :
					if "retweeted_status" in wLine :
						continue
				
				###日時の変換
				wTime = CLS_OSIF.sGetTimeformat_Twitter( wLine['created_at'] )
				if wTime['Result']!=True :
					wRes['Reason'] = "sGetTimeformat_Twitter is failed(1): " + str(wLine['created_at'])
					gVal.OBJ_L.Log( "B", wRes )
					continue
				wLine['created_at'] = wTime['TimeDate']
				
				###荒らしチェック
				if gVal.STR_SearchMode[wIndex]['Arashi']==True :
					if self.OBJ_Parent.CheckTrolls( wLine )==False :
						continue
				
				###検索からセンシティブを除外する場合、
				###  センシティブツイートはスキップする
				if gVal.STR_SearchMode[wIndex]['ExcSensi']==True :
					if "possibly_sensitive" in wLine :
						if wLine['possibly_sensitive']==True :
							continue
				###ユーザ名に除外文字が含まれている
				if self.OBJ_Parent.CheckExcUserName( wLine['user']['name'] )==False :
					continue
				###ツイートに除外文字が含まれている
				if self.OBJ_Parent.CheckExcWord( wLine['text'] )==False :
					continue
				###端末名に除外文字が含まれている
				wCHR_Term = CLS_OSIF.sDel_HTML( str(wLine['source']) )
				if self.OBJ_Parent.CheckExcWord( wCHR_Term )==False :
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
				
				self.__set_KeyUser( wLine, gVal.STR_SearchMode[wIndex]['Keyword'] )
				gVal.STR_SearchMode[wIndex]['Count'] += 1
				
				###リツイート元
				if "retweeted_status" in wLine :
					###検索からセンシティブを除外する場合、
					###  センシティブツイートはスキップする
					if gVal.STR_SearchMode[wIndex]['ExcSensi']==True :
						if "possibly_sensitive" in wLine['retweeted_status'] :
							if wLine['retweeted_status']['possibly_sensitive']==True :
								continue
					###ユーザ名に除外文字が含まれている
					if self.OBJ_Parent.CheckExcUserName( wLine['retweeted_status']['user']['name'] )==False :
						continue
					###ツイートに除外文字が含まれている
					if self.OBJ_Parent.CheckExcWord( wLine['retweeted_status']['text'] )==False :
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
					
					self.__set_KeyUser( wLine['retweeted_status'], gVal.STR_SearchMode[wIndex]['Keyword'] )
					gVal.STR_SearchMode[wIndex]['Count'] += 1
		
		#############################
		# キーユーザ数
		self.OBJ_Parent.STR_Cope['KeyUserNum'] += len( self.OBJ_Parent.STR_KeyUser )
		
		self.OBJ_Parent.STR_Cope['ArashiNum'] = len( self.OBJ_Parent.ARR_newExcUser )
		wArashiOnNum = 0
		wKeylist = list( self.OBJ_Parent.ARR_newExcUser )
		for wIndex in wKeylist :
			if self.OBJ_Parent.ARR_newExcUser[wIndex]['count']>=gVal.DEF_STR_TLNUM['excTwitterID'] :
				wArashiOnNum += 1
		self.OBJ_Parent.STR_Cope['ArashiOnNum'] = wArashiOnNum
		
		#############################
		# 正常終了
		wRes['Result'] = True
		return wRes

	#####################################################
	def __set_KeyUser( self, inLine, inWord ):
		###既に同じユーザを抽出した
		if str(inLine['user']['id']) in self.OBJ_Parent.STR_KeyUser :
			return False
		
		wSTR_Cell = {}
		###セット
		wSTR_Cell.update({ "id"          : str(inLine['user']['id']) })
###		wSTR_Cell.update({ "id"          : inLine['user']['id'] })
		wSTR_Cell.update({ "user_name"   : str(inLine['user']['name']) })
		wSTR_Cell.update({ "screen_name" : str(inLine['user']['screen_name']) })
		wSTR_Cell.update({ "hit_word"    : inWord })
		wSTR_Cell.update({ "text_id"     : inLine['id'] })
		wSTR_Cell.update({ "text"        : inLine['text'] })
		wSTR_Cell.update({ "statuses_count" : str(inLine['user']['statuses_count']) })
		wSTR_Cell.update({ "protected"   : inLine['user']['protected'] })
		
		self.OBJ_Parent.STR_KeyUser.update({ str(inLine['user']['id']) : wSTR_Cell })
		return True



#####################################################
# キーユーザ変更
#####################################################
	def SetKeyuser(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterKeyword"
		wRes['Func']  = "SetKeyuser"
		
		#############################
		# コンソールを表示
		while True :
			wWord = self.__view_Keyuser( wRes )
			
			if wWord=="\\q" :
				###終了
				break
			if wWord=="" :
				###未入力は再度入力
				continue
			
			self.__run_Keyuser( wWord, wRes )
			if wRes['Result']!=True :
				break	#異常
			CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
		
		return wRes

	#####################################################
	# キーユーザ 画面表示
	#####################################################
	def __view_Keyuser( self, outRes ):
		pRes = outRes
		
		wResDisp = CLS_MyDisp.sViewDisp( "KeyuserConsole" )
		if wResDisp['Result']==False :
			pRes['Reason'] = "__view_Keyuser is failed: " + CLS_OSIF.sCatErr( wResDisp )
			return "\\q"	#失敗=強制終了
		
		wWord = CLS_OSIF.sInp( "コマンド？=> " )
		return wWord

	#####################################################
	# キーユーザ 実行
	#####################################################
	def __run_Keyuser( self, inWord, outRes ):
		pRes = outRes
		
###		### ※最初はコマンドチェックなので全正常で返す
###		pRes['Result'] = True
		#############################
		# コマンドの分析
		if inWord.find("\\")!=0 :
			###先頭が \\ 以外はコマンドではない
			CLS_OSIF.sPrn( "コマンドが誤ってます！" )
			pRes['Result'] = True
			return
		
		wCommand = inWord.split(":")	#分解
		wID  = 0
		wLen = len(wCommand)
		wFLG_Valid = False
		if wLen==1 :
			### \n
			wCommand = wCommand[0]
###			if wCommand=="\\n" :
			if wCommand=="\\n" or wCommand=="\\ax" or wCommand=="\\ar" :
				wFLG_Valid = True
		
		elif wLen==2 :
			### \s \x \c \d
			wID      = int( wCommand[1] )
			wCommand = wCommand[0]
			if wCommand=="\\s" or wCommand=="\\x" or \
			   wCommand=="\\c" or wCommand=="\\d" :
				wFLG_Valid = True
		
		if wFLG_Valid==False :
			CLS_OSIF.sPrn( "コマンドが誤ってます！" )
			pRes['Result'] = True
			return
		
		wRange = len( gVal.STR_SearchMode )
		#############################
		# 新規の場合：IDを発行する
		#   IDの被りがなくなるまでループを回し続ける
		if wCommand=="\\n" :
			wID = 1
			while True :
				wFLG_Detect = False
				for wIndex in range( wRange ) :
					if gVal.STR_SearchMode[wIndex]['id']==wID :
						wID += 1
						wFLG_Detect = True
						break
				if wFLG_Detect==False :
					break
			
			###キーユーザ 行を割り当てる
			gVal.sStruct_SearchMode()
			wIndex = len( gVal.STR_SearchMode ) - 1
			gVal.STR_SearchMode[wIndex]['id'] = wID
###			gVal.STR_SearchMode[wIndex]['Update'] = True
		
		#############################
		# 全未選択
		elif wCommand=="\\ax" :
###			self.__set_Keyuser( -1, True, False, pRes )
			self.__select_Keyuser( -1, True, False, pRes )
		
		#############################
		# \\ar：カウンタリセット
		elif wCommand=="\\ar" :
			self.__reset_Keyuser( pRes )
		
		#############################
		# 既存の場合：IDのインデックスを探す
		else:
			if wID==0 :
				CLS_OSIF.sPrn( "範囲外のIDです。 ID=1以上" )
				pRes['Result'] = True
				return
			
			wFLG_Detect = False
			for wIndex in range( wRange ) :
				if gVal.STR_SearchMode[wIndex]['id']==wID :
					wFLG_Detect = True
					break
			
			if wFLG_Detect!=True :
				CLS_OSIF.sPrn( "そのIDは存在しません。" )
				pRes['Result'] = True
				return
		
##		### ※ここから処理結果としてセットさせる
##		pRes['Result'] = False
		#############################
		# \\n：新規キー追加
		if wCommand=="\\n" :
			self.__view_SetKeyuser( wIndex, pRes )
		
		#############################
		# \\c：キー変更
		elif wCommand=="\\c" :
			self.__view_SetKeyuser( wIndex, pRes )
		
		#############################
		# \\d：キー削除
		elif wCommand=="\\d" :
			self.__del_Keyuser( wIndex, pRes )
		
		#############################
		# \\s：キー選択
		elif wCommand=="\\s" :
###			self.__set_Keyuser( wIndex, False, True, pRes )
			self.__select_Keyuser( wIndex, False, True, pRes )
		
		#############################
		# \\x：キー未選択
		elif wCommand=="\\x" :
###			self.__set_Keyuser( wIndex, False, False, pRes )
			self.__select_Keyuser( wIndex, False, False, pRes )
		
##		#############################
##		# \\ax：全キー未選択
##		elif wCommand=="\\ax" :
##			self.__set_Keyuser( wIndex, True, False, pRes )
##		
##		#############################
##		# \\ar：カウンタリセット
##		elif wCommand=="\\ar" :
##			self.__reset_Keyuser( pRes )
##		
###		#############################
###		# 正常
###		pRes['Result'] = True
		return

	#####################################################
	# 設定画面 新規キー or キー変更 入力
	#####################################################
	def __view_SetKeyuser( self, inIndex, outRes ):
		pRes = outRes
		
		#############################
		# コンソールを表示
		while True :
##			wWord = self.__view_TweetSearch()
			wWord = self.__view_SetKeyuserDisp( inIndex, outRes )
			
			if wWord=="\\q" :
				###終了
				
				###データが更新され、かつ選択数が上限に達してなければ
				###  選択するか確認する
				if gVal.STR_SearchMode[inIndex]['Update']==True and \
				   gVal.STR_SearchMode[inIndex]['Choice']==False :
					wCount = self.__get_KeyuserChoice()
					if gVal.DEF_STR_TLNUM['maxKeywordNum']>wCount :
						wSelect = CLS_OSIF.sInp( "このキーユーザを有効にしますか？(y/N)=> " )
						if wSelect=="y" :
							gVal.STR_SearchMode[inIndex]['Choice'] = True
				break
			if wWord=="" :
				###未入力は再度入力
				continue
			
			#############################
			# 入力の解析
			wResCmd = self.ChangeSearchMode( inIndex, wWord )
###			if wResCmd['Result']!=True :
###				### 検索文字？
###				if wWord!="" :
###					gVal.STR_SearchMode[inIndex]['Keyword'] = wWord
###					gVal.STR_SearchMode[inIndex]['Update']  = True
			CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
			if wResCmd['Result']!=True :
				### 処理失敗
				continue
			
			#############################
			# 更新する
			gVal.STR_SearchMode[inIndex]['Update'] = True
			
			#############################
			# 検索文字入力だったら検索文字を保存する
			if wResCmd['Responce']==False :
				gVal.STR_SearchMode[inIndex]['Keyword'] = wWord
		
		#############################
		# 正常
		pRes['Result'] = True
		return

	#####################################################
	# 設定画面 (ツイート検索画面の上のほう)
	#####################################################
	def __view_SetKeyuserDisp( self, inIndex, outRes ):
		pRes = outRes
		
		wResDisp = CLS_MyDisp.sViewDisp( "SearchConsole", inIndex )
		if wResDisp['Result']==False :
			pRes['Reason'] = "__view_SetKeyuserDisp is failed: " + CLS_OSIF.sCatErr( wResDisp )
			return "\\q"	#失敗=強制終了
		
		wWord = CLS_OSIF.sInp( "検索文字？=> " )
		return wWord

	#####################################################
	# キー削除
	#####################################################
	def __del_Keyuser( self, inIndex, outRes ):
		pRes = outRes
		
		#############################
		# 実行の確認
		wID = str(gVal.STR_SearchMode[inIndex]['id'])
###		wStr = "ID " + str(gVal.STR_SearchMode[inIndex]['id']) + " のキーユーザを削除します。" + '\n'
		wStr = "ID=" + wID + " このキーユーザを削除します。" + '\n'
		CLS_OSIF.sPrn( wStr )
		wSelect = CLS_OSIF.sInp( "よろしいですか？(y/N)=> " )
		if wSelect!="y" :
			##キャンセル  処理は正常扱い
			pRes['Result'] = True
			return
		
		#############################
		# 削除
		wQuery = "delete from tbl_keyword_data " + \
					"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
					" and id = '" + str(gVal.STR_SearchMode[inIndex]['id']) + "' ;"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed: RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		
		gVal.STR_SearchMode.pop( inIndex )
		
###		wStr = "ID " + str(gVal.STR_SearchMode[inIndex]['id']) + " のキーユーザを削除しました。" + '\n'
		wStr = "キーユーザを削除しました。 ID=" + wID + '\n'
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 正常
		pRes['Result'] = True
		return

	#####################################################
	# キー選択/未選択
	#####################################################
###	def __set_Keyuser( self, inIndex, inFLG_Alls, in_FLG_Choice, outRes ):
	def __select_Keyuser( self, inIndex, inFLG_Alls, in_FLG_Choice, outRes ):
		pRes = outRes
		
		#############################
		# 選択
		if inFLG_Alls==False and in_FLG_Choice==True :
			if gVal.STR_SearchMode[inIndex]['Choice']==True :
				wStr = "既に選択されています。 ID=" + str(gVal.STR_SearchMode[inIndex]['id']) + '\n'
				CLS_OSIF.sPrn( wStr )
				pRes['Result'] = True	#正常扱い
				return
			
			wCount = self.__get_KeyuserChoice()
			if gVal.DEF_STR_TLNUM['maxKeywordNum']<=wCount :
				###選択の上限
				wStr = "選択数が上限に達してるため設定できません。 ID=" + str(gVal.STR_SearchMode[inIndex]['id']) + '\n'
				CLS_OSIF.sPrn( wStr )
				pRes['Result'] = True	#正常扱い
				return
			
			###選択
			gVal.STR_SearchMode[inIndex]['Choice'] = True
			gVal.STR_SearchMode[inIndex]['Update']  = True
			
			wStr = "キーユーザを選択しました。 ID=" + str(gVal.STR_SearchMode[inIndex]['id']) + '\n'
			CLS_OSIF.sPrn( wStr )
		
		#############################
		# 選択
		elif inFLG_Alls==False and in_FLG_Choice==False :
			if gVal.STR_SearchMode[inIndex]['Choice']==False :
				wStr = "既に未選択です。 ID=" + str(gVal.STR_SearchMode[inIndex]['id']) + '\n'
				CLS_OSIF.sPrn( wStr )
				return
			
			###選択
			gVal.STR_SearchMode[inIndex]['Choice'] = False
			gVal.STR_SearchMode[inIndex]['Update']  = True
			
			wStr = "キーユーザを選択解除しました。 ID=" + str(gVal.STR_SearchMode[inIndex]['id']) + '\n'
			CLS_OSIF.sPrn( wStr )
		
		#############################
		# 全選択
		elif inFLG_Alls==True and in_FLG_Choice==False :
			wRange = len( gVal.STR_SearchMode )
			for wIndex in range( wRange ) :
				if gVal.STR_SearchMode[wIndex]['Choice']==True :
					gVal.STR_SearchMode[wIndex]['Choice'] = False
					gVal.STR_SearchMode[wIndex]['Update']  = True
		
			wStr = "全キーユーザを選択解除しました。" + '\n'
			CLS_OSIF.sPrn( wStr )
		
		#############################
		# 正常
		pRes['Result'] = True
		return

	#####################################################
	# カウンタリセット
	#####################################################
	def __reset_Keyuser( self, outRes ):
		pRes = outRes
		
		wSelect = CLS_OSIF.sInp( "ヒットカウンタをリセットしますか？(y/N)=> " )
		if wSelect!="y" :
			##キャンセル  処理は正常扱い
			pRes['Result'] = True
			return
		
		#############################
		# リセット処理
		wRange = len( gVal.STR_SearchMode )
		for wIndex in range( wRange ) :
			gVal.STR_SearchMode[wIndex]['Count']  = 0
			gVal.STR_SearchMode[wIndex]['Update'] = True
		
		CLS_OSIF.sPrn( "全カウンタをリセットしました" )
		
		#############################
		# 正常
		pRes['Result'] = True
		return

	#####################################################
	# 選択数取得
	#####################################################
	def __get_KeyuserChoice(self):
		wCount = 0
		wRange = len(gVal.STR_SearchMode)
		for wIndex in range(wRange) :
			if gVal.STR_SearchMode[wIndex]['Choice']==True :
				wCount += 1
		return wCount



#####################################################
# 検索コマンド変更
#####################################################
	def ChangeSearchMode( self, inIndex, inWord ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterKeyword"
		wRes['Func']  = "ChangeSearchMode"
		
		#############################
		### wRes['Responce'] = True  =コマンド
		### wRes['Responce'] = False =検索文字
		
		if inWord.find("\\")!=0 :
			###先頭が \\ 以外はコマンドではない
			wRes['Responce'] = False
			wRes['Reason'] = "コマンド以外: " + str(inWord)
			wRes['Result'] = True
			return wRes
		
		###コマンド処理
		wRes['Responce'] = True
		
		wMsg = None
		#############################
		# [\jp] 日本語のみ：いいえ→[はい]
		if inWord=="\\jp" :
			if gVal.STR_SearchMode[inIndex]['JPonly']==True :
				###はい→いいえ
				gVal.STR_SearchMode[inIndex]['JPonly'] = False
				wMsg = "いいえ"
			else:
				###いいえ→はい
				gVal.STR_SearchMode[inIndex]['JPonly'] = True
				wMsg = "はい"
			wMsg = "日本語のみ=" + wMsg
		
		#############################
		# [\i] 検索に画像を含める：含める→除外する→[無条件]
		elif inWord=="\\i" :
			if gVal.STR_SearchMode[inIndex]['IncImage']==True and gVal.STR_SearchMode[inIndex]['ExcImage']==False :
				###含める→除外する
				gVal.STR_SearchMode[inIndex]['IncImage'] = False
				gVal.STR_SearchMode[inIndex]['ExcImage'] = True
				wMsg = "除外する"
			elif gVal.STR_SearchMode[inIndex]['IncImage']==False and gVal.STR_SearchMode[inIndex]['ExcImage']==True :
				###除外する→無条件
				gVal.STR_SearchMode[inIndex]['IncImage'] = False
				gVal.STR_SearchMode[inIndex]['ExcImage'] = False
				wMsg = "無条件"
			elif gVal.STR_SearchMode[inIndex]['IncImage']==False and gVal.STR_SearchMode[inIndex]['ExcImage']==False :
				###無条件→含める
				gVal.STR_SearchMode[inIndex]['IncImage'] = True
				gVal.STR_SearchMode[inIndex]['ExcImage'] = False
				wMsg = "含める"
			else:
				###両方Trueは矛盾
				wRes['Reason'] = "フラグ取り扱い矛盾: 検索に画像を含める Dual flag is True"
				gVal.OBJ_L.Log( "A", wRes )
				return wRes	#正常扱い
			wMsg = "画像を含める=" + wMsg
		
		#############################
		# [\v] 検索に動画を含める：含める→除外する→[無条件]
		elif inWord=="\\v" :
			if gVal.STR_SearchMode[inIndex]['IncVideo']==True and gVal.STR_SearchMode[inIndex]['ExcVideo']==False :
				###含める→除外する
				gVal.STR_SearchMode[inIndex]['IncVideo'] = False
				gVal.STR_SearchMode[inIndex]['ExcVideo'] = True
				wMsg = "除外する"
			elif gVal.STR_SearchMode[inIndex]['IncVideo']==False and gVal.STR_SearchMode[inIndex]['ExcVideo']==True :
				###除外する→無条件
				gVal.STR_SearchMode[inIndex]['IncVideo'] = False
				gVal.STR_SearchMode[inIndex]['ExcVideo'] = False
				wMsg = "無条件"
			elif gVal.STR_SearchMode[inIndex]['IncVideo']==False and gVal.STR_SearchMode[inIndex]['ExcVideo']==False :
				###無条件→含める
				gVal.STR_SearchMode[inIndex]['IncVideo'] = True
				gVal.STR_SearchMode[inIndex]['ExcVideo'] = False
				wMsg = "含める"
			else:
				###両方Trueは矛盾
				wRes['Reason'] = "フラグ取り扱い矛盾: 検索に動画を含める Dual flag is True"
				gVal.OBJ_L.Log( "A", wRes )
				return wRes	#正常扱い
			wMsg = "動画を含める=" + wMsg
		
		#############################
		# [\l] 検索にリンクを含める：含める→除外する→[無条件]
		elif inWord=="\\l" :
			if gVal.STR_SearchMode[inIndex]['IncLink']==True and gVal.STR_SearchMode[inIndex]['ExcLink']==False :
				###含める→除外する
				gVal.STR_SearchMode[inIndex]['IncLink'] = False
				gVal.STR_SearchMode[inIndex]['ExcLink'] = True
				wMsg = "除外する"
			elif gVal.STR_SearchMode[inIndex]['IncLink']==False and gVal.STR_SearchMode[inIndex]['ExcLink']==True :
				###除外する→無条件
				gVal.STR_SearchMode[inIndex]['IncLink'] = False
				gVal.STR_SearchMode[inIndex]['ExcLink'] = False
				wMsg = "無条件"
			elif gVal.STR_SearchMode[inIndex]['IncLink']==False and gVal.STR_SearchMode[inIndex]['ExcLink']==False :
				###無条件→含める
				gVal.STR_SearchMode[inIndex]['IncLink'] = True
				gVal.STR_SearchMode[inIndex]['ExcLink'] = False
				wMsg = "含める"
			else:
				###両方Trueは矛盾
				wRes['Reason'] = "フラグ取り扱い矛盾: 検索にリンクを含める Dual flag is True"
				gVal.OBJ_L.Log( "A", wRes )
				return wRes	#正常扱い
			wMsg = "リンクを含める=" + wMsg
		
		#############################
		# [\o] 公式マークのみ：いいえ→はい
		elif inWord=="\\o" :
			if gVal.STR_SearchMode[inIndex]['OFonly']==True :
				###はい→いいえ
				gVal.STR_SearchMode[inIndex]['OFonly'] = False
				wMsg = "いいえ"
			else:
				###いいえ→はい
				gVal.STR_SearchMode[inIndex]['OFonly'] = True
				wMsg = "はい"
			wMsg = "公式マークのみ=" + wMsg
		
		#############################
		# [\rt] リツイートを含めない：いいえ→[はい]
		elif inWord=="\\rt" :
			if gVal.STR_SearchMode[inIndex]['ExcRT']==True :
				###はい→いいえ
				gVal.STR_SearchMode[inIndex]['ExcRT'] = False
				wMsg = "いいえ"
			else:
				###いいえ→はい
				gVal.STR_SearchMode[inIndex]['ExcRT'] = True
				wMsg = "はい"
			wMsg = "リツイートを含めない=" + wMsg
		
		#############################
		# [\sn] センシティブを除外する：いいえ→[はい]
		elif inWord=="\\sn" :
			if gVal.STR_SearchMode[inIndex]['ExcSensi']==True :
				###はい→いいえ
				gVal.STR_SearchMode[inIndex]['ExcSensi'] = False
				wMsg = "いいえ"
			else:
				###いいえ→はい
				gVal.STR_SearchMode[inIndex]['ExcSensi'] = True
				wMsg = "はい"
			wMsg = "センシティブを除外する=" + wMsg
		
		#############################
		# [\tr] 荒らしを除外する：[いいえ]→はい
		elif inWord=="\\tr" :
			if gVal.STR_SearchMode[inIndex]['Arashi']==True :
				###はい→いいえ
				gVal.STR_SearchMode[inIndex]['Arashi'] = False
				wMsg = "いいえ"
			else:
				###いいえ→はい
				gVal.STR_SearchMode[inIndex]['Arashi'] = True
				wMsg = "はい"
			wMsg = "荒らしを除外する=" + wMsg
		
		#############################
		# [\rs] 再検索(手動検索時のみ)
		elif inWord=="\\rs" and inIndex==0 :
			wRes['Responce'] = False	#コマンドではなくする
			wRes['Result'] = True
			return wRes
		
		else:
			###ないコマンド
			CLS_OSIF.sPrn( "そのコマンドはありません: " + inWord + '\n' )
			return wRes
		
		#############################
		if wMsg==None :
			###やらかしてる
			wRes['Reason'] = "メッセージ抜け: wMsg=None"
			gVal.OBJ_L.Log( "A", wRes )
			return wRes
		
		#############################
		# 正常
		CLS_OSIF.sPrn( "検索モードを変更しました: " + wMsg + '\n' )
		wRes['Result'] = True
		return wRes



#####################################################
# 検索コマンド追加
#####################################################
	def IncSearchMode( self, inIndex, inCommand ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterKeyword"
		wRes['Func']  = "IncSearchMode"
		
		wCommand = inCommand + ""
		#############################
		# [\j] 日本語のみ
		if gVal.STR_SearchMode[inIndex]['JPonly']==True :
			###はい
			wCommand = wCommand + " lang:ja"
		
		#############################
		# [\i] 検索に画像を含める
		if gVal.STR_SearchMode[inIndex]['IncImage']==True and gVal.STR_SearchMode[inIndex]['ExcImage']==False :
			###含める
			wCommand = wCommand + " filter:images"
		elif gVal.STR_SearchMode[inIndex]['IncImage']==False and gVal.STR_SearchMode[inIndex]['ExcImage']==True :
			###除外する
			wCommand = wCommand + " -filter:images"
		elif gVal.STR_SearchMode[inIndex]['IncImage']==True and gVal.STR_SearchMode[inIndex]['ExcImage']==True :
			###両方Trueは矛盾
			wRes['Reason'] = "フラグ取り扱い矛盾: 検索に画像を含める Dual flag is True"
			return wRes
		
		#############################
		# [\v] 検索に動画を含める
		if gVal.STR_SearchMode[inIndex]['IncVideo']==True and gVal.STR_SearchMode[inIndex]['ExcVideo']==False :
			###含める
			wCommand = wCommand + " filter:videos"
		elif gVal.STR_SearchMode[inIndex]['IncVideo']==False and gVal.STR_SearchMode[inIndex]['ExcVideo']==True :
			###除外する
			wCommand = wCommand + " -filter:videos"
		elif gVal.STR_SearchMode[inIndex]['IncVideo']==True and gVal.STR_SearchMode[inIndex]['ExcVideo']==True :
			###両方Trueは矛盾
			wRes['Reason'] = "フラグ取り扱い矛盾: 検索に動画を含める Dual flag is True"
			return wRes
		
		#############################
		# [\l] 検索にリンクを含める
		if gVal.STR_SearchMode[inIndex]['IncLink']==True and gVal.STR_SearchMode[inIndex]['ExcLink']==False :
			###含める
			wCommand = wCommand + " filter:links"
		elif gVal.STR_SearchMode[inIndex]['IncLink']==False and gVal.STR_SearchMode[inIndex]['ExcLink']==True :
			###除外する
			wCommand = wCommand + " -filter:links"
		elif gVal.STR_SearchMode[inIndex]['IncLink']==True and gVal.STR_SearchMode[inIndex]['ExcLink']==True :
			###両方Trueは矛盾
			wRes['Reason'] = "フラグ取り扱い矛盾: 検索にリンクを含める Dual flag is True"
			return wRes
		
		#############################
		# [\o] 公式マークのみ
		if gVal.STR_SearchMode[inIndex]['OFonly']==True :
			###はい
			wCommand = wCommand + " filter:verified"
		
		#############################
		# 正常
		wRes['Responce'] = wCommand
		wRes['Result']   = True
		return wRes



#####################################################
# キーユーザフォロー(手動)
#####################################################
	def KeyUserFollow(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterKeyword"
		wRes['Func']  = "KeyUserFollow"
		
		wKeyUserNum = len(self.OBJ_Parent.STR_KeyUser)
		if wKeyUserNum==0 :
			CLS_OSIF.sPrn( "まず監視情報取得を実行してください。" + '\n' )
			return wRes
		
		#############################
		# DBのフォロワー一覧取得(一度でもフォローしたことがある)
		wQuery = "select id from tbl_follower_data where " + \
					"twitterid = '" + gVal.STR_UserInfo['Account'] + "' and " + \
					"r_myfollow = True or " + \
					"r_remove = True or " + \
					"rc_follower = True " + \
					";"
		
		wResDB = gVal.OBJ_DB.RunQuery( wQuery )
		wResDB = gVal.OBJ_DB.GetQueryStat()
		if wResDB['Result']!=True :
			##失敗
			wRes['Reason'] = "Run Query is failed(1): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
			return wRes
		
		#############################
		# リスト型に整形
		wARR_Followers = []
		gVal.OBJ_DB.ChgList( wResDB['Responce']['Data'], outList=wARR_Followers )
		
		#############################
		# un_refollowl登録者とマージする
		wListsRes = gVal.OBJ_Twitter.GetListMember( gVal.STR_UserInfo['UrfList'] )
		if wListsRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error(GetListMember:UrfList): " + wListsRes['Reason']
			return wRes
		for wROW in wListsRes['Responce'] :
			if str(wROW['id']) not in wARR_Followers :
				wARR_Followers.append( str(wROW['id']) )
		
		#############################
		# 時間を取得
		wTD = CLS_OSIF.sGetTime()
		if wTD['Result']!=True :
			###時間取得失敗  時計壊れた？
			wRes['Reason'] = "PC時間の取得に失敗しました"
			return wRes
		### wTD['TimeDate']
		
		#############################
		# 画面クリア(=通常モード時)
		if gVal.FLG_Test_Mode==False :
			CLS_OSIF.sDispClr()
		
		#############################
		# ヘッダ表示
		wStr = "--------------------" + '\n'
		wStr = wStr + " キーユーザフォロー(手動)" + '\n'
		wStr = wStr + "--------------------" + '\n'
		wStr = wStr + '\n'
		wStr = wStr + "選出された " + str(wKeyUserNum) + " 人のキーユーザのうち " + str(gVal.DEF_STR_TLNUM['randFollowNum']) +  " 人までフォローできます。"
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# キーユーザからランダムに選出する
		wARR_RandID = []
		wARR_FollowedID = []
		wKeylist = list( self.OBJ_Parent.STR_KeyUser.keys() )
		wKeyNum  = len( wKeylist )
		wCount   = 0
		while True:
			if gVal.DEF_STR_TLNUM['randFollowNum']<=wCount :
				break	#選出数上限
			
			if self.OBJ_Parent.VAL_KeyUser_Index==-1 :
				wRand = CLS_OSIF.sGetRand( wKeyNum )
				wKey  = wKeylist[wRand]
				wID   = self.OBJ_Parent.STR_KeyUser[wKey]['id']
				
				###候補から除外されていたらスキップ
				if wID in gVal.STR_ExcFollowID :
					continue
				
				###一度でもフォローしたことがある or un_followerリスト登録者
				if wID in wARR_Followers :
					wARR_RandID.append( wID )
					continue
				###この機能では鍵垢は除外する仕様とする
				if self.OBJ_Parent.STR_KeyUser[wKey]['protected']==True :
					wARR_RandID.append( wID )
					continue
				
				###既に選出されたIDならスキップする
				if wID in wARR_RandID :
					continue
				
				#※候補あり
				#############################
				# 候補の表示
				wStr = '\n' + "--------------------" + '\n'
				wStr = wStr + "フォロー候補= " + str(self.OBJ_Parent.STR_KeyUser[wKey]['user_name']) + "(@" + str(self.OBJ_Parent.STR_KeyUser[wKey]['screen_name']) + ")" + '\n'
				wStr = wStr + '\n' + str(self.OBJ_Parent.STR_KeyUser[wKey]['text']) + '\n'
				wStr = wStr + '\n' + "対処コマンド：" + '\n'
				wStr = wStr + "    y=フォロー / q=選定中止 / v=ブラウザで表示" + '\n'
				wStr = wStr + "    n=次から候補除外 / Other=拒否"
				CLS_OSIF.sPrn( wStr )
			
			else:
				###キーが保存されている場合
				wKey  = self.OBJ_Parent.VAL_KeyUser_Index
				wID   = self.OBJ_Parent.STR_KeyUser[wKey]['id']
				self.OBJ_Parent.VAL_KeyUser_Index = -1
			
			wStr = "対処コマンドを指定してください=> "
			wSelect = CLS_OSIF.sInp( wStr )
			if wSelect!="y" :
				if wSelect=="q" :
					###選出中止
					CLS_OSIF.sPrn( "選出を終了しました。" + '\n' )
					wRes['Result'] = True
					return wRes
				
				elif wSelect=="v" :
					###ブラウザで表示
					wURL = "https://twitter.com/" + gVal.STR_UserInfo['Account'] + "/status/" + str(self.OBJ_Parent.STR_KeyUser[wKey]['text_id'])
					CLS_HTMLIF.sOpenURL( wURL )
					self.OBJ_Parent.VAL_KeyUser_Index = wKey
					continue
				
				elif wSelect=="n" :
					###次から候補から外す
					wQuery = "insert into tbl_exc_followid values (" + \
								"'" + str(wTD['TimeDate']) + "'," + \
								"" + str( wID ) + " " + \
								") ;"
					
					wResDB = gVal.OBJ_DB.RunQuery( wQuery )
					wResDB = gVal.OBJ_DB.GetQueryStat()
					if wResDB['Result']!=True :
						##失敗
						wRes['Reason'] = "Run Query is failed(3): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
						gVal.OBJ_L.Log( "B", wRes )
						return wRes
					
					gVal.STR_ExcFollowID.append( wID )
					continue
				
				###拒否はスキップ
				wARR_RandID.append( wID )
				continue
			
			#############################
			# 候補をフォローする
			wTwitterRes = gVal.OBJ_Twitter.CreateFollow( wID )
			if wTwitterRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error(CreateFollow): " + wTwitterRes['Reason']
				return wRes
			
			#############################
			# normalリストへ追加
			wTwitterRes = gVal.OBJ_Twitter.AddUserList( gVal.STR_UserInfo['NorList'], wID )
			if wTwitterRes['Result']!=True :
				wRes['Reason'] = "Twitter API Error(AddUserList): " + wTwitterRes['Reason']
				return wRes
			
			#############################
			# DBにレコードがあるか
			wQuery = "twitterid = '" + gVal.STR_UserInfo['Account'] + "' and " + \
						"id = '" + str(wID) + "' "
			
			wResDB = gVal.OBJ_DB.RunExist( "tbl_follower_data", wQuery )
			wResDB = gVal.OBJ_DB.GetQueryStat()
			if wResDB['Result']!=True :
				##失敗
				wRes['Reason'] = "Run Query is failed(2): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
				return wRes
			
			#############################
			# DBに記録する
			if wResDB['Responce']==True :
				###DBに記録あり
				wQuery = "update tbl_follower_data set " + \
							"r_myfollow = True, " + \
							"foldate = '" + str(wTD['TimeDate']) + "' " + \
							"where twitterid = '" + gVal.STR_UserInfo['Account'] + "'" + \
							" and id = '" + str( wID ) + "' ;"
			
			else:
				###DBに記録なし
				wName = str(self.OBJ_Parent.STR_KeyUser[wKey]['user_name']).replace( "'", "''" )
				wQuery = "insert into tbl_follower_data values (" + \
							"'" + gVal.STR_UserInfo['Account'] + "'," + \
							"'" + str(wTD['TimeDate']) + "'," + \
							"True," + \
							"False," + \
							"False," + \
							"'" + str(wTD['TimeDate']) + "'," + \
							"False," + \
							"False," + \
							"'" + str( wID ) + "'," + \
							"'" + wName + "'," + \
							"'" + str(self.OBJ_Parent.STR_KeyUser[wKey]['screen_name']) + "'," + \
							str(self.OBJ_Parent.STR_KeyUser[wKey]['statuses_count']) + "," + \
							"'" + str(wTD['TimeDate']) + "'," + \
							"''" + \
							") ;"
			
			wResDB = gVal.OBJ_DB.RunQuery( wQuery )
			wResDB = gVal.OBJ_DB.GetQueryStat()
			if wResDB['Result']!=True :
				##失敗
				wRes['Reason'] = "Run Query is failed(4): RunFunc=" + wResDB['RunFunc'] + " reason=" + wResDB['Reason'] + " query=" + wResDB['Query']
				gVal.OBJ_L.Log( "B", wRes )
				return wRes
			
			CLS_OSIF.sPrn( '\n' + "フォローが正常に完了しました。" )
			wARR_RandID.append( wID )
			wCount += 1
			wRetry = 0
		
		#############################
		# 正常終了
		CLS_OSIF.sPrn( "上限に達したため選出を終了します。" + '\n' )
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
		wCHR_File_path = self.__get_CSVpath()
		
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
	def __get_CSVpath(self):
		wPath = gVal.DEF_USERDATA_PATH + "keyusers_" + str(gVal.STR_UserInfo['Account']) + ".csv"
		return wPath

	#####################################################
	def __get_ArashiCSVpath(self):
		wPath = gVal.DEF_USERDATA_PATH + "arashi_" + str(gVal.STR_UserInfo['Account']) + ".csv"
		return wPath

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
			wUserName = self.OBJ_Parent.STR_KeyUser[wKey]['user_name'].replace( ",", "" )
			
			wLine = ""
			wLine = wLine + wUserName + ", "
			wLine = wLine + self.OBJ_Parent.STR_KeyUser[wKey]['screen_name'] + ", "
			wLine = wLine + str(self.OBJ_Parent.STR_KeyUser[wKey]['hit_word']) + ", "
			wLine = wLine + "https://twitter.com/" + self.OBJ_Parent.STR_KeyUser[wKey]['screen_name'] + ", " + '\n'
			wSetLine.append(wLine)
		
		#############################
		# ファイル上書き書き込み
		if CLS_File.sWriteFile( inPath, wSetLine, inExist=False )!=True :
			return False	#失敗
		
		return True



#####################################################
# ツイート検索
#####################################################
	def TweetSearch(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterKeyword"
		wRes['Func']  = "TweetSearch"
		
		#############################
		# 検索モードの ID=0 のインデックスを設定する
		wRange = len( gVal.STR_SearchMode )
		wFLG_Detect = False
		for wIndex in range( wRange ) :
			if gVal.STR_SearchMode[wIndex]['id']==0 :
				wFLG_Detect = True
				break
		if wFLG_Detect!=True :
			wRes['Reason'] = "Index of id is not found"
			gVal.OBJ_L.Log( "A", wRes )
			return wRes
		
		#############################
		# コンソールを表示
		while True :
###			wWord = self.__view_TweetSearch()
			wWord = self.__view_TweetSearch( wIndex )
			
			if wWord=="\\q" :
				###終了
				break
			if wWord=="" :
				###未入力は再度入力
				continue
			
###			wResSearch = self.__run_TweetSearch( wWord )
			wResSearch = self.__run_TweetSearch( wIndex, wWord )
###			if wResSearch['Result']==True :
###				CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
			CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
			if wResSearch['Result']!=True :
				### 処理失敗
				continue
			
			#############################
			# 更新する
###			gVal.STR_SearchMode[0]['Update']  = True
			gVal.STR_SearchMode[wIndex]['Update']  = True
			
###			#############################
###			# 検索文字入力だったら検索文字を保存する
###			if wResSearch['Responce']==False :
###				gVal.STR_SearchMode[0]['Keyword'] = wWord
		
		wRes['Result'] = True
		return wRes

	#####################################################
	# ツイート検索 画面表示
	#####################################################
###	def __view_TweetSearch(self):
	def __view_TweetSearch( self, inIndex ):
###		wResDisp = CLS_MyDisp.sViewDisp( "SearchConsole", 0 )
		wResDisp = CLS_MyDisp.sViewDisp( "SearchConsole", inIndex )
		if wResDisp['Result']==False :
			gVal.OBJ_L.Log( "D", wResDisp )
			return "\\q"	#失敗=強制終了
		
###		wWord = CLS_OSIF.sInp( "検索文字？=> " )
		wWord = CLS_OSIF.sInp( "検索文字？(\\rs=検索再実行)=> " )
		return wWord

	#####################################################
	# ツイート検索 実行
	#####################################################
###	def __run_TweetSearch( self, inWord ):
	def __run_TweetSearch( self, inIndex, inWord ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterKeyword"
		wRes['Func']  = "__run_TweetSearch"
		
		#############################
		# コマンド入力か
###		wResCmd = self.ChangeSearchMode( 0, inWord )
		wResCmd = self.ChangeSearchMode( inIndex, inWord )
###		if wResCmd['Result']==True :
###			### 先頭が\\ =コマンド処理をした
###			wRes['Result'] = True
###			return wRes
		if wResCmd['Result']!=True :
			### 処理失敗
			wRes['Result'] = False
			return wRes
		wRes['Responce'] = wResCmd['Responce']
		if wResCmd['Responce']==True :
			### 先頭が\\ =コマンド処理
			wRes['Result'] = True
			return wRes
		
		###※以下コマンド以外の場合
		
		wWord = "" + inWord
		#############################
		# 再実行の場合
		if wWord=="\\rs" :
###			wWord = gVal.STR_SearchMode[0]['Keyword']
			wWord = gVal.STR_SearchMode[inIndex]['Keyword']
			if wWord=="" or wWord==None :
				CLS_OSIF.sPrn( "再実行を指示されましたが、キーワードが未設定です。" )
				wRes['Result'] = False
				return wRes
		
		#############################
		# コマンド付加
###		wResCmd = self.IncSearchMode( 0, inWord )
###		wResCmd = self.IncSearchMode( 0, wWord )
		wResCmd = self.IncSearchMode( inIndex, wWord )
		if wResCmd['Result']!=True :
			###やらかし
			wRes['Reason'] = "IncSearchModeのやらかし: reason=" + wResCmd['Reason']
			gVal.OBJ_L.Log( "A", wRes )
			return wRes
		wCommand = wResCmd['Responce']
		
		#############################
		# 取得開始の表示
		CLS_OSIF.sPrn( "タイムラインサーチ中。しばらくお待ちください......" )
		CLS_OSIF.sPrn( "取得中... 検索語=" + wCommand )
		
		#############################
		# Twitterで検索 取得
		wTwitterRes = gVal.OBJ_Twitter.GetSearch( inKeyword=wCommand, inRoundNum=gVal.DEF_STR_TLNUM['searchRoundNum'] )
		if wTwitterRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error: " + wTwitterRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		
		self.OBJ_Parent.STR_KeyUser = {}
		wARR_UserID = []
		wVAL_AllCount = len(wTwitterRes['Responce'])
		wVAL_Count    = 0
		#############################
		# 結果の表示
		for wLine in wTwitterRes['Responce'] :
			###検索にリツイートを含めない場合、
			###  リツイートはスキップする
			if gVal.STR_SearchMode[inIndex]['ExcRT']==True :
				if "retweeted_status" in wLine :
					continue
			
			###日時の変換
			wTime = CLS_OSIF.sGetTimeformat_Twitter( wLine['created_at'] )
			if wTime['Result']!=True :
				wRes['Reason'] = "sGetTimeformat_Twitter is failed(1): " + str(wLine['created_at'])
				gVal.OBJ_L.Log( "B", wRes )
				continue
			wLine['created_at'] = wTime['TimeDate']
			
			###荒らしチェック
			if gVal.STR_SearchMode[inIndex]['Arashi']==True :
				if self.OBJ_Parent.CheckTrolls( wLine )==False :
					continue
			
###			###検索にリツイートを含めない場合、
###			###  リツイートはスキップする
###			if gVal.STR_SearchMode[inIndex]['ExcRT']==True :
###				if "retweeted_status" in wLine :
###					continue
			###検索からセンシティブを除外する場合、
			###  センシティブツイートはスキップする
			if gVal.STR_SearchMode[inIndex]['ExcSensi']==True :
				if "possibly_sensitive" in wLine :
					if wLine['possibly_sensitive']==True :
						continue
			###ユーザ名に除外文字が含まれている
			if self.OBJ_Parent.CheckExcUserName( wLine['user']['name'] )==False :
				continue
			###ツイートに除外文字が含まれている
			if self.OBJ_Parent.CheckExcWord( wLine['text'] )==False :
				continue
			###端末名に除外文字が含まれている
			wCHR_Term = CLS_OSIF.sDel_HTML( str(wLine['source']) )
			if self.OBJ_Parent.CheckExcWord( wCHR_Term )==False :
				continue
			
###			###日時の変換
###			wTime = CLS_OSIF.sGetTimeformat_Twitter( wLine['created_at'] )
###			if wTime['Result']!=True :
###				wRes['Reason'] = "sGetTimeformat_Twitter is failed(1): " + str(wLine['created_at'])
###				gVal.OBJ_L.Log( "B", wRes )
###				continue
###			wLine['created_at'] = wTime['TimeDate']
###			
###			###荒らしチェック
###			if gVal.STR_SearchMode[inIndex]['Arashi']==True :
###				if self.OBJ_Parent.CheckTrolls( wLine )==False :
###					continue
			
			wStrLine = self.__getStr_TweetSearch( wLine )
			CLS_OSIF.sPrn( wStrLine )
			if str(wLine['user']['id']) not in wARR_UserID :
				wARR_UserID.append( str(wLine['user']['id']) )
			self.__set_KeyUser( wLine, wCommand )
			wVAL_Count += 1
			
			###リツイート元
			if "retweeted_status" in wLine :
				###検索からセンシティブを除外する場合、
				###  センシティブツイートはスキップする
				if gVal.STR_SearchMode[inIndex]['ExcSensi']==True :
					if "possibly_sensitive" in wLine['retweeted_status'] :
						if wLine['retweeted_status']['possibly_sensitive']==True :
							continue
				###ユーザ名に除外文字が含まれている
				if self.OBJ_Parent.CheckExcUserName( wLine['retweeted_status']['user']['name'] )==False :
					continue
				###ツイートに除外文字が含まれている
				if self.OBJ_Parent.CheckExcWord( wLine['retweeted_status']['text'] )==False :
					continue
				
				###日時の変換
				wTime = CLS_OSIF.sGetTimeformat_Twitter( wLine['retweeted_status']['created_at'] )
				if wTime['Result']!=True :
					wRes['Reason'] = "sGetTimeformat_Twitter is failed(2): " + str(wLine['retweeted_status']['created_at'])
					gVal.OBJ_L.Log( "B", wRes )
					continue
				wLine['retweeted_status']['created_at'] = wTime['TimeDate']
				
				wStrLine = self.__getStr_TweetSearch( wLine['retweeted_status'] )
				CLS_OSIF.sPrn( wStrLine )
				if str(wLine['retweeted_status']['user']['id']) not in wARR_UserID :
					wARR_UserID.append( str(wLine['retweeted_status']['user']['id']) )
###				self.__set_KeyUser( wLine['retweeted_status']['user'], wCommand )
				self.__set_KeyUser( wLine['retweeted_status'], wCommand )
				wVAL_Count += 1
		
		#############################
		# 統計
		wStr = "--------------------" + '\n'
		wStr = wStr + "検索ワード     = " + wCommand + '\n'
		wStr = wStr + "結果ツイート数 = " + str( wVAL_AllCount ) + '\n'
		wStr = wStr + "ツイート合計数 = " + str( wVAL_Count ) + '\n'
		wStr = wStr + '\n'
		
		#############################
		# コンソールに表示
		CLS_OSIF.sPrn( wStr )
		

		#############################
		# CSV書き込み
		
		# ファイル名の設定
		wCHR_File_path = self.__get_CSVpath()
		
		if self.__out_TweetSearchCSV( wCHR_File_path )!=True :
			###失敗
			wRes['Reason'] = "sWriteFile is failed: " + wCHR_File_path
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		
		#############################
		# 取得開始の表示
		CLS_OSIF.sPrn( "ユーザ一覧をCSVに出力しました: " + wCHR_File_path + '\n' )
		
		#############################
		# 荒らしCSV書き込み
###		wResArashi = self.OutArashiCSV( inHeader=False )
		wResArashi = self.__out_tsOutArashiCSV()
		if wResArashi['Result']!=True :
###			wRes['Reason'] = "OutArashiCSV is failed: " + CLS_OSIF.sCatErr( wResArashi )
			wRes['Reason'] = "__out_tsOutArashiCSV is failed: " + CLS_OSIF.sCatErr( wResArashi )
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		
		#############################
		# 検索ワードを保存する
		gVal.STR_SearchMode[inIndex]['Keyword'] = wWord
		
		#############################
		# 正常終了
		wRes['Result'] = True
		return wRes

	#####################################################
	# 結果文字を組み立てて返す
	#####################################################
	def __getStr_TweetSearch( self, inLine ):
		wStr = inLine['text'] + '\n'
		wStr = wStr + "ツイ日=" + str(inLine['created_at'])
		wStr = wStr + "  ユーザ=" + inLine['user']['name'] + "(@" + inLine['user']['screen_name'] + ")" + '\n'
		wStr = wStr + "--------------------" + '\n'
		return wStr

	#####################################################
	def __out_TweetSearchCSV( self, inPath ):
		#############################
		# 書き込みデータを作成
		wSetLine = []
		
		#############################
		# ヘッダ部
		wLine = "user_name, screen_name, hit_word, url, " + '\n'
		wSetLine.append(wLine)
		
		#############################
		# データ部
		
		wKeylist = self.OBJ_Parent.STR_KeyUser.keys()
		for wKey in wKeylist :
			wUserName = self.OBJ_Parent.STR_KeyUser[wKey]['user_name'].replace( ",", "" )
			
			wLine = ""
			wLine = wLine + wUserName + ", "
			wLine = wLine + self.OBJ_Parent.STR_KeyUser[wKey]['screen_name'] + ", "
			wLine = wLine + str(self.OBJ_Parent.STR_KeyUser[wKey]['hit_word']) + ", "
			wLine = wLine + "https://twitter.com/" + self.OBJ_Parent.STR_KeyUser[wKey]['screen_name'] + ", " + '\n'
			wSetLine.append(wLine)
		
		#############################
		# ファイル上書き書き込み
		if CLS_File.sWriteFile( inPath, wSetLine, inExist=False )!=True :
			return False	#失敗
		
		return True



#####################################################
# 荒らしユーザCSV出力
#####################################################
###	def OutArashiCSV( self, inHeader=True ):
	def OutArashiCSV( self, inReSearch=False ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterKeyword"
		wRes['Func']  = "OutArashiCSV"
		
		#############################
		# 検索モードの ID=0 のインデックスを設定する
		wRange = len( gVal.STR_SearchMode )
		wFLG_Detect = False
		for wIndex in range( wRange ) :
			if gVal.STR_SearchMode[wIndex]['id']==0 :
				wFLG_Detect = True
				break
		if wFLG_Detect!=True :
			wRes['Reason'] = "Index of id is not found"
			gVal.OBJ_L.Log( "A", wRes )
			return wRes
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# 再実行モード
		if inReSearch==True :
			### 画面表示
			wStr = "--------------------" + '\n'
			wStr = wStr + " 荒らしユーザCSVの出力 (再実行モード)" + '\n'
			wStr = wStr + "--------------------" + '\n'
			CLS_OSIF.sPrn( wStr )
			
			wWord = gVal.STR_SearchMode[wIndex]['Keyword']
		
		#############################
		# 通常モード
		else :
			### 画面表示
			wStr = "--------------------" + '\n'
			wStr = wStr + " 荒らしユーザCSVの出力" + '\n'
			wStr = wStr + "--------------------" + '\n'
			wStr = wStr + '\n'
			wStr = wStr + "荒らし判定をおこなう検索ワードを指定してください。" + '\n'
			if gVal.STR_SearchMode[wIndex]['Keyword']=="" or gVal.STR_SearchMode[wIndex]['Keyword']==None :
				wStr = wStr + "  現在の設定ワード： (未設定)" + '\n'
			else:
				wStr = wStr + "  現在の設定ワード： " + gVal.STR_SearchMode[wIndex]['Keyword'] + '\n'
			
			CLS_OSIF.sPrn( wStr )
			wWord = CLS_OSIF.sInp( "検索文字？(\\rs=検索再実行/\\q=キャンセル)=> " )
			
			if wWord.find("\\")==0 :
				###先頭が \\ はコマンド
				if wWord=="\\rs" :
					###再実行
					wWord = gVal.STR_SearchMode[wIndex]['Keyword']
				
				elif wWord=="\\q" :
					###終了
					wRes['Result'] = True
					return wRes
				else:
					###ないコマンド
					CLS_OSIF.sPrn( "そのコマンドはありません。" )
					wRes['Result'] = True
					return wRes
		
		if wWord=="" :
			CLS_OSIF.sPrn( "キーワードが設定されていません。" )
			wRes['Result'] = True
			return wRes
		
		#############################
		# 取得開始の表示
		CLS_OSIF.sPrn( "タイムラインサーチ中。しばらくお待ちください......" )
		CLS_OSIF.sPrn( "取得中... 検索語=" + wWord )
		
		#############################
		# Twitterで検索 取得
		wTwitterRes = gVal.OBJ_Twitter.GetSearch( inKeyword=wWord, inRoundNum=gVal.DEF_STR_TLNUM['searchRoundNum'] )
		if wTwitterRes['Result']!=True :
			wRes['Reason'] = "Twitter API Error: " + wTwitterRes['Reason']
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		
		wARR_UserID = []
		wVAL_AllCount = len(wTwitterRes['Responce'])
		wVAL_Count    = 0
		#############################
		# 結果の表示
		for wLine in wTwitterRes['Responce'] :
			###リツイートはスキップする
			if "retweeted_status" in wLine :
				continue
			
			###日時の変換
			wTime = CLS_OSIF.sGetTimeformat_Twitter( wLine['created_at'] )
			if wTime['Result']!=True :
				wRes['Reason'] = "sGetTimeformat_Twitter is failed(1): " + str(wLine['created_at'])
				gVal.OBJ_L.Log( "B", wRes )
				continue
			wLine['created_at'] = wTime['TimeDate']
			
			###荒らしチェック
			self.OBJ_Parent.CheckTrolls( wLine )
			wVAL_Count += 1
		
		#############################
		# 統計
		wStr = "--------------------" + '\n'
		wStr = wStr + "検索ワード     = " + wWord + '\n'
		wStr = wStr + "結果ツイート数 = " + str( wVAL_AllCount ) + '\n'
		wStr = wStr + "ツイート合計数 = " + str( wVAL_Count ) + '\n'
		wStr = wStr + '\n'
		CLS_OSIF.sPrn( wStr )
		
		#############################
		# 検索ワードを保存する
		gVal.STR_SearchMode[wIndex]['Keyword'] = wWord
		gVal.STR_SearchMode[wIndex]['Update']  = True
		
		#############################
		# ヘッダ表示
		wStr = "出力するキーユーザを選出しています。しばらくお待ちください......" + '\n'
		CLS_OSIF.sPrn( wStr )
		
		if len(self.OBJ_Parent.ARR_newExcUser)==0 :
			###登録者なし
			CLS_OSIF.sPrn( "荒らし登録者がないため、CSVは出力していません。" )
			wRes['Result'] = True
			return wRes
		
		# ファイル名の設定
		wCHR_ArashiFile_path = self.__get_ArashiCSVpath()
		
		#############################
		# 書き込み
		if self.__out_ArashiCSV( wCHR_ArashiFile_path )!=True :
			###失敗
			wRes['Reason'] = "sWriteFile is failed: " + wCHR_ArashiFile_path
			return wRes
		
		#############################
		# 取得開始の表示
		CLS_OSIF.sPrn( "荒らし一覧をCSVに出力しました: " + wCHR_ArashiFile_path + '\n' )
		
		#############################
		# 正常終了
		wRes['Result'] = True
		return wRes

	#####################################################
	def __out_tsOutArashiCSV(self):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterKeyword"
		wRes['Func']  = "__out_tsOutArashiCSV"
		
		if len(self.OBJ_Parent.ARR_newExcUser)==0 :
			###登録者なし
			CLS_OSIF.sPrn( "荒らし登録者がないため、CSVは出力していません。" )
			wRes['Result'] = True
			return wRes
		
		# ファイル名の設定
		wCHR_ArashiFile_path = self.__get_ArashiCSVpath()
		
		#############################
		# 書き込み
		if self.__out_ArashiCSV( wCHR_ArashiFile_path )!=True :
			###失敗
			wRes['Reason'] = "sWriteFile is failed: " + wCHR_ArashiFile_path
			return wRes
		
		#############################
		# 取得開始の表示
		CLS_OSIF.sPrn( "荒らし一覧をCSVに出力しました: " + wCHR_ArashiFile_path + '\n' )
		
		#############################
		# 正常終了
		wRes['Result'] = True
		return wRes

	#####################################################
	def __out_ArashiCSV( self, inPath ):
		#############################
		# 書き込みデータを作成
		wSetLine = []
		
		#############################
		# ヘッダ部
		wLine = "screen_name, count, url, lastdate, reason, " + '\n'
		wSetLine.append(wLine)
		
		#############################
		# データ部
		
		wKeylist = list( self.OBJ_Parent.ARR_newExcUser.keys() )
		for wIndex in wKeylist :
			if self.OBJ_Parent.ARR_newExcUser[wIndex]['count']==0 :
				### 0は荒らし判定なしなのでスキップ
				continue
			elif self.OBJ_Parent.ARR_newExcUser[wIndex]['arashi']==False :
				### 荒らし判定なしのためスキップ
				continue
###			elif self.OBJ_Parent.ARR_newExcUser[wIndex]['count']>=gVal.DEF_STR_TLNUM['excTwitterID'] :
###				wMark = "■"
###			else:
###				wMark = ""
			
			###理由の日本語変換
			wReasonID = self.OBJ_Parent.ARR_newExcUser[wIndex]['reason_id']
			if wReasonID in self.OBJ_Parent.DEF_STR_ARASHI_REASON_ID :
				wCHR_Reason = self.OBJ_Parent.DEF_STR_ARASHI_REASON_ID[wReasonID]
			else :
				wCHR_Reason = "Undefined(" + str(wReasonID) + ")"
			
###			wLine = ""
			wLine = self.OBJ_Parent.ARR_newExcUser[wIndex]['screen_name'] + ", "
			wLine = wLine + str( self.OBJ_Parent.ARR_newExcUser[wIndex]['count']) + ", "
			wLine = wLine + "https://twitter.com/" + self.OBJ_Parent.ARR_newExcUser[wIndex]['screen_name'] + ", "
			wLine = wLine + str( self.OBJ_Parent.ARR_newExcUser[wIndex]['lastdate']) + ", "
			wLine = wLine + wCHR_Reason + ", "
###			wLine = wLine + wMark + ", " + '\n'
			wLine = wLine + '\n'
			wSetLine.append(wLine)
		
		#############################
		# ファイル上書き書き込み
		if CLS_File.sWriteFile( inPath, wSetLine, inExist=False )!=True :
			return False	#失敗
		
		return True



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



