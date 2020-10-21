#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : Twitter監視 キーワード抽出
# 
# ::Update= 2020/10/22
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
		
##		#############################
##		# ★検索キーの取得（仮処理）★
##		self.OBJ_Parent.STR_Keywords = {
##			"マインクラフト OR マイクラ OR minecraft"	: 0,
##			"#ARK"										: 0,
##			"アズレン OR アズールレーン"				: 0,
##			"#ETS2 OR Euro Truck"						: 0,
##			"#ATS OR American Truck"					: 0,
##			"ホロライブ OR Hololive"					: 0
##		}
###		self.OBJ_Parent.FLG_Search_JP    = True		#検索は日本語のみ
###		self.OBJ_Parent.FLG_Search_IncRt = False	#検索にリツイートを含める
		
		#############################
		self.OBJ_Parent.STR_KeyUser = {}
		#############################
		# 取得
		self.OBJ_Parent.STR_Keywords = {}
###		wKeylist = self.OBJ_Parent.STR_Keywords.keys()
		wRange = len( gVal.STR_SearchMode )
###		for wKey in wKeylist :
		for wIndex in range( wRange ) :
			#############################
			# 選択中でない、もしくは手動モードのキー は除外
			if gVal.STR_SearchMode[wIndex]['Choice']==False or \
			   gVal.STR_SearchMode[wIndex]['id']==0 :
				continue
			
			#############################
			# コマンド付加
###			wResCmd = self.IncSearchMode( wKey )
			wResCmd = self.IncSearchMode( wIndex, gVal.STR_SearchMode[wIndex]['Keyword'] )
			if wResCmd['Result']!=True :
				###やらかし
				wResCmd['Reason'] = "IncSearchModeのやらかし: reason=" + wResCmd['Reason']
				gVal.OBJ_L.Log( "A", wResCmd )
###				CLS_OSIF.sPrn( "プログラムミスのためこの用語はスキップされます 検索語=" + wKey )
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
				###検索からセンシティブを除外する場合、
				###  センシティブツイートはスキップする
				if gVal.STR_SearchMode[wIndex]['ExcSensi']==True :
					if "possibly_sensitive" in wLine :
						if wLine['possibly_sensitive']==True :
							continue
				###ユーザ名に除外文字が含まれている
				if self.OBJ_Parent.CheckExcUserName( wLine['user']['name'] )==False :
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
				
###				self.__set_KeyUser( wLine['user'], wKey )
###				self.OBJ_Parent.STR_Keywords[wKey] += 1
				self.__set_KeyUser( wLine['user'], wIndex )
				self.OBJ_Parent.STR_Keywords[wIndex] += 1
				
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
					###既にフォローしているユーザ
					if str(wLine['retweeted_status']['user']['id']) in self.OBJ_Parent.ARR_MyFollowID :
						continue
					###一度でもフォロー・リムーブしたことあるユーザ
					if str(wLine['retweeted_status']['user']['id']) in self.OBJ_Parent.ARR_OldUserID :
						continue
					###アンフォローリストに登録しているユーザ
					if str(wLine['retweeted_status']['user']['id']) in self.OBJ_Parent.ARR_UnRefollowListMenberID :
						continue
					
###					self.__set_KeyUser( wLine['retweeted_status']['user'], wKey )
###					self.OBJ_Parent.STR_Keywords[wKey] += 1
					self.__set_KeyUser( wLine['retweeted_status']['user'], wIndex )
					self.OBJ_Parent.STR_Keywords[wIndex] += 1
		
		#############################
		# キーユーザ数
		self.OBJ_Parent.STR_Cope['KeyUserNum'] += len(self.OBJ_Parent.STR_KeyUser)
		
		#############################
		# 正常終了
		wRes['Result'] = True
		return wRes

	#####################################################
	def __set_KeyUser( self, inLine, inWord ):
		###既に同じユーザを抽出した
		if str(inLine['id']) in self.OBJ_Parent.STR_KeyUser :
			return False
		
		###セット
		wSTR_Cell = {}
		wSTR_Cell.update({ "id"          : str(inLine['id']) })
		wSTR_Cell.update({ "user_name"   : str(inLine['name']) })
		wSTR_Cell.update({ "screen_name" : str(inLine['screen_name']) })
		wSTR_Cell.update({ "hit_word"    : inWord })
		self.OBJ_Parent.STR_KeyUser.update({ str(inLine['id']) : wSTR_Cell })
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
			
			self.__run_Keyuser( wWord, wRes )
###			if wRes['Result']==True :
###				CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
###			else:
			if wRes['Result']!=True :
				break	#異常
		
###		wRes['Result'] = True
		return wRes

	#####################################################
	# キーユーザ 画面表示
	#####################################################
	def __view_Keyuser( self, outRes ):
		pRes = outRes
		
		wResDisp = CLS_MyDisp.sViewDisp( "KeyuserConsole" )
		if wResDisp['Result']==False :
###			gVal.OBJ_L.Log( "D", wResDisp )
			pRes['Reason'] = "__view_Keyuser is failed: " + CLS_OSIF.sCatErr( wResDisp )
			return "\\q"	#失敗=強制終了
		
		wWord = CLS_OSIF.sInp( "コマンド？=> " )
		return wWord

	#####################################################
	# キーユーザ 実行
	#####################################################
	def __run_Keyuser( self, inWord, outRes ):
		pRes = outRes
		
		#############################
		# コマンドの分析
		if inWord.find("\\")!=0 :
			###先頭が \\ 以外はコマンドではない
			CLS_OSIF.sPrn( "コマンドが誤ってます！" )
			return
		
		wCommand = inWord.split(":")
		wID  = 0
		wLen = len(wCommand)
		wFLG_Valid = False
		if wLen==1 :
			wCommand = wCommand[0]
			if wCommand=="\\n" :
				wFLG_Valid = True
		
		elif wLen==2 :
			wID      = int( wCommand[1] )
			wCommand = wCommand[0]
			if wCommand=="\\s" or wCommand=="\\x" or \
			   wCommand=="\\c" or wCommand=="\\d" :
				wFLG_Valid = True
		
		if wFLG_Valid==False :
			CLS_OSIF.sPrn( "コマンドが誤ってます！" )
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
		# 既存の場合：IDのインデックスを探す
		else:
			if wID==0 :
				CLS_OSIF.sPrn( "コマンドが誤ってます！" )
				return
			
			wFLG_Detect = False
			for wIndex in range( wRange ) :
				if gVal.STR_SearchMode[wIndex]['id']==wID :
					wFLG_Detect = True
			if wFLG_Detect!=True :
				CLS_OSIF.sPrn( "コマンドが誤ってます！" )
				return
		
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
			self.__set_Keyuser( wIndex, False, True, pRes )
		
		#############################
		# \\x：キー未選択
		elif wCommand=="\\x" :
			self.__set_Keyuser( wIndex, False, False, pRes )
		
		#############################
		# \\ax：全キー未選択
		elif wCommand=="\\ax" :
			self.__set_Keyuser( wIndex, True, False, pRes )
		
		#############################
		# 正常
		pRes['Result'] = True
		return

	#####################################################
	# 設定画面 入力
	#####################################################
	def __view_SetKeyuser( self, inIndex, outRes ):
		pRes = outRes
		
		#############################
		# コンソールを表示
		while True :
			wWord = self.__view_TweetSearch()
			
			if wWord=="\\q" :
				###終了
				break
			
			#############################
			# コマンド入力か
			wResCmd = self.ChangeSearchMode( inIndex, wWord )
			if wResCmd['Result']!=True :
				### 検索文字？
				if wWord!="" :
					gVal.STR_SearchMode[inIndex]['Keyword'] = wWord
					gVal.STR_SearchMode[inIndex]['Update']  = True
				
				### 先頭が\\ =コマンド処理をした
###			
###			CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
		
		return

	#####################################################
	# 設定画面 (ツイート検索s画面の上のほう)
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
		wStr = "ID " + str(gVal.STR_SearchMode[inIndex]['id']) + " のキーユーザを削除します。" + '\n'
		CLS_OSIF.sPrn( wStr )
		wSelect = CLS_OSIF.sInp( "よろしいですか？(y/N)=> " )
		if wSelect!="y" :
			##キャンセル
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
		
		wStr = "ID " + str(gVal.STR_SearchMode[inIndex]['id']) + " のキーユーザを削除しました。" + '\n'
		CLS_OSIF.sPrn( wStr )
		return

	#####################################################
	# キー選択/未選択
	#####################################################
	def __set_Keyuser( self, inIndex, inFLG_Alls, in_FLG_Choice, outRes ):
		pRes = outRes
		
		#############################
		# 選択
		if inFLG_Alls==False and in_FLG_Choice==True :
			if gVal.STR_SearchMode[inIndex]['Choice']==True :
				wStr = "既に選択されています。 ID=" + str(gVal.STR_SearchMode[inIndex]['id']) + '\n'
				CLS_OSIF.sPrn( wStr )
				return
			
			wCount = self.__get_KeyuserChoice()
			if gVal.DEF_STR_TLNUM['maxKeywordNum']<=wCount :
				###選択の上限
				wStr = "選択数が上限に達してるため設定できません。 ID=" + str(gVal.STR_SearchMode[inIndex]['id']) + '\n'
				CLS_OSIF.sPrn( wStr )
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
					gVal.STR_SearchMode[inIndex]['Choice'] = False
					gVal.STR_SearchMode[inIndex]['Update']  = True
		
			wStr = "全キーユーザを選択解除しました。" + '\n'
			CLS_OSIF.sPrn( wStr )
		
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
###	def ChangeSearchMode( self, inWord ):
	def ChangeSearchMode( self, inIndex, inWord ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterKeyword"
		wRes['Func']  = "ChangeSearchMode"
		
		if inWord.find("\\")!=0 :
			###先頭が \\ 以外はコマンドではない
			wRes['Reason'] = "コマンド以外: " + str(inWord)
			return wRes
		
		###コマンド処理なので 以後は全て正常で返す仕様
		wRes['Result'] = True
		
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
		
		else:
			###ないコマンド
			CLS_OSIF.sPrn( "そのコマンドはありません: " + inWord + '\n' )
			return wRes	#コマンドの処理をした扱い
		
		#############################
		if wMsg==None :
			###やらかしてる
			wRes['Reason'] = "メッセージ抜け: wMsg=None"
			gVal.OBJ_L.Log( "A", wRes )
			return wRes	#正常扱い
		
		#############################
		# 結果表示
		CLS_OSIF.sPrn( "検索モードを変更しました: " + wMsg + '\n' )
		return wRes	#コマンドの処理をした



#####################################################
# 検索コマンド追加
#####################################################
###	def IncSearchMode( self, inCommand ):
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
###		wCHR_File_path = gVal.DEF_USERDATA_PATH + "keyusers_" + str(gVal.STR_UserInfo['Account']) + ".csv"
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
###			wLine = wLine + self.OBJ_Parent.STR_KeyUser[wKey]['user_name'] + ", "
			wLine = wLine + wUserName + ", "
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
		# コンソールを表示
		while True :
			wWord = self.__view_TweetSearch()
			
			if wWord=="\\q" :
				###終了
				break
			
			wResSearch = self.__run_TweetSearch( wWord )
			if wResSearch['Result']==True :
				CLS_OSIF.sInp( "リターンキーを押すと戻ります。[RT]" )
		
		wRes['Result'] = True
		return wRes

	#####################################################
	# ツイート検索 画面表示
	#####################################################
	def __view_TweetSearch(self):
		wResDisp = CLS_MyDisp.sViewDisp( "SearchConsole", 0 )
		if wResDisp['Result']==False :
			gVal.OBJ_L.Log( "D", wResDisp )
			return "\\q"	#失敗=強制終了
		
		wWord = CLS_OSIF.sInp( "検索文字？=> " )
		return wWord

	#####################################################
	# ツイート検索 実行
	#####################################################
	def __run_TweetSearch( self, inWord ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_TwitterKeyword"
		wRes['Func']  = "__run_TweetSearch"
		
		#############################
		# コマンド入力か
		wResCmd = self.ChangeSearchMode( inWord )
		if wResCmd['Result']==True :
			### 先頭が\\ =コマンド処理をした
			wRes['Result'] = True
			return wRes
		
		###※以下コマンド以外の場合
		
		#############################
		# コマンド付加
		wResCmd = self.IncSearchMode( 0, inWord )
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
			if gVal.STR_SearchMode[0]['ExcRT']==True :
				if "retweeted_status" in wLine :
					continue
			###検索からセンシティブを除外する場合、
			###  センシティブツイートはスキップする
			if gVal.STR_SearchMode[0]['ExcSensi']==True :
				if "possibly_sensitive" in wLine :
					if wLine['possibly_sensitive']==True :
						continue
			###ユーザ名に除外文字が含まれている
			if self.OBJ_Parent.CheckExcUserName( wLine['user']['name'] )==False :
				continue
			
			###日時の変換
			wTime = CLS_OSIF.sGetTimeformat_Twitter( wLine['created_at'] )
			if wTime['Result']!=True :
				wRes['Reason'] = "sGetTimeformat_Twitter is failed(1): " + str(wLine['created_at'])
				gVal.OBJ_L.Log( "B", wRes )
				continue
			wLine['created_at'] = wTime['TimeDate']
			
			wStrLine = self.__getStr_TweetSearch( wLine )
			CLS_OSIF.sPrn( wStrLine )
			if str(wLine['user']['id']) not in wARR_UserID :
				wARR_UserID.append( str(wLine['user']['id']) )
			self.__set_KeyUser( wLine['user'], wCommand )
			wVAL_Count += 1
			
			###リツイート元
			if "retweeted_status" in wLine :
				###検索からセンシティブを除外する場合、
				###  センシティブツイートはスキップする
				if gVal.STR_SearchMode[0]['ExcSensi']==True :
					if "possibly_sensitive" in wLine['retweeted_status'] :
						if wLine['retweeted_status']['possibly_sensitive']==True :
							continue
				###ユーザ名に除外文字が含まれている
				if self.OBJ_Parent.CheckExcUserName( wLine['retweeted_status']['user']['name'] )==False :
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
				self.__set_KeyUser( wLine['retweeted_status']['user'], wCommand )
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
		
		if self.__out_CSV( wCHR_File_path, wARR_UserID )!=True :
			###失敗
			wRes['Reason'] = "sWriteFile is failed: " + wCHR_File_path
			gVal.OBJ_L.Log( "B", wRes )
			return wRes
		
		#############################
		# 取得開始の表示
		CLS_OSIF.sPrn( "ユーザ一覧をCSVに出力しました: " + wCHR_File_path + '\n' )
		
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



