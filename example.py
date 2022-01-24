import double
import sys
from navigate import navigate
d3 = double.DRDoubleSDK()
nav = navigate(0,0.5)



""" arr1 = nav.getPosition()
widefindStart = [0.677, -2.656]
widefindDest = [1.77, -1.94]
arr2 = nav.calcWFtoD3(arr1, widefindStart, widefindDest)

nav.navigation(arr2[0], arr2[1]) """

nav.navigation(0,0)
#nav.cancelNavigation()