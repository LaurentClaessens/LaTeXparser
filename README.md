# DEPRECATION

This project is deprecated. It is now merged with pytex.

Please, download [pytex](https://github.com/LaurentClaessens/pytex)



# Presentation

`LaTeXParser` is a small parser of LaTeX written in Python. It allows to know, in Python, where such and such macro is used and replace the occurrence of a macro by an user-defined string. 

The aim is to help writing pre-(LaTeX)compilation scripts in Python for complex documents. Examples are :

* There is in fact no code duplication in the sources of the preprint [BTZ black hole from the structure of the algebra so(2,n)](http://arxiv.org/abs/0912.2267)
* Extracting a managing the source code of [Le Frido](http://laurent.claessens-donadello.eu/pdf/lefrido.pdf) from the ones of [mazhe](http://laurent.claessens-donadello.eu/pdf/mazhe.pdf)



# HOW DOES THE SHA1SUM RECORD WORKS


The XML file in which are recorded the sha1sum of the followed files is of the form 

```html
<?xml version="1.0" ?>
<Followed_files>
	<fichier name="ess.py" sha1sum="a329313819092a183ca8b08bb7c178807a1a68b7"/>
	<fichier name="ess.aux" sha1sum="be730c54ff1d1a75398a496283efe45c675dc54f"/>
</Followed_files>
```


The principal XML object is got by
root = minidom.parse(<filename>)

Then the «list of lists» of elements "Followed_files" is got by
fileNodes = root.getElementsByTagName("Followed_files")

In the example above, there is only one. At this point fileNodes is a list whole element 0 represents the lines
	<fichier name="ess.py" sha1sum="a329313819092a183ca8b08bb7c178807a1a68b7"/>
	<fichier name="ess.aux" sha1sum="be730c54ff1d1a75398a496283efe45c675dc54f"/>

Each element in these lines has the tag "fichier". Then the list is given by
fileNode.getElementsByTagName("fichier")

The first element of that list represents the line
	<fichier name="ess.py" sha1sum="a329313819092a183ca8b08bb7c178807a1a68b7"/>

If F = fileNode.getElementsByTagName("fichier")[0], then we get the name by
F.getAttribute("sha1sum")


--------------------------------------------
HOW DOES THE MAGICAL BOX WORKS
--------------------------------------------

See the "DOM example" in "Python Library Reference Release 2.3.5".


The file containing the pieces of LaTeX code have the structure
+++++++++++++++++++++++++++++++++++++++++++
<?xml version="1.0" ?>

<TheBoxes>

<CodeBox label="My first example">
	Bonjour
</CodeBox>
<CodeBox label="My second example">
	Au revoir
</CodeBox>

</TheBoxes>
+++++++++++++++++++++++++++++++++++++++++++

We extract the interesting informations in the following way :



dom = minidom.parse("ess.xml")
for box in dom.getElementsByTagName("CodeBox"):
	print box.getAttribute("label")
	text = getText(box.childNodes)
	print "\n".join(text.split("\n")[1:-1])	# Because minidom adds an empty line at first and last position.

See also tests.py and magical_box.tex
