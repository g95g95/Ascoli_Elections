# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 21:36:52 2019

@author: Giulio
"""

import random as rd
import numpy as np

statistical_weight = float(800/50000)





class Politician:
	
	def __init__(self):
		self.party    =  rd.choice(['centrodestra','centrosinistra','centro','sinistra','destra'])
		
		if  np.random.rand()<0.75:
			self.sex  = 'male'
		
		else :
			self.sex  = 'female'
		self.age      = int(rd.choice(np.linspace(25,65,40)))
		
		if np.random.rand()<0.9:
			self.religion = 'credente'
		else:
			self.religion = 'non credente'
		
		self.job      = rd.choice(['artigiano','ristoratore','insegnante','avvocato','politico di professione'])
		self.person   = [self.party,self.sex,self.age,self.job]
		
	def __str__(self):
		person = self.person[0]+','+self.person[1]+','+str(self.person[2])+','+self.person[3]
		return person

class voter_path:
	def __init__(self,age,sex,work,pos,len_chessboard):
		self.age = age
		self.sex = sex
		self.work= work
		
		self.job      = rd.choice(['artigiano','ristoratore','insegnante','avvocato'])
		self.chessboard = np.array([[' '*100 for j in range(len_chessboard)]for i in range(len_chessboard)])
		self.party = rd.choice(['destra','centrodestra','sinistra','centrosinistra','centro'])
		
		for j in range(len_chessboard):
			for i in range(len_chessboard):
				if(np.random.rand()<statistical_weight):
					print("C'è un politico")
					print(Politician())
					self.chessboard[j,i]= Politician()
					print(j,i)
				else:
					self.chessboard[j,i]= 0
				
		self.pos = pos
		
	def Make_Move(self,lenmove = 1):
		self.pos += [i+rd.choice([-1,1])*lenmove for i in self.pos]
	
	
	
	def check_board(self):
		if (self.chessboard[self.pos[0],self.pos[1]]!='0'):
			return True
	
	def Make_path (self):
		for i in range(1000):
			pos = self.pos 
			self.Make_Move()
			if (self.pos[0]<0 or self.pos[1]<0 or self.pos[0]>len(self.chessboard)-1 or self.pos[1]>len(self.chessboard)-1):
				self.pos = pos
	
	def Make_Favour(self):
		
a = voter_path(24,'maschio,','studente',[0,0],200)
b = Politician()













	