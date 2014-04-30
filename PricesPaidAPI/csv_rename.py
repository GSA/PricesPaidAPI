import csv
from os import listdir
import os
from os.path import isfile,join
import re
import shutil
import subprocess

from os import listdir
from os.path import isfile, join

process = subprocess.Popen("sh split.sh",shell=True)
process.wait()
onlyfiles = [ f for f in listdir('./cookedData') if isfile(join('./cookedData',f)) ]
onlycsvfiles = [ f for f in onlyfiles if re.search(".csv(\d+)",f)]
shutil.rmtree('cookedData/EDW')
os.mkdir('cookedData/EDW')

os.chdir('./cookedData')
for filename in onlycsvfiles:
	if filename[-2:] == '00':
		with open(filename) as myfile:
			reader = csv.reader(myfile)
			for row in reader:
				header = row
				break
		print 'header = ', header
		rename_file = filename[-4:] + '_' + filename[0:len(filename)-4] + '_header'
	else:
		rename_file = filename[-4:] + '_' + filename[0:len(filename)-4] + '_header_no'
	os.rename(filename,rename_file)
 	shutil.move(rename_file,'./EDW/')
 

onlyfiles = [ f for f in listdir('./EDW') if isfile(join('./EDW',f)) ]
onlycsvfiles = [ f for f in onlyfiles if re.search(".csv_header*",f)]

os.chdir('./EDW')
for filename in onlycsvfiles:
	if filename[0:4] == '0000':
		rename_file = filename[0:len(filename)-7]
	else:
		rename_file = filename[0:len(filename)-10]

	if filename[0:4] <> '0000':
		i = 0
		with open(filename,'r') as inputfile:
			reader = csv.reader(inputfile)
			with open(rename_file,'w') as outputfile:
				writer = csv.writer(outputfile)
				for row in reader:
					if i == 0:
						writer.writerows([header])
						i+=1
					writer.writerows([row])
	else:
		with open(filename,'r') as inputfile:
			reader = csv.reader(inputfile)
			with open(rename_file,'w') as outputfile:
				writer = csv.writer(outputfile)
				for row in reader:
					writer.writerows([row])
	print 'Split Files = ', rename_file			
	os.remove(filename)



