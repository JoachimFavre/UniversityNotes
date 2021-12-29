# -*- coding: utf-8 -*-
"""
Created on Sat Nov 27 23:56:38 2021

@author: joach
"""
def recursivePrint(nBarsLeft, nFruitsLeft):
    if nBarsLeft > 0:
        for text in recursivePrint(nBarsLeft - 1, nFruitsLeft):
            yield "| & " + text
    if nFruitsLeft > 0:    
        for text in recursivePrint(nBarsLeft, nFruitsLeft - 1):
            yield "$\\bullet$ & " + text
    
    if nBarsLeft <= 0 and nFruitsLeft <= 0:
        yield ""
            
for text in recursivePrint(2, 4):
    print(text)