import numpy as np
import scipy.signal

def get_a_weighting(f):
    """Calculate A-weighting attenuation in dB at frequency f."""
    f = np.asarray(f, dtype=float)
    # Avoid divide by zero for f = 0
    f = np.where(f == 0, 1e-6, f)
    
    f2 = f**2
    f4 = f**4
    
    # Standard IEC 61672-1 formula
    num = (12194**2) * f4
    den = (f2 + 20.6**2) * np.sqrt((f2 + 107.7**2) * (f2 + 737.9**2)) * (f2 + 12194**2)
    
    R_A = num / den
    A = 20 * np.log10(R_A) + 2.00
    return A

def compute_fft(signal, fs):
    """
    Compute FFT of a signal, apply Hanning window, and scale to RMS amplitude.
    Returns:
        freqs: array of frequencies
        rms_amplitudes: array of RMS amplitudes in physical units
    """
    N = len(signal)
    # Apply Hanning window
    window = np.hanning(N)
    windowed_signal = signal * window
    
    # Calculate coherent amplitude gain correction for Hanning window
    # Hanning window average is 0.5, so we need to multiply by 2.0 to restore amplitude.
    # To get RMS, we divide the peak amplitude by sqrt(2).
    # Combined factor: 2.0 / sqrt(2) = sqrt(2)
    window_correction = 1.0 / np.mean(window) # = 2.0 for hanning
    
    # Compute RFFT
    fft_vals = np.fft.rfft(windowed_signal)
    freqs = np.fft.rfftfreq(N, 1/fs)
    
    # Magnitude scaling:
    # rfft returns N/2 + 1 bins. The DC bin and Nyquist bin (if N is even) should not be multiplied by 2,
    # but for simplicity and since we care about LFG, we scale the bins.
    mags = np.abs(fft_vals) / N
    # Multiply by 2 because we discarded negative frequencies
    mags[1:-1] *= 2.0
    
    # Apply window correction to restore peak amplitude
    mags *= window_correction
    
    # Convert peak amplitude to RMS
    rms_amplitudes = mags / np.sqrt(2.0)
    
    return freqs, rms_amplitudes

def test_sine_wave():
    # Test with a 10 Hz sine wave, amplitude = 2.0 Pascal (RMS = 2 / sqrt(2) = 1.414 Pa)
    fs = 100.0  # sample rate of 100 Hz
    duration = 10.0 # 10 seconds
    t = np.arange(0, duration, 1/fs)
    freq = 10.0
    amp = 2.0
    
    signal = amp * np.sin(2 * np.pi * freq * t)
    
    freqs, rms_vals = compute_fft(signal, fs)
    
    # Find the peak
    peak_idx = np.argmax(rms_vals)
    peak_freq = freqs[peak_idx]
    peak_rms = rms_vals[peak_idx]
    
    expected_rms = amp / np.sqrt(2.0)
    print(f"Test Sine Wave (10 Hz, Amp {amp} Pa):")
    print(f"  Detected Peak Freq: {peak_freq:.2f} Hz (Expected: {freq:.2f} Hz)")
    print(f"  Detected RMS: {peak_rms:.4f} Pa (Expected: {expected_rms:.4f} Pa)")
    assert np.abs(peak_freq - freq) < 0.2, "Frequency mismatch"
    assert np.abs(peak_rms - expected_rms) < 0.05, "RMS amplitude mismatch"
    print("  -> PASS")

def test_a_weighting():
    # Test values for A-weighting:
    # 10 Hz: approx -70.4 dB
    # 100 Hz: approx -19.1 dB
    # 1000 Hz: 0.0 dB
    # 10000 Hz: -2.5 dB
    print("Test A-weighting values:")
    for f, expected in [(10, -70.4), (100, -19.1), (1000, 0.0), (10000, -2.5)]:
        a_val = get_a_weighting(f)
        print(f"  {f} Hz: {a_val:.1f} dB (Expected: {expected:.1f} dB)")
        assert np.abs(a_val - expected) < 1.0, f"A-weighting mismatch at {f} Hz"
    print("  -> PASS")

if __name__ == "__main__":
    test_sine_wave()
    test_a_weighting()
