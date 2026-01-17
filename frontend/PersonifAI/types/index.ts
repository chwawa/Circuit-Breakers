export interface Friend {
  id: string;
  name: string;
  personality?: string;
  imageUrl: string;
  isProcessing: boolean;
  createdAt: number;
}

export interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: number;
}