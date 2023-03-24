

class AudioBufferProcessor extends AudioWorkletProcessor {
  // Set the buffer size to 2 seconds of audio data at 44100 Hz
  bufferSize = 8192;

  // Track the current buffer fill level
  _bytesWritten = 0;

  // Create a buffer of fixed size
  _buffer = new Float32Array(this.bufferSize);

  // Set the input and output channel count
  static get parameterDescriptors() {
    return [
      { name: 'inputChannelCount', defaultValue: 1 },
      { name: 'outputChannelCount', defaultValue: 1 },
    ];
  }

  // Reset the buffer when a new instance is created
  constructor() {
    super();
    this.initBuffer();
  }

  // Reset the buffer fill level
  initBuffer() {
    this._bytesWritten = 0;
  }

  // Check if the buffer is empty
  isBufferEmpty() {
    return this._bytesWritten === 0;
  }

  // Check if the buffer is full
  isBufferFull() {
    return this._bytesWritten === this.bufferSize;
  }

  // The main processing function
  process(inputs) {
    // Grab the audio data from the first input channel
    const inputChannelData = inputs[0][0];

    // Append the audio data to the buffer
    this.append(inputChannelData);

    // If the buffer is full, send the data to the main thread
    if (this.isBufferFull()) {
      this.flush();
    }

    // Continue processing
    return true;
  }

  // Append audio data to the buffer
  append(channelData) {
    if (!channelData) return;

    for (let i = 0; i < channelData.length; i++) {
      this._buffer[this._bytesWritten++] = channelData[i];
    }
  }

  // Send the contents of the buffer to the main thread
  flush() {
    this.port.postMessage(this._buffer);
    this.initBuffer();
  }
}

// Register the processor with the browser
registerProcessor('audio-buffer.worklet', AudioBufferProcessor);

// export {streamaudio, stopAudioStream};