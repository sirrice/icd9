# Python library for ICD9 Codes

The library encodes ICD9 codes in their natural hierarchy.  For example,
Cholera due to vibrio cholerae has the ICD9 code `0010`, and are categorized as
as type of Cholera, which in turn is a type of Intestinal Infectious Disease.
Specifically, `001.0` has the following hierarchy:

    001-139     Infectious and Parasitic Diseases
      001-009   Intestinal Infectious Diseases
        001     Cholera
          001.0 Cholera due to vibrio cholerae

This library encodes all ICD9 codes into a tree that captures this
relationship.  This tree only contains codes, and not the description text.


## Using the library

Include `icd9.py` in your python path.  The following is an example:

    from icd9 import ICD9

    tree = ICD9('codes.json')

    # list of top level codes (e.g., '001-139', ...)
    toplevelnodes = tree.children
    toplevelcodes = [node.code for node in toplevelnodes]
    print '\t'.join(toplevelcodes)


The hierarchy is encoded in a tree of `Node` objects.  `Node` has the following methods:

`search(code)`

    # find all sub-nodes whose codes contain '001'
    tree.search('001')

`find(code)`

    # find sub-node with code '001.0'. Returns None if code is not found
    tree.find('001.0')

And the following properties:

`children`

    # get node's children
    tree.children

    # search for '001.0' in root's first child
    tree.children[0].search('001.0')

`parent`

    # get 001.0 node's parent.  None if node is a root
    tree.find('001.0').parent

`parents`

    # get 001.0 node's parent path from the root.  Root node is the first element
    tree.find('001.0').parents

`leaves`

    # get all leaf nodes under root's first child
    tree.children[0].leaves

`siblings`

    # get all of 001.0 node's siblings that share the same parent
    tree.find('001.0').siblings


## ICD9 Descriptions

`descriptions.txt` contains a fixed width file of all ICD9 codes and their short and long descriptions.
This file can be used in conjuction with this library to look up descriptions of each code.

**NOTE**: The hierarchy uses codes that contain a period (`.`).  This
description file doesn't include the periods.  This must be taken into account
when using this file as a lookup table.

Alternatively, you can use
[drobhbins's](https://raw.github.com/drobbins/ICD9/master/output/output.txt)
csv file of ICD9 descriptions.

## Scraper

The `scraper/` directory includes the scraper code used to generate the
dataset.  `scraper/scraper.py` creates a json file `codes.json` of each ICD9 code's parent codes:

    [None, "001-139", "001-009", "001", "001.0"]

The last element is the actual code, the preceeding elements are coarser groupings of codes


