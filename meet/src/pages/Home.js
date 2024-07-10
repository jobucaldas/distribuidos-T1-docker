import { useNavigate } from 'react-router-dom';
import './Home.css';
import { useState } from 'react';

export default function Home() {
    const navigate = useNavigate();
    const [userName, setUserName] = useState('');
    const [chosenId, setChosenId] = useState('');
    const [clicked, setClicked] = useState(false);

    function EnterCall(){
        if(userName.length < 3){
            setClicked(true);
        } else{
            sessionStorage.setItem("userName", userName);
            sessionStorage.setItem("callId", chosenId);
            navigate("/call")
        }
    }

    function StartCall(){
        if(userName.length < 3){
            setClicked(true);
        } else{
            sessionStorage.setItem("userName", userName);
            sessionStorage.setItem("callId", (Math.floor(Math.random() * (9999 - 1 + 1)) + 1));
            navigate("/call")
        }
    }

    return (
        <div className="Home" class="flex flex-col justify-center items-center h-screen">
            <h1 class="text-lg font-medium text-gray-900 mb-6">ZMQ Meeting</h1>
            <div class='pb-6'>
                <label for="user_name" class="block mb-2 text-sm font-medium text-gray-900">Nickname</label>
                <input type="text" onChange={e => {setUserName(e.target.value)}} id="call_id" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5" />
                {
                    userName.length < 3 && clicked ?
                    <p class="text-red-500">O nickname deve ter no mínimo 3 caracteres</p> : null
                }
            </div>
            <div class="flex flex-row max-w-120">
                <div class="flex flex-col justify-center items-center">
                    <button type="button"
                        onClick={StartCall}
                        class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5">
                        Nova Chamada
                    </button>
                </div>
                <div class="flex flex-col justify-center items-center">
                    <p class="p-2 m-4 border-r-2 border-l-2">Ou</p>
                </div>
                <div class="flex flex-col justify-center items-center">
                    <div class='pb-6'>
                        <label for="call_id" class="block mb-2 text-sm font-medium text-gray-900">ID da Chamada</label>
                        <input type="number" onChange={e => {setChosenId(e.target.value)}} id="call_id" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5" />
                    </div>
                    <button type="button"
                        onClick={EnterCall}
                        class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5">
                        Conectar a Chamada
                    </button>
                </div>
            </div>
        </div>
    );
}