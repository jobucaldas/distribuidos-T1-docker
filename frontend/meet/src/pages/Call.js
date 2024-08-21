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

const blobToBase64 = blob => {
  const reader = new FileReader();
  reader.readAsDataURL(blob);
  return new Promise(resolve => {
    reader.onloadend = () => {
      resolve(reader.result);
    };
  });
};

const Call = () => {
  const navigate = useNavigate();

  const [users, setUsers] = useState([])
  const [chatMsg, setChatMsg] = useState('');
  const [chatLog, setChatLog] = useState([{"user": "Mensagem do Sistema", "msg": "Carregando mensagens"}]);
  const [videos, setVideos] = useState([]); 

  // controls if media input is on or off
  const [playing, setPlaying] = useState(false);

  // controls the current stream value
  const [stream, setStream] = useState(null);
  
  // controls if audio/video is on or off (seperately from each other)
  const [audio, setAudio] = useState(true);
  const [video, setVideo] = useState(true);

  // chat
  useInterval(async () => {
    const msgs = [{"user": "Mensagem do Sistema", "msg": "Você entrou na chamada"}]

    await fetch("http://127.0.0.1:5000/get_chat/" + sessionStorage.getItem("callId"), 
      {method: 'GET',
      headers: {
        'Access-Control-Allow-Origin': '*',
      },
      crossDomain: true,
    })
    .then(response => response.json())
    .then(data => {
      if(data !== 401)
        data.forEach(msg => {
          msgs.push(msg)
        })
    })
    .catch((error) => { console.error('Error:', error) })

    setChatLog(msgs);
  }, 1000);

  // controls the video DOM element
  const webcamVideo = useRef();

  // get the user's media stream
  const startStream = async () => {
      let newStream = await navigator.mediaDevices
        .getUserMedia({
          video: { width: 640, height: 360, facingMode: "user" },
          audio: true,
        })
        .then((newStream) => {
          webcamVideo.current.srcObject = newStream;
          setStream(newStream);
        })

      setPlaying(true);
  };

  // get users
  useInterval(async () => {
    await fetch(
      "http://127.0.0.1:5000/get_users/" + sessionStorage.getItem("callId"), 
      {
        method: 'GET',
        headers: {
          'Access-Control-Allow-Origin': '*',
        },
        crossDomain: true
      }
    )
    .then(response => response.json())
    .then(data => {
      setUsers(data['users'])
    })
  }, 5000)

  // Video chat
  useInterval(() => {
    // Send video
    if(playing && video){
      var canvas = document.createElement("canvas");
      canvas.width = webcamVideo.current.videoWidth;
      canvas.height = webcamVideo.current.videoHeight;
      var contex = canvas.getContext("2d");
      contex.drawImage(webcamVideo.current, 0, 0, canvas.width, canvas.height);
      
      canvas.toBlob(async function(blob){
        let formData = new FormData()
        formData.append('frame', blob)

        await fetch(
          "http://127.0.0.1:5000/send_video/" + sessionStorage.getItem("callId") + "/" + sessionStorage.getItem("userId"), 
          {
            method: 'POST',
            headers: {
              'Access-Control-Allow-Origin': '*',
            },
            crossDomain: true,
            body: formData
          }
        )
      }, 'image/jpg', 0.80)
    }

    let tempVideo = []
    let len = users.length
    users.forEach(async (user) => {
      if(user === sessionStorage.getItem("userId")){
        len--
      } else{
        await fetch("http://127.0.0.1:5000/get_video/" + sessionStorage.getItem("callId") + "/" + user, 
          {method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          },
          crossDomain: true,
        })
        .then(response => response.blob())
        .then(blobToBase64)
        .then(res => {
          const base64String = res
            .replace('data:', '')
            .replace(/^.+,/, '')
          tempVideo.push({"key": user, "res": base64String})
          if(--len === 0){
            setVideos([...tempVideo])
          }
        })
        .catch((error) => {
          console.error('Error:', error);
        })
      }
    })
  }, 100);

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
            onClick={async ()=>{
              await fetch("http://127.0.0.1:5000/exit_call/" + sessionStorage.getItem("callId"), 
                {method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                crossDomain: true,
                body: JSON.stringify({
                    "uid": sessionStorage.getItem("userId")
                }),
                })
                .then(response => response.json())
                navigate("/call")
                navigate("/")
              }}>
          Sair
        </button>
        <>
          <h1>Call ID: {sessionStorage.getItem("callId")}</h1>
          <h1>Username: {sessionStorage.getItem("userName")}</h1>
        </>
      </div>
      <div class="grid grid-cols-4 min-h-screen">
        <div class="fixed w-3/4 h-screen col-span-4 md:col-span-3">
          <div class=" absolute py-20 px-8 flex align-center justify-center space-x-6 h-full w-full">
            {videos.map(video => (
              <img key={video.key} alt="video" src={"data:image/jpeg;base64," + video.res} class='w-full'/>
            ))}
          </div>
          <video class="fixed bottom-4 right-1/4 max-w-64" ref={webcamVideo} autoPlay playsInline></video> 
          <div class="flex flex-row space-x-4 mx-4 fixed bottom-4">
            <button
              class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5"
              onClick={playing ? stopStream : startStream}>
                {playing ?  "Desligar webcam" : "Iniciar webcam"}
            </button>
            {playing ?
              <>
                <button class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5" onClick={toggleAudio}>{audio?"Habilitar Som":"Desabilitar Som"}</button>
                <button class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5" onClick={toggleVideo}>{video?"Desabilitar Video":"Habilitar Video"}</button>
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
                    await fetch("http://127.0.0.1:5000/send_message/" + sessionStorage.getItem("callId") + "/" + sessionStorage.getItem("userName"), 
                      {method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                      },
                      crossDomain: true,
                      body: JSON.stringify({
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