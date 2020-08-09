
### An explanation of the evolution of the different directories

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
