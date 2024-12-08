import React, { useState, useEffect } from 'react';
import { GoogleMap, LoadScript, MarkerF } from '@react-google-maps/api';
import './App.css';

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
  const [logs, setLogs] = useState([]); // 로그 데이터를 저장할 상태

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
        setWeatherData(data);
      } catch (error) {
        console.error('Error fetching weather data:', error);
      }
    };

    fetchWeatherData();
  }, []);

  // 두 서버로부터 로그 데이터를 가져와 병합하는 함수
useEffect(() => {
  const fetchLogs = async () => {
    try {
      const endpoints = [
        'http://165.229.125.73:8000/api/logs',
        'http://165.229.125.65:8000/api/logs',
      ];

      // 두 서버에서 동시에 로그 요청
      const responses = await Promise.all(endpoints.map((url) => fetch(url)));
      const logsFromBothServers = await Promise.all(
        responses.map((response) => response.json())
      );

      // 로그 데이터 검사
      console.log('Logs from server 1:', logsFromBothServers[0]);
      console.log('Logs from server 2:', logsFromBothServers[1]);

      // 로그 병합 후 시간순 정렬
      const mergedLogs = [...logsFromBothServers[0], ...logsFromBothServers[1]].sort(
        (a, b) => new Date(a.timestamp) - new Date(b.timestamp)
      );

      setLogs((prevLogs) => [...prevLogs, ...mergedLogs]);
    } catch (error) {
      console.error('Error fetching logs:', error);
    }
  };

  // 5초 간격으로 로그를 업데이트
  const interval = setInterval(fetchLogs, 10000);

  return () => clearInterval(interval); // 컴포넌트 언마운트 시 정리
}, []);

  return (
    <div>
      <header className="title">Smart Farm Anti-Theft System</header>
      <div className="dashboard">
        <div className="cam1">
          {/* Raspberry Pi에서 제공하는 스트리밍 */}
          <img
            src="http://165.229.125.73:8000/video_feed"
            alt="Live Stream CAM1"
            className="camera-video"
          />
        </div>
        <div className="cam2">
          {/* Raspberry Pi에서 제공하는 스트리밍 */}
          <img
            src="http://165.229.125.65:8000/video_feed"
            alt="Live Stream CAM2"
            className="camera-video"
          />
        </div>

        {/* 로그 박스 */}
        <div className="system-log">
          <h3>System Log</h3>
          <div className="system-log-log">
          <ul>
            {logs.map((log, index) => (
              <li key={index}>
                <span>{log.timestamp}</span>: <span>{log.message}</span>
              </li>
            ))}
          </ul>
          </div>
        </div>

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
