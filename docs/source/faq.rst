FAQ
===

Sprinter keeps overriding my custom *rc! How can I stop it?
-----------------------------------------------------------

Sprinter will always inject itself after everything in a profile or rc
file, with the exception of text in a block surrounded by
#SPRINTER_OVERRIDES. These will always run after any sprinter
configuration.

How do I make a sprinter formula?
---------------------------------

A sprinter formula is just a python module or egg that a python class
extends the 'formulabase' class, located in
`sprinter.formula.formulabase
<https://github.com/toumorokoshi/sprinter/blob/develop/sprinter/formulabase.py>`_.

If you're not familiar with python, it's easier to just follow an
example, like this one: https://github.com/toumorokoshi/yt.formula.node.

I need help! Who do I talk to?
------------------------------

If you have a question about a specific formula, it's best to pots a bug or talk to the author or the formula.

If you have questions about sprinter, your best bet is to post a message in the
`Google Group
<https://groups.google.com/forum/#!forum/sprinter-dev>`_.

If there's behaviour that you think is a bug, you can also
`create a ticket <https://github.com/toumorokoshi/sprinter/issues?state=open>`_.
