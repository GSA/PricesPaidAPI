#!/bin/sh
echo "Inside shell"
echo "Split parameter passed 1 = " $1
echo "Split parameter passed 2 = " $2
cd $1
#for file in *.csv
#ado
split -l 100000 -d -a 4  "$2" "$2"
pwd
#done
echo "Outside shell"
