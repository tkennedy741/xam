import sys
from pathlib import Path

# Import file with cli arguments
importFile = sys.argv[1]
if importFile is None:
    sys.exit(1)

# define method bytes
literal = 0x01
rle = 0x02
pattern = 0x03


def main():
    # read .xam file and check magic bytes
    with open(importFile, 'rb') as f:
        magic = f.read(3)

    if magic == b'XAM':
        data = decompressData()
        unwriteXam(data)
    # if file is not .xam, compress it
    else:
        data = toByte()
        compressed = compressData(data)
        writeXam(compressed)
        compressionStats(data, compressed)

def decompressData():
    try:
        with open(importFile, 'rb') as f:
            data = f.read()
        # skip magic bytes
        i = 3

        # create output buffer as bytearray
        output = bytearray()

        while i < len(data):
            # method determines decompression approach, size determines how many bytes to apply method to
            method = data[i]
            size = data[i + 1]
            i += 2
            if method == literal:
                output.extend(data[i:i + size])
                i += size
            elif method == rle:
                byte = data[i]
                i += 1
                output.extend([byte] * size)
            elif method == pattern:
                distance = data[i]
                i += 1

                start = len(output) - distance
                for j in range(size):
                    output.append(output[start + j])
        return output
    except FileNotFoundError:
        print(f"Error: File '{importFile}' not found.")
        return []

# helper function to commit literal buffer to output array, splitting into chunks if necessary
def commitLiteral(barray, literalBuffer, literal):
    while len(literalBuffer) > 255:

        chunk = literalBuffer[:255]

        barray.append(literal)
        barray.append(255)
        barray.extend(chunk)
        del literalBuffer[:255]
    if literalBuffer:
        barray.append(literal)
        barray.append(len(literalBuffer))
        barray.extend(literalBuffer)
        literalBuffer.clear()

# helper function to read file as bytes, returning empty array if file not found
def toByte():
    try:
        with open(importFile, 'rb') as f:
            data = f.read()
            return data
    except FileNotFoundError:
        print(f"Error: File '{importFile}' not found.")
        return []

# helper function to emit RLE sequence to output array
def emitRle(barray, rle, length, byte):
    barray.append(rle)
    barray.append(length)
    barray.append(byte)

# helper function to count length of run starting at pos, up to maxRun
def countRun(data, pos, maxRun=255):
    runByte = data[pos]
    length = 1

    while (
        pos + length < len(data) and
        data[pos + length] == runByte and
        length < maxRun
    ):
        length += 1
    return length

# primary function to find longest pattern match in sliding window, returning distance and length if above minLen
def findPattern(data, pos, window=255, minLen=3):
    bestLen = 0
    bestDist = 0

    start = max(0, pos-window)

    for j in range(start, pos):
        length = 0
        while (
            pos + length < len(data) and
            data[j + length] == data[pos + length] and
            length < 255
        ):
            length += 1
        if length > bestLen:
            bestLen = length
            bestDist = pos - j

    if bestLen >= minLen:
        return bestDist, bestLen

    return None

# helper function to emit pattern sequence to output array
def emitPattern(barray, pattern, distance, length):
    barray.append(pattern)
    barray.append(length)
    barray.append(distance)    

# primary function to compress data using RLE and pattern matching, returning compressed bytearray
def compressData(data):
    # define magic byte to represent method    
    # create literal buffer
    literalBuffer = []
    barray = bytearray(b'XAM')

    i = 0
    while i < len(data):
        # Check for RLE
        runLength = countRun(data, i)
        if runLength >= 3:
            commitLiteral(barray, literalBuffer, literal)
            emitRle(barray, rle, runLength, data[i])
            i += runLength
            continue
        # Check for pattern
        match = findPattern(data, i)
        if match:
            dist, length = match
            commitLiteral(barray, literalBuffer, literal)
            emitPattern(barray, pattern, dist, length)
            i += length
            continue
        # Otherwise, add to literal buffer
        literalBuffer.append(data[i])
        i += 1    
    # commit any remaining literals
    commitLiteral(barray, literalBuffer, literal)
    
    return barray

# primary function to write compressed bytearray to .xam file for final assembly
def writeXam(barray):    
    with open(f'{importFile}.xam', 'wb') as f:
        f.write(barray)
# primary function to write decompressed bytearray to file, checking for existing file and prompting user if necessary
def unwriteXam(data):
    newFile = Path(importFile).with_suffix("")
    
    if newFile.exists():
        print(f"{newFile} already exists. Would you like to overwrite it? (y/n): ")
        choice = input().lower()
        if choice == 'y':
            with open(newFile, 'wb') as f:
                f.write(data)
            return
        elif choice == 'n':
            count = 1

            while True:
                candidate = newFile.with_name(f"{newFile.stem}_{count}{newFile.suffix}")
                if not candidate.exists():
                    with open(candidate, 'wb') as f:
                        f.write(data)
                    print(f"File saved as {candidate}")
                    return
                count += 1
        else: 
            print("Invalid choice. Aborting.")

    else:
        with open(newFile, 'wb') as f:
            f.write(data)
# function to print compression statistics, including original size, compressed size, and compression ratio
def compressionStats(data, barray):
    originalSize = len(data)
    compressedSize = len(barray)
    ratio = compressedSize / originalSize if originalSize > 0 else 0
    print("Compression Complete!")
    print("\n\nCompression Statistics:")
    print(f"Original Size: {originalSize} bytes")
    print(f"Compressed Size: {compressedSize} bytes")
    print(f"Compression Ratio: {ratio:.2f}")   


if __name__ == "__main__":
    main()
