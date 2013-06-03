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
relationship.  It also includes a code descriptions file that can also be
imported to provide english descriptions for each code.


## Using the library

Include `icd9.py` in your python path.  Then put `codes.json` and `descriptions.csv` somewhere convenient.
Here's a simple example:

    from icd9 import ICD9

    # feel free to replace with your path to the json file
    tree = ICD9('codes.json', 'descriptions.csv')

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

`code`

    # get node's ICD9 code
    tree.find('001.1').code

`description`: if you also passed it `descriptions.csv` in the constructor.  Otherwise it returns the code.

    # get english description of ICD9 code
    # prints: 'Cholera due to vibrio cholerae el tor'
    tree.find('001.1').description

    # prints: 'ROOT'
    tree.description

    # prints: '001'
    tree.find('001.1').parent.description

`descr`: alias for `description`

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

`descriptions.txt` contains a csv file of ICD9 codes and their long and short descriptions.
This file can be used in this library to provide text descriptions for each ICD9 code.

You can thank [drobhbins](https://github.com/drobbins/ICD9) who actually
created the file.  I just stole it.

## Scraper

The `scraper/` directory includes the scraper code used to generate the
dataset.  `scraper/scraper.py` creates a json file `codes.json` of each ICD9 code's parent codes:

    [None, "001-139", "001-009", "001", "001.0"]

The last element is the actual code, the preceeding elements are coarser groupings of codes


