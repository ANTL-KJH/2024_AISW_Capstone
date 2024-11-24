import React, { useState, useEffect } from 'react';
import { GoogleMap, LoadScript, MarkerF } from '@react-google-maps/api';
import './App.css';

const containerStyle = {
    width: '100%',
    height: '300px',
};

const center = {
    lat: 35.8307,
    lng: 128.75435,
};

function App() {
    const [time, setTime] = useState(new Date().toLocaleTimeString());

    useEffect(() => {
        const timer = setInterval(() => setTime(new Date().toLocaleTimeString()), 1000);
        return () => clearInterval(timer);
    }, []);

    return (
        <div>
            <header className="title">Smart Farm Anti-Theft System</header>
            <div className="dashboard">
                <div className="cam1">
                    {/* Raspberry Pi에서 제공하는 스트리밍 */}
                    <img
                        src="http://165.229.125.102:8000/video_feed:8000/video_feed"
                        alt="Live Stream CAM1"
                        className="camera-video"
                    />
                </div>
                <div className="system-log">System Log</div>
                <div className="sidebar">
                    <div className="current-time">
                        <span>현재시간</span>
                        <span>{time}</span>
                    </div>

                    <div className="map-container">
                        <LoadScript googleMapsApiKey="AIzaSyD_i7-WbK7U3IseXApUuRvLgsxOjPrN_Ck">
                            <GoogleMap
                                mapContainerStyle={containerStyle}
                                center={center}
                                zoom={14}
                            >
                                <MarkerF position={center} label="영남대학교" />
                            </GoogleMap>
                        </LoadScript>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default App;
