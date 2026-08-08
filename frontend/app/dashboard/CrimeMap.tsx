'use client';

import { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface Station {
  id: number;
  name: string;
  lat: number;
  lng: number;
  division: string;
  type: string;
  mobile: string;
  email: string;
}

interface CrimeMapProps {
  apiBase: string;
  isKannada: boolean;
}

// Heatmap layer component using Canvas for performance
function HeatmapLayer({ points }: { points: number[][] }) {
  const map = useMap();

  useEffect(() => {
    if (!points || points.length === 0) return;

    // Use canvas-based circle rendering for heatmap effect
    const canvasRenderer = L.canvas({ padding: 0.5 });
    const layerGroup = L.layerGroup();

    points.forEach(([lat, lng, intensity]) => {
      const color = intensity > 0.7 ? '#FF4B2B' : intensity > 0.4 ? '#F59E0B' : '#3B82F6';
      L.circleMarker([lat, lng], {
        radius: 6 + Math.random() * 4,
        fillColor: color,
        color: 'transparent',
        fillOpacity: 0.45,
        renderer: canvasRenderer,
      }).addTo(layerGroup);
    });

    layerGroup.addTo(map);

    return () => {
      map.removeLayer(layerGroup);
    };
  }, [map, points]);

  return null;
}

// Simulate dispatch animation
function DispatchAnimation({ path }: { path: number[][] | null }) {
  const map = useMap();

  useEffect(() => {
    if (!path || path.length < 2) return;

    const polyline = L.polyline(path as L.LatLngExpression[], {
      color: '#FF4B2B',
      weight: 3,
      opacity: 0.8,
      dashArray: '10 6',
    }).addTo(map);

    // Animate dash offset
    let offset = 0;
    const interval = setInterval(() => {
      offset -= 1;
      (polyline.getElement() as SVGElement)?.setAttribute('style', `stroke-dashoffset: ${offset}`);
    }, 50);

    return () => {
      clearInterval(interval);
      map.removeLayer(polyline);
    };
  }, [map, path]);

  return null;
}

export default function CrimeMap({ apiBase, isKannada }: CrimeMapProps) {
  const [hotspots, setHotspots] = useState<number[][]>([]);
  const [stations, setStations] = useState<Station[]>([]);
  const [categories, setCategories] = useState<string[]>(['All']);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [showStations, setShowStations] = useState(true);
  const [loading, setLoading] = useState(true);
  const [dispatchPath, setDispatchPath] = useState<number[][] | null>(null);
  const [dispatchInfo, setDispatchInfo] = useState<{ station: string; distance: string; time: string } | null>(null);

  useEffect(() => {
    loadMapData();
  }, []);

  useEffect(() => {
    loadHotspots();
  }, [selectedCategory]);

  const loadMapData = async () => {
    setLoading(true);
    try {
      const [stationsRes, categoriesRes, hotspotsRes] = await Promise.allSettled([
        fetch(`${apiBase}/map/stations`),
        fetch(`${apiBase}/map/categories`),
        fetch(`${apiBase}/map/hotspots`),
      ]);

      if (stationsRes.status === 'fulfilled' && stationsRes.value.ok) {
        setStations(await stationsRes.value.json());
      }
      if (categoriesRes.status === 'fulfilled' && categoriesRes.value.ok) {
        setCategories(await categoriesRes.value.json());
      }
      if (hotspotsRes.status === 'fulfilled' && hotspotsRes.value.ok) {
        setHotspots(await hotspotsRes.value.json());
      }
    } catch (e) {
      console.error('Map data load error:', e);
    } finally {
      setLoading(false);
    }
  };

  const loadHotspots = async () => {
    try {
      const url = selectedCategory === 'All'
        ? `${apiBase}/map/hotspots`
        : `${apiBase}/map/hotspots?crime_type=${encodeURIComponent(selectedCategory)}`;
      const res = await fetch(url);
      if (res.ok) setHotspots(await res.json());
    } catch (e) {
      console.error('Hotspot load error:', e);
    }
  };

  const simulateCrime = async () => {
    try {
      const res = await fetch(`${apiBase}/map/simulate_crime`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setDispatchPath(data.path);
        setDispatchInfo({
          station: data.station.name,
          distance: `${data.station.distance_km} km`,
          time: `${Math.round(data.station.duration_sec / 60)} min`,
        });
        // Clear after 15 seconds
        setTimeout(() => { setDispatchPath(null); setDispatchInfo(null); }, 15000);
      }
    } catch (e) {
      console.error('Simulation error:', e);
    }
  };

  return (
    <div className="w-full h-full relative">
      {/* Map Controls Overlay */}
      <div className="absolute top-4 left-4 z-[1000] flex flex-col gap-3">
        {/* Category Filter */}
        <div className="bg-white/95 backdrop-blur-sm border border-[var(--color-line)] shadow-lg p-3">
          <label className="text-[9px] font-mono font-bold text-[var(--color-muted)] uppercase tracking-wider block mb-1.5">
            {isKannada ? 'ಅಪರಾಧ ವರ್ಗ' : 'Crime Category'}
          </label>
          <select
            value={selectedCategory}
            onChange={e => setSelectedCategory(e.target.value)}
            className="w-full bg-[var(--color-page-bg)] border border-[var(--color-line)] px-2 py-1.5 text-[11px] font-mono text-[var(--color-ksp-text)] focus:outline-none focus:border-black"
          >
            {categories.map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        {/* Toggle Stations */}
        <button
          onClick={() => setShowStations(!showStations)}
          className={`bg-white/95 backdrop-blur-sm border shadow-lg px-3 py-2 text-[10px] font-mono font-bold uppercase tracking-wider flex items-center gap-2 transition-colors ${
            showStations ? 'border-black text-[var(--color-ksp-text)]' : 'border-[var(--color-line)] text-[var(--color-muted)]'
          }`}
        >
          <span className="material-symbols-outlined text-[14px]">local_police</span>
          {isKannada ? 'ಠಾಣೆಗಳು' : 'Stations'} ({stations.length})
        </button>

        {/* Simulate Button */}
        <button
          onClick={simulateCrime}
          className="bg-[#FF4B2B] text-white border border-[#FF4B2B] shadow-lg px-3 py-2 text-[10px] font-mono font-bold uppercase tracking-wider flex items-center gap-2 hover:bg-[#e04328] transition-colors"
        >
          <span className="material-symbols-outlined text-[14px]">emergency</span>
          {isKannada ? 'ಡಿಸ್ಪ್ಯಾಚ್ ಅನುಕರಣೆ' : 'Simulate Dispatch'}
        </button>
      </div>

      {/* Stats Badge */}
      <div className="absolute top-4 right-4 z-[1000] bg-black/80 backdrop-blur-sm border border-white/10 p-3 flex flex-col gap-1">
        <span className="text-[9px] font-mono text-white/50 uppercase tracking-wider">
          {isKannada ? 'ಹೀಟ್‌ಮ್ಯಾಪ್ ಬಿಂದುಗಳು' : 'Heatmap Points'}
        </span>
        <span className="text-[20px] font-bold text-white font-mono leading-none">{hotspots.length.toLocaleString()}</span>
        <span className="text-[9px] font-mono text-white/30">{selectedCategory}</span>
      </div>

      {/* Dispatch Info */}
      {dispatchInfo && (
        <div className="absolute bottom-4 left-4 z-[1000] bg-[#FF4B2B] text-white p-4 shadow-xl border border-white/20 animate-stream-in max-w-[300px]">
          <div className="flex items-center gap-2 mb-2">
            <span className="material-symbols-outlined text-[16px] animate-pulse">emergency</span>
            <span className="text-[11px] font-mono font-bold uppercase tracking-wider">DISPATCH ACTIVE</span>
          </div>
          <div className="text-[12px] font-bold">{dispatchInfo.station}</div>
          <div className="text-[10px] font-mono opacity-80 mt-1">Distance: {dispatchInfo.distance} · ETA: {dispatchInfo.time}</div>
        </div>
      )}

      {/* Loading overlay */}
      {loading && (
        <div className="absolute inset-0 z-[1001] bg-[#0A0A0A] flex flex-col items-center justify-center">
          <span className="material-symbols-outlined text-[48px] text-white/20 animate-pulse mb-4">map</span>
          <span className="text-[12px] font-mono text-white/40 animate-pulse">
            {isKannada ? 'ನಕ್ಷೆ ಡೇಟಾ ಲೋಡ್ ಆಗುತ್ತಿದೆ...' : 'Loading map intelligence...'}
          </span>
        </div>
      )}

      {/* Leaflet Map */}
      <MapContainer
        center={[12.9716, 77.5946]}
        zoom={11}
        className="w-full h-full"
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {/* Crime Heatmap Points */}
        <HeatmapLayer points={hotspots} />

        {/* Station Markers */}
        {showStations && stations.map(station => (
          <CircleMarker
            key={station.id}
            center={[station.lat, station.lng]}
            radius={5}
            fillColor="#22C55E"
            color="#166534"
            weight={2}
            fillOpacity={0.9}
          >
            <Popup>
              <div className="font-sans text-sm">
                <div className="font-bold text-[var(--color-ksp-text)] mb-1">{station.name}</div>
                <div className="text-[11px] text-[var(--color-muted)]">{station.division}</div>
                <div className="text-[10px] font-mono text-[var(--color-muted)] mt-1">ID: {station.id} · {station.type}</div>
                {station.mobile && <div className="text-[10px] font-mono mt-1">📞 {station.mobile}</div>}
              </div>
            </Popup>
          </CircleMarker>
        ))}

        {/* Dispatch Route */}
        <DispatchAnimation path={dispatchPath} />
      </MapContainer>
    </div>
  );
}
