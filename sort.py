#!/usr/bin/python3
#
# Sort Florida line list data available at (click Download → Spreadsheet):
# https://open-fdoh.hub.arcgis.com/datasets/florida-covid19-case-line-data
#
# Direct link: https://opendata.arcgis.com/datasets/37abda537d17458bae6677b8ab75fcb9_0.csv

import sys, csv

def sort(fname):
    offset_objectid = 15
    arr = []
    first = True
    for l in csv.reader(open(fname)):
        if first:
            assert l[offset_objectid] == 'ObjectId'
            first = False
        del(l[offset_objectid])
        arr.append(l)
    arr = sorted(arr)
    wr = csv.writer(sys.stdout, lineterminator='\n')
    for l in arr:
        wr.writerow(l)

def main():
    if len(sys.argv) < 2:
        raise Exception('Usage: sort.py <csvfile>')
    sort(sys.argv[1])

if __name__ == '__main__':
    main()
