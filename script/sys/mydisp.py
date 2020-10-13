#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : ディスプレイ表示
# 
# ::Update= 2020/10/13
#####################################################
# Private Function:
#   __write( self, inLogFile, inDate, inMsg ):
#
# Instance Function:
#   __init__( self, inPath ):
#   Log( cls, inLevel, inMsg, inView=False ):
#
# Class Function(static):
#   (none)
#
#####################################################

from osif import CLS_OSIF
from filectrl import CLS_File
from gval import gVal
#####################################################
class CLS_MyDisp():
#####################################################

#####################################################
# ディスプレイファイル 読み込み→画面表示
#####################################################
	@classmethod
	def sViewDisp( cls, inDisp ):
		#############################
		# 応答形式の取得
		#   "Result" : False, "Class" : None, "Func" : None, "Reason" : None, "Responce" : None
		wRes = CLS_OSIF.sGet_Resp()
		wRes['Class'] = "CLS_MyDisp"
		wRes['Func']  = "sViewDisp"
		
		#############################
		# ディスプレイファイルの確認
		wKeylist = gVal.DEF_STR_DISPFILE.keys()
		if inDisp not in wKeylist :
			###キーがない(指定ミス)
			wRes['Reason'] = "Display key is not found: inDisp= " + inDisp
			return wRes
		
		if CLS_File.sExist( gVal.DEF_STR_DISPFILE[inDisp] )!=True :
			###ファイルがない...(消した？)
			wRes['Reason'] = "Displayファイルがない: file=" + gVal.DEF_STR_DISPFILE[inDisp]
			return wRes
		
		#############################
		# ディスプレイファイルの読み込み
		wDispFile = []
		if CLS_File.sReadFile( gVal.DEF_STR_DISPFILE[inDisp], outLine=wDispFile, inStrip=False )!=True :
			wRes['Reason'] = "Displayファイルがない(sReadFile): file=" + gVal.DEF_STR_DISPFILE[inDisp]
			return wRes
		
		if len(wDispFile)<=1 :
			wRes['Reason'] = "Displayファイルが空: file=" + gVal.DEF_STR_DISPFILE[inDisp]
			return wRes
		
		#############################
		# 画面クリア
		CLS_OSIF.sDispClr()
		
		#############################
		# 画面に表示する
		for wLine in wDispFile :
			###コメントはスキップ
			if wLine.find("#")==0 :
				continue
			
			###インプリ：ユーザアカウント
			if "[@USER-ACCOUNT@]"==wLine :
				wLine = "Twitter ID : " + gVal.STR_UserInfo['Account']
			
			###インプリ：検索 画像を含める
			if "[@SEARCH-IMAGE@]"==wLine :
				wJPstr = cls.__get_JPstr_Dual( gVal.STR_SearchMode['IncImage'], gVal.STR_SearchMode['ExcImage'] )
				if wJPstr==None :
					wRes['Reason'] = "フラグ取り扱い矛盾: 検索に画像を含める Dual flag is True"
					return wRes
				wLine = "    検索に画像を含める    [\\i]: " + wJPstr
			
			###インプリ：検索 動画を含める
			if "[@SEARCH-VIDEO@]"==wLine :
				wJPstr = cls.__get_JPstr_Dual( gVal.STR_SearchMode['IncVideo'], gVal.STR_SearchMode['ExcVideo'] )
				if wJPstr==None :
					wRes['Reason'] = "フラグ取り扱い矛盾: 検索に動画を含める Dual flag is True"
					return wRes
				wLine = "    検索に動画を含める    [\\v]: " + wJPstr
			
			###インプリ：検索 リンクを含める
			if "[@SEARCH-LINK@]"==wLine :
				wJPstr = cls.__get_JPstr_Dual( gVal.STR_SearchMode['IncLink'], gVal.STR_SearchMode['ExcLink'] )
				if wJPstr==None :
					wRes['Reason'] = "フラグ取り扱い矛盾: 検索にリンクを含める Dual flag is True"
					return wRes
				wLine = "    検索にリンクを含める  [\\l]: " + wJPstr
			
			###インプリ：検索 公式マークのみ
			if "[@SEARCH-OFFICIAL@]"==wLine :
				wLine = "    検索は公式マークのみ  [\\o]: " + cls.__get_JPstr_Single( gVal.STR_SearchMode['OFonly'] )
			
			###インプリ：検索 日本語のみ
			if "[@SEARCH-JPONLY@]"==wLine :
				wLine = "    検索は日本語のみ     [\\jp]: " + cls.__get_JPstr_Single( gVal.STR_SearchMode['JPonly'] )
			
			###インプリ：検索 リツイート含む
			if "[@SEARCH-RT@]"==wLine :
				wLine = "    リツイート含めない   [\\rt]: " + cls.__get_JPstr_Single( gVal.STR_SearchMode['ExcRT'] )
			
			###インプリ：検索 センシティブな内容を含めない
			if "[@SEARCH-SENSI@]"==wLine :
				wLine = "    センシティブを除外   [\\sn]: " + cls.__get_JPstr_Single( gVal.STR_SearchMode['ExcSensi'] )
			
			#############################
			# print表示
			CLS_OSIF.sPrn( wLine )
		
		#############################
		# 正常処理
		wRes['Result'] = True
		return wRes

	#####################################################
	@classmethod
	def __get_JPstr_Single( cls, inFLG_Inc ):
		if inFLG_Inc==True :
			wStr = "はい"
		else:
			wStr = "いいえ"
		return wStr


	#####################################################
	@classmethod
	def __get_JPstr_Dual( cls, inFLG_Inc, inFLG_Exc ):
		if inFLG_Inc==True and inFLG_Exc==False :
			wStr = "含める"
		elif inFLG_Inc==False and inFLG_Exc==True :
			wStr = "除外する"
		elif inFLG_Inc==False and inFLG_Exc==False :
			wStr = "無条件"
		else:
			wStr = None
		return wStr



