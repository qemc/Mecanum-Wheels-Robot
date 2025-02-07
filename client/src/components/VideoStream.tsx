import { useEffect, useState } from "react";
import useWebSocket from "../hooks/useWebSocket";
import { WS_BASE_URL } from "../config";


const VideoStream = () => {
  const { message } = useWebSocket(`${WS_BASE_URL}/video`);
  const [currentFrame, setCurrentFrame] = useState("");

  useEffect(() => {
      setCurrentFrame(message);
  }, [message]);

  return (
    <div>
      <img
        src={currentFrame || ""}
        alt="Video Stream"
        width="640"
        height="360"
      />
    </div>
  );
};

export default VideoStream;