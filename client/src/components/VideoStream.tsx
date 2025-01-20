import { useEffect, useState } from "react";
import useWebSocket from "../hooks/useWebSocket";

const VideoStream = () => {
  const { message } = useWebSocket("ws://localhost:8000/video");
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