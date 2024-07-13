import React, { useState, useEffect, useRef } from 'react';
import {useNavigate} from 'react-router-dom';
 
function useInterval(callback, delay) {
  const savedCallback = useRef();
 
  // Remember the latest callback.
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);
 
  // Set up the interval.
  useEffect(() => {
    function tick() {
      savedCallback.current();
    }
    if (delay !== null) {
      let id = setInterval(tick, delay);
      return () => clearInterval(id);
    }
  }, [delay]);
}

const Call = () => {
  const navigate = useNavigate();

  const [chatMsg, setChatMsg] = useState('');
  const [chatLog, setChatLog] = useState([{"user": "Mensagem do Sistema", "msg": "Carregando mensagens"}]);

  // controls if media input is on or off
  const [playing, setPlaying] = useState(false);

  // controls the current stream value
  const [stream, setStream] = useState(null);
  
  // controls if audio/video is on or off (seperately from each other)
  const [audio, setAudio] = useState(true);
  const [video, setVideo] = useState(true);

  useInterval(async () => {
    const msgs = [{"user": "Mensagem do Sistema", "msg": "Você entrou na chamada"}]
    const response = await fetch("http://127.0.0.1:5000/get_chat", 
      {method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
      crossDomain: true,
      body: JSON.stringify({
        "id": sessionStorage.getItem("callId"), 
        "user": sessionStorage.getItem("userName")
      }),
    })
    .then(response => response.json())
    .then(data => {
      console.log(data)
      data.forEach(msg => {
        msgs.push(msg)
      })
      
      console.log(msgs)
    })
    .catch((error) => {
      console.error('Error:', error);
    })
    
    setChatLog(msgs);
  }, 3000);

  // controls the video DOM element
  const webcamVideo = useRef();

  // get the user's media stream
  const startStream = async () => {
      let newStream = await navigator.mediaDevices
        .getUserMedia({
          video: { width: 1280, height: 720, facingMode: "user" },
          audio: true,
        })
        .then((newStream) => {
          webcamVideo.current.srcObject = newStream;
          setStream(newStream);
        });

      
      await fetch("http://127.0.0.1:5000/send_frame", 
        {method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
        crossDomain: true,
        body: JSON.stringify({
          "id": sessionStorage.getItem("callId"), 
          "user": sessionStorage.getItem("userName"),
          "frame": stream.getVideoTracks()[0]
        }),
      })
      .then(response => response.json())
      .then(data => {
        console.log('Data:', data);
      })
      .catch((error) => {
        console.error('Error:', error);
      })

      setPlaying(true);
  };

  // stops the user's media stream
  const stopStream = () => {
      stream.getTracks().forEach((track) => track.stop());

      setPlaying(false);
  };
  
  // enable/disable audio tracks in the media stream
  const toggleAudio = () => {
      setAudio(!audio);
      stream.getAudioTracks()[0].enabled = audio;
  };

  // enable/disable video tracks in the media stream
  const toggleVideo = () => {
      setVideo(!video);
      stream.getVideoTracks()[0].enabled = !video;
  };

  return (
    <>
      <div class="flex flex-row space-x-2 items-center fixed left-4 top-4 z-30">
        <button
            type="button"
            class="text-white bg-gray-700 hover:bg-gray-800 focus:ring-4 focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5"
            onClick={()=>{navigate("/")}}>
          Sair
        </button>
        <>
          <h1>Call ID: {sessionStorage.getItem("callId")}</h1>
          <h1>Username: {sessionStorage.getItem("userName")}</h1>
        </>
      </div>
      <div class="grid grid-cols-4 min-h-screen">
        <div class="relative col-span-4 md:col-span-3">
          <video class="absolute bottom-4 right-4 max-w-64" ref={webcamVideo} autoPlay playsInline></video>
          <div class="flex flex-row space-x-4 mx-4 fixed bottom-4">
            <button
              class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5"
              onClick={playing ? stopStream : startStream}>
                {playing ?  "Desligar webcam" : "Iniciar webcam"}
            </button>
            {playing ?
              <>
                <button class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5" onClick={toggleAudio}>Habilitar Som</button>
                <button class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5" onClick={toggleVideo}>Habilitar Video</button>
              </>
              :
              null
            }
          </div>
        </div>
        <div className="relative flex flex-col col-start-4 min-h-screen w-full justify-end content-end bg-slate-200">
          <div class="w-full">
            <div class="flex flex-col space-y-4 p-4 bg-slate-200">
              {chatLog.map(message => (
                  <div class="bg-white rounded-lg shadow-md p-4">
                    <div class="flex flex-row space-x-2 space-y-2">
                      <div class="flex flex-col">
                        <span class="font-medium">{message.user}</span>
                        <span class="text-gray-500 text-sm">{message.msg}</span>
                      </div>
                    </div>
                  </div>
                )
              )}
            </div>
          </div>
          <div class="sticky bottom-4 right-0 w-full z-10 screen-x-0">
            <div>
              <form class="flex flex-col bg-white rounded-lg shadow-md p-4 m-4 mb-0" onSubmit={
                async event => {
                    event.preventDefault();
                    await fetch("http://127.0.0.1:5000/send_message", 
                      {method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                      },
                      crossDomain: true,
                      body: JSON.stringify({
                        "id": sessionStorage.getItem("callId"), 
                        "user": sessionStorage.getItem("userName"),
                        "msg": chatMsg
                      }),
                    })
                    .then(response => response.json())
                    .catch((error) => {
                      console.error('Error:', error);
                    })

                    setChatMsg('')
                    const tempMsg = chatLog
                    tempMsg.push({
                      "user": sessionStorage.getItem("userName"),
                      "msg": chatMsg
                    })

                    setChatLog(tempMsg);
                  }
                }>
                <input
                  type="text"
                  value={chatMsg}
                  onChange={e => {setChatMsg(e.target.value)}}
                  placeholder="Insira sua mensagem..."
                  className="border border-gray-300 rounded-lg px-4 py-2"
                />
                <button
                  type="submit"
                  className="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 mt-2"
                >
                  Enviar
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default Call;