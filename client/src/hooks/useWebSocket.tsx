import { useEffect, useState } from "react";

const useWebSocket = (url: string) => {
    const [socket, setSocket] = useState<WebSocket | null>(null);
    const [message, setMessage] = useState<any>(null); 

    useEffect(() => {
        const ws = new WebSocket(url);

        ws.onopen = () => {
            console.log(`WebSocket connected to ${url}`);
        };

        ws.onmessage = (event) => {
            setMessage(event.data);
        };

        ws.onclose = () => {
            console.log(`WebSocket disconnected from ${url}`);
        };

        ws.onerror = (error) => {
            console.error(`WebSocket error on ${url}:`, error);
        };

        setSocket(ws);

        return () => {
            ws.close();
        };
    }, [url]);

    const sendMessage = (message: string) => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(message);
        } else {
            console.warn("WebSocket is not open");
        }
    };

    return { socket, message, sendMessage }; 
};

export default useWebSocket;
