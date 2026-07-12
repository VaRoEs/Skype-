import asyncio
import json
import logging
import socket
import os
import ssl
from aiohttp import web
import aiohttp_cors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

signaling_store = {}

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

async def signaling_handler(request):
    try:
        data = await request.json()
        action = data.get('action')
        target = data.get('target')
        sender = data.get('sender')
        
        if action in ['offer', 'answer', 'candidate']:
            if target:
                if target not in signaling_store:
                    signaling_store[target] = []
                signaling_store[target].append({
                    'action': action,
                    'sender': sender,
                    'data': data.get('data')
                })
                return web.json_response({'status': 'ok'})
        elif action == 'get_messages':
            if target:
                messages = signaling_store.get(target, [])
                signaling_store[target] = []
                return web.json_response({'messages': messages})
        elif action == 'register':
            if target:
                signaling_store[target] = []
                return web.json_response({'status': 'registered'})
        return web.json_response({'error': 'Invalid action'})
    except Exception as e:
        return web.json_response({'error': str(e)})

async def index(request):
    my_ip = get_local_ip()
    protocol = "https" if os.path.exists('keys.crt') and os.path.exists('keys.key') else "http"
    
    html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>📱 Мобильный Скайп</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
        
        body {{
            background: #000; min-height: 100vh; height: 100dvh; display: flex; 
            justify-content: center; align-items: center; overflow: hidden;
        }}
        
        .app-container {{
            width: 100vw; height: 100vh; height: 100dvh;
            background: #0f172a; position: relative; overflow: hidden;
            display: flex; flex-direction: column;
        }}

        /* --- ГЛАВНОЕ МЕНЮ --- */
        #menuScreen {{
            padding: 30px 20px; text-align: center; height: 100%; display: flex; 
            flex-direction: column; align-items: center; justify-content: center;
            max-width: 500px; margin: 0 auto; width: 100%;
        }}
        h1 {{ color: #fff; font-size: 28px; margin-bottom: 30px; }}
        
        .id-box {{ background: #1e293b; padding: 25px; border-radius: 20px; margin-bottom: 25px; width: 100%; border: 1px solid #334155; }}
        .id-box p {{ color: #94a3b8; font-size: 14px; margin-bottom: 5px; }}
        .my-id {{ font-size: 48px; font-weight: bold; color: #38bdf8; letter-spacing: 5px; }}
        
        .status {{ padding: 12px; border-radius: 10px; color: #fff; font-weight: 500; margin-bottom: 25px; font-size: 15px; background: rgba(255,255,255,0.1); width: 100%; }}
        .status.success {{ background: rgba(34, 197, 94, 0.2); color: #4ade80; }}
        .status.warning {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; }}
        
        input {{
            width: 100%; padding: 20px; border: none; border-radius: 15px; font-size: 20px;
            background: #1e293b; color: white; text-align: center; margin-bottom: 15px; outline: none;
            border: 2px solid transparent; transition: 0.3s;
        }}
        input:focus {{ border-color: #38bdf8; }}
        input::placeholder {{ color: #475569; }}
        
        .btn-call {{
            width: 100%; padding: 20px; border: none; border-radius: 15px; font-size: 20px; font-weight: bold;
            background: #22c55e; color: white; cursor: pointer; transition: 0.2s;
        }}
        .btn-call:active {{ transform: scale(0.95); }}
        
        .incoming-box {{
            display: none; background: rgba(56, 189, 248, 0.1); border: 2px solid #38bdf8;
            padding: 20px; border-radius: 20px; margin-top: 30px; width: 100%; animation: pulse 1.5s infinite;
        }}
        .incoming-box.active {{ display: block; }}
        .incoming-box p {{ color: white; font-size: 18px; margin-bottom: 15px; }}
        .action-buttons {{ display: flex; gap: 10px; }}
        .btn-answer {{ background: #22c55e; flex: 1; padding: 15px; border-radius: 12px; border: none; color: white; font-size: 16px; font-weight: bold; cursor: pointer; }}
        .btn-reject {{ background: #ef4444; flex: 1; padding: 15px; border-radius: 12px; border: none; color: white; font-size: 16px; font-weight: bold; cursor: pointer; }}

        /* --- ЭКРАН ЗВОНКА --- */
        #callScreen {{
            display: none; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: #000;
        }}
        
        .video-remote {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
            object-fit: contain; z-index: 1; background: #111;
        }}
        
        .video-local {{
            display: none; 
            position: absolute; top: 80px; right: 20px; width: 110px; height: 160px;
            object-fit: cover; border-radius: 15px; background: #222; border: 2px solid rgba(255,255,255,0.3);
            box-shadow: 0 10px 25px rgba(0,0,0,0.5); transform: scaleX(-1); z-index: 5; transition: opacity 0.3s;
        }}

        .top-panel {{
            position: absolute; top: 30px; left: 0; right: 0; display: flex; justify-content: center;
            z-index: 10; transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .top-panel.hidden {{ opacity: 0; transform: translateY(-30px); pointer-events: none; }}
        
        .timer-box {{
            background: rgba(0,0,0,0.5); backdrop-filter: blur(10px); color: white;
            padding: 8px 20px; border-radius: 30px; font-size: 16px; font-weight: 500; letter-spacing: 1px;
        }}

        .controls-panel {{
            position: absolute; bottom: 40px; left: 0; right: 0;
            display: flex; justify-content: center; gap: 15px; align-items: center; padding: 0 10px;
            z-index: 10; transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .controls-panel.hidden {{ opacity: 0; transform: translateY(80px); pointer-events: none; }}
        
        .circle-btn {{
            width: 55px; height: 55px; border-radius: 50%; border: none; font-size: 22px;
            display: flex; align-items: center; justify-content: center; cursor: pointer;
            background: rgba(255,255,255,0.25); backdrop-filter: blur(15px); color: white; transition: 0.2s;
        }}
        .circle-btn:active {{ transform: scale(0.9); }}
        .circle-btn.off {{ background: #fff; color: #000; }}
        
        .btn-hangup {{ background: #ef4444; width: 70px; height: 70px; font-size: 32px; box-shadow: 0 10px 20px rgba(239, 68, 68, 0.4); margin: 0 5px; }}
        .btn-hangup:active {{ transform: scale(0.9); }}

        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.4); }}
            70% {{ box-shadow: 0 0 0 15px rgba(56, 189, 248, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(56, 189, 248, 0); }}
        }}
    </style>
</head>
<body>
    <div class="app-container">
        
        <div id="menuScreen">
            <h1>Видеочат</h1>
            
            <div class="id-box">
                <p>Твой постоянный ID:</p>
                <div class="my-id" id="myIdDisplay">0000</div>
            </div>
            
            <div class="status" id="status">🎤 Проверка камеры и микрофона...</div>
            
            <input type="text" id="remoteId" placeholder="ID друга (4 цифры)" maxlength="4" />
            <button class="btn-call" id="connectBtn">Позвонить</button>
            
            <div class="incoming-box" id="incomingCall">
                <p>📞 Входящий звонок от ID: <strong id="callerIdDisplay">...</strong></p>
                <div class="action-buttons">
                    <button class="btn-answer" id="answerBtn">Принять</button>
                    <button class="btn-reject" id="rejectBtn">Отклонить</button>
                </div>
            </div>
        </div>

        <div id="callScreen">
            <video id="remoteVideo" class="video-remote" autoplay playsinline></video>
            <video id="localVideo" class="video-local" autoplay muted playsinline></video>
            
            <div class="top-panel" id="topPanel">
                <div class="timer-box" id="timerDisplay">Подключение...</div>
            </div>
            
            <div class="controls-panel" id="controlsPanel">
                <button class="circle-btn" id="toggleMicBtn">🎤</button>
                <button class="circle-btn" id="toggleCamBtn">📷</button>
                <button class="circle-btn btn-hangup" id="hangupBtn">📞</button>
                <button class="circle-btn" id="flipCamBtn">🔄</button>
                <button class="circle-btn off" id="togglePipBtn">👁️</button>
            </div>
        </div>

    </div>
    
    <script>
        const CONFIG = {{
            serverUrl: window.location.origin,
            stunServers: [
                {{ urls: 'stun:stun.l.google.com:19302' }},
                {{ urls: 'stun:stun1.l.google.com:19302' }}
            ]
        }};
        
        let myId = localStorage.getItem('my_skype_id');
        if (!myId) {{
            myId = Math.floor(1000 + Math.random() * 9000).toString();
            localStorage.setItem('my_skype_id', myId);
        }}
        document.getElementById('myIdDisplay').textContent = myId;
        
        let localStream = null;
        let peerConnection = null;
        let remotePeerId = null;
        let incomingOffer = null;
        let incomingCaller = null;
        let iceCandidatesQueue = [];
        let wakeLock = null;
        
        let callTimer = null;
        let callSeconds = 0;
        let hideControlsTimeout = null;

        let isVideoEnabled = true; 
        let isAudioEnabled = true;
        let isPipVisible = false;
        let currentFacingMode = 'user'; 

        function updateStatus(msg, type = '') {{
            const el = document.getElementById('status');
            el.textContent = msg;
            el.className = 'status ' + type;
        }}

        function switchScreen(isCalling) {{
            if (isCalling) {{
                document.getElementById('menuScreen').style.display = 'none';
                document.getElementById('callScreen').style.display = 'block';
                showControls();
            }} else {{
                document.getElementById('menuScreen').style.display = 'flex';
                document.getElementById('callScreen').style.display = 'none';
                stopTimer();
                clearTimeout(hideControlsTimeout);
            }}
        }}

        function showControls() {{
            const controls = document.getElementById('controlsPanel');
            const top = document.getElementById('topPanel');
            controls.classList.remove('hidden');
            top.classList.remove('hidden');
            
            clearTimeout(hideControlsTimeout);
            hideControlsTimeout = setTimeout(() => {{
                controls.classList.add('hidden');
                top.classList.add('hidden');
            }}, 3500);
        }}

        document.getElementById('callScreen').addEventListener('mousemove', showControls);
        document.getElementById('callScreen').addEventListener('touchstart', showControls);
        document.getElementById('callScreen').addEventListener('click', showControls);

        function startTimer() {{
            callSeconds = 0;
            const timerEl = document.getElementById('timerDisplay');
            timerEl.textContent = "00:00";
            if (callTimer) clearInterval(callTimer);
            callTimer = setInterval(() => {{
                callSeconds++;
                const mins = String(Math.floor(callSeconds / 60)).padStart(2, '0');
                const secs = String(callSeconds % 60).padStart(2, '0');
                timerEl.textContent = `${{mins}}:${{secs}}`;
            }}, 1000);
        }}

        function stopTimer() {{
            if (callTimer) clearInterval(callTimer);
            document.getElementById('timerDisplay').textContent = "Подключение...";
        }}

        async function keepScreenOn() {{
            try {{ if ('wakeLock' in navigator) wakeLock = await navigator.wakeLock.request('screen'); }} catch (err) {{}}
        }}
        function allowScreenSleep() {{
            if (wakeLock !== null) {{ wakeLock.release(); wakeLock = null; }}
        }}

        async function startMedia() {{
            try {{
                localStream = await navigator.mediaDevices.getUserMedia({{
                    audio: {{ echoCancellation: true, noiseSuppression: true }},
                    video: {{ width: {{ ideal: 1280 }}, height: {{ ideal: 720 }}, facingMode: currentFacingMode }}
                }});
                
                isVideoEnabled = true;
                document.getElementById('localVideo').srcObject = localStream;
                updateStatus('✅ Готов к видеозвонкам', 'success');
            }} catch (e) {{
                console.warn("Нет камеры, пробуем только звук");
                try {{
                    localStream = await navigator.mediaDevices.getUserMedia({{ audio: true, video: false }});
                    isVideoEnabled = false;
                    document.getElementById('toggleCamBtn').style.display = 'none'; 
                    document.getElementById('flipCamBtn').style.display = 'none'; 
                    document.getElementById('togglePipBtn').style.display = 'none'; 
                    updateStatus('✅ Режим аудио', 'success');
                }} catch (err) {{
                    updateStatus('⚠️ Нет доступа к медиа', 'warning');
                }}
            }}
        }}

        async function flipCamera() {{
            if (!localStream) return;
            const oldVideoTrack = localStream.getVideoTracks()[0];
            if (oldVideoTrack) oldVideoTrack.stop();

            currentFacingMode = currentFacingMode === 'user' ? 'environment' : 'user';

            try {{
                const newStream = await navigator.mediaDevices.getUserMedia({{
                    video: {{ facingMode: currentFacingMode, width: {{ ideal: 1280 }}, height: {{ ideal: 720 }} }}
                }});

                const newVideoTrack = newStream.getVideoTracks()[0];
                newVideoTrack.enabled = isVideoEnabled; 

                localStream.removeTrack(oldVideoTrack);
                localStream.addTrack(newVideoTrack);
                document.getElementById('localVideo').srcObject = localStream;

                if (peerConnection) {{
                    const sender = peerConnection.getSenders().find(s => s.track && s.track.kind === 'video');
                    if (sender) sender.replaceTrack(newVideoTrack);
                }}

                document.getElementById('localVideo').style.transform = currentFacingMode === 'user' ? 'scaleX(-1)' : 'none';

            }} catch (e) {{
                console.error("Ошибка переворота камеры", e);
            }}
        }}

        document.getElementById('toggleMicBtn').onclick = (e) => {{
            e.stopPropagation();
            if (localStream && localStream.getAudioTracks().length > 0) {{
                isAudioEnabled = !isAudioEnabled;
                localStream.getAudioTracks()[0].enabled = isAudioEnabled;
                const btn = document.getElementById('toggleMicBtn');
                btn.classList.toggle('off', !isAudioEnabled);
                btn.textContent = isAudioEnabled ? '🎤' : '🔇';
            }}
            showControls();
        }};

        document.getElementById('toggleCamBtn').onclick = (e) => {{
            e.stopPropagation();
            if (localStream && localStream.getVideoTracks().length > 0) {{
                isVideoEnabled = !isVideoEnabled;
                localStream.getVideoTracks()[0].enabled = isVideoEnabled;
                const btn = document.getElementById('toggleCamBtn');
                btn.classList.toggle('off', !isVideoEnabled);
                btn.textContent = isVideoEnabled ? '📷' : '🚫';
            }}
            showControls();
        }};

        document.getElementById('flipCamBtn').onclick = (e) => {{
            e.stopPropagation();
            flipCamera();
            showControls();
        }};

        document.getElementById('togglePipBtn').onclick = (e) => {{
            e.stopPropagation();
            isPipVisible = !isPipVisible;
            const btn = document.getElementById('togglePipBtn');
            btn.classList.toggle('off', !isPipVisible);
            document.getElementById('localVideo').style.display = isPipVisible ? 'block' : 'none';
            showControls();
        }};

        async function register() {{
            await fetch(CONFIG.serverUrl + '/signaling', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ action: 'register', target: myId }})
            }});
            setInterval(getMessages, 1000);
        }}

        async function getMessages() {{
            try {{
                const res = await fetch(CONFIG.serverUrl + '/signaling', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ action: 'get_messages', target: myId }})
                }});
                const data = await res.json();
                if (data.messages) {{
                    for (let msg of data.messages) await handleMessage(msg);
                }}
            }} catch(e) {{}}
        }}

        async function handleMessage(msg) {{
            if (msg.action === 'offer') {{
                incomingOffer = msg.data;
                incomingCaller = msg.sender;
                document.getElementById('callerIdDisplay').textContent = incomingCaller;
                document.getElementById('incomingCall').classList.add('active');
                
            }} else if (msg.action === 'answer' && peerConnection) {{
                await peerConnection.setRemoteDescription(new RTCSessionDescription(msg.data));
                processIceQueue(); 
                
            }} else if (msg.action === 'candidate') {{
                if (peerConnection && peerConnection.remoteDescription) {{
                    peerConnection.addIceCandidate(new RTCIceCandidate(msg.data)).catch(console.error);
                }} else {{
                    iceCandidatesQueue.push(msg.data); 
                }}
            }}
        }}

        function processIceQueue() {{
            while (iceCandidatesQueue.length > 0) {{
                let cand = iceCandidatesQueue.shift();
                peerConnection.addIceCandidate(new RTCIceCandidate(cand)).catch(console.error);
            }}
        }}

        // --- ЛОГИКА WEBRTC С ИСПРАВЛЕНИЕМ ДЛЯ УСТРОЙСТВ БЕЗ КАМЕРЫ ---
        function createPeerConnection() {{
            peerConnection = new RTCPeerConnection({{ iceServers: CONFIG.stunServers }});
            
            if (localStream) {{
                // Добавляем наши треки (звук, или звук+видео)
                localStream.getTracks().forEach(t => peerConnection.addTrack(t, localStream));
                
                // ВОТ ОНО! Если у нас нет камеры (длина массива видео-треков равна 0),
                // мы принудительно говорим собеседнику: "Я готов ПРИНИМАТЬ видео от тебя!"
                if (localStream.getVideoTracks().length === 0) {{
                    peerConnection.addTransceiver('video', {{ direction: 'recvonly' }});
                }}
            }} else {{
                // Если нет вообще ничего (ни камеры, ни микрофона), все равно готовы смотреть и слушать
                peerConnection.addTransceiver('audio', {{ direction: 'recvonly' }});
                peerConnection.addTransceiver('video', {{ direction: 'recvonly' }});
            }}
            
            peerConnection.ontrack = e => {{
                const remoteVid = document.getElementById('remoteVideo');
                if (remoteVid.srcObject !== e.streams[0]) {{
                    remoteVid.srcObject = e.streams[0];
                }}
            }};
            
            peerConnection.onicecandidate = e => {{
                if (e.candidate && remotePeerId) {{
                    sendMessage('candidate', e.candidate, remotePeerId);
                }}
            }};

            peerConnection.onconnectionstatechange = () => {{
                const state = peerConnection.connectionState;
                if (state === 'connected') {{
                    keepScreenOn();
                    startTimer();
                }} else if (state === 'disconnected' || state === 'failed') {{
                    hangup();
                }}
            }};
        }}

        async function sendMessage(action, data, target) {{
            await fetch(CONFIG.serverUrl + '/signaling', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ action, data, target, sender: myId }})
            }}).catch(console.error);
        }}

        document.getElementById('connectBtn').onclick = async () => {{
            remotePeerId = document.getElementById('remoteId').value.trim();
            if (!remotePeerId || remotePeerId === myId || remotePeerId.length !== 4) {{
                return alert('Введи 4 цифры ID друга');
            }}
            
            iceCandidatesQueue = []; 
            switchScreen(true);
            
            createPeerConnection();
            const offer = await peerConnection.createOffer();
            await peerConnection.setLocalDescription(offer);
            await sendMessage('offer', offer, remotePeerId);
        }};

        document.getElementById('answerBtn').onclick = async () => {{
            document.getElementById('incomingCall').classList.remove('active');
            remotePeerId = incomingCaller;
            
            switchScreen(true);
            
            createPeerConnection();
            await peerConnection.setRemoteDescription(new RTCSessionDescription(incomingOffer));
            
            processIceQueue();

            const answer = await peerConnection.createAnswer();
            await peerConnection.setLocalDescription(answer);
            await sendMessage('answer', answer, remotePeerId);
        }};

        document.getElementById('rejectBtn').onclick = () => {{
            document.getElementById('incomingCall').classList.remove('active');
        }};

        function hangup() {{
            if (peerConnection) {{
                peerConnection.close();
                peerConnection = null;
            }}
            document.getElementById('remoteVideo').srcObject = null;
            iceCandidatesQueue = []; 
            allowScreenSleep();
            switchScreen(false);
        }}

        document.getElementById('hangupBtn').onclick = (e) => {{
            e.stopPropagation(); 
            hangup();
        }};

        async function init() {{
            await startMedia();
            await register();
        }}
        
        init();
    </script>
</body>
</html>
    """
    return web.Response(text=html, content_type='text/html')

async def main():
    app = web.Application()
    
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    
    app.router.add_get('/', index)
    app.router.add_post('/signaling', signaling_handler)
    
    for route in app.router.routes():
        cors.add(route)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    ssl_context = None
    protocol_name = "http"
    
    if os.path.exists('keys.crt') and os.path.exists('keys.key'):
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain('keys.crt', 'keys.key')
        protocol_name = "https"
    
    site = web.TCPSite(runner, '0.0.0.0', 8080, ssl_context=ssl_context)
    await site.start()
    
    my_ip = get_local_ip()
    
    print("\n" + "="*55)
    if ssl_context:
        print("🔒 МОБИЛЬНЫЙ СКАЙП ЗАПУЩЕН ПО ЗАЩИЩЕННОМУ HTTPS!")
    else:
        print("⚠️ МОБИЛЬНЫЙ СКАЙП ЗАПУЩЕН ПО HTTP (Сгенерируй ключи!)")
        
    print(f"🔗 Ссылка для друга: {protocol_name}://{my_ip}:8080")
    print("="*55 + "\n")
    
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\nОстановка сервера...")
        await runner.cleanup()

if __name__ == '__main__':
    asyncio.run(main())