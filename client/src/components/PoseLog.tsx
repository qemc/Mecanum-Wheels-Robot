import { useEffect, useState } from "react";
import useWebSocket from "../hooks/useWebSocket";

interface Marker {
    id: number;
    x_cm?: number;
    z_cm?: number;
    Roll?: number;
}

const PoseLog = () => {
    const { message } = useWebSocket("ws://localhost:8000/pose");
    const [markers, setMarkers] = useState<{ [key: number]: Marker | null }>({ 0: null, 1: null });

    useEffect(() => {
        if (message) {
            try {
                const parsedMarkers: Marker[] = JSON.parse(message); // Parse the latest message
                const newMarkers: { [key: number]: Marker | null } = { 0: null, 1: null };

                // Process the array of markers
                if (Array.isArray(parsedMarkers)) {
                    parsedMarkers.forEach((marker) => {
                        if (marker.id === 0 || marker.id === 1) {
                            newMarkers[marker.id] = marker;
                        }
                    });
                }

                setMarkers(newMarkers); // Update markers state
            } catch (error) {
                console.error("Failed to parse pose data:", error);
            }
        }
    }, [message]);

    return (
        <div>
            <h2>Marker Positions</h2>
            <div>
                {[0, 1].map((id) => (
                    <div key={id}>
                        <h3>Marker {id}</h3>
                        <div>
                            <div>X: {markers[id]?.x_cm?.toFixed(2) || "-"} cm</div>
                            <div>Z: {markers[id]?.z_cm?.toFixed(2) || "-"} cm</div>
                            <div>Roll: {markers[id]?.Roll?.toFixed(2) || "-"}°</div>
                        </div>
                        <div>{markers[id] ? "Detected" : "Not Detected"}</div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default PoseLog;
