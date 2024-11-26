import os

def rle_compress(data: str) -> str:
    """Compress the given string using the RLE algorithm."""
    compressed = []
    count = 1

    for i in range(1, len(data)):
        if data[i] == data[i - 1]:
            count += 1
        else:
            # Only encode if there's more than 1 repetition
            if count > 1:
                compressed.append(data[i - 1] + str(count))
            else:
                compressed.append(data[i - 1])
            count = 1

    # Handle the last run
    if count > 1:
        compressed.append(data[-1] + str(count))
    else:
        compressed.append(data[-1])

    return ''.join(compressed)


def rle_decompress(data: str) -> str:
    """Decompress the RLE compressed string."""
    decompressed = []
    i = 0

    while i < len(data):
        char = data[i]
        count = ""
        
        i += 1
        while i < len(data) and data[i].isdigit():
            count += data[i]
            i += 1
        
        if count:
            decompressed.append(char * int(count))
        else:
            decompressed.append(char)
    
    return ''.join(decompressed)


def compress_file(input_file: str, output_file: str):
    """Compress the contents of the input file and save to the output file."""
    with open(input_file, 'r') as f:
        original_data = f.read()
    
    compressed_data = rle_compress(original_data)

    # Check if compression is effective
    if len(compressed_data) < len(original_data):
        with open(output_file, 'w') as f:
            f.write(compressed_data)
    else:
        # No compression if it's not reducing size
        with open(output_file, 'w') as f:
            f.write(original_data)

def decompress_file(input_file: str, output_file: str):
    """Decompress the contents of the input file and save to the output file."""
    with open(input_file, 'r') as f:
        compressed_data = f.read()

    decompressed_data = rle_decompress(compressed_data)

    with open(output_file, 'w') as f:
        f.write(decompressed_data)

# Example usage:
# input_file = "input.txt"  # Replace with the path of your input file
# compressed_file = "compressed.txt"
# decompressed_file = "decompressed.txt"

# Compress the file
# compress_file(input_file, compressed_file)

# Decompress the file
# decompress_file(compressed_file, decompressed_file)