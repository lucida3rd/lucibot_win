#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL  : https://twitter.com/lucida3hai
# ::Class       : ディスプレイ表示
# 
# ::Update= 2020/10/12
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
			
			###インプリ：検索 日本語のみ
			if "[@SEARCH-JPONLY@]"==wLine :
				wLine = "    検索は日本語のみ [\\jp] : " + str(gVal.STR_SearchMode['JPonly'])
			
			###インプリ：検索 リツイート含む
			if "[@SEARCH-INCRT@]"==wLine :
				wLine = "    リツイート含む   [\\rt] : " + str(gVal.STR_SearchMode['IncRT'])
			
			#############################
			# print表示
			CLS_OSIF.sPrn( wLine )
		
		#############################
		# 正常処理
		wRes['Result'] = True
		return wRes



