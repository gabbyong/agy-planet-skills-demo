#!/usr/bin/env python3
"""
generate_narration_video.py
Synthesizes professional 3Blue1Brown-style voiceover narration calibrated to the 
exact visual scene transitions of Figure 1 (ALU Pipeline) in alu_figure1_storytelling.mp4,
and muxes them together into alu_figure1_narrated.mp4.
"""

import subprocess
import os
import wave
import struct

SCENES = [
    (0.2, "To delineate 100 million smallholder farms, we stack multi-temporal satellite passes, combining seasonal crops while removing clouds."),
    (8.2, "We partition into Level 13 S2 cells, using a 150-meter buffer to preserve boundary farms."),
    (15.2, "A multi-scale U-Net with five heads predicts ground semantics and pixel affinities for fields, wells, and trees."),
    (22.2, "BAT deduplication stitches overlapping tiles, while dagger removal prunes sharp neural spike artifacts."),
    (28.6, "Delivering clean cadastral parcels via S2 APIs.")
]

def synthesize_narration(total_duration=32.0, sample_rate=22050, temp_dir="/tmp/alu_narration"):
    os.makedirs(temp_dir, exist_ok=True)
    wav_segments = []
    
    print("1. Synthesizing voiceover clips with macOS 'say' (Daniel - 3B1B tone)...")
    for i, (t_start, text) in enumerate(SCENES):
        aiff_file = os.path.join(temp_dir, f"scene_{i}.aiff")
        wav_file = os.path.join(temp_dir, f"scene_{i}.wav")
        
        subprocess.run(["say", "-v", "Daniel", "-r", "205", "-o", aiff_file, text], check=True)
        subprocess.run(["afconvert", "-f", "WAVE", "-d", f"LEI16@{sample_rate}", aiff_file, wav_file], check=True)
        
        with wave.open(wav_file, "rb") as wf:
            frames = wf.readframes(wf.getnframes())
        wav_segments.append((t_start, frames))
    
    print("2. Assembling continuous 32.0s audio track...")
    total_samples = int(total_duration * sample_rate)
    master_buffer = bytearray(total_samples * 2)  # 16-bit mono
    
    for t_start, frames in wav_segments:
        start_sample = int(t_start * sample_rate)
        n_samples = len(frames) // 2
        end_sample = min(start_sample + n_samples, total_samples)
        valid_bytes = (end_sample - start_sample) * 2
        master_buffer[start_sample * 2 : start_sample * 2 + valid_bytes] = frames[:valid_bytes]
        
    master_wav = os.path.join(temp_dir, "master_narration.wav")
    master_m4a = os.path.join(temp_dir, "master_narration.m4a")
    
    with wave.open(master_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(master_buffer)
        
    subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", master_wav, master_m4a], check=True)
    return master_m4a

def mux_mp4_m4a(video_path, audio_path, output_path):
    print(f"3. Muxing video '{video_path}' and audio '{audio_path}' -> '{output_path}'...")
    with open(video_path, "rb") as f:
        vdata = f.read()
    with open(audio_path, "rb") as f:
        adata = f.read()

    def parse_atoms(data):
        atoms = {}
        offset = 0
        while offset < len(data):
            if offset + 8 > len(data): break
            size, name = struct.unpack(">I4s", data[offset:offset+8])
            name = name.decode("latin1", errors="ignore")
            hlen = 8
            if size == 1:
                size = struct.unpack(">Q", data[offset+8:offset+16])[0]
                hlen = 16
            elif size == 0:
                size = len(data) - offset
            atoms[name] = (offset, size, hlen)
            offset += size
        return atoms

    va = parse_atoms(vdata)
    aa = parse_atoms(adata)

    v_ftyp_off, v_ftyp_sz, _ = va["ftyp"]
    v_mdat_off, v_mdat_sz, v_mdat_hl = va["mdat"]
    v_moov_off, v_moov_sz, _ = va["moov"]

    a_mdat_off, a_mdat_sz, a_mdat_hl = aa["mdat"]
    a_moov_off, a_moov_sz, _ = aa["moov"]

    a_moov_data = adata[a_moov_off : a_moov_off + a_moov_sz]
    t_off = a_moov_data.find(b"trak")
    if t_off == -1:
        raise RuntimeError("No trak in audio moov")
    t_sz = struct.unpack(">I", a_moov_data[t_off-4:t_off])[0]
    audio_trak = bytearray(a_moov_data[t_off-4 : t_off-4+t_sz])

    # Update track ID in audio tkhd to 2
    tkhd_off = audio_trak.find(b"tkhd")
    if tkhd_off != -1:
        ver = audio_trak[tkhd_off + 4]
        track_id_pos = tkhd_off + (16 if ver == 0 else 24)
        struct.pack_into(">I", audio_trak, track_id_pos, 2)

    v_mdat_payload = vdata[v_mdat_off + v_mdat_hl : v_mdat_off + v_mdat_sz]
    a_mdat_payload = adata[a_mdat_off + a_mdat_hl : a_mdat_off + a_mdat_sz]

    merged_mdat_payload = v_mdat_payload + a_mdat_payload
    merged_mdat_header = struct.pack(">I4s", len(merged_mdat_payload) + 8, b"mdat")

    new_audio_payload_start = v_ftyp_sz + 8 + len(v_mdat_payload)
    orig_audio_payload_start = a_mdat_off + a_mdat_hl
    delta_audio = new_audio_payload_start - orig_audio_payload_start

    stco_off = audio_trak.find(b"stco")
    if stco_off != -1:
        entry_count = struct.unpack(">I", audio_trak[stco_off + 8 : stco_off + 12])[0]
        for i in range(entry_count):
            pos = stco_off + 12 + i * 4
            old_val = struct.unpack(">I", audio_trak[pos : pos + 4])[0]
            struct.pack_into(">I", audio_trak, pos, old_val + delta_audio)
    else:
        co64_off = audio_trak.find(b"co64")
        if co64_off != -1:
            entry_count = struct.unpack(">I", audio_trak[co64_off + 8 : co64_off + 12])[0]
            for i in range(entry_count):
                pos = co64_off + 12 + i * 8
                old_val = struct.unpack(">Q", audio_trak[pos : pos + 8])[0]
                struct.pack_into(">Q", audio_trak, pos, old_val + delta_audio)

    v_moov_data = bytearray(vdata[v_moov_off : v_moov_off + v_moov_sz])
    mvhd_off = v_moov_data.find(b"mvhd")
    if mvhd_off != -1:
        mvhd_sz = struct.unpack(">I", v_moov_data[mvhd_off-4 : mvhd_off])[0]
        struct.pack_into(">I", v_moov_data, mvhd_off - 4 + mvhd_sz - 4, 3)

    new_moov_data = v_moov_data + audio_trak
    struct.pack_into(">I", new_moov_data, 0, len(new_moov_data))

    ftyp_data = vdata[v_ftyp_off : v_ftyp_off + v_ftyp_sz]
    with open(output_path, "wb") as f:
        f.write(ftyp_data)
        f.write(merged_mdat_header)
        f.write(merged_mdat_payload)
        f.write(new_moov_data)

    print(f"Muxing complete! Output file saved to: {output_path}")

if __name__ == "__main__":
    audio_path = synthesize_narration()
    video_input = "alu_figure1_storytelling.mp4"
    video_output = "alu_figure1_narrated.mp4"
    mux_mp4_m4a(video_input, audio_path, video_output)
