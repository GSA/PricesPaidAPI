import csv
from Transaction import RawTransaction,BasicTransaction,replaceUndumpableData,UNITS, \
     PRICE,AGENCY,VENDOR,PSC,DESCR,DATE,LONGDESCR,AWARDIDIDV,DATASOURCE

from Transaction import ensureZipCodeHasFiveDigits,MANUFACTURER_NAME,MANUFACTURER_PART_NUMBER,BUREAU,CONTRACT_NUMBER,TO_ZIP_CODE,FROM_ZIP_CODE,UNIT_OF_ISSUE

import datetime
import calendar

import sys, traceback
import logging
import os

logger = logging.getLogger('PricesPaidTrans')
hdlr = logging.FileHandler('../logs/PricesPaidTrans.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)

def tryToInferUnitsFromDescriptionOrDefaultToOne(descr):
    return "1"

def getDictionaryFromEDWGSAAdv(raw,datasource):
    try:
# Choosing the "Charge Processing Date" as the official date"
        #d = datetime.datetime.strptime(raw.data[6].strip(' \t\n\r'),"%m/%d/%Y")
        d = datetime.datetime.strptime(raw.data[6].strip(' \t\n\r'),"%b %d %Y")
        return { \
        DATASOURCE : datasource, \
        UNITS : tryToInferUnitsFromDescriptionOrDefaultToOne(replaceUndumpableData(raw.data[3])), \
        PRICE : replaceUndumpableData(raw.data[2]), \
        AGENCY : replaceUndumpableData(raw.data[9]), \
        VENDOR : replaceUndumpableData(raw.data[5]),    \
    # I know all of this data is office supplies---this may not be too accurate
    # but it matches
        DESCR : replaceUndumpableData(raw.data[7]),   \
        LONGDESCR : replaceUndumpableData(raw.data[7]),   \
        DATE : replaceUndumpableData(d.date().isoformat()), \
        AWARDIDIDV : "GSAAdv", \
        "GSA Schedule Number" : replaceUndumpableData(raw.data[12]),\
        "Special Item Number" : replaceUndumpableData(raw.data[13]),\
        MANUFACTURER_NAME : replaceUndumpableData(raw.data[1]), \
        MANUFACTURER_PART_NUMBER : replaceUndumpableData(raw.data[0]), \
        BUREAU : replaceUndumpableData(raw.data[10]),   \
        CONTRACT_NUMBER : replaceUndumpableData(raw.data[11]), \
        TO_ZIP_CODE : replaceUndumpableData(ensureZipCodeHasFiveDigits(raw.data[15])), \
        FROM_ZIP_CODE : replaceUndumpableData(ensureZipCodeHasFiveDigits(raw.data[14]))  \
        }
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stderr)
        logger.error("don't know what went wrong here")
        return {}

def loadEDWGSAAdvFromCSVFile(filename,pattern,adapter,LIMIT_NUM_MATCHING_TRANSACTIONS):
   try:
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
        return transactions
   except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)

