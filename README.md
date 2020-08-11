
There are 2 obvious core ideas in Edgar xbrl files...

* contextRefs
* us-gaap: tags

```
us-gaap:EarningsPerShareBasic
```

So the Edgar xbrl files are very uniform...
The above tag is located in 8 different places in a 10Q file.
Each one of the tags has a
* contextRef
* a unique ID
* a value

So contextRef processing is critical in understanding.
If you have contextRef's down then you can easily select what tags you are seeking out.

Here are the things we are going to need...

Be able to understand the time scope of a contextRef.

Depending on the QTR you are looking at the way you grab and understand
the time data changes slightly.  So you have to be able to automagically
figure this out and grab data accordingly.

I may have to have a preprocessor that knows ahead of time for a set of companies when their fiscal year ends...   This is what may guide in the end the exact automatic processing of 10q's and 10k's

### An explanation of the evolution of the different directories

## pc

Given a set of context ref's show what tags are in that group...

We will start out with the context ref that is the default set
of context ref's from the code in the pv directory.

Be able to figure out what context ref's you want, how to generate
them generically across a set of different companies.

And showing the basic concepts of context refs matching up with
the 10q's and 10k's.

Go out and get all of the context refs and then show what tags
are in each one...

Go out and get all of the tags and then show the associated context refs.

## pv

So pv is the original directory and is historically based on
[Joe Cabrera's repo (alias greedo)](https://github.com/greedo/python-xbrl)

pvx.py is the [original parser](https://github.com/greedo/python-xbrl/blob/master/xbrl/xbrl.py)

The premise of this directory is that you start out with a known tag
that you want and then you go out and see if its contextref is part of
the context refs that you have in hand based on the time period that
has been pre-selected according to a start date (that is usually a function
of the date in the filename dowloaded from the edgar site.)

The other parser's in this directory are in 1 of 2 categories

* Trying to pear down the code to just pull a couple of tags that you want
* Trying to better understand how to show what context id's / ref's are
associated with each individual tag in a category of preselected tags.

```
python pvxt.py
```

This prints the context id's for each tag that has a contextref associated
with it...  If a tag that you are trying to pull is not part of the pulled
context ref's then it shows up as zero in the final serialization but
is not shown in the top list.

```
python pv4xui.py
```

This shows the total number of context_tags and a couple of tags
and their associated values.
