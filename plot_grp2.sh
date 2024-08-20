#!/bin/bash

CSV_FILE="$1"
shift
BASEDIR=$(dirname $(realpath $0))

mv $CSV_FILE $BASEDIR/current_csv.csv
