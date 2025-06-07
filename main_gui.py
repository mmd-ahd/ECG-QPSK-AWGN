import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np 
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import os 

# Importing custom functions we made
from simulation_functions.get_ecg_segment_wfdb import get_ecg_segment_wfdb
from simulation_functions.estimate_bandwidth import estimate_bandwidth
from simulation_functions.resample_signal import resample_signal
from simulation_functions.quantize_signal import quantize_signal
from simulation_functions.qpsk_modulate import qpsk_modulate
from simulation_functions.add_awgn import add_awgn
from simulation_functions.qpsk_demodulate import qpsk_demodulate
from simulation_functions.reconstruct_signal_from_bits import reconstruct_signal_from_bits
from simulation_functions.calculate_ber import calculate_ber


class ECGSimApp:
    def __init__(self, master):
        self.master = master
        master.title("ECG Signal Transmission Simulator")
        master.geometry("1080x800") 

        self.style = ttk.Style()
        self.style.theme_use('clam') 

        control_frame = ttk.LabelFrame(master, text="Simulation Controls", padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        results_frame = ttk.LabelFrame(master, text="Results", padding="10")
        results_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        plot_frame = ttk.Frame(master, padding="5")
        plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        default_record_path = "s0379lre"
        
        ttk.Label(control_frame, text="WFDB Record Path/Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.wfdb_record_var = tk.StringVar(value=default_record_path) 
        ttk.Entry(control_frame, textvariable=self.wfdb_record_var, width=40).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(control_frame, text="WFDB Channel Index:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.wfdb_channel_var = tk.StringVar(value="0") 
        ttk.Entry(control_frame, textvariable=self.wfdb_channel_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(control_frame, text="ECG Segment Duration (s):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.duration_var = tk.StringVar(value="3") 
        ttk.Entry(control_frame, textvariable=self.duration_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(control_frame, text="System Sampling Rate (Hz):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.fs_system_var = tk.StringVar(value="250") 
        ttk.Entry(control_frame, textvariable=self.fs_system_var, width=10).grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(control_frame, text="Quantization Bits:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.quant_bits_var = tk.StringVar(value="8") 
        ttk.Entry(control_frame, textvariable=self.quant_bits_var, width=10).grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(control_frame, text="SNR (dB):").grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        self.snr_db_var = tk.StringVar(value="10")
        ttk.Entry(control_frame, textvariable=self.snr_db_var, width=10).grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)
        
        run_button = ttk.Button(control_frame, text="Run Simulation", command=self.run_simulation)
        run_button.grid(row=6, column=0, columnspan=2, pady=10)

        self.ber_label = ttk.Label(results_frame, text="BER: -")
        self.ber_label.pack(side=tk.LEFT, padx=10)
        self.status_label = ttk.Label(results_frame, text="Status: Idle", foreground="blue") 
        self.status_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.fig = Figure(figsize=(10, 7), dpi=100) 
        self.ax1_ecg = self.fig.add_subplot(211) 
        self.ax2_qpsk = self.fig.add_subplot(212) 

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        self.toolbar.update()

    def run_simulation(self):
        try:
            wfdb_record = self.wfdb_record_var.get()
            wfdb_channel = int(self.wfdb_channel_var.get())
            duration = float(self.duration_var.get())
            fs_system = float(self.fs_system_var.get())
            quant_bits = int(self.quant_bits_var.get())
            snr_db = float(self.snr_db_var.get())

            if not wfdb_record: messagebox.showerror("Input Error", "WFDB Record Path/Name cannot be empty."); return
            if wfdb_channel < 0: messagebox.showerror("Input Error", "WFDB Channel Index must be non-negative."); return
            if duration <= 0 : messagebox.showerror("Input Error", "Duration must be positive."); return
            if fs_system <= 0: messagebox.showerror("Input Error", "System Sampling Rate must be positive."); return
            if not 1 <= quant_bits <= 16: messagebox.showerror("Input Error", "Quantization Bits must be between 1 and 16."); return

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numerical values for channel index, duration, sampling rate, quantization bits, and SNR.")
            return

        self.status_label.config(text="Status: Running...", foreground="orange")
        self.master.update_idletasks() 
        current_warnings = []

        ecg_base_segment, time_base, fs_base, wfdb_err = get_ecg_segment_wfdb(wfdb_record, wfdb_channel, duration)
        if wfdb_err:
            messagebox.showerror("WFDB Error", wfdb_err)
            self.status_label.config(text=f"Status: Error - {wfdb_err}", foreground="red"); return
        if len(ecg_base_segment) == 0:
            messagebox.showerror("ECG Error", "Failed to load ECG segment from WFDB record.")
            self.status_label.config(text="Status: Error - Failed to load ECG.", foreground="red"); return

        B_ecg_base = estimate_bandwidth(ecg_base_segment, fs_base)
        nyquist_rate_ecg = 2 * B_ecg_base
        if fs_system < nyquist_rate_ecg:
            warn_msg = (f"Warning: System fs ({fs_system:.1f} Hz) < Nyquist ({nyquist_rate_ecg:.1f} Hz) for ECG BW ({B_ecg_base:.1f} Hz). Aliasing likely.")
            current_warnings.append(warn_msg); print(warn_msg)

        ecg_to_process, time_system = resample_signal(ecg_base_segment, fs_base, fs_system, duration)
        if len(ecg_to_process) == 0:
            err_msg = f"Resampling to {fs_system} Hz failed. Input signal might be too short or fs_system too low."
            messagebox.showerror("Resampling Error", err_msg)
            self.status_label.config(text=f"Status: Error - {err_msg}", foreground="red"); return

        original_bitstream, _, q_min, q_max, q_step = quantize_signal(ecg_to_process, quant_bits)
        if not original_bitstream and len(ecg_to_process)>0 : # Check for empty bitstream
            err_msg = "Quantization failed. Check signal or quant_bits."
            messagebox.showerror("Quantization Error", err_msg)
            self.status_label.config(text=f"Status: Error - {err_msg}", foreground="red"); return

        qpsk_symbols, effective_original_bitstream = qpsk_modulate(original_bitstream)
        if len(effective_original_bitstream) == 0 and len(original_bitstream) > 0:
            err_msg = "Modulation failed: Not enough bits for a QPSK symbol."
            messagebox.showerror("Modulation Error", err_msg)
            self.status_label.config(text=f"Status: Error - {err_msg}", foreground="red"); return
        if len(qpsk_symbols) == 0 and len(original_bitstream) > 1 : 
             err_msg = "QPSK modulation resulted in no symbols. Check bitstream."
             messagebox.showerror("Modulation Error", err_msg)
             self.status_label.config(text=f"Status: Error - {err_msg}", foreground="red"); return

        noisy_symbols = add_awgn(qpsk_symbols, snr_db)
        received_bitstream = qpsk_demodulate(noisy_symbols)
        reconstructed_ecg = reconstruct_signal_from_bits(received_bitstream, quant_bits, q_min, q_max, q_step)

        ber, num_errors, total_bits = calculate_ber(effective_original_bitstream, received_bitstream)
        if total_bits > 0:
            self.ber_label.config(text=f"BER: {ber:.2e} ({num_errors}/{total_bits} errs)")
        else:
            self.ber_label.config(text="BER: N/A (0 bits tx)")

        if current_warnings:
            self.status_label.config(text="Status: Completed with warnings. " + "; ".join(current_warnings), foreground="#FF8C00") 
        else:
            self.status_label.config(text="Status: Simulation Completed Successfully!", foreground="green")

        self.ax1_ecg.clear()
        self.ax1_ecg.plot(time_system, ecg_to_process, label="Original ECG", color='blue', alpha=0.7)
        if len(reconstructed_ecg) > 0 and not np.all(np.isnan(reconstructed_ecg)): # Check for NaNs from reconstruction
            valid_reconstructed_indices = ~np.isnan(reconstructed_ecg)
            if np.any(valid_reconstructed_indices):
                if len(reconstructed_ecg) == len(time_system):
                    self.ax1_ecg.plot(time_system[valid_reconstructed_indices], reconstructed_ecg[valid_reconstructed_indices], label=f"Reconstructed ECG (SNR: {snr_db} dB)", color='red', linestyle=':')
                else: 
                    shorter_len = min(len(reconstructed_ecg), len(time_system))
                    valid_indices_short = valid_reconstructed_indices[:shorter_len]
                    self.ax1_ecg.plot(time_system[:shorter_len][valid_indices_short], reconstructed_ecg[:shorter_len][valid_indices_short], label=f"Reconstructed ECG (SNR: {snr_db} dB) - Partial", color='orange', linestyle=':')
                    current_warnings.append("Plot length/NaNs in reconstructed ECG.")

        self.ax1_ecg.set_title("Original vs. Reconstructed ECG Signal")
        self.ax1_ecg.set_xlabel("Time (s)"); self.ax1_ecg.set_ylabel("Amplitude")
        self.ax1_ecg.legend(loc='upper right'); self.ax1_ecg.grid(True)

        self.ax2_qpsk.clear()
        if len(qpsk_symbols) > 0:
             self.ax2_qpsk.scatter(np.real(qpsk_symbols), np.imag(qpsk_symbols), marker='o', color='blue', label='Tx Symbols', s=30, alpha=0.7, zorder=3)
        if len(noisy_symbols) > 0:
            self.ax2_qpsk.scatter(np.real(noisy_symbols), np.imag(noisy_symbols), marker='x', color='red', label='Rx Noisy Symbols', s=15, alpha=0.5, zorder=2)
        
        ideal_constellation = np.array([(1+1j)/np.sqrt(2), (-1+1j)/np.sqrt(2), (-1-1j)/np.sqrt(2), (1-1j)/np.sqrt(2)])
        self.ax2_qpsk.scatter(np.real(ideal_constellation), np.imag(ideal_constellation), marker='s', label='Ideal', s=80, facecolors='none', edgecolors='black', zorder=1)

        self.ax2_qpsk.set_title(f"QPSK Constellation (SNR: {snr_db} dB)")
        self.ax2_qpsk.set_xlabel("In-Phase (I)"); self.ax2_qpsk.set_ylabel("Quadrature (Q)")
        self.ax2_qpsk.axhline(0, color='black', lw=0.5); self.ax2_qpsk.axvline(0, color='black', lw=0.5)
        plot_limit = 1.5 
        self.ax2_qpsk.set_xlim([-plot_limit, plot_limit]); self.ax2_qpsk.set_ylim([-plot_limit, plot_limit])
        self.ax2_qpsk.set_aspect('equal', adjustable='box')
        
        self.fig.tight_layout(pad=3.0) 
        self.canvas.draw()

def create_dummy_wfdb_files(dummy_record_stem):
    sample_data_dir = os.path.dirname(dummy_record_stem)
    if not os.path.exists(sample_data_dir):
        try:
            os.makedirs(sample_data_dir, exist_ok=True) 
        except Exception as e:
            print(f"Could not create directory {sample_data_dir}: {e}")
            return False # Indicate failure

    if not os.path.exists(dummy_record_stem + ".hea") or not os.path.exists(dummy_record_stem + ".dat"):
        try:
            with open(dummy_record_stem + ".hea", "w") as f:
                f.write("00001_lr 2 100 3000 0:0:0 0:0:0\n") 
                f.write("00001_lr.dat 212+0 100 0 0 0 I\n")   
                f.write("00001_lr.dat 212+0 100 0 0 0 II\n")   
            
            num_samples = 3000 
            time_dummy = np.linspace(0, 30, num_samples, endpoint=False)

            signal_ch1 = (np.sin(2 * np.pi * 1 * time_dummy) + 0.5 * np.sin(2 * np.pi * 10 * time_dummy)) * 5 
            signal_ch2 = (np.cos(2 * np.pi * 1 * time_dummy) + 0.3 * np.sin(2 * np.pi * 15 * time_dummy)) * 4 

            adc_ch1 = (signal_ch1 * 100).astype(np.int16) 
            adc_ch2 = (signal_ch2 * 100).astype(np.int16)

            dat_data = np.column_stack((adc_ch1, adc_ch2)) 

            dat_data.tofile(dummy_record_stem + ".dat")
            print(f"Created dummy WFDB record at: {dummy_record_stem}")
            print("NOTE: This is a DUMMY record for basic GUI testing. Use REAL WFDB data for actual simulation.")
            return True
        except Exception as e:
            print(f"Could not create dummy WFDB files at {dummy_record_stem}: {e}")
            return False
    return True # Files already exist

def main():
    dummy_record_stem = os.path.join("sample_data", "ptb-xl", "records100", "00000", "00001_lr").replace("\\","/")
    create_dummy_wfdb_files(dummy_record_stem)

    root = tk.Tk()
    app = ECGSimApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
