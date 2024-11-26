import tkinter as tk
import threading
import os
from tkinter import filedialog, messagebox
from naveen import huffman
from prashant import lzw
from bhanu import RLE
from nitin import dct_image
from nitin import dct_video

# Main app window
root = tk.Tk()
root.title("Text and Image Compressor")
root.geometry("800x600")

file_path = ""
outputfilesize = [0]
outputfile = ""

def upload_file():
    global file_path
    file_path = filedialog.askopenfilename(
        filetypes=[("Text", "*.txt"), ("JPEG", "*.jpg"), ("PNG", "*.png"),("MP4","*.mp4")]
    )
    if file_path:
        file_label.config(text=f"File selected: {file_path}")
        apply_button.config(state="normal")  # Enable the apply button after selecting a file
    else:
        file_label.config(text="No file selected")

def show_loading():
    loading_label.config(text="Processing... Please wait.")
    loading_label.pack(pady=5)

def hide_loading():
    loading_label.config(text="")
    loading_label.pack_forget()

def reset_application():
    global file_path, outputfile
    file_path = ""
    outputfile = ""
    outputfilesize[0] = 0

    # Reset labels and button
    file_label.config(text="No file selected")
    output_label.config(text="")
    apply_button.config(text="Compress File", state="disabled")
    compression_menu.config(state="normal")
    compression_var.set("None")

def apply_technique():
    selected_technique = compression_var.get()

    if file_path:
        if apply_button["text"] == "Compress File":
            output_label.config(text=f"Applying {selected_technique} on {file_path} for compression")
            processing_thread = threading.Thread(target=process_file, args=(selected_technique, "compress"))
            processing_thread.start()
        elif apply_button["text"] == "Decompress File":
            output_label.config(text=f"Applying {selected_technique} on {outputfile} for decompression")
            processing_thread = threading.Thread(target=process_file, args=(selected_technique, "decompress"))
            processing_thread.start()
    else:
        messagebox.showwarning("Warning", "Please upload a file to proceed.")

def process_file(selected_technique, mode):
    root.after(0, show_loading)
    out =""
    global outputfile
    if mode == "compress":
        if selected_technique == "huffman-txt":
            outputfile = "comp-huffman-txt-output.txt"
            huffman.huffman_encode(file_path, outputfile)
        elif selected_technique == "lzw-txt":
            outputfile = "comp-lzw-txt-output.txt"
            lzw.lzw_compress(file_path, outputfile)
        elif selected_technique == "RLE-txt":
            outputfile = "comp-rle-txt-output.txt"
            RLE.compress_file(file_path, outputfile)
        elif selected_technique == "DCT-video":
            outputfile = "comp-DCT-video-output.mp4"
            dct_video.compress_video(file_path, outputfile)
        elif selected_technique == "DCT-image":
            outputfile = "comp-DCT-image-output.jpg"
            dct_image.dct_image_compreser(file_path, outputfile)
            outputfilesize[0] = os.path.getsize(outputfile)
            # Disable decompression if DCT is used
            root.after(0, lambda: apply_button.config(text="Compress File", state="disabled"))
            root.after(0, lambda: output_label.config(text="DCT-image compression does not support decompression."))
        outputfilesize[0] = os.path.getsize(outputfile)
        # Only switch button to decompression if not DCT-image
        if selected_technique != "DCT-image":
            root.after(0, lambda: apply_button.config(text="Decompress File"))
            root.after(0, lambda: compression_menu.config(state="disabled"))

    elif mode == "decompress":
        if selected_technique == "huffman-txt":
            out = "decomp-huffman-txt-output.txt"
            huffman.huffman_decode(outputfile, "decomp-huffman-txt-output.txt")
        elif selected_technique == "lzw-txt":
            out = "decomp-lzw-txt-output.txt"
            lzw.lzw_decompress(outputfile, "decomp-lzw-txt-output.txt")
        elif selected_technique == "RLE-txt":
            out = "decomp-rle-txt-output.txt"
            RLE.decompress_file(outputfile, "decomp-rle-txt-output.txt")
        
        # Reset application after decompression
        root.after(0, reset_application)
        outputfilesize[0] = os.path.getsize(out)
        
    if outputfilesize[0]:
        size_mb = round(outputfilesize[0] / (1024 * 1024), 2)  # Convert to Megabytes for readability
        root.after(0, lambda: output_label.config(
            text=f"Output: {selected_technique} {mode}ion applied on file. Output file size: {size_mb} MB"))
    else:
        root.after(0, lambda: output_label.config(
            text=f"Output: {selected_technique} {mode}ion applied on file, but no output file found."))
        
    root.after(0, hide_loading)

upload_button = tk.Button(root, text="Upload File", command=upload_file)
upload_button.pack(pady=10)

file_label = tk.Label(root, text="No file selected")
file_label.pack()

# Dropdown for selecting compression technique
compression_var = tk.StringVar(value="None")
compression_techniques = ["None", "huffman-txt", "lzw-txt", "RLE-txt", "DCT-image","DCT-video"]
compression_menu = tk.OptionMenu(root, compression_var, *compression_techniques)
compression_menu.config(width=25)
compression_menu.pack(pady=10)
compression_label = tk.Label(root, text="Select a compression technique:")
compression_label.pack()

# Apply button (initially set to compression mode)
apply_button = tk.Button(root, text="Compress File", command=apply_technique, state="disabled")
apply_button.pack(pady=10)

# Loading label (hidden by default)
loading_label = tk.Label(root, text="", fg="blue")

# Label to display output
output_label = tk.Label(root, text="")
output_label.pack(pady=20)

root.mainloop()
