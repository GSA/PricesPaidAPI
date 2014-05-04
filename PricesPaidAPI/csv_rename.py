import csv
from os import listdir
import os
from os.path import isfile,join
import re
import shutil
import subprocess
import ppApiConfig
from os import listdir
from os.path import isfile, join
import shlex 
def splitfiles(filename):
	fileslocation = ppApiConfig.PathToActualInputFiles
	splitfileslocation = ppApiConfig.PathToDataFiles

	this_dir = os.path.dirname(os.path.abspath(__file__))
	cmd = [os.path.join(this_dir,'split.sh'),ppApiConfig.PathToActualInputFiles,filename]
	print 'cmd = ', cmd
	process = subprocess.Popen(cmd)
	process.wait()

	onlyfiles = [ f for f in listdir(fileslocation) if isfile(join(fileslocation,f)) ]
	onlycsvfiles = [ f for f in onlyfiles if re.search(".csv(\d+)",f)]

	shutil.rmtree(splitfileslocation)

	os.mkdir(splitfileslocation)
	os.chdir(fileslocation)

	for filename in onlycsvfiles:
		if filename[-4:] == '0000':
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
		shutil.move(rename_file,splitfileslocation)
	 

	onlyfiles = [ f for f in listdir(splitfileslocation) if isfile(join(splitfileslocation,f)) ]
	onlycsvfiles = [ f for f in onlyfiles if re.search(".csv_header*",f)]

       	os.chdir(splitfileslocation)
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
        print 'csv rename get cwd = ', os.getcwd()
        os.chdir("../../PricesPaidAPI") 



