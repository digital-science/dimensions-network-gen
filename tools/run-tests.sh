#!/bin/bash

# simple script to automate the steps involved in running tests

# prerequisites: chmod u+x run-tests.sh

clear
cd ..

echo "=================="
echo "CALLING [test_one] in 1 second..."
echo "=================="
sleep 1
python -m networkgen.tests.test_one
sleep 2

clear 


echo ""
echo "=================="
echo "Completed."
echo "=================="