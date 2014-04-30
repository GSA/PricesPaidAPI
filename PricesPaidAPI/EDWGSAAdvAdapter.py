import csv
from Transaction import RawTransaction,BasicTransaction,replaceUndumpableData,UNITS, \
     PRICE,AGENCY,VENDOR,PSC,DESCR,DATE,LONGDESCR,AWARDIDIDV,DATASOURCE

from Transaction import ensureZipCodeHasFiveDigits,MANUFACTURER_NAME,MANUFACTURER_PART_NUMBER,BUREAU,CONTRACT_NUMBER,TO_ZIP_CODE,FROM_ZIP_CODE,UNIT_OF_ISSUE,EXTENDED_PRICE,PRODUCT_DESCRIPTION,QUANTITY,UNSPSC_CODE,ORDERING_PROCESS,PSC_DESCRIPTION,DUNS_NUMBER

import datetime
import calendar

import sys, traceback
import logging
import time
import os
from time import gmtime, strftime

logger = logging.getLogger('PricesPaidTrans')
hdlr = logging.FileHandler('../logs/PricesPaidTrans.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)

def tryToInferUnitsFromDescriptionOrDefaultToOne(descr):
    return "1"

def getDictionaryFromEDWGSAAdv(raw,datasource):
    try:
# Choosing the "Charge Processing Date" as the official date"
        d = datetime.datetime.strptime(raw.data[5].strip(' \t\n\r'),"%m/%d/%Y")
        #d = datetime.datetime.strptime(raw.data[5].strip(' \t\n\r'),"%b %d, %Y")
        return { \
        AGENCY : replaceUndumpableData(raw.data[0]), \
        AWARDIDIDV : replaceUndumpableData(raw.data[1]), \
        BUREAU : replaceUndumpableData(raw.data[2]),   \
        CONTRACT_NUMBER : replaceUndumpableData(raw.data[3]), \
        DATASOURCE : replaceUndumpableData(raw.data[4]), \
        DATE : replaceUndumpableData(d.date().isoformat()), \
        DESCR : replaceUndumpableData(raw.data[6]),   \
        FROM_ZIP_CODE : replaceUndumpableData(ensureZipCodeHasFiveDigits(raw.data[7])),  \
        LONGDESCR : replaceUndumpableData(raw.data[8]),  
	MANUFACTURER_NAME : replaceUndumpableData(raw.data[9]), \
	MANUFACTURER_PART_NUMBER : replaceUndumpableData(raw.data[10]), \
	PRICE : replaceUndumpableData(raw.data[11]), \
	PSC : replaceUndumpableData(raw.data[12]), \
	TO_ZIP_CODE : replaceUndumpableData(ensureZipCodeHasFiveDigits(raw.data[13])), \
	UNIT_OF_ISSUE : replaceUndumpableData(raw.data[14]), \
	UNITS : tryToInferUnitsFromDescriptionOrDefaultToOne(replaceUndumpableData(raw.data[15])), \
	VENDOR : replaceUndumpableData(raw.data[16]),    \
	EXTENDED_PRICE : replaceUndumpableData(raw.data[17]), \
	PRODUCT_DESCRIPTION : replaceUndumpableData(raw.data[18]), \
	QUANTITY : replaceUndumpableData(raw.data[19]),
	UNSPSC_CODE : replaceUndumpableData(raw.data[20]),
	ORDERING_PROCESS : replaceUndumpableData(raw.data[21]), \
	PSC_DESCRIPTION : replaceUndumpableData(raw.data[22]), \
	DUNS_NUMBER: replaceUndumpableData(raw.data[23]), \
	}
    except:
	exc_type, exc_value, exc_traceback = sys.exc_info()
	traceback.print_exception(exc_type, exc_value, exc_traceback,
			      limit=2, file=sys.stderr)
        logger.error("don't know what went wrong here")
	return {}

def loadEDWGSAAdvFromCSVFile(filename,pattern,adapter,LIMIT_NUM_MATCHING_TRANSACTIONS,error_file):
   try:
        print 'filename = {0}'.format(filename)
        logger.error('EDWGSAAdv reader opened:'+filename)
        transactions = []
        with open(filename, 'rb') as f:
            basename = os.path.basename(filename)
            reader = csv.reader(f)
            logger.error('EDWGSAAdv reader opened:'+filename)
            n = len(transactions)
            i = 0
            for row in reader:
                tr = RawTransaction("spud")
                tr.data = row;
                try:
                    bt = BasicTransaction(adapter,tr,basename)
                    if (pattern):
                        result = re.search(pattern, bt.getSearchMemento())
                    else:
                        result = True
                    if (result):
                        if (bt.isValidTransaction()):
                            transactions.append(bt)
                            i = i + 1
                    if (i+n) > LIMIT_NUM_MATCHING_TRANSACTIONS:
                        break
                except:
                    print "Error on this row:"
                    print repr(row)
		    if i <> 0:
		       error_file.write('filename::: {0}'.format(basename) + ':::' +'record ::: {0}'.format(repr(row))+'\n')
        return transactions
   except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)

