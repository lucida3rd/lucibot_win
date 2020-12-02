#!/usr/bin/python
# coding: UTF-8
#####################################################
# ::ProjectName : Lucibot Win
# ::github      : https://github.com/lucida3rd/lucibot_win
# ::Admin       : Lucida（lucida3hai@twitter.com）
# ::TwitterURL : https://twitter.com/lucida3hai
# ::Class       : HTML制御
# 
# ::Update= 2020/11/5
#####################################################
# Private Function:
#   (none)
#
# Instance Function:
#   (none)
#
# Class Function(static):
#   (none)
#
#####################################################
import os
import webbrowser

#####################################################
class CLS_HTMLIF() :

	DEF_MOJI_ENCODE = 'utf-8'								#文字エンコード

#####################################################
# URLオープン
#####################################################
	@classmethod
	def sOpenURL( cls, inURL ):
		try:
			webbrowser.open( inURL )
		except ValueError as err :
			return False
		
		return True



