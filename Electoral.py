# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 21:36:52 2019

@author: Giulio
"""

import random as rd
import numpy as np

class Politician:
	def __init__(self):
		self.party 
		self.characteristics = 
	


class voter_path:
	def __init__(self,age,sex,work,pos,len_chessboard):
		self.age = age
		self.sex = sex
		self.work= work
		self.chessboard = np.array([Politician.make_list_of_politicians()for j in range(len(len_chessboard))])
		self.pos = pos
		
	def Make_Move(self,lenmove = 1):
		self.pos += [i+rd.choice([-1,1])*lenmove for i in self.pos]
	
	
	def check_board(self):
		if (self.chessboard[self.pos[0],self.pos[1]]==1):
			return True
	
	def Make_Favour(self):
		
	