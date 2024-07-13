import React, { useState, useRef } from 'react';
import {useNavigate} from 'react-router-dom';

const Call = () => {
  const navigate = useNavigate();

  const [sendSuccess, setSendSuccess] = useState(false);

  const [chatMsg, setChatMsg] = useState('');
  const [chatLog, setChatLog] = useState([]);

  // controls if media input is on or off
  const [playing, setPlaying] = useState(false);

  // controls the current stream value
  const [stream, setStream] = useState(null);
  
  // controls if audio/video is on or off (seperately from each other)
  const [audio, setAudio] = useState(true);
  const [video, setVideo] = useState(true);

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
      <div class="flex flex-row space-x-2 items-center fixed left-4 top-4">
        <button
            class="text-white bg-gray-700 hover:bg-gray-800 focus:ring-4 focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5"
            onClick={() => {navigate("/")}}>
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
        <div className="col-start-4 relative h-screen justify-end content-end bg-slate-200">
          <h1 class="absolute z-20 w-full space-y-4 pt-6 p-4 bg-slate-200">Chat</h1>
          <div class="absolute bottom-0 flex flex-col space-y-4 m-4">
            <div class="bg-white rounded-lg shadow-md p-4">
              <div class="flex flex-row space-x-2 space-y-2">
                <div class="flex flex-col">
                  <span class="font-medium">Mensagem do Sistema</span>
                  <span class="text-gray-500 text-sm">Você entrou na chamada</span>
                </div>
              </div>
              {sendSuccess ?
                <div class="flex flex-row space-x-2 space-y-2">
                  <div class="flex flex-col">
                    <span class="font-medium">{sessionStorage.getItem("userName")}</span>
                    <span class="text-gray-500 text-sm">Você entrou na chamada</span>
                  </div>
                </div>
                :
                null
              }
            </div>
            <div className="flex flex-col z-10 bg-white rounded-lg shadow-md p-4">
              <input
                type="text"
                onChange={e => {setChatMsg(e.target.value)}}
                placeholder="Insira sua mensagem..."
                className="border border-gray-300 rounded-lg px-4 py-2"
              />
              <button
                onClick={
                  async () => {
                    await fetch("http://127.0.0.1:5000/send_text", 
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
                    .then(data => {
                      console.log('Success:', data);
                      setSendSuccess(true)
                    })
                    .catch((error) => {
                      console.error('Error:', error);
                    })
                  }
                }
                type="button"
                className="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 mt-2"
              >
                Enviar
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default Call;