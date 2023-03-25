
"""man/Rules.hxmd
Define a rule by a function with a variable amount of keyword arguments (`**kwargs`),
and then add it to the global `RULES` list.

----------------------------------------------------------------------------------------------------

Conventions|Nomenclature|Abbrevations:

    - the amount of neighbours is denoted by either :
        - a lowercase `n`
        - the word `neighbours` (british only, thus `neighbors` will not be recognized natively)

    - the state of the current cell is denoted by either :
        - a lowercase `c`   |   this may be changed to `s` in the future
        - the word `cell`   |   this may be changed to `state` in the future

    It is possible that only the abbreviation will remain,
    as having to declare each term each assignement is quite tedious,
    unless a more concise way gets added later on.

    **For now**, please stick to abbreviations ;
    that is, only make use of the first key declared for each entry above.

    This does make for less readable code, but once again,
    __this will hopefully get patched later on__.
"""


def isolation(**kwargs):
    # if cellState is False, do not change anything (and skip to the next rule)
    if kwargs['c'] is False: return

    # kill the cell if it has stricly less than 2 neighbours
    if kwargs['n'] < 2: return False


### [NOTE] : this is implied by its absence,
###          thus is not required (it would never change the cellState)
# def survival(**kwargs):
#     if kwargs['c'] is False: return

def overpopulation(**kwargs):
    if kwargs['c'] is False: return

    if kwargs['n'] > 3: return False


def birth(**kwargs):
    # only execute the rest if the cell is not alive
    if kwargs['c'] is True: return

    if kwargs['n'] == 3: return True






RULES = [
    isolation,
    #survival,
    overpopulation,
    birth,
]
