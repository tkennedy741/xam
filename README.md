# XAM Compressor

XAM is a simple experimental lossless file compressor written in Python.
It uses Run-Length Encoding (RLE) and LZ-style pattern matching to reduce
file size for highly repetitive data.

## Features

 - Custom binary format
 - Run Length Encoding (RLE)
 - Pattern matching compression
 - Automatic compression/decompression detection
 - Compression Statistics

## Usage

Compress:

 - XAM file.txt

Decompress:
 - XAM file.txt.xam

 - During decompresion, you have the option to overwrite the original file if in the current working directory

=======
# XAM
Simple File Compressor written in Python

How it works:
XAM, upon receiving a file iterates through every byte, scanning and packing these bytes to be reassembled into a new file structure .xam

.xam files are assembled as such:

XAM magic bytes
[Method] [Size] [Data]
....
[Method] [Size] [Data]

Where Method represents either RLE, LZ-Style Pattern Compression, or Literals
Size represents how many bytes are in Data

RLE, or Run-Length Encoding is a simple compression technique that reduces file size by replacing consecutive repeated bytes with a single value and count of occurences. When XAM detects that more than 3 bytes in a row have the same value (Ex: "AAAAA"), it is represented in the file structure as [RLE][5][A]

LZ-Style Pattern compression reduces file size by replacing repeated patterns with references to earlier occurrences in the data stream. XAM records the distance where the pattern last occured (In a window of 255 bytes) and how long the matching sequence is. This is represented in the file structure as 
[LZ][Length][Distance]

If neither LZ or RLE is detected, the string is stored as its literal bytes from the source file.

Decompression is done when XAM detects a file that contains the .xam file's magic bytes. Instead of running the file through the standard compression logic, XAM iterates through the bytestream and repackages it back into the original file by reading the file structure. 

XAM excels with plain text files such with common repeating phrases and characters, some ideal file types include

.txt
.log
.csv
.json
.xml
.py
.c
.cpp
.java
.js
.sh
.html
.css
.sql
.ini
.yaml
.toml

XAM does not work well with complex files such as already compressed formats and large media files. XAM is a lossless compressor but may result in negative compression with incompatible file types. 

