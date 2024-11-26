import numpy as np
from PIL import Image
import os
import math
Image.MAX_IMAGE_PIXELS = None
def create_dct_matrix(N=8):
    """Create the DCT transformation matrix of size NxN."""
    dct_matrix = np.zeros((N, N))
    
    # Factor for the first row (k=0)
    factor_0 = math.sqrt(1/N)
    # Factor for other rows (k>0)
    factor_k = math.sqrt(2/N)
    
    for k in range(N):
        for n in range(N):
            if k == 0:
                dct_matrix[k, n] = factor_0
            else:
                dct_matrix[k, n] = factor_k * math.cos((math.pi * (2*n + 1) * k) / (2*N))
    
    return dct_matrix

def custom_dct2d(block):
    """Apply 2D DCT to a block."""
    N = block.shape[0]
    dct_matrix = create_dct_matrix(N)
    
    # 2D DCT = D * block * D^T
    result = np.matmul(dct_matrix, block)
    result = np.matmul(result, dct_matrix.T)
    
    return result

def custom_idct2d(block):
    """Apply 2D inverse DCT to a block."""
    N = block.shape[0]
    dct_matrix = create_dct_matrix(N)
    
    # 2D IDCT = D^T * block * D
    result = np.matmul(dct_matrix.T, block)
    result = np.matmul(result, dct_matrix)
    
    return result

def get_quantization_matrix(quality):
    """Generate quantization matrix based on quality factor."""
    # Standard JPEG quantization matrix
    base_matrix = np.array([
        [16, 11, 10, 16, 24, 40, 51, 61],
        [12, 12, 14, 19, 26, 58, 60, 55],
        [14, 13, 16, 24, 40, 57, 69, 56],
        [14, 17, 22, 29, 51, 87, 80, 62],
        [18, 22, 37, 56, 68, 109, 103, 77],
        [24, 35, 55, 64, 81, 104, 113, 92],
        [49, 64, 78, 87, 103, 121, 120, 101],
        [72, 92, 95, 98, 112, 100, 103, 99]
    ])
    
    if quality < 50:
        scale = 5000 / quality
    else:
        scale = 200 - 2 * quality
    
    q_matrix = np.floor((base_matrix * scale + 50) / 100)
    q_matrix[q_matrix == 0] = 1  # Prevent division by zero
    
    return q_matrix
def split_into_blocks(image, block_size=8):
    """Split image into 8x8 blocks for each channel."""
    if len(image.shape) == 3:
        height, width, channels = image.shape
    else:
        height, width = image.shape
        channels = 1
        
    blocks = [[] for _ in range(channels)]
    
    for i in range(0, height, block_size):
        for j in range(0, width, block_size):
            for c in range(channels):
                block = image[i:i+block_size, j:j+block_size, c] if channels > 1 else image[i:i+block_size, j:j+block_size]
                # Pad block if it's smaller than block_size
                if block.shape[0] < block_size or block.shape[1] < block_size:
                    padded_block = np.zeros((block_size, block_size))
                    padded_block[:block.shape[0], :block.shape[1]] = block
                    block = padded_block
                blocks[c].append(block)
    
    return blocks, height, width, channels

def merge_blocks(blocks, height, width, channels, block_size=8):
    """Merge 8x8 blocks back into a color image."""
    if channels > 1:
        image = np.zeros((height, width, channels))
    else:
        image = np.zeros((height, width))
        
    for c in range(channels):
        block_idx = 0
        for i in range(0, height, block_size):
            for j in range(0, width, block_size):
                if block_idx < len(blocks[c]):
                    h = min(block_size, height - i)
                    w = min(block_size, width - j)
                    if channels > 1:
                        image[i:i+h, j:j+w, c] = blocks[c][block_idx][:h, :w]
                    else:
                        image[i:i+h, j:j+w] = blocks[c][block_idx][:h, :w]
                    block_idx += 1
    
    return image

def compress_image(input_path, output_path, max_dimension,quality=50):
    """Compress color image using DCT."""
    # Read image (now in color)
    img = Image.open(input_path)
        # Resize if image is too large
    if max(img.size) > max_dimension:
        ratio = max_dimension / max(img.size)
        new_size = tuple(int(dim * ratio) for dim in img.size)
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    image_array = np.array(img)
    
    # Split image into 8x8 blocks for each channel
    blocks, height, width, channels = split_into_blocks(image_array)
    
    # Get quantization matrix
    Q = get_quantization_matrix(quality)
    
    # Process each channel
    compressed_blocks = [[] for _ in range(channels)]
    for c in range(channels):
        for block in blocks[c]:
            # Apply DCT
            dct_block = custom_dct2d(block)  #dct(dct(block.T, norm='ortho').T, norm='ortho')
            # Quantize
            quantized = np.round(dct_block / Q)
            compressed_blocks[c].append(quantized)
    
    # Save compressed data
    compressed_data = {
        'blocks': compressed_blocks,
        'height': height,
        'width': width,
        'channels': channels,
        'quality': quality
    }
    np.save(output_path, compressed_data)
    
    # Calculate compression ratio
    original_size = os.path.getsize(input_path)
    compressed_size = os.path.getsize(output_path)
    compression_ratio = original_size / compressed_size
    
    return compression_ratio

def decompress_image(input_path, output_path):
    """Decompress color image from DCT coefficients."""
    # Load compressed data
    compressed_data = np.load(input_path, allow_pickle=True).item()
    compressed_blocks = compressed_data['blocks']
    height = compressed_data['height']
    width = compressed_data['width']
    channels = compressed_data['channels']
    quality = compressed_data['quality']
    
    # Get quantization matrix
    Q = get_quantization_matrix(quality)
    
    # Process each channel
    decompressed_blocks = [[] for _ in range(channels)]
    for c in range(channels):
        for quantized in compressed_blocks[c]:
            # Dequantize
            dct_block = quantized * Q
            # Apply inverse DCT
            block =custom_idct2d(dct_block)    # idct(idct(dct_block.T, norm='ortho').T, norm='ortho')
            decompressed_blocks[c].append(block)
    
    # Merge blocks back into image
    reconstructed_image = merge_blocks(decompressed_blocks, height, width, channels)
    
    # Clip values and convert to uint8
    reconstructed_image = np.clip(reconstructed_image, 0, 255).astype(np.uint8)
    
    # Save reconstructed image
    Image.fromarray(reconstructed_image).save(output_path)
def dct_image_compreser(input_image,output_image):
    
    compressed_file = "compressed_image.npy"
    
    # Compress image
    max_dimension=6000
    quality = 50  # Quality factor (1-100, higher means better quality but larger file)
    compression_ratio = compress_image(input_image, compressed_file, max_dimension, quality)
    # print(f"Compression ratio: {compression_ratio:.2f}:1")
    
    # Decompress image
    decompress_image(compressed_file, output_image)
    # print("Compression and decompression completed successfully!")


# def main():
#    dct_image_compreser("14.jpg","rr.jpg")
# if __name__ == "__main__":
#     main()