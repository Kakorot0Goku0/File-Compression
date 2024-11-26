from os.path import getsize

PARSE_BYTES = 6
MAX_CHARACTERS = 65536


def init_lzw_compression_table():
    compression_table = {}
    for i in range(0, MAX_CHARACTERS):
        compression_table[chr(i)] = i
    return compression_table


def init_lzw_decompression_table():
    decompression_table = {}
    for i in range(0, MAX_CHARACTERS):
        decompression_table[i] = chr(i)
    return decompression_table


def lzw_compress(input_file_path, output_file_path):
    file = open(input_file_path, "r", encoding="utf-8")
    compressed_file = open(output_file_path, "wb")
    if getsize(input_file_path) == 0:
        file.close()
        compressed_file.close()
        return
    compression_table = init_lzw_compression_table()
    p = file.read(0)
    code = MAX_CHARACTERS
    file.seek(0)
    while True:
        ch = file.read(1)
        if not ch:
            break
        if ch == '\ufeff':
            continue
        c = ch
        if p + c in compression_table.keys():
            p = p + c
        else:
            compressed_file.write(compression_table[p].to_bytes(PARSE_BYTES, byteorder='big'))
            compression_table[p + c] = code
            code = code + 1
            p = c
    compressed_file.write(compression_table[p].to_bytes(PARSE_BYTES, byteorder='big'))
    compressed_file.close()
    file.close()


def lzw_decompress(input_file_path, output_file_path):
    file = open(input_file_path, "rb")
    decompressed_file = open(output_file_path, "w", encoding="utf-8")
    if getsize(input_file_path) == 0:
        file.close()
        decompressed_file.close()
        return
    file.seek(0)
    decompression_table = init_lzw_decompression_table()
    old = int.from_bytes(file.read(PARSE_BYTES), byteorder='big')
    s = decompression_table[old]
    decompressed_file.write(s)
    c = s[0]
    count = MAX_CHARACTERS
    while True:
        num_bytes = file.read(PARSE_BYTES)
        if not num_bytes:
            break
        num = int.from_bytes(num_bytes, byteorder='big')
        if num not in decompression_table:
            s = decompression_table[old] + c
        else:
            s = decompression_table[num]
        decompressed_file.write(s)
        c = s[0]
        decompression_table[count] = decompression_table[old] + c
        count = count + 1
        old = num
    decompressed_file.close()
    file.close()
