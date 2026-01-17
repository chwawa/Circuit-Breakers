export class AudioStreamPlayer {
  private socket: WebSocket | null = null;
  private audioQueue: Blob[] = [];
  private isPlaying = false;
  private shouldStop = false;

  connect() {
    this.shouldStop = false;
    this.socket = new WebSocket("ws://100.66.83.158:8000/ws/audio");
    this.socket.binaryType = "arraybuffer";

    this.socket.onmessage = (event) => {
      // Binary audio
      if (event.data instanceof ArrayBuffer) {
        const blob = new Blob([event.data], { type: "audio/mpeg" });
        this.audioQueue.push(blob);
        this.playNext();
      }

      // JSON control message
      else {
        const data = JSON.parse(event.data);
        console.log("WS command:", data);
      }
    };

    this.socket.onclose = () => {
      console.log("Audio socket closed");
    };
  }

  private playNext() {
    if (this.isPlaying || this.audioQueue.length === 0 || this.shouldStop) {
      return;
    }

    const blob = this.audioQueue.shift()!;
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);

    this.isPlaying = true;

    audio.onended = () => {
      URL.revokeObjectURL(url);
      this.isPlaying = false;
      this.playNext(); // play next chunk
    };

    audio.onerror = () => {
      console.error("Audio playback error");
      this.isPlaying = false;
      this.playNext();
    };

    audio.play();
  }

  stop() {
    this.shouldStop = true;
    this.audioQueue = [];

    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}
