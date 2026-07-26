'use client';

import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { useEffect, useState } from 'react';
import 'leaflet.heat';

// Fix for default marker icons in Leaflet with Webpack/Next.js
const DefaultIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

// Custom icons for the simulation
const RedIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const YellowIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-gold.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

function HeatmapLayer({ points }: { points: [number, number, number][] }) {
  const map = useMap();
  useEffect(() => {
    // @ts-ignore
    if (!L.heatLayer) return;
    // @ts-ignore
    const heat = L.heatLayer(points, { 
      radius: 35, 
      blur: 25, 
      maxZoom: 13,
      max: 1.0,
      gradient: {
        0.4: 'blue',
        0.6: 'cyan',
        0.7: 'lime',
        0.8: 'yellow',
        1.0: 'red'
      }
    }).addTo(map);
    
    return () => { 
      map.removeLayer(heat); 
    };
  }, [map, points]);
  
  return null;
}

interface LocationData {
  id: number | string;
  lat: number;
  lng: number;
  intensity: string;
  description: string;
}

export default function HeatmapMap({ payload, incident }: { payload: any, incident?: any }) {
  const locations: LocationData[] = Array.isArray(payload) ? payload : [];
  
  // Convert our backend payload into heat points [lat, lng, intensity]
  const heatPoints: [number, number, number][] = locations.map(loc => {
    let intensityValue = 0.4;
    if (loc.intensity === 'High') intensityValue = 1.0;
    else if (loc.intensity === 'Medium') intensityValue = 0.7;
    return [loc.lat, loc.lng, intensityValue];
  });

  return (
    <div className="w-full h-full min-h-[550px] z-0">
      <MapContainer 
        center={[12.9716, 77.5946]} 
        zoom={11} 
        style={{ height: '100%', width: '100%', background: '#EAEAEA' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {heatPoints.length > 0 && <HeatmapLayer points={heatPoints} />}
        
        {/* Render simulated incident if active */}
        {incident && (
          <>
            <Marker position={[13.00, 77.50]} icon={RedIcon}>
              <Popup><strong>Dispatch Unit</strong><br/>{incident.unit}</Popup>
            </Marker>
            <Marker position={[12.98, 77.62]} icon={YellowIcon}>
              <Popup><strong>Live Incident</strong><br/>Crime Detected</Popup>
            </Marker>
            <Polyline 
              positions={[[13.00, 77.50], [12.99, 77.55], [12.98, 77.62]]} 
              color="#D31225" 
              weight={4} 
              dashArray="10, 10" 
            />
          </>
        )}
        
        {/* Optionally render a few markers for context if no incident */}
        {!incident && locations.slice(0, 5).map((loc) => (
          <Marker key={loc.id} position={[loc.lat, loc.lng]}>
            <Popup>
              <div className="font-sans text-[12px] text-black">
                <strong className="text-[#F97316]">Intensity: {loc.intensity}</strong><br/>
                {loc.description}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
