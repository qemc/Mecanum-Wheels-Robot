import { useState, useEffect } from "react";
import useWebSocket from "../hooks/useWebSocket";
import { WS_BASE_URL } from "../config";


interface ForkliftState {
  command_up: boolean;
  command_down: boolean;
  status: string;
  zero: boolean;
}

interface ForkliftCommand {
  command_up: boolean;
  command_down: boolean;
  zero: boolean;
}

const Forklift = () => {

  const { message, sendMessage } = useWebSocket(`${WS_BASE_URL}/forklift`);
  
  const [state, setState] = useState<ForkliftState>({
    command_up: false,
    command_down: false,
    status: "",
    zero: false
  });

  useEffect(() => {
    if (message) {
      try {
        const parsedMessage = typeof message === 'string' ? JSON.parse(message) : message;
        setState(parsedMessage);
      } catch (error) {
        console.error('Failed to parse message:', error);
      }
    }
  }, [message]);

  const sendCommand = (command: ForkliftCommand) => {
    
      sendMessage(JSON.stringify(command));
  };

  const forkliftUp = () => {
    sendCommand({
      'command_up': true,
      'command_down': false,
      'zero': false,
    });
  };

  const forkliftDown = () => {
    sendCommand({
      'command_up': false,
      'command_down': true,
      'zero': false,
    });
  };

  const forkliftZero = () => {
    sendCommand({
      'command_up': false,
      'command_down': false,
      'zero': true,
    });
  };

  const isDisabled = state.command_up || state.command_down || state.zero;

  return (
    <div className="forklift-control">
     
      
      <div className="button-group">
        <button 
          onClick={forkliftUp} 
          disabled={isDisabled}
          className={state.command_up ? 'active' : ''}
        >
          Up
        </button>
        
        <button 
          onClick={forkliftDown} 
          disabled={isDisabled}
          className={state.command_down ? 'active' : ''}
        >
          Down
        </button>
        
        <button 
          onClick={forkliftZero} 
          disabled={isDisabled}
          className={state.zero ? 'active' : ''}
        >
          Zero
        </button>
      </div>

      <div className="status">
        Forklift Status: {state.status || "No data received yet"}
      </div>
    </div>
  );
};

export default Forklift;