import React, { useState, useEffect } from 'react';
import { GoogleMap, LoadScript, MarkerF } from '@react-google-maps/api';
import './App.css';

// Importing the video files
import cam1 from './videos/188861-883827797_small.mp4';
import cam2 from './videos/27400-363524230_small.mp4';

const containerStyle = {
  width: '100%',
  height: '300px',
};

// 영남대학교 경산캠퍼스 좌표
const center = {
  lat: 35.8307,
  lng: 128.75435,
};

function App() {
  const [time, setTime] = useState(new Date().toLocaleTimeString());
  const [weatherData, setWeatherData] = useState(null); // 날씨 데이터를 저장할 상태

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date().toLocaleTimeString()), 1000);
    return () => clearInterval(timer);
  }, []);

  // OpenWeatherMap API를 사용하여 날씨 데이터를 가져오는 함수
  useEffect(() => {
    const fetchWeatherData = async () => {
      try {
        const apiKey = '32d0cb5d1c08de744627c416e83e5756'; // 여기에 자신의 OpenWeatherMap API 키를 넣으세요
        const response = await fetch(
          `https://api.openweathermap.org/data/2.5/weather?lat=35.8307&lon=128.75435&appid=${apiKey}&units=metric`
        );
        const data = await response.json();
        console.log(data);
        setWeatherData(data);
      } catch (error) {
        console.error('Error fetching weather data:', error);
      }
    };

    fetchWeatherData();
  }, []);

  return (
    <div>
      <header className="title">Smart Farm Anti-Theft System</header>
      <div className="dashboard">
        <div className="cam1">
          <video
            src={cam1} // Using the imported video for CAM1
            controls
            autoPlay
            loop
            muted
            className="camera-video"
          ></video>
        </div>
        <div className="cam2">
          <video
            src={cam2} // Using the imported video for CAM2
            controls
            autoPlay
            loop
            muted
            className="camera-video"
          ></video>
        </div>

        <div className="system-log">System Log</div>

        <div className="sidebar">
          <div className="current-time">
            <span>현재시간</span>
            <span>{time}</span>
          </div>

          {/* 지도 추가 */}
          <div className="map-container">
            <LoadScript googleMapsApiKey="AIzaSyD_i7-WbK7U3IseXApUuRvLgsxOjPrN_Ck">
              <GoogleMap
                mapContainerStyle={containerStyle}
                center={center} // 영남대학교를 중심으로
                zoom={14} // 줌 레벨을 14로 설정해 주변을 함께 볼 수 있도록 함
              >
                {/* 영남대학교 마커 */}
                <MarkerF position={center} label="영남대학교" />
              </GoogleMap>
            </LoadScript>
          </div>

          <div className="spacer"></div>
        </div>
      </div>
    </div>
  );
}

export default App;
