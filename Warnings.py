# -*- coding: utf8 -*-

###########################################################################
#   This is the package latexparser
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

# copyright (c) Laurent Claessens, 2010,2012-2016
# email: laurent@claessens-donadello.eu


class LaTeXWarning(object):
    def __init__(self,label,page):
        self.label = label
        self.page = page
    def grep_result(self):
        import subprocess
        a=[]
        command_e="grep --color=always -n \\\\ref{"+self.label+"} *.tex"
        a.append(subprocess.getoutput(command_e))
        command_e="grep --color=always -n \\label{"+self.label+"} *.tex"
        a.append(subprocess.getoutput(command_e))
        return "\n".join(a)

class ReferenceWarning(LaTeXWarning):
    def __init__(self,label,page):
        LaTeXWarning.__init__(self,label,page)
    def __str__(self):
        return "\033[35;33m------ Undefined reference \033[35;37m {0} \033[35;33m à la page\033[35;33m {1} \033[35;33m------".format(self.label,self.page)+"\n"+self.grep_result()#+"\n"
class CitationWarning(LaTeXWarning):
    def __init__(self,label,page):
        LaTeXWarning.__init__(self,label,page)
    def __str__(self):
        return "\033[35;33m------ Undefined citation \033[35;37m %s \033[35;33m à la page\033[35;33m %s \033[35;33m------"%(self.label,str(self.page))+"\n"+self.grep_result()#+"\n"
class MultiplyLabelWarning(LaTeXWarning):
    def __init__(self,label,page):
        LaTeXWarning.__init__(self,label,page)
    def __str__(self):
        return "\033[35;33m------ \033[35;33m Multiply defined label \033[35;33m %s --------- "%self.label+"\n"+self.grep_result()#+"\n"
class TeXCapacityExceededWarning(object):
    def __init__(self,text):
        self.text=text
    def __str__(self):
        return "\033[35;34m This is a serious problem : {0} ".format(self.text)
class LabelWarning(object):
    def __init__(self,text):
        self.text=text
    def __str__(self):
        return "\033[35;32m {0} ".format(self.text)

