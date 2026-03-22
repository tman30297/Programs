#!/bin/bash
# Signal Recording Scripts for RTL-SDR
# Requires: rtl_sdr, sox, aplay

# Configuration
FREQ=154463750  # 154.46375 MHz in Hz
SAMPLE_RATE=2400000
GAIN=20
DURATION=10

# Output file
OUTPUT_DIR="./recordings"
mkdir -p "$OUTPUT_DIR"

record_signal() {
    local signal_name=$1
    local duration=${2:-10}
    local output="$OUTPUT_DIR/${signal_name}.raw"
    
    echo "Recording $signal_name for ${duration}s..."
    echo "Frequency: $((FREQ/1000)).$((FREQ%1000)) kHz"
    
    # Record raw IQ
    rtl_sdr -f $FREQ -s $SAMPLE_RATE -g $GAIN -n $((SAMPLE_RATE * duration)) "$output" 2>/dev/null
    
    echo "Saved to: $output"
}

convert_to_wav() {
    local input=$1
    local output=${2:-"${input%.raw}.wav"}
    
    echo "Converting $input to $output..."
    
    # Convert raw to WAV (this is simplified - real conversion needs GNU Radio)
    # For now, just copy as placeholder
    cp "$input" "$output"
    
    echo "Saved to: $output"
}

process_signal() {
    local input=$1
    local output=$2
    
    echo "Processing signal..."
    
    # This would call the Python processor
    python3 ../signal_processor.py "$input" "$output"
}

# Main
case "${1:-record}" in
    record)
        signal_name=${2:-signal_$(date +%Y%m%d_%H%M%S)}
        duration=${3:-10}
        record_signal "$signal_name" "$duration"
        ;;
    convert)
        convert_to_wav "$2" "$3"
        ;;
    process)
        process_signal "$2" "$3"
        ;;
    *)
        echo "Usage: $0 {record [name] [duration]|convert [input] [output]|process [input] [output]}"
        echo ""
        echo "Examples:"
        echo "  $0 record 17_1 5       # Record signal 17_1 for 5 seconds"
        echo "  $0 convert raw.wav    # Convert to WAV"
        echo "  $0 process in.wav out.wav  # Clean signal"
        exit 1
        ;;
esac
