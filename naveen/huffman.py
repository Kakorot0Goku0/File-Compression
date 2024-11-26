import heapq
from collections import defaultdict

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    # For heapq to compare nodes
    def __lt__(self, other):
        return self.freq < other.freq

# Function to calculate frequency of characters in the text
def calculate_frequencies(text):
    frequency = defaultdict(int)
    for char in text:
        frequency[char] += 1
    return frequency

# Function to build the Huffman tree
def build_huffman_tree(frequencies):
    heap = [Node(char, freq) for char, freq in frequencies.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    return heap[0]

# Function to generate Huffman codes from the tree
def generate_codes(node, prefix='', codebook={}):
    if node:
        if node.char is not None:
            codebook[node.char] = prefix
        generate_codes(node.left, prefix + '0', codebook)
        generate_codes(node.right, prefix + '1', codebook)
    return codebook

# Function to encode the text using Huffman codes
def encode_text(text, codebook):
    return ''.join(codebook[char] for char in text)

def save_compressed_file(encoded_text, codebook, filename):
    with open(filename, 'wb') as f:
        # Save the codebook size as 2 bytes
        f.write(len(codebook).to_bytes(2, 'big'))
        
        # Write the codebook entries
        for char, code in codebook.items():
            # Store the character and its binary code
            if char == '\n':
                char = '\\n'
            f.write(char.encode('utf-8') + b' ' + code.encode('utf-8') + b'\n')
        
        # Pack the encoded text into bytes
        padded_encoded_text = encoded_text + '0' * ((8 - len(encoded_text) % 8) % 8)  # Padding to make sure it fits into bytes
        byte_array = bytearray()
        
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]  # Get 8 bits
            byte_array.append(int(byte, 2))  # Convert to byte
            
        f.write(byte_array)

# Function to load the codebook from the compressed file
def load_codebook(filename):
    codebook = {}
    with open(filename, 'rb') as f:
        codebook_size = int.from_bytes(f.read(2), 'big')
        for _ in range(codebook_size):
            line = f.readline().decode('utf-8').strip()
            a = line.split(' ', 1)
            if len(a) == 2:
                if a[0] == '\\n':
                    codebook[a[1]] = '\n'
                else:
                    codebook[a[1]] = a[0]
            else :
                codebook[a[0]] = ' '

        
        # Read the rest as binary encoded data
        encoded_data = f.read()
    
    # Convert to bit string
    bit_string = ''
    for byte in encoded_data:
        bit_string += f'{byte:08b}'  # Convert byte to 8-bit binary string
        
    return codebook, bit_string


# Function to decode the encoded text using the codebook
def decode_text(encoded_text, codebook):
    decoded_text = []
    code = ''
    for bit in encoded_text:
        code = code + bit
        if code in codebook:
            decoded_text.append(codebook[code])
            code = ''
    return ''.join(decoded_text)

# Main function to perform Huffman encoding
def huffman_encode(input_file, output_file):
    with open(input_file, 'r') as f:
        text = f.read()
    frequencies = calculate_frequencies(text)
    huffman_tree = build_huffman_tree(frequencies)
    codebook = generate_codes(huffman_tree)
    encoded_text = encode_text(text, codebook)

    save_compressed_file(encoded_text, codebook, output_file)


# Main function to perform Huffman decoding
def huffman_decode(compressed_file, output_file):
    codebook, encoded_text = load_codebook(compressed_file)
    decoded_text = decode_text(encoded_text, codebook)

    with open(output_file, 'w') as f:
        f.write(decoded_text)



# huffman_encode("literature.txt","comp.txt")
# huffman_decode("comp.txt","decomp.txt")