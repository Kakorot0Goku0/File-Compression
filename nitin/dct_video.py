import cv2
import numpy as np
import multiprocessing as mp
from functools import partial
import ctypes
from numpy.ctypeslib import ndpointer

# Load the C library (keep your existing C DCT implementation)
lib = ctypes.CDLL('./dct_functions.so')
lib.dct2.argtypes = [ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
                     ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
                     ctypes.c_int, ctypes.c_int]
lib.dct2.restype = None

lib.idct2.argtypes = [ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
                      ndpointer(ctypes.c_double, flags="C_CONTIGUOUS"),
                      ctypes.c_int, ctypes.c_int]
lib.idct2.restype = None

def dct2(block):
    M, N = block.shape
    input_array = block.astype(np.float64)
    output_array = np.zeros((M, N), dtype=np.float64)
    lib.dct2(input_array, output_array, M, N)
    return output_array

def idct2(block):
    M, N = block.shape
    input_array = block.astype(np.float64)
    output_array = np.zeros((M, N), dtype=np.float64)
    lib.idct2(input_array, output_array, M, N)
    return output_array

def compress_channel(channel, quality):
    height, width = channel.shape
    # Pad the image if dimensions are not multiples of 8
    pad_h = (8 - height % 8) % 8
    pad_w = (8 - width % 8) % 8
    if pad_h > 0 or pad_w > 0:
        channel = np.pad(channel, ((0, pad_h), (0, pad_w)), mode='edge')
    
    # Reshape the array to work with 8x8 blocks
    blocks = channel.reshape(height//8, 8, width//8, 8).transpose(0, 2, 1, 3).reshape(-1, 8, 8)
    compressed_blocks = np.zeros_like(blocks, dtype=np.float32)
    
    # Process each block
    for i, block in enumerate(blocks):
        dct_block = dct2(block.astype(np.float64))
        dct_block = np.round(dct_block / quality) * quality
        compressed_blocks[i] = idct2(dct_block)
    
    # Reshape back to original dimensions
    compressed = compressed_blocks.reshape(height//8, width//8, 8, 8).transpose(0, 2, 1, 3).reshape(height+pad_h, width+pad_w)
    
    # Remove padding if added
    if pad_h > 0 or pad_w > 0:
        compressed = compressed[:height, :width]
    
    return np.clip(compressed, 0, 255).astype(np.uint8)

def compress_frame(frame, quality):
    return compress_channel(frame, quality)

def process_batch(frames, quality):
    return [compress_frame(frame, quality) for frame in frames]

def compress_video(input_path, output_path, quality=5, batch_size=64):
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height), isColor=False)
    
    frame_count = 0
    frames_batch = []
    
    with mp.Pool(mp.cpu_count()) as pool:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert frame to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frames_batch.append(gray_frame)
            
            if len(frames_batch) == batch_size:
                # Process batch of frames in parallel
                compressed_frames = pool.map(partial(compress_frame, quality=quality), frames_batch)
                for compressed in compressed_frames:
                    out.write(compressed)
                frame_count += len(frames_batch)
                print(f"Processed {frame_count} frames")
                frames_batch = []
        
        # Process remaining frames
        if frames_batch:
            compressed_frames = pool.map(partial(compress_frame, quality=quality), frames_batch)
            for compressed in compressed_frames:
                out.write(compressed)
            frame_count += len(frames_batch)
    
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Compression complete. Processed {frame_count} frames.")

# # Usage example
# if __name__ == '__main__':
#     input_video = "1.mp4"
#     output_video = "compressed_video1_gray1.mp4"
#     compress_video(input_video, output_video)