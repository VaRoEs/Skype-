Skype7 - Peer-to-Peer Video Call Application

Skype7 is a lightweight, browser-based P2P video calling application that enables direct video and audio communication between users using unique 4-digit IDs. No registration, no personal data collection, just instant connections.


✨ Features

🔗 Direct P2P Connections - WebRTC-based peer-to-peer communication without server-side media processing
🎯 Simple ID System - Each user gets a unique 4-digit ID for easy identification and calling
📱 Mobile-Friendly UI - Clean, responsive interface optimized for both desktop and mobile devices
🎥 Full Video Controls:

Camera toggle (on/off)
Microphone toggle (on/off)
Camera flip (front/back)
Picture-in-Picture mode toggle
⏱️ Call Timer - Track call duration in real-time
🔒 Optional HTTPS - Supports SSL/TLS encryption for secure signaling
💾 Local Storage - Your ID is stored locally, remains consistent between sessions
🔄 Auto-Reconnect - Handles network interruptions gracefully
📡 STUN Support - Uses Google's public STUN servers for NAT traversal
🚀 Quick Start

Prerequisites

Windows 10 or later
Python 3.7+
Modern browser (Chrome 100+, Firefox 110+, Edge 100+)
Working webcam and microphone
Network connectivity (for P2P connections)
Installation

Clone the repository:

bash
git clone https://github.com/yourusername/skype7.git
cd skype7

Run the server:

python skype+.py
Open your browser and navigate to:

http://YOUR_IP_ADDRESS:8080
(Replace YOUR_IP_ADDRESS with your machine's local IP)
🛠️ Advanced Setup

HTTPS Configuration (Recommended)

Generate SSL certificates for secure HTTPS connections:

bash
openssl req -x509 -newkey rsa:4096 -keyout keys.key -out keys.crt -days 365 -nodes
Place the keys.crt and keys.key files in the same directory as skype7.py. The server will automatically detect and enable HTTPS.

Network Requirements

For P2P connections to work:

STUN Server: Required for NAT traversal (included by default)
Open Ports: For direct connections, ensure UDP ports are not blocked
Firewall: Allow WebRTC traffic through your firewall
🎮 How to Use

Launch the application and note your unique 4-digit ID displayed on screen
Share your ID with the person you want to call
Enter their ID in the input field
Click "Call" to initiate a video call
Accept incoming calls when they appear on screen
Use on-screen controls during the call:

🎤 Mute/unmute microphone
📷 Toggle camera on/off
🔄 Switch between front/back camera
👁️ Show/hide picture-in-picture
📞 End call
🏗️ Architecture

text
┌─────────────┐    Signaling    ┌─────────────┐
│   Caller    │ ◄────────────►  │   Server    │
│  (Browser)  │                 │  (Python)   │
│             │                 │             │
│    P2P      │                 │    P2P      │
│   Media     │                 │   Media     │
│   Stream    │                 │   Stream    │
│      \      │                 │      /      │
│       \     │                 │     /       │
│        └────┼─────────────────┼────┘        │
│             │                 │             │
└─────────────┘                 └─────────────┘
      WebRTC                         WebRTC
Signaling Server: Python-based aiohttp server handling ID registration and message passing
WebRTC: Direct peer-to-peer media streaming between browsers
STUN: NAT traversal for establishing connections across networks
📁 Project Structure

text
skype7/
├── skype7.py          # Main server application
├── keys.crt          # SSL certificate (optional)
├── keys.key          # SSL private key (optional)
🔧 Dependencies

Python: 3.7+
aiohttp: 3.8.0+ - Async HTTP server
aiohttp-cors: 0.7.0+ - CORS support
🌐 Browser Compatibility

Browser	Version	Support
Chrome	100+	✅ Full
Firefox	110+	✅ Full
Edge	100+	✅ Full
Safari	16+	⚠️ Partial
🔐 Privacy & Security

✅ No Account Required - No registration or personal information
✅ End-to-End Encryption - WebRTC provides secure media streams
✅ No Data Storage - All data is ephemeral, nothing is stored
✅ Local IDs - IDs are generated and stored locally in your browser
✅ Optional HTTPS - Secure signaling channel available
🚧 Troubleshooting

Common Issues

"No camera/microphone found"

Ensure your device has working camera/microphone
Grant browser permissions for media access
Try restarting your browser
"Cannot connect to friend"

Verify both parties are on the same network or have internet access
Check firewall settings
Ensure both users have unique IDs
"Poor video quality"

Check your network speed
Reduce video resolution (modify width/height in getUserMedia)
Close other bandwidth-intensive applications
"Connection drops frequently"

Check network stability
Ensure STUN servers are reachable
Try using HTTPS for more stable connections
