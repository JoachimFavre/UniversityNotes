# -*- coding: utf-8 -*-
"""
Draws table for combinations with repetitions.

Output:
| & | & $\bullet$ & $\bullet$ & $\bullet$ & $\bullet$ &
| & $\bullet$ & | & $\bullet$ & $\bullet$ & $\bullet$ &
| & $\bullet$ & $\bullet$ & | & $\bullet$ & $\bullet$ &
| & $\bullet$ & $\bullet$ & $\bullet$ & | & $\bullet$ &
| & $\bullet$ & $\bullet$ & $\bullet$ & $\bullet$ & | &
$\bullet$ & | & | & $\bullet$ & $\bullet$ & $\bullet$ &
$\bullet$ & | & $\bullet$ & | & $\bullet$ & $\bullet$ &
$\bullet$ & | & $\bullet$ & $\bullet$ & | & $\bullet$ &
$\bullet$ & | & $\bullet$ & $\bullet$ & $\bullet$ & | &
$\bullet$ & $\bullet$ & | & | & $\bullet$ & $\bullet$ &
$\bullet$ & $\bullet$ & | & $\bullet$ & | & $\bullet$ &
$\bullet$ & $\bullet$ & | & $\bullet$ & $\bullet$ & | &
$\bullet$ & $\bullet$ & $\bullet$ & | & | & $\bullet$ &
$\bullet$ & $\bullet$ & $\bullet$ & | & $\bullet$ & | &
$\bullet$ & $\bullet$ & $\bullet$ & $\bullet$ & | & | &

Created on Sat Nov 27 23:56:38 2021
@author: Joachim Favre
"""


def recursive_print(n_bars_left, n_fruits_left):
    if n_bars_left > 0:
        for text in recursive_print(n_bars_left - 1, n_fruits_left):
            yield "| & " + text
    if n_fruits_left > 0:
        for text in recursive_print(n_bars_left, n_fruits_left - 1):
            yield "$\\bullet$ & " + text

    if n_bars_left <= 0 and n_fruits_left <= 0:
        yield ""


for text in recursive_print(2, 4):
    print(text)
