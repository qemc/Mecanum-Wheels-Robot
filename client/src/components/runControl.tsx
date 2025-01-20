import { useState, useEffect } from "react";
import useWebSocket from "../hooks/useWebSocket";

const RunControl = () => {

  const {message, sendMessage} = useWebSocket("ws://localhost:8000/runPick")
  const [status, setStatus] = useState<string|null>(null); //mode from server
  const [startPickingProcess, setPickingProcess] = useState<boolean|null>(null);



  useEffect(() => {
    if (message) {
      try {
        const parsedMessage = typeof message === 'string' ? JSON.parse(message) : message;
        setStatus(parsedMessage.status);
        setPickingProcess(parsedMessage.start_picking_process) 
          } catch (error) {
        console.error('Failed to parse message:', error);
      }
    }
  }, [message]);

  const startPickingProcessFun = () =>{

      sendMessage(
        JSON.stringify({
          start_picking_process: true,
        })
      )
  }

  const stopPickingProcessFun = () =>{
    
      sendMessage(
        JSON.stringify({
          start_picking_process: false
        })
      )
  }

  return (
    <div>
      <button onClick={startPickingProcessFun} disabled={startPickingProcess == true}> Start </button>
      <button onClick={stopPickingProcessFun} disabled = {startPickingProcess == false}> Stop</button>

      <div>Picking Status: {status || "no data recieved yet"}</div>
    </div>
  );
};

export default RunControl;