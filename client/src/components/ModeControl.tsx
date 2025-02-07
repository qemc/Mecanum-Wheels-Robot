import { useState, useEffect } from "react";
import useWebSocket from "../hooks/useWebSocket";
import { WS_BASE_URL } from "../config";

const ModeControl = () => {

  const {message, sendMessage} = useWebSocket(`${WS_BASE_URL}/mode`)
  const [mode, setMode] = useState<string|null>(null); 

  useEffect(() => {
    if (message) {
        const parsedMessage = JSON.parse(message); 
        setMode(parsedMessage.mode); 
    
  }}, [message]);

  const modeSetupAuto = () =>{
      sendMessage(
        JSON.stringify({
          mode: 'auto',
        })
      )
  }

  const modeSetupManual = () =>{
      sendMessage(
        JSON.stringify({
          mode:'manual'
        })
      )
  }

  return (
    <div>
      <button onClick={modeSetupAuto} disabled={mode == 'auto'}> Auto </button>
      <button onClick={modeSetupManual} disabled = {mode == 'manual'}> Manual</button>
      <div>MODE: {mode || "no data recieved yet"}</div>
    </div>
  );
};

export default ModeControl;