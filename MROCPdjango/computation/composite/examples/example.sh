#!/bin/bash
echo "Example downloads ./testdata directory from http://mrbrain.cs.jhu.edu/data/projects/disa/OCPprojects/testdata/ ..."
echo "Example script running ..."

# VAR DECL
TEST_DATA=./testdata
FIBER=./testdata/test_fiber.dat
ROI_XML=./testdata/test_roi.xml
ROI_RAW=./testdata/test_roi.raw
SMALL_DIR=./testdata/small
BIG_DIR=./testdata/big

SMALL_GR_FN=test_fiber_small.graphml
BIG_GR_FN=test_fiber_big.graphml

if [ -f $FIBER ]
then
  echo "$FIBER exists ..."
else
  if [ ! -d "$mkdir"]
  then
    echo "making $TEST_DATA directory ..."
    mkdir $TEST_DATA
  fi
  echo "downloading $FIBER file..."
  wget --output-document=$FIBER http://mrbrain.cs.jhu.edu/data/projects/disa/OCPprojects/testdata/test_fiber.dat
fi

if [ -f $ROI_RAW ]
then
  echo "$ROI_RAW exists ..."
else
  echo "downloading $ROI_RAW file..."
  wget --output-document=$ROI_RAW http://mrbrain.cs.jhu.edu/data/projects/disa/OCPprojects/testdata/test_roi.raw
fi

if [ -f $ROI_XML ]
then
  echo "$ROI_XML exists ..."
else
  echo "downloading $ROI_XML file..."
  wget --output-document=$ROI_XML http://mrbrain.cs.jhu.edu/data/projects/disa/OCPprojects/testdata/test_roi.xml
fi

# SMALL
# Graph generation:
echo "../graph_exec -h. For help"
# Build a small graph given fiber streamline: test_fiber, fiber ROI's: test_roi.xml and test_roi.raw
.././graph_exec $FIBER $ROI_XML $ROI_RAW -S $SMALL_DIR -g $SMALL_GR_FN

# Invariants:
echo "./inv_exec -h. For help"
.././inv_exec $SMALL_DIR/$SMALL_GR_FN -A -S $SMALL_DIR 

# BIG
# Uncomment to Build big graph WARNING: Can take up to 6 hours to complete
.././graph_exec $FIBER $ROI_XML $ROI_RAW -S $BIG_DIR -b -g $BIG_GR_FN

# Invariants:
echo "./inv_exec -h. For help"
.././inv_exec $BIG_DIR/$BIG_GR_FN -A -S $BIG_DIR 

