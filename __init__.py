# -*- coding: utf8 -*-

###########################################################################
#	This is LaTeXparser.py
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################

# copyright (c) Laurent Claessens, 2010
# email: moky.math@gmail.com

"""
This is a very basic LaTeX parser and manipulation intended to be used within phystricks and other of my scripts.
"""

import os
import re

class Compilation(object):
	"""
	Launch the compilation of a document in various ways.
	Takes a filename as argument

	Usage examples
	X=LaTeXparser.Compilation("MyLaTeXFile.tex")	# Creates the Compilation object
	X.bibtex()					# Apply bibtex
	X.chain_dvi_ps_pdf()				# Produce the pdf file
	"""
	def __init__(self,filename):
		self.filename=filename
		self.generic_filename = self.filename[:self.filename.rindex(".")]
	def bibtex(self):
		commande_e="bibtex "+self.generic_filename
		os.system(commande_e)
	def makeindex(self):
		commande_e="makeindex "+self.generic_filename
		os.system(commande_e)
	def nomenclature(self):
		commande_e="makeindex -s nomencl.ist -o "+self.generic_filename+".nls "+self.generic_filename+".nlo"		
		os.system(commande_e)
	def special_stuffs(self):
		self.bibtex()
		self.makeindex()
		self.nomenclature()
	def latex(self):
		"""Produce a dvi file"""
		commande_e="/usr/bin/latex --src-specials "+self.filename
		os.system(commande_e)
	def chain_dvi_ps(self,papertype="a4"):
		"""
		The chain tex->div->ps

		After compiling by self.latex(), produce a ps file from the dvi by the command
		dvips -t <papertype> <self.filename>.dvi
		
		Optional parameter : papertype is "a4" by default
		"""
		self.latex()
		commande_e="dvips -t %s %s.dvi"%(papertype,self.generic_filename)
		os.system(commande_e)
	def chain_dvi_ps_pdf(self,papertype="a4"):
		"""
		The chain tex->dvi-ps->pdf 
		This is more or less the only way to produce a pdf file containing pstricsk figures and hyperref links.

		After having produced the ps by self.chain_dvi_ps(), produce a pdf file from the ps by the command
		ps2pdf <self.filename>.ps
		
		Optional parameter : papertype is "a4" by default (to be passed to dvips)
		"""
		self.chain_dvi_ps(papertype)
		commande_e="ps2pdf "+self.generic_filename+".ps" 
		os.system(commande_e)
	def latex_more(self):
		self.special_stuffs()
		self.latex()
		self.special_stuffs()

paires = { "{":"}","[":"]" }
accepted_between_arguments = ["%","\n"," ","	"] # the last one is a TAB
definition_commands = [ "\\newcommand","\\renewcommand" ]	# In the method dict_of_definition_macros, I hard-code the fact that 
								# these definition commands have 3 arguments.
def FileToCodeLaTeX(name):
	""" return a codeLaTeX from a file """
	list_content = list(open(name,"r"))
	return CodeLaTeX("".join(list_content),filename=name)

class Occurrence(object):
	"""
	self.as_written : the code as it appears in the file, including \MyMacro, including the backslash.
	"""
	def __init__(self,name,arguments,as_written=""):
		self.arguments = arguments
		self.number_of_arguments = len(arguments)
		self.name = name
		self.as_written = as_written
		self.arguments_list = [ a[0] for a in self.arguments ]
	def analyse(self):
		return globals()["Occurrence_"+self.name[1:]](self)		# We have to remove the initial "\" in the name of the macro.
	def __getitem__(self,a):
		return self.arguments[a]
	def __str__(self):
		return str(self.arguments)

def SearchFitBrace(text,position,opening):
	"""
	return a tuple containing the text withing the next pair of open/close brace and the position where the pair closes in text

	As an example, consider the string 
	s="Hello (Louis) how are you ?"
	SearchFitBrace(s,4,["(",")"])
	returns ('Louis', 6, 12)
	because the next brace begins at position 6, finishes at position 12 and the text within in "Louis"
	"""
	close = paires[opening]
	level = 0
	giventext = text[position:]
	startPosition = position+giventext.find(opening)
	for i in range(startPosition,len(text)):
		if text[i] == opening :
			level = level+1
		if text[i] == close :
			level = level-1
		if level == 0:
			return text[startPosition+1:i],startPosition,i

def ContinueSearch(s,opening):
	r"""
	Given the string s and the position s, return True if there is still a good candidate.
	A «good» candidate is an opening bracket which is separated from the previous closing one by only elements of accepted_between_arguments. It does not takes into accounts stuff between a % and a \n 
	Return a tuple (boolean,int) where the integer is the position (in s) of the found opening bracket.
	
	Id the result is False, the returned offset is -1

	Example
	s=" \n % blahblah \n { other  "
	CntinueSearch(s,"{")
	return True and the offset of the last opening bracket
	"""
	close = paires[opening]
	turtle = 0
	while turtle < len(s):
		if s[turtle]=="%":
			a=s[turtle:]
			pos = a.find("\n")
			if pos == -1:
				return False,-1
			turtle = turtle+pos
		if s[turtle] == opening :
			return True,turtle
		if s[turtle] not in accepted_between_arguments :
			return False,-1
		else :
			turtle=turtle+1
	return False,-1

def SearchArguments(s,number_of_arguments):
	r"""
	From a string of the form {A}...{B}...{C}, returns the list ["A","B","C"] where the dots are elements of the list accepted_between_arguments.
	Inside A,B and C you can have anything including the elements of the list accepted_between_arguments.
	It is important that the string s begins on an opening bracket «{»
	/!\ (THIS IS BUGGY : for the moment we erase most of accepted_between_arguments inside A,B and C. The consequence is that as_written is wrong) /!\
	"""
	# The way it will work after debug
	# Let be the string s=«{A}...{B}...{C}» 					(1)
	# 	where A,B and C are strings and the dots are elements of the list accepted_between_arguments.
	# First we start on the first «{» and we determine the corresponding closing bracket. This is the first argument.
	# 	We add in the list of argument the string s[0:fin] where fin is the position of the closing bracket
	# Then we find the next opening bracket, that is the next «{» and we determine if there is something between it and the previous closing bracket that
	#	is not in the accepted_between_arguments. In other terms, we study the content of what is represented by dots in (1)
	# We put the whole in a loop.
	# at the end, as_written is then set as the string s[0:end] where end is the last closing bracket.
	# The string s itself is never changed and all the positions of characters are computed as offset inside s.
	turtle = 0
	arguments = []
	while len(arguments) < number_of_arguments :
		arg,start,end=SearchFitBrace(s,turtle,"{")
		arguments.append(arg)
		turtle=end+1
		if turtle >= len(s):
			as_written = s
			return arguments,as_written
		if s[turtle] <> "{":
			boo,offset = ContinueSearch(s[turtle:],"{")
			if boo:
				turtle=turtle+offset-1
			if (not boo) or (len(arguments)==number_of_arguments):
				as_written = s[0:turtle]
				return arguments,as_written

def compactization(text,accepted_between_arguments):		
	for acc in accepted_between_arguments :
		text=text.replace(acc,"")
	return text

def NextMacroCandidate(s,macro_name):
	turtle = 0
	while turtle < len(s):
		if s[turtle:turtle+len(macro_name)+1] == "\\"+macro_name :
			return True,turtle
		if s[turtle]=="%":
			a=s[turtle:]
			pos = a.find("\n")
			if pos == -1:
				return False,-1
			turtle = turtle+pos
		turtle=turtle+1


def SearchUseOfMacro(code,name,number_of_arguments=None):
	r"""
	number_of_arguments is the number of arguments expected. 
				Giving a too large number produces wrong results in the following example case where \MyMacro
				is supposed to have 3 arguments :
				\MyMacro{A}{B}{C}
				{\bf An other text}
				The {\bf ...} group is not a parameter of \MyMacro, while it will be fitted as a parameter.
			It None is given, we search first for the definition and then the expected number of arguments is deduced.

			Notice that the number_of_arguments is supposed to be the number of non optional arguments. We do not count the arguments
			within [] in the number.
	We do not fit the macros that are used in the comments.

	name is the name of the macro to be fitted like \MyMacro (including the backslash).
	"""
	turtle = 0
	remaining = code.text_brut
	while name in remaining :
		turtle = 



def MacroDefinition(code,name):
	r"""
	Finds the (last) definition of a macro and returns the corresponding object

	text : the text (a LaTeX source file) where we are searching in
	name : the name of the macro we want to analyse

	We search for the definition under one of the two forms
	\newcommand{\name}[n]{definitio}
	\newcommand{\name}{definitio}

	A crash is probably raised if the macro is not defined in the text :(
	"""
	if type(code) == CodeLaTeX :
		return code.dict_of_definition_macros()[name]
	else :
		print "Warning: something is wrong. I'm not supposed to be here. Please contact the developer"
		return CodeLaTeX(code).dict_of_definition_macros()[name]

class Occurrence_newlabel(object):
	r"""
	takes an occurrence of \newlabel and creates an object which contains the information.

	In the self.section_name we remove "\relax" from the string.
	"""
	def __init__(self,occurrence):
		self.occurrence = occurrence
		self.arguments = self.occurrence.arguments
		if len(self.arguments) == 0 :
			self.name = "Non interesting; probably the definition"
			self.listoche = [None,None,None,None,None]
			self.value,self.page,self.section_name,self.fourth,self.fifth=(None,None,None,None,None)

		else :
			self.name = self.arguments[0][0]
			self.listoche = [a[0] for a in SearchArguments(self.arguments[1][0],5)[0]]
			self.value = self.listoche[0]
			self.page = self.listoche[1]
			self.section_name = self.listoche[2].replace(r"\relax","")
			self.fourth = self.listoche[3]		# I don't know the role of the fourth argument
			self.fifth = self.listoche[4]		# I don't know the role of the fifth argument

class Occurrence_newcommand(object):
	def __init__(self,occurrence):
		self.occurrence = occurrence
		self.number_of_arguments = 0
		if self.occurrence[1][1] == "[]":
			self.number_of_arguments = self.occurrence[1][0]
		self.name = self.occurrence[0][0]#[0]
		self.definition = self.occurrence[-1][0]

class Occurrence_input(object):
	def __init__(self,occurrence):
		self.occurrence = occurrence
		self.filename = self.occurrence[0]

class StatisticsOfTheMacro(object):
	def __init__(self,code,name):
		if type(code) != CodeLaTeX :
			code = CodeLaTeX(code)
		self.name = name
		self.definition = MacroDefinition(code,name)
		self.occurrences = SearchUseOfMacro(code,name)
		self.number_of_use = len(self.occurrences)

def RemoveComments(text):
	"""
	Takes text as a tex source file and remove the comments including what stands after \end{document}
	Input : string
	Output : string
	"""
	line_withoutPC = []
	# we remove the end of lines with %
	for lineC in text.split("\n"):
		ligne = lineC
		placePC = lineC.find("%")
		to_be_removed = lineC[placePC:]
		if placePC != -1:
			ligne = ligne.replace(to_be_removed,"%")
		line_withoutPC.append(ligne+"\n")
	code_withoutPC = "".join(line_withoutPC)

	final_code = code_withoutPC
	# Now we remove what is after \end{document}
	if "\end{document}" in final_code :
		final_code = code_withoutPC.split("\end{document}")[0]+"\end{document}"
	return final_code

class newlabelNotFound(object):
	"""Exception class for CodeLaTeX.get_newlabel_value"""
	def __init__(self,label_name):
		self.label_name = label_name

def CodeLaTeXToRoughSource(codeLaTeX,filename,bibliography_bbl_filename=None,index_ind_filename=None):
	"""
	Return a file containing rough self-contained sources that are ready for upload to Arxiv.
	What it does
		1. Perform all the \input recursively
		2. Remove the commented lines (it leavec the % symbol itself)
		3. Include the bibliography, include .bbl file (no bibtex needed)
		4. Include the index, include .ind file (no makeindex needed)
	What is does not
		1. Check for pdflatex compliance. If you are using phystricks, please refer to the documentation in order to produce a pdflatex compliant source code.

	Input 
		codeLaTeX : an object of type LaTeXparser.CodeLaTeX
		filename : the name of the file in which the new code will be written
	Optional
		bibliography_bbl_filename : the name of the .bbl file. If not give, will be guesse by changing ".tex"->".bbl" in codeLaTeX.filename
		index_ind_filename :        the name of the .bbl file. If not give, will be guesse by changing ".tex"->".ind" in codeLaTeX.filename
	Output
		Create the file named <filename>
		return the new code as LaTeXparser.CodeLaTeX

	The result is extremely hard-coded. One has not to understand it as a workable LaTeX source file.
	"""
	if not bibliography_bbl_filename :
		bibliography_bbl_filename = codeLaTeX.filename.replace(".tex",".bbl")
	if not index_ind_filename :
		index_ind_filename = codeLaTeX.filename.replace(".tex",".ind")
	code_biblio = FileToCodeLaTeX(bibliography_bbl_filename)
	code_index = FileToCodeLaTeX(index_ind_filename)

	new_code = CodeLaTeX(codeLaTeX.text_without_comments)
	new_code = new_code.substitute_all_input()
	resultBib = re.search("\\\\bibliography\{.*\}",new_code.text_brut)
	if resultBib != None :
		ligne_biblio = resultBib.group()
		new_code = new_code.replace(ligne_biblio,code_biblio.text_brut)
	resultIndex = re.search("\printindex",new_code.text_brut)
	if resultIndex != None :
		new_code = new_code.replace("\printindex",code_index.text_brut)
	new_code.filename = filename
	new_code.save()
	return new_code

class CodeLaTeX(object):
	""" Contains the informations about a tex file """
	def __init__(self,text_brut,filename=None):
		"""
		self.text_brut			contains the tex code as given
		self.text_without_comments 	contains the tex code from which one removed the comments.
		"""
		self.text_brut = text_brut
		self.text_without_comments = RemoveComments(self.text_brut)
		self._dict_of_definition_macros = {}
		self._list_of_input_files = []
		self.filename = filename
	def copy(self):
		"""
		Return a copy of self in a new object
		"""
		return CodeLaTeX(self.text_brut)
	def save(self,filename=None):
		"""
		Save the code in a file. The optional argument provides a file name that overrides the self.filename. If none of filename and self.filename are give, an exception is raised.
		"""
		if not filename :
			filename = self.filename
		if not self.filename:
			self.filename=filename
		f = open(filename,"w")
		f.write(self.text_brut)
		f.close()
	def get_newlabel_value(self,label_name):
		r"""
		Assumes that self is a .aux file. Return the value associated to the line \newlabel{<label_name>}

		It it appears many times, return the last time, and prints a warning.

		If not found, raise an newlabelNotFound exception 
		"""
		list_newlabel = self.analyse_use_of_macro("\\newlabel",2)
		if label_name not in [x.name for x in list_newlabel] :
			raise newlabelNotFound(label_name)
		list_interesting  = [x for x in list_newlabel if x.name==label_name]
		if len(list_interseting) > 1 :
			print "Warning : label %s has %s different values"%(label_name,str(len(list_interesting)))
		return list_interesting[-1].value
		

	def search_use_of_macro(self,name,number_of_arguments=None):
		"""
		Return a list of Occurrence of a given macro

		Optional argument: number_of_arguments=None
		"""
		return SearchUseOfMacro(self,name,number_of_arguments)
	def analyse_use_of_macro(self,name,number_of_arguments=None):
		"""
		Provide a list of analyse of the occurrences of a macro.

		Optional argument: number_of_arguments=None, to be passed to search_use_of_macro
		"""
		return [occurence.analyse() for occurence in self.search_use_of_macro(name,number_of_arguments) ]
	def macro_definition(self,name):
		return MacroDefinition(self,name)
	def statistics_of_the_macro(self,name):
		return StatisticsOfTheMacro(self,name)
	def dict_of_definition_macros(self):
		r"""
		Returns a dictionnary wich gives, for each name of macros found to be defined in self.text, the occurrence 
		in which it was defined.
		If X is the output of dict_of_definition_macro, X.keys() is the list of the names of the macros and
		X.values() is the list of definition (type Occurrence_newcommand).

		The macro Foo is "defined" in the text when "Foo" comes as first argument of a definition command.
		(cf. the global variable definition_commands) Typically when
		\\newcommand{\Foo}[2]{bar}
		or
		\\renewcommand{\Foo}{bar}
		"""
		if self._dict_of_definition_macros == {} :
			print "Je réinvente la roue"
			dico = {}
			for definer in definition_commands :			
				for occurrence in self.search_use_of_macro(definer,3):
					newcommand = Occurrence_newcommand(occurrence)
					name = newcommand.name
					if name in dico.keys() :
						print "%s was already defined !!"%name
					else :
						dico[name]=newcommand
			self._dict_of_definition_macros = dico
		return self._dict_of_definition_macros
	def list_of_input_files(self):
		if self._list_of_input_files == []:
			list = []
			for occurrence in self.search_use_of_macro("\input",1):
				list.append(occurrence.analyse().filename)
			self._list_of_input_files = list
		return self._list_of_input_files

	def substitute_input(self,filename,text=None):
		r""" 
		replace \input{<filename>} by <text>.

		By default, it replaces by the content of <filename> (add .tex if no extension is given) which is taken in the current directory.

		Some remarks
		1. This function is not recursive
		2. It does not really check the context. A \input in a verbatim environment will be replaced !
		3. If a file is not found, a warning is printed and no replacement are done.
		"""
		list = []
		if text==None:
			strict_filename = filename
			if "." not in filename:
				strict_filename=filename+".tex"
			try:
				text = "".join( open(strict_filename,"r") )
			except IOError :
				print "Warning : file «%s» not found. No replacement done."%strict_filename
				return self
		list_input = self.search_use_of_macro("\input",1)
		for occurrence in list_input:
			x = occurrence.analyse()
			if x.filename == filename :			# Create the list of all the texts of the form \input{<filename>}
				list.append(x.occurrence.as_written)
		A = CodeLaTeX(self.text_brut)
		for as_written in list :
			A = A.replace(as_written,text)
		return A
	def substitute_all_input(self):
		r"""
		Recursively change all the \input{...} by the content of the corresponding file. 
		Return a new object LaTeXparser.CodeLaTeX
		"""
		A = CodeLaTeX(self.text_brut)
		list_input = A.search_use_of_macro("\input",1)
		while list_input :
			for occurrence in list_input :
				x = occurrence.analyse()
				A = A.substitute_input(x.filename)
			list_input = A.search_use_of_macro("\input",1)
		return A
	def remove_comments(self):
		return CodeLaTeX(self.text_without_comments)
	def find(self,arg):
		return self.text.find(arg)
	def replace(self,textA,textB):
		"""
		Replaces textA by textB in self.text_brut, but without performing the replacement in the comments.
		This is not able to replace multiline texts. For that, see self.replace_full()
		"""
		lines = self.text_brut.split("\n")
		new_text = ""
		for line in lines :
			placePC = line.find("%")
			if placePC == -1:
				new_line = line.replace(textA,textB)+"\n"
			else:
				new_line = line[:placePC+1].replace(textA,textB)+line[placePC+1:]+"\n"
			new_text = new_text + new_line
		return CodeLaTeX(new_text)
	def replace_full(self,textA,textB):
		""" Replace textA by textB including in the comments """
		new_text = self.text_brut.replace(textA,textB)
		return CodeLaTeX(new_text)
	def rough_source(self,filename,bibliography_bbl_filename=None,index_ind_filename=None):
		"""
		Return the name of a file where there is a rough latex code ready to be published to Arxiv
		See the docstring of LaTeXparser.CodeLaTeXToRoughSource
		"""
		return CodeLaTeXToRoughSource(self,filename,bibliography_bbl_filename,index_ind_filename)
