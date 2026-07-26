'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';

// ── Types for backend response ──────────────────────────────────────────────
interface Citation {
  fir_id: string;
  crime_type: string;
  district: string;
  date_filed: string;
  relevance_score: number;
  snippet: string;
  full_text?: string;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  intent?: string;
  citations?: Citation[];
}

interface FeedItem {
  id: string | number;
  incident_date: string;
  fir_number: string;
  district: string;
  crime_category: string;
  description?: string;
}

// ── Citation Card Component ───────────────────────────────────────────────────
function CitationCard({ cite }: { cite: Citation }) {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <div className="bg-gray-50 border border-gray-300 p-4 hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,0.1)] transition-shadow group relative">
      <div className="absolute top-0 left-0 w-1 h-full bg-black"></div>
      <div className="flex flex-wrap gap-2 mb-4 items-center justify-between pl-2">
        <div className="flex flex-wrap gap-2">
          <div className="px-2 py-1 bg-white border border-gray-300 text-[10px] font-mono font-bold text-black uppercase">
            FIR: {cite.fir_id}
          </div>
          <div className="px-2 py-1 bg-white border border-gray-300 text-[10px] font-mono font-bold uppercase">
            {cite.crime_type}
          </div>
          <div className="px-2 py-1 bg-white border border-gray-300 text-[10px] font-mono font-bold uppercase">
            {cite.district}
          </div>
        </div>
        <div className="px-2 py-1 bg-white border border-gray-300 text-[10px] font-mono font-bold text-[#FF4B2B]">
          MATCH: {(cite.relevance_score * 100).toFixed(0)}%
        </div>
      </div>
      
      <div 
        className={`text-[13px] text-gray-700 leading-relaxed mt-2 whitespace-pre-wrap transition-all duration-300 ease-in-out overflow-hidden pl-2 font-mono ${
          expanded ? 'max-h-[5000px] opacity-100' : 'max-h-[60px] opacity-80'
        }`}
      >
        {expanded && cite.full_text ? cite.full_text : cite.snippet}
      </div>
      
      <div className="flex justify-between items-center mt-4 pt-3 border-t border-gray-200 border-dashed pl-2">
        <span className="text-[10px] font-mono text-gray-500 uppercase tracking-widest">
          Filed: {cite.date_filed}
        </span>
        <button 
          onClick={() => setExpanded(!expanded)} 
          className="text-[#FF4B2B] text-[10px] font-mono font-bold flex items-center gap-1 hover:bg-[#FF4B2B] hover:text-white px-2 py-1 transition-colors border border-transparent hover:border-[#FF4B2B]"
        >
          <span className="material-symbols-outlined notranslate text-[14px]">
            {expanded ? 'unfold_less' : 'unfold_more'}
          </span>
          {expanded ? 'COLLAPSE REPORT' : 'EXPAND FULL REPORT'}
        </button>
      </div>
    </div>
  );
}

// ── Intent View Components ──────────────────────────────────────────────────
const DynamicHeatmapMap = dynamic(() => import('../components/HeatmapMap'), {
  ssr: false,
  loading: () => <div className="flex-1 flex items-center justify-center text-[var(--color-muted)] font-mono animate-pulse">Initializing Spatial Link...</div>
});

function HeatmapComponent({ payload }: { payload: any }) {
  const [liveMode, setLiveMode] = useState(false);
  const [incident, setIncident] = useState<any>(null);

  const simulateIncident = () => {
    setLiveMode(true);
    setIncident({
      unit: "Malleswaram Police Station",
      time: "18 mins",
      dist: "11.1 km"
    });
  };

  const stopLiveMode = () => {
    setLiveMode(false);
    setIncident(null);
  };

  return (
    <div className="flex-1 overflow-y-auto p-4 md:p-8 pb-32 flex flex-col gap-4 animate-stream-in">
      {/* Control Panel */}
      <div className="bg-white rounded-lg border border-gray-100 p-4 shadow-[0_2px_8px_rgba(0,0,0,0.04)] flex items-center gap-4">
        <div className="flex items-center gap-2 text-gray-700 mr-2">
          <div className="w-3 h-3 rounded-full bg-[#FCA5A5] animate-pulse"></div>
          <span className="font-bold text-[15px]">Live Simulation:</span>
        </div>
        <button onClick={simulateIncident} className="bg-[#F8C471] hover:bg-[#F39C12] text-white font-bold py-2 px-6 rounded text-[14px] transition-colors shadow-sm">
          Simulate 1 Incident
        </button>
        <button onClick={stopLiveMode} className="bg-[#DF1B22] hover:bg-[#C0392B] text-white font-bold py-2 px-6 rounded text-[14px] transition-colors shadow-sm">
          Stop Live Mode
        </button>
      </div>

      {/* Incident Alert */}
      {incident && (
        <div className="bg-[#FFF8E7] border border-[#FDE5B4] rounded-lg p-4 shadow-[0_2px_8px_rgba(0,0,0,0.04)] flex items-center gap-8 text-[14px] text-[#8C4A1C]">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-[#DF1B22] animate-pulse shrink-0"></div>
            <span className="font-bold text-[16px] leading-tight">Live Incident<br/>Detected!</span>
          </div>
          
          <div className="flex flex-col leading-tight ml-4">
            <span><span className="font-bold">Dispatch Unit:</span> {incident.unit.split(' ')[0]}</span>
            <span>{incident.unit.split(' ').slice(1).join(' ')}</span>
          </div>
          
          <div className="flex flex-col leading-tight ml-4">
            <span><span className="font-bold">Est. Arrival:</span> {incident.time}</span>
            <span>({incident.dist})</span>
          </div>
        </div>
      )}

      {/* Map */}
      <div className="bg-white rounded-xl border border-gray-200 p-1 shadow-sm min-h-[550px] flex flex-col relative z-0 mt-2">
        <div className="flex-1 overflow-hidden rounded-lg relative z-0 bg-gray-100">
          <DynamicHeatmapMap payload={payload} incident={incident} />
        </div>
      </div>
    </div>
  );
}

function NetworkComponent({ payload }: { payload: any }) {
  const nodes = payload?.nodes || [];
  const edges = payload?.edges || [];

  return (
    <div className="flex-1 overflow-y-auto p-8 pb-32 flex flex-col gap-4 animate-stream-in">
      <div className="bg-[var(--color-panel-bg)] rounded-sm border border-[var(--color-line)] p-6 shadow-sm min-h-[400px] flex flex-col">
        <h2 className="text-[14px] font-mono font-bold text-[#00FF00] uppercase tracking-widest flex items-center gap-2 mb-4">
          <span className="material-symbols-outlined notranslate">hub</span>
          Node/Entity Graph
        </h2>
        <div className="flex-1 flex gap-6">
          <div className="w-1/2 flex flex-col gap-4">
            <h3 className="text-[12px] font-mono text-[var(--color-muted)] uppercase border-b border-[var(--color-line)] pb-2">Identified Entities</h3>
            {nodes.map((node: any, idx: number) => (
              <div key={idx} className="bg-white border border-[var(--color-line)] p-3 shadow-sm flex justify-between items-center">
                <div className="flex flex-col">
                  <span className="font-bold text-[14px] text-black">{node.id}</span>
                  <span className="text-[10px] font-mono uppercase text-[var(--color-muted)]">{node.type}</span>
                </div>
                {node.risk && (
                  <span className={`text-[10px] font-mono font-bold px-2 py-1 border ${node.risk === 'High' ? 'text-red-600 border-red-600 bg-red-50' : 'text-orange-500 border-orange-500 bg-orange-50'}`}>
                    {node.risk} RISK
                  </span>
                )}
              </div>
            ))}
          </div>
          <div className="w-1/2 flex flex-col gap-4">
            <h3 className="text-[12px] font-mono text-[var(--color-muted)] uppercase border-b border-[var(--color-line)] pb-2">Known Linkages</h3>
            {edges.map((edge: any, idx: number) => (
              <div key={idx} className="bg-[#0a0a0a] border border-[var(--color-line)] p-3 shadow-sm flex flex-col gap-2">
                <span className="text-[10px] font-mono text-[#00FF00] uppercase font-bold">{edge.type}</span>
                <div className="flex justify-between items-center text-[12px] text-white">
                  <span>{edge.from}</span>
                  <span className="material-symbols-outlined notranslate text-[var(--color-muted)] text-[16px]">arrow_forward</span>
                  <span>{edge.to}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function PredictComponent({ payload, isKannada }: { payload: any; isKannada: boolean }) {
  if (!payload) return (
    <div className="flex-1 overflow-y-auto p-8 flex items-center justify-center">
      <span className="text-[var(--color-muted)] font-mono text-[12px]">No prediction payload available.</span>
    </div>
  );

  return (
    <div className="flex-1 overflow-y-auto p-8 pb-32 flex flex-col gap-4 animate-stream-in">
      <div className="bg-[var(--color-panel-bg)] rounded-sm border border-[var(--color-line)] p-6 shadow-sm min-h-[400px] flex flex-col">
        <h2 className="text-[14px] font-mono font-bold text-[#3B82F6] uppercase tracking-widest flex items-center gap-2 mb-6">
          <span className="material-symbols-outlined notranslate">trending_up</span>
          Forecasting Model
        </h2>

        <div className="flex-1 flex flex-col gap-6">
          <div className="bg-blue-500/10 border border-blue-500 p-6 flex items-center justify-between">
            <div className="flex flex-col gap-2">
              <span className="text-[10px] font-mono text-blue-600 font-bold tracking-widest">PREDICTED EVENT</span>
              <span className="text-[20px] font-bold text-black">{payload.prediction}</span>
              <span className="text-[12px] font-mono text-black/60">Estimated Timeline: {payload.timeline}</span>
            </div>
            <div className="flex flex-col items-center justify-center w-24 h-24 rounded-full border-4 border-blue-500 bg-white shadow-sm shrink-0">
              <span className="text-[24px] font-bold text-blue-600 leading-none">{payload.confidence}%</span>
              <span className="text-[8px] font-mono text-blue-600 mt-1">{isKannada ? 'ವಿಶ್ವಾಸಾರ್ಹತೆ' : 'CONFIDENCE'}</span>
            </div>
          </div>

          <div className="flex flex-col gap-3 mt-4">
            <h3 className="text-[12px] font-mono text-[var(--color-muted)] uppercase border-b border-[var(--color-line)] pb-2">{isKannada ? 'ಅನುಗುಣವಾದ ಅಂಶಗಳು' : 'Contributory Factors'}</h3>
            {payload.factors?.map((factor: string, idx: number) => (
              <div key={idx} className="flex items-start gap-3 bg-white border border-[var(--color-line)] p-4 shadow-sm">
                <span className="material-symbols-outlined notranslate text-[16px] text-blue-500 shrink-0 mt-0.5">adjust</span>
                <span className="text-[13px] text-black leading-relaxed">{factor}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function DirectoryComponent() {
  const [data, setData] = useState<{ items: any[], total: number, page: number }>({ items: [], total: 0, page: 1 });
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [localLang, setLocalLang] = useState('en');
  
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCase, setSelectedCase] = useState<any | null>(null);

  useEffect(() => {
    setLoading(true);
    fetch(`http://localhost:8000/api/directory?page=${page}&limit=50&lang=${localLang}`)
      .then(res => res.json())
      .then(resData => {
        setData(resData);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [page, localLang]);

  const filteredItems = data.items.filter(item => 
    item.fir_id.toLowerCase().includes(searchTerm.toLowerCase()) || 
    item.district.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const displayItems = filteredItems.slice(0, 6);

  return (
    <div className="flex-1 overflow-y-auto p-8 pb-32 flex flex-col gap-6 animate-stream-in bg-[#FCFAF8]">
      
      {/* Header Area */}
      <div className="flex justify-between items-start mb-2">
        <div>
          <h2 className="text-[22px] font-bold uppercase text-black mb-1 tracking-tight">Case Directory</h2>
          <p className="text-[10px] font-mono text-gray-500 uppercase tracking-widest">Master FIR Repository - Official Records</p>
        </div>
        <div className="border border-gray-300 px-4 py-2 bg-white flex items-center shadow-sm">
          <span className="text-[10px] font-mono text-gray-500 tracking-widest">CASES: {data.total}</span>
        </div>
      </div>

      {/* Search Bar */}
      <div className="border-[3px] border-black bg-white p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] flex items-center gap-3">
        <span className="material-symbols-outlined notranslate text-gray-400 text-2xl">search</span>
        <input 
          type="text" 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search by FIR number or district..." 
          className="flex-1 bg-transparent border-none outline-none font-mono text-[14px] text-black placeholder:text-gray-400"
        />
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center text-[var(--color-muted)] font-mono text-[12px]">
          Loading Directory Data...
        </div>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          {displayItems.map((item, idx) => {
            const riskColor = 'bg-[#3B82F6]'; // Blue for cases

            return (
              <div key={idx} className="bg-white border-[3px] border-black p-6 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] flex flex-col relative group transition-all hover:-translate-y-1 hover:-translate-x-1 hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                {/* Top Border Line */}
                <div className={`absolute top-0 left-0 w-full h-2 ${riskColor}`}></div>
                
                <div className="flex justify-between items-start mt-2 mb-6">
                  <div className="flex flex-col gap-1">
                    <span className="text-[10px] font-mono text-gray-500 uppercase tracking-widest">FIR NO</span>
                    <span className="font-bold text-[18px] text-black tracking-tight">{item.fir_id}</span>
                  </div>
                  <div className="border border-gray-300 px-3 py-1 bg-gray-50 flex items-center justify-center">
                    <span className="text-[10px] font-mono text-gray-500 uppercase font-bold tracking-wider">OPEN</span>
                  </div>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="border border-gray-200 bg-gray-50 p-3 flex flex-col justify-center">
                    <div className="text-[9px] font-mono text-gray-500 mb-1 uppercase tracking-widest">Date Filed</div>
                    <div className="font-bold text-[14px] text-black">{item.date_filed}</div>
                  </div>
                  <div className="border border-gray-200 bg-gray-50 p-3 flex flex-col justify-center">
                    <div className="text-[9px] font-mono text-gray-500 mb-1 uppercase tracking-widest">Crime Type</div>
                    <div className="font-bold text-[12px] text-black mt-1 line-clamp-1">{item.crime_type}</div>
                  </div>
                </div>

                {/* District */}
                <div className="mb-8">
                  <div className="text-[9px] font-mono text-gray-500 mb-2 uppercase tracking-widest">Jurisdiction</div>
                  <div className="border border-gray-200 px-3 py-1.5 inline-block text-[11px] font-mono text-black bg-white">
                    {item.district}
                  </div>
                </div>

                {/* Button */}
                <button 
                  onClick={() => setSelectedCase(item)} 
                  className="mt-auto w-full border-[3px] border-black py-3 bg-white hover:bg-gray-50 font-bold text-[12px] uppercase tracking-widest shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-transform active:translate-y-1 active:translate-x-1 active:shadow-none flex justify-center items-center gap-2"
                >
                  Open Full Dossier
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal */}
      {selectedCase && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-stream-in">
          <div className="bg-[#FCFAF8] w-full max-w-5xl flex flex-col border-[4px] border-black shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] relative max-h-[90vh] overflow-y-auto">
             
             <button 
               onClick={() => setSelectedCase(null)} 
               className="absolute top-4 right-4 w-8 h-8 border-2 border-black flex justify-center items-center hover:bg-gray-100 z-10 bg-white"
             >
               <span className="material-symbols-outlined notranslate text-[18px]">close</span>
             </button>

             {/* Header */}
             <div className="p-8 border-b border-gray-200 bg-white relative">
               <div className="flex items-center gap-3 mb-3">
                 <span className="material-symbols-outlined notranslate text-[#FF4B2B] text-2xl">folder_special</span>
                 <h2 className="text-[20px] font-bold uppercase tracking-wider text-black">CASE FILE DOSSIER // FIR #{selectedCase.fir_id}</h2>
               </div>
               <div className="flex items-center gap-4 text-[11px] font-mono text-gray-500 uppercase tracking-widest">
                 <span>DISTRICT: {selectedCase.district} | FILED: {selectedCase.date_filed}</span>
                 <span className="border border-[#FF4B2B] text-[#FF4B2B] px-2 py-0.5 font-bold">OPEN</span>
               </div>
             </div>

             {/* Body */}
             <div className="p-8 bg-[#FAFAFA] flex flex-col gap-6">
               <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                 <div className="bg-white border border-gray-200 p-4 shadow-sm flex flex-col">
                   <div className="text-[10px] font-mono text-gray-400 mb-2 uppercase tracking-widest">Crime Type</div>
                   <div className="font-bold text-[13px] text-black">{selectedCase.crime_type}</div>
                 </div>
                 <div className="bg-white border border-gray-200 p-4 shadow-sm flex flex-col">
                   <div className="text-[10px] font-mono text-gray-400 mb-2 uppercase tracking-widest">Police Station</div>
                   <div className="font-bold text-[13px] text-black">{selectedCase.district}</div>
                 </div>
                 <div className="bg-white border border-gray-200 p-4 shadow-sm flex flex-col">
                   <div className="text-[10px] font-mono text-gray-400 mb-2 uppercase tracking-widest">Incident Location</div>
                   <div className="font-bold text-[13px] text-black">{selectedCase.district}</div>
                 </div>
                 <div className="bg-white border border-gray-200 p-4 shadow-sm flex flex-col">
                   <div className="text-[10px] font-mono text-gray-400 mb-2 uppercase tracking-widest">Acts & Sections</div>
                   <div className="font-bold text-[13px] text-black">N/A</div>
                 </div>
               </div>

               <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                 <div className="bg-white border border-gray-200 p-5 shadow-sm flex flex-col">
                   <div className="text-[10px] font-mono text-gray-400 mb-3 uppercase tracking-widest border-b border-gray-100 pb-2">Complainant / Victim</div>
                   <div className="font-bold text-[14px] text-black">Unknown</div>
                 </div>
                 <div className="bg-white border border-gray-200 p-5 shadow-sm flex flex-col">
                   <div className="text-[10px] font-mono text-[#FF4B2B] mb-3 uppercase tracking-widest border-b border-gray-100 pb-2">Accused / Suspects</div>
                   <div className="font-bold text-[14px] text-black">See Detailed Narrative</div>
                 </div>
               </div>

               <div className="mt-2">
                 <div className="text-[10px] font-mono text-gray-400 mb-3 uppercase tracking-widest">Incident Narrative</div>
                 <div className="bg-white border border-gray-200 p-6 shadow-sm text-[13px] leading-loose text-gray-700 font-mono">
                   {selectedCase.text}
                 </div>
               </div>
             </div>

             {/* Footer */}
             <div className="bg-[#111111] p-6 flex justify-end mt-auto">
               <button 
                 onClick={() => setSelectedCase(null)}
                 className="bg-[#FF4B2B] hover:bg-[#E03A1A] text-white px-8 py-3 text-[12px] font-bold uppercase tracking-widest flex items-center gap-3 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-transform active:translate-y-1 active:translate-x-1 active:shadow-none border border-transparent"
               >
                 <span className="material-symbols-outlined notranslate text-[16px] text-yellow-300">bolt</span>
                 Investigate In Live Workspace
                 <span className="material-symbols-outlined notranslate text-[18px]">arrow_forward</span>
               </button>
             </div>
          </div>
        </div>
      )}
    </div>
  );
}

function SuspectDirectoryComponent() {
  const [data, setData] = useState<{ items: any[], total: number, page: number }>({ items: [], total: 0, page: 1 });
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [localLang, setLocalLang] = useState('en');
  
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSuspect, setSelectedSuspect] = useState<any | null>(null);

  useEffect(() => {
    setLoading(true);
    fetch(`http://localhost:8000/api/suspects?page=${page}&limit=50&lang=${localLang}`)
      .then(res => res.json())
      .then(resData => {
        setData(resData);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [page, localLang]);

  const filteredItems = data.items.filter(item => 
    item.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    item.district.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const displayItems = filteredItems.slice(0, 6);

  return (
    <div className="flex-1 overflow-y-auto p-8 pb-32 flex flex-col gap-6 animate-stream-in bg-[#FCFAF8]">
      
      {/* Header Area */}
      <div className="flex justify-between items-start mb-2">
        <div>
          <h2 className="text-[22px] font-bold uppercase text-black mb-1 tracking-tight">Suspect Dossiers</h2>
          <p className="text-[10px] font-mono text-gray-500 uppercase tracking-widest">Active Suspect Profiles - Threat Intelligence</p>
        </div>
        <div className="border border-gray-300 px-4 py-2 bg-white flex items-center shadow-sm">
          <span className="text-[10px] font-mono text-gray-500 tracking-widest">PROFILES: {data.total}</span>
        </div>
      </div>

      {/* Search Bar */}
      <div className="border-[3px] border-black bg-white p-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] flex items-center gap-3">
        <span className="material-symbols-outlined notranslate text-gray-400 text-2xl">search</span>
        <input 
          type="text" 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search by name, alias, or district..." 
          className="flex-1 bg-transparent border-none outline-none font-mono text-[14px] text-black placeholder:text-gray-400"
        />
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center text-[var(--color-muted)] font-mono text-[12px]">
          Loading Suspect Data...
        </div>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          {displayItems.map((item, idx) => {
            const initials = item.name.split(' ').map((n: string) => n[0]).join('').substring(0, 2).toUpperCase();
            const isHighRisk = item.risk === 'High';
            const riskColor = isHighRisk ? 'bg-[#F97316]' : 'bg-[#EAB308]';
            const riskText = isHighRisk ? '75% - HIGH' : '45% - MEDIUM';
            const riskWidth = isHighRisk ? '75%' : '45%';

            return (
              <div key={idx} className="bg-white border-[3px] border-black p-6 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] flex flex-col relative group transition-all">
                {/* Top Border Line */}
                <div className={`absolute top-0 left-0 w-full h-2 ${riskColor}`}></div>
                
                <div className="flex justify-between items-start mt-2 mb-6">
                  <div className="flex items-center gap-4">
                    <div className={`w-14 h-14 ${riskColor} border-[3px] border-black flex justify-center items-center font-bold text-white shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] text-[18px]`}>
                      {initials}
                    </div>
                    <span className="font-bold text-[18px] text-black tracking-tight">{item.name}</span>
                  </div>
                  <div className="border border-gray-300 px-3 py-1 bg-gray-50 flex items-center justify-center">
                    <span className="text-[10px] font-mono text-gray-500 uppercase font-bold tracking-wider">At Large</span>
                  </div>
                </div>

                {/* Risk Score */}
                <div className="mb-6">
                  <div className="flex justify-between items-end mb-2 text-[10px] font-mono tracking-widest">
                    <span className="text-gray-500">RISK SCORE</span>
                    <span className={`${isHighRisk ? 'text-[#F97316]' : 'text-[#EAB308]'} font-bold text-[11px]`}>{riskText}</span>
                  </div>
                  <div className="h-2 w-full bg-gray-200">
                    <div className={`h-full ${riskColor}`} style={{ width: riskWidth }}></div>
                  </div>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="border border-gray-200 bg-gray-50 p-3 flex flex-col justify-center">
                    <div className="text-[9px] font-mono text-gray-500 mb-1 uppercase tracking-widest">Associated FIRs</div>
                    <div className="font-bold text-[20px] text-black">1</div>
                  </div>
                  <div className="border border-gray-200 bg-gray-50 p-3 flex flex-col justify-center">
                    <div className="text-[9px] font-mono text-gray-500 mb-1 uppercase tracking-widest">Gang Affiliation</div>
                    <div className="font-bold text-[12px] text-black mt-1">Unknown</div>
                  </div>
                </div>

                {/* District */}
                <div className="mb-8">
                  <div className="text-[9px] font-mono text-gray-500 mb-2 uppercase tracking-widest">Operational District</div>
                  <div className="border border-gray-200 px-3 py-1.5 inline-block text-[11px] font-mono text-black bg-white">
                    {item.district}
                  </div>
                </div>

                {/* Button */}
                <button 
                  onClick={() => setSelectedSuspect(item)} 
                  className="mt-auto w-full border-[3px] border-black py-3 bg-white hover:bg-gray-50 font-bold text-[12px] uppercase tracking-widest shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-transform active:translate-y-1 active:translate-x-1 active:shadow-none flex justify-center items-center gap-2"
                >
                  Open Full Dossier
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal */}
      {selectedSuspect && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-stream-in">
          <div className="bg-[#FCFAF8] w-full max-w-5xl flex flex-col border-[4px] border-black shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] relative max-h-[90vh] overflow-y-auto">
             
             <button 
               onClick={() => setSelectedSuspect(null)} 
               className="absolute top-4 right-4 w-8 h-8 border-2 border-black flex justify-center items-center hover:bg-gray-100 z-10 bg-white"
             >
               <span className="material-symbols-outlined notranslate text-[18px]">close</span>
             </button>

             {/* Header */}
             <div className="p-8 border-b border-gray-200 bg-white relative">
               <div className="flex items-center gap-3 mb-3">
                 <span className="material-symbols-outlined notranslate text-[#FF4B2B] text-2xl">folder_special</span>
                 <h2 className="text-[20px] font-bold uppercase tracking-wider text-black">CASE FILE DOSSIER // FIR #{selectedSuspect.fir_id}</h2>
               </div>
               <div className="flex items-center gap-4 text-[11px] font-mono text-gray-500 uppercase tracking-widest">
                 <span>DISTRICT: {selectedSuspect.district} | FILED: {selectedSuspect.date_filed}</span>
                 <span className="border border-[#FF4B2B] text-[#FF4B2B] px-2 py-0.5 font-bold">OPEN</span>
               </div>
             </div>

             {/* Body */}
             <div className="p-8 bg-[#FAFAFA] flex flex-col gap-6">
               <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                 <div className="bg-white border border-gray-200 p-4 shadow-sm flex flex-col">
                   <div className="text-[10px] font-mono text-gray-400 mb-2 uppercase tracking-widest">Crime Type</div>
                   <div className="font-bold text-[13px] text-black">{selectedSuspect.crime_type}</div>
                 </div>
                 <div className="bg-white border border-gray-200 p-4 shadow-sm flex flex-col">
                   <div className="text-[10px] font-mono text-gray-400 mb-2 uppercase tracking-widest">Police Station</div>
                   <div className="font-bold text-[13px] text-black">{selectedSuspect.district}</div>
                 </div>
                 <div className="bg-white border border-gray-200 p-4 shadow-sm flex flex-col">
                   <div className="text-[10px] font-mono text-gray-400 mb-2 uppercase tracking-widest">Incident Location</div>
                   <div className="font-bold text-[13px] text-black">{selectedSuspect.district}</div>
                 </div>
                 <div className="bg-white border border-gray-200 p-4 shadow-sm flex flex-col">
                   <div className="text-[10px] font-mono text-gray-400 mb-2 uppercase tracking-widest">Acts & Sections</div>
                   <div className="font-bold text-[13px] text-black">N/A</div>
                 </div>
               </div>

               <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                 <div className="bg-white border border-gray-200 p-5 shadow-sm flex flex-col">
                   <div className="text-[10px] font-mono text-gray-400 mb-3 uppercase tracking-widest border-b border-gray-100 pb-2">Complainant / Victim</div>
                   <div className="font-bold text-[14px] text-black">Unknown</div>
                 </div>
                 <div className="bg-white border border-gray-200 p-5 shadow-sm flex flex-col">
                   <div className="text-[10px] font-mono text-[#FF4B2B] mb-3 uppercase tracking-widest border-b border-gray-100 pb-2">Accused / Suspects</div>
                   <div className="font-bold text-[14px] text-black">{selectedSuspect.name}</div>
                 </div>
               </div>

               <div className="mt-2">
                 <div className="text-[10px] font-mono text-gray-400 mb-3 uppercase tracking-widest">Incident Narrative</div>
                 <div className="bg-white border border-gray-200 p-6 shadow-sm text-[13px] leading-loose text-gray-700 font-mono">
                   {selectedSuspect.details}
                 </div>
               </div>
             </div>

             {/* Footer */}
             <div className="bg-[#111111] p-6 flex justify-end mt-auto">
               <button 
                 onClick={() => setSelectedSuspect(null)}
                 className="bg-[#FF4B2B] hover:bg-[#E03A1A] text-white px-8 py-3 text-[12px] font-bold uppercase tracking-widest flex items-center gap-3 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-transform active:translate-y-1 active:translate-x-1 active:shadow-none border border-transparent"
               >
                 <span className="material-symbols-outlined notranslate text-[16px] text-yellow-300">bolt</span>
                 Investigate In Live Workspace
                 <span className="material-symbols-outlined notranslate text-[18px]">arrow_forward</span>
               </button>
             </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function DashboardPage() {
  const [isKannada, setIsKannada] = useState(false);
  const [sessionId, setSessionId] = useState('------');

  // ── Chat state ──────────────────────────────────────────────────────────
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentIntent, setCurrentIntent] = useState<string>('LOOKUP');
  const [currentPayload, setCurrentPayload] = useState<any>(null);
  const [telemetry, setTelemetry] = useState({ active_entities: 0, identified_edges: 0, critical_anomalies: 0 });
  const [feed, setFeed] = useState<FeedItem[]>([]);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setSessionId(new Date().getTime().toString().slice(-6));
  }, []);

  useEffect(() => {
    fetch('http://localhost:8000/api/telemetry')
      .then(res => res.json())
      .then(data => setTelemetry(data))
      .catch(err => console.error('Failed to fetch telemetry:', err));

    fetch(`http://localhost:8000/api/feed?lang=${isKannada ? 'kn' : 'en'}`)
      .then(res => res.json())
      .then(data => setFeed(data))
      .catch(err => console.error('Failed to fetch feed:', err));
  }, [isKannada]);

  // Google Translate initialization
  useEffect(() => {
    if (!document.getElementById('google-translate-script')) {
      const addScript = document.createElement('script');
      addScript.id = 'google-translate-script';
      addScript.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
      addScript.async = true;
      document.body.appendChild(addScript);

      (window as any).googleTranslateElementInit = () => {
        new (window as any).google.translate.TranslateElement(
          { pageLanguage: 'en', includedLanguages: 'kn,en', layout: (window as any).google.translate.TranslateElement.InlineLayout.SIMPLE, autoDisplay: false },
          'google_translate_element'
        );
      };
    }
  }, []);

  // Auto-scroll to latest message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const submitDirectQuery = async (query: string) => {
    if (!query || isLoading) return;

    const userMessage: ChatMessage = { role: 'user', content: query };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, lang: isKannada ? 'kn' : 'en' }),
      });

      if (!res.ok) throw new Error(`Backend responded with status ${res.status}`);
      const data = await res.json();

      setCurrentIntent(data.intent || 'LOOKUP');
      setCurrentPayload(data.route_payload || null);

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: data.answer_text ?? 'No response received.',
        intent: data.intent,
        citations: data.citations ?? [],
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `⚠ Connection error — could not reach the intelligence gateway. (${err instanceof Error ? err.message : 'Unknown error'})`,
        intent: 'ERROR',
        citations: [],
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = () => {
    const query = inputValue.trim();
    if (query) {
      setInputValue('');
      submitDirectQuery(query);
    }
  };

  // ── Keyboard handler for Enter key ─────────────────────────────────────
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="min-h-screen bg-[var(--color-page-bg)] flex flex-col font-sans overflow-hidden">

      {/* Header Bar */}
      <header className="fixed top-0 left-0 right-0 z-50 h-[70px] bg-white border-b border-[var(--color-line)] flex items-center justify-between px-6 shadow-sm">
        <div className="flex items-center gap-3">
          <img src="/image copy.png" alt="KSP Crest" className="w-10 h-10 object-contain drop-shadow-sm" />
          <div className="flex flex-col">
            <span className="font-bold text-[var(--color-ksp-text)] text-[14px] leading-tight tracking-tight uppercase">
              {isKannada ? 'ಗುಪ್ತಚರ ಕನ್ಸೋಲ್' : 'Intelligence Console'}
            </span>
            <span className="text-[10px] text-[var(--color-muted)] font-mono tracking-widest">
              {isKannada ? 'ಕಾರ್ಯಾಚರಣೆ ಕೇಂದ್ರ' : 'OPS CENTER'}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div id="google_translate_element" style={{ display: 'none' }}></div>
          <button
            onClick={() => {
              const newLang = !isKannada;
              setIsKannada(newLang);
              setTimeout(() => {
                const select = document.querySelector('.goog-te-combo') as HTMLSelectElement;
                if (select) {
                  select.value = newLang ? 'kn' : 'en';
                  select.dispatchEvent(new Event('change'));
                }
              }, 100);
            }}
            className="flex items-center gap-2 px-3 py-1.5 border border-[var(--color-line)] bg-[var(--color-page-bg)] hover:bg-[var(--color-soft-card-2)] rounded-sm text-[11px] font-bold uppercase tracking-wider text-[var(--color-ksp-text)] transition-colors"
          >
            <span className="material-symbols-outlined notranslate text-[14px]">translate</span>
            <span>{isKannada ? 'ENG' : 'ಕನ್ನಡ'}</span>
          </button>

          <div className="w-[1px] h-4 bg-[var(--color-line)]"></div>

          <Link
            href="/"
            className="flex items-center gap-2 px-3 py-1.5 bg-black text-white rounded-sm text-[11px] font-bold uppercase tracking-wider hover:bg-[var(--color-ksp-text)] transition-colors"
          >
            <span>{isKannada ? 'ಲಾಗ್ ಔಟ್' : 'LOGOUT'}</span>
            <span className="material-symbols-outlined notranslate text-[14px]">logout</span>
          </Link>
        </div>
      </header>

      {/* Main 3-Column Layout */}
      <main className="flex-1 pt-[70px] flex h-screen overflow-hidden">

        {/* Column 1: Control Panel (20%) */}
        <aside className="w-[20%] min-w-[250px] border-r border-[var(--color-line)] bg-[var(--color-panel-bg)] flex flex-col justify-between">
          <div className="p-4 flex flex-col gap-2">
            <div className="text-[10px] font-mono text-[var(--color-muted)] uppercase tracking-widest mb-2 px-2">
              {isKannada ? 'ನೇವಿಗೇಷನ್' : 'Navigation'}
            </div>

            <button onClick={() => setCurrentIntent('LOOKUP')} className={`flex items-center gap-3 px-3 py-3 ${currentIntent === 'LOOKUP' ? 'bg-[var(--color-white-card)] border border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] text-[var(--color-ksp-text)]' : 'bg-transparent border border-transparent hover:border-[var(--color-line)] hover:bg-white text-[var(--color-muted)] hover:text-[var(--color-ksp-text)]'} text-[12px] font-bold uppercase tracking-wider transition-colors mb-1 min-h-[48px] h-auto text-left break-words overflow-hidden`}>
              <span className="material-symbols-outlined notranslate text-[18px] shrink-0">radar</span>
              <span className="flex-1 break-words leading-tight min-w-0">{isKannada ? 'ಲೈವ್ ತನಿಖೆ' : 'Live Investigation'}</span>
            </button>

            <button onClick={() => submitDirectQuery('/run-heatmap ')} className={`flex items-center gap-3 px-3 py-3 ${currentIntent === 'PATTERN' ? 'bg-[var(--color-white-card)] border border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] text-[var(--color-ksp-text)]' : 'bg-transparent border border-transparent hover:border-[var(--color-line)] hover:bg-white text-[var(--color-muted)] hover:text-[var(--color-ksp-text)]'} text-[12px] font-bold uppercase tracking-wider transition-colors mb-1 min-h-[48px] h-auto text-left break-words overflow-hidden`}>
              <span className="material-symbols-outlined notranslate text-[18px] shrink-0">map</span>
              <span className="flex-1 break-words leading-tight min-w-0">{isKannada ? 'ಸ್ಪೇಷಿಯಲ್ ಮ್ಯಾಪಿಂಗ್' : 'Spatial Mapping'}</span>
            </button>

            <button onClick={() => setCurrentIntent('DIRECTORY')} className={`flex items-center gap-3 px-3 py-3 ${currentIntent === 'DIRECTORY' ? 'bg-[var(--color-white-card)] border border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] text-[var(--color-ksp-text)]' : 'bg-transparent border border-transparent hover:border-[var(--color-line)] hover:bg-white text-[var(--color-muted)] hover:text-[var(--color-ksp-text)]'} text-[12px] font-bold uppercase tracking-wider transition-colors mb-1 min-h-[48px] h-auto text-left break-words overflow-hidden`}>
              <span className="material-symbols-outlined notranslate text-[18px] shrink-0">folder_open</span>
              <span className="flex-1 break-words leading-tight min-w-0">{isKannada ? 'ಕೇಸ್ ಡೈರೆಕ್ಟರಿ (ಎಫ್ಐಆರ್)' : 'Case Directory (FIR)'}</span>
            </button>

            <button onClick={() => setCurrentIntent('SUSPECTS')} className={`flex items-center gap-3 px-3 py-3 ${currentIntent === 'SUSPECTS' ? 'bg-[var(--color-white-card)] border border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] text-[var(--color-ksp-text)]' : 'bg-transparent border border-transparent hover:border-[var(--color-line)] hover:bg-white text-[var(--color-muted)] hover:text-[var(--color-ksp-text)]'} text-[12px] font-bold uppercase tracking-wider transition-colors mb-1 min-h-[48px] h-auto text-left break-words overflow-hidden`}>
              <span className="material-symbols-outlined notranslate text-[18px] shrink-0">contact_page</span>
              <span className="flex-1 break-words leading-tight min-w-0">{isKannada ? 'ಶಂಕಿತ ಡೋಸಿಯರ್‌ಗಳು' : 'Suspect Dossiers'}</span>
            </button>
          </div>

          <div className="p-4 border-t border-[var(--color-line)] bg-[#0A0A0A] text-white">
            <div className="font-mono text-[10px] flex flex-col gap-2">
              <div className="flex items-center gap-2 text-[#00FF00]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#00FF00] animate-blink"></span>
                <span>SECURE NODE // ONLINE</span>
              </div>
              <div className="text-white/60">
                OPERATOR: AMOGH M.
              </div>
              <div className="text-white/40 mt-1">
                SESSION: {sessionId}
              </div>
            </div>
          </div>
        </aside>

        {/* Column 2: Center Core Workspace */}
        <section className="flex-1 flex flex-col bg-[var(--color-page-bg)] relative pr-[380px]">

          {/* Top subtle fade overlay */}
          <div className="absolute top-0 w-full h-8 bg-gradient-to-b from-[var(--color-page-bg)] to-transparent z-10 pointer-events-none"></div>

          {/* Dynamic Intent Rendering */}
          {currentIntent === 'PATTERN' ? (
            <HeatmapComponent payload={currentPayload} />
          ) : currentIntent === 'NETWORK' ? (
            <NetworkComponent payload={currentPayload} />
          ) : currentIntent === 'PREDICT' ? (
            <PredictComponent payload={currentPayload} isKannada={isKannada} />
          ) : currentIntent === 'DIRECTORY' ? (
            <DirectoryComponent />
          ) : currentIntent === 'SUSPECTS' ? (
            <SuspectDirectoryComponent />
          ) : (
            /* Chat Stream Area (Fallback / LOOKUP) */
            <div className="flex-1 overflow-y-auto p-8 pb-40 flex flex-col gap-6">

              {/* Empty state — shown when no messages yet */}
              {messages.length === 0 && (
                <div className="flex-1 flex flex-col items-center justify-center text-center opacity-50">
                  <span className="material-symbols-outlined notranslate text-[48px] text-[var(--color-muted)] mb-3">radar</span>
                  <p className="text-[14px] text-[var(--color-muted)] font-mono">
                    {isKannada ? 'ತನಿಖೆ ಪ್ರಾರಂಭಿಸಲು ಪ್ರಶ್ನೆಯನ್ನು ನಮೂದಿಸಿ' : 'Enter a query to begin investigation'}
                  </p>
                </div>
              )}

              {/* Dynamic message rendering */}
              {messages.map((msg, idx) => (
                msg.role === 'user' ? (
                  /* ── User message bubble ── */
                  <div key={idx} className="flex gap-4 items-start max-w-[85%] animate-stream-in">
                    <div className="w-8 h-8 rounded-sm bg-[var(--color-white-card)] border border-[var(--color-line)] shrink-0 flex items-center justify-center">
                      <span className="material-symbols-outlined notranslate text-[16px] text-black">person</span>
                    </div>
                    <div className="bg-[var(--color-white-card)] border border-[var(--color-line)] p-4 shadow-sm text-[14px] leading-relaxed">
                      {msg.content}
                    </div>
                  </div>
                ) : (
                  /* ── Assistant message bubble with citations ── */
                  <div key={idx} className="flex gap-4 items-start max-w-[90%] self-end flex-row-reverse animate-stream-in w-full">
                    <div className="w-10 h-10 bg-black border-[3px] border-black shrink-0 flex items-center justify-center shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">
                      <span className="material-symbols-outlined notranslate text-[20px] text-[#FF4B2B]">auto_awesome</span>
                    </div>
                    <div className="bg-white border-[3px] border-black p-6 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] flex flex-col relative group transition-all w-full">
                      {/* Top Border Line */}
                      <div className="absolute top-0 left-0 w-full h-2 bg-[#FF4B2B]"></div>
                      
                      <div className="flex justify-between items-start mt-2 mb-4">
                        <div className="flex flex-col gap-1">
                           <span className="text-[10px] font-mono text-gray-500 uppercase tracking-widest">Intelligence Report</span>
                        </div>
                        {msg.intent && (
                          <div className="border border-gray-300 px-3 py-1 bg-gray-50 flex items-center justify-center">
                            <span className="text-[10px] font-mono text-gray-500 uppercase font-bold tracking-wider">INTENT: {msg.intent}</span>
                          </div>
                        )}
                      </div>

                      <div className="text-[14px] leading-relaxed text-black font-medium mb-6">
                        {msg.content}
                      </div>
                      
                      {/* Citations — retrieved FIR records */}
                      {msg.citations && msg.citations.length > 0 && (
                        <div className="flex flex-col gap-4 mt-2 border-t border-gray-200 pt-6">
                          <div className="text-[11px] font-mono font-bold text-gray-400 uppercase tracking-widest">
                            {isKannada ? 'ಮೂಲ ದಾಖಲೆಗಳು' : 'Source Records'} ({msg.citations.length})
                          </div>
                          {msg.citations.map((cite, cIdx) => (
                            <CitationCard key={cIdx} cite={cite} />
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )
              ))}

              {/* Loading indicator */}
              {isLoading && (
                <div className="flex gap-4 items-start max-w-[90%] self-end flex-row-reverse animate-stream-in">
                  <div className="w-8 h-8 rounded-sm bg-black border border-black shrink-0 flex items-center justify-center">
                    <span className="material-symbols-outlined notranslate text-[16px] text-[#FF4B2B] animate-spin">progress_activity</span>
                  </div>
                  <div className="bg-[var(--color-panel-bg)] border border-[var(--color-line)] p-4 shadow-sm flex flex-col gap-3">
                    <p className="text-[14px] leading-relaxed text-[var(--color-muted)] font-mono">
                      {isKannada ? 'ಗುಪ್ತಚರ ಪೈಪ್‌ಲೈನ್ ಪ್ರಕ್ರಿಯೆ ಮಾಡುತ್ತಿದೆ...' : 'Intelligence pipeline processing...'}
                    </p>
                  </div>
                </div>
              )}

              {/* Scroll anchor */}
              <div ref={chatEndRef} />

            </div>
          )}
        </section>

        {/* Floating Command Entry Bar */}
        <div className="fixed bottom-6 left-[20%] right-[380px] flex justify-center z-50 pointer-events-none">
          <div className="w-full max-w-2xl flex flex-col pointer-events-auto">
            <div className="bg-white border-[3px] border-black p-3 flex items-center shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">
              <span className="material-symbols-outlined notranslate text-[20px] text-gray-400 px-3 shrink-0">terminal</span>
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={isKannada ? 'ನಿಮ್ಮ ತನಿಖಾ ಪ್ರಶ್ನೆಯನ್ನು ನಮೂದಿಸಿ...' : 'Enter your investigation query...'}
                disabled={isLoading}
                className="flex-1 min-w-0 bg-transparent border-none outline-none text-[15px] font-mono focus:ring-0 px-2 text-black placeholder:text-gray-400"
              />
              <button
                onClick={handleSubmit}
                disabled={isLoading || !inputValue.trim()}
                className="w-12 h-12 shrink-0 bg-black flex items-center justify-center ml-2 relative group hover:bg-gray-900 transition-colors"
              >
                <span className="absolute inset-0 border border-[#F97316] animate-mic-glow group-hover:border-[2px]"></span>
                <span className="material-symbols-outlined notranslate text-[#F97316] relative z-10 text-[24px]">send</span>
              </button>
            </div>
            <div className="flex gap-2 mt-4 pl-2 opacity-80 hover:opacity-100 transition-opacity">
              <button onClick={() => setInputValue('/query-suspects ')} className="text-[11px] font-mono font-bold px-3 py-1.5 border border-black bg-white hover:bg-gray-100 text-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-transform active:translate-y-[1px] active:translate-x-[1px] active:shadow-none">/query-suspects</button>
              <button onClick={() => setInputValue('/run-heatmap ')} className="text-[11px] font-mono font-bold px-3 py-1.5 border border-black bg-white hover:bg-gray-100 text-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-transform active:translate-y-[1px] active:translate-x-[1px] active:shadow-none">/run-heatmap</button>
            </div>
          </div>
        </div>

        {/* Floating Telemetry/Matrix Panel */}
        <aside className="fixed right-6 top-[90px] bottom-6 w-[350px] border-[3px] border-black bg-white flex flex-col z-40 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">

          {/* Top Half: Matrix Visualization */}
          <div className="h-[50%] border-b border-[var(--color-line)] p-6 flex flex-col relative overflow-hidden bg-[#0A0A0A]">
            <div className="flex justify-between items-center mb-6 relative z-10">
              <h3 className="text-[11px] font-mono font-bold text-white uppercase tracking-widest flex items-center gap-2">
                <span className="material-symbols-outlined notranslate text-[14px]">share</span>
                {isKannada ? 'ಮ್ಯಾಟ್ರಿಕ್ಸ್ ಟೆಲಿಮೆಟ್ರಿ' : 'Matrix Telemetry'}
              </h3>
              <span className="w-2 h-2 bg-green-500 animate-blink"></span>
            </div>

            <div className="flex-1 flex flex-col justify-center gap-4 relative z-10">
              <div className="flex justify-between items-end border-b border-white/20 pb-2">
                <span className="text-[10px] font-mono text-white/60">{isKannada ? 'ಸಕ್ರಿಯ ಘಟಕಗಳು' : 'ACTIVE ENTITIES'}</span>
                <span className="text-[20px] font-bold text-white font-mono leading-none">{telemetry.active_entities.toLocaleString()}</span>
              </div>
              <div className="flex justify-between items-end border-b border-white/20 pb-2">
                <span className="text-[10px] font-mono text-white/60">{isKannada ? 'ಗುರುತಿಸಲಾದ ಕೊಂಡಿಗಳು' : 'IDENTIFIED EDGES'}</span>
                <span className="text-[20px] font-bold text-white font-mono leading-none">{telemetry.identified_edges.toLocaleString()}</span>
              </div>

              <div className="mt-4 border border-[#FF4B2B] bg-[#FF4B2B]/10 p-3 flex justify-between items-center">
                <span className="text-[10px] font-mono text-[#FF4B2B] font-bold tracking-wider">{isKannada ? 'ನಿರ್ಣಾಯಕ ವಿಲಕ್ಷಣಗಳು' : 'CRITICAL CROSS-ANOMALIES'}</span>
                <span className="text-[24px] font-bold text-[#FF4B2B] leading-none">{telemetry.critical_anomalies.toLocaleString()}</span>
              </div>
            </div>

            {/* Wireframe background animation (SVG) */}
            <div className="absolute inset-0 opacity-20 pointer-events-none overflow-hidden">
              <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
                <g stroke="#ffffff" strokeWidth="1" fill="none" opacity="0.5">
                  <line x1="10%" y1="20%" x2="40%" y2="60%" className="animate-edge-dash" strokeDasharray="4 4" />
                  <line x1="40%" y1="60%" x2="80%" y2="40%" className="animate-edge-dash" strokeDasharray="4 4" />
                  <line x1="80%" y1="40%" x2="50%" y2="80%" className="animate-edge-dash" strokeDasharray="4 4" />
                  <line x1="50%" y1="80%" x2="10%" y2="20%" className="animate-edge-dash" strokeDasharray="4 4" />
                </g>
                <circle cx="10%" cy="20%" r="4" fill="#ffffff" className="animate-node-pulse" />
                <circle cx="40%" cy="60%" r="4" fill="#ffffff" className="animate-node-pulse" />
                <circle cx="80%" cy="40%" r="4" fill="#FF4B2B" className="animate-node-pulse" />
                <circle cx="50%" cy="80%" r="4" fill="#ffffff" className="animate-node-pulse" />
              </svg>
            </div>
          </div>

          {/* Bottom Half: Live Threat Feed */}
          <div className="h-[50%] p-6 flex flex-col overflow-hidden bg-[var(--color-panel-bg)]">
            <h3 className="text-[11px] font-mono font-bold text-[var(--color-ksp-text)] uppercase tracking-widest flex items-center gap-2 mb-4 shrink-0">
              <span className="material-symbols-outlined notranslate text-[14px]">history</span>
              {isKannada ? 'ಲೈವ್ ಘಟನೆ ಫೀಡ್' : 'Live Incident Feed'}
            </h3>

            <div className="relative flex-1 overflow-hidden mask-image-vertical">
              <div className="absolute w-full flex flex-col gap-3 animate-ticker hover:[animation-play-state:paused]">

                {feed.length > 0 ? feed.map((item: { id: string | number; incident_date: string; fir_number: string; district: string; crime_category: string; description?: string }, idx: number) => (
                  <div key={`feed-${item.id}-${idx}`} className="bg-white border border-[var(--color-line)] p-3 shadow-sm">
                    <div className="text-[10px] font-mono text-[var(--color-muted)] mb-1">
                      [{new Date(item.incident_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}] {isKannada ? 'ಎಫ್ಐಆರ್' : 'FIR'} {item.fir_number} {isKannada ? 'ದಾಖಲಾಗಿದೆ' : 'Filed'} ({item.district})
                    </div>
                    <div className="text-[12px] font-bold text-[var(--color-ksp-text)]">
                      {item.crime_category} - {item.description?.substring(0, 50)}...
                    </div>
                  </div>
                )) : [1, 2, 3, 4, 5, 6, 7].map((i) => (
                  <div key={i} className="bg-white border border-[var(--color-line)] p-3 shadow-sm">
                    <div className="text-[10px] font-mono text-[var(--color-muted)] mb-1">
                      [Loading...] Fetching Incident Data
                    </div>
                    <div className="text-[12px] font-bold text-[var(--color-ksp-text)]">
                      Connecting to secure node...
                    </div>
                  </div>
                ))}

                {/* Duplicate for infinite scroll illusion */}
                {feed.length > 0 && feed.map((item: { id: string | number; incident_date: string; fir_number: string; district: string; crime_category: string; description?: string }, idx: number) => (
                  <div key={`feed-dup-${item.id}-${idx}`} className="bg-white border border-[var(--color-line)] p-3 shadow-sm">
                    <div className="text-[10px] font-mono text-[var(--color-muted)] mb-1">
                      [{new Date(item.incident_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}] FIR {item.fir_number} Filed ({item.district})
                    </div>
                    <div className="text-[12px] font-bold text-[var(--color-ksp-text)]">
                      {item.crime_category} - {item.description?.substring(0, 50)}...
                    </div>
                  </div>
                ))}

              </div>
            </div>

            {/* Custom CSS for mask image to fade out edges */}
            <style dangerouslySetInnerHTML={{
              __html: `
              .mask-image-vertical {
                mask-image: linear-gradient(to bottom, transparent, black 10%, black 90%, transparent);
                -webkit-mask-image: linear-gradient(to bottom, transparent, black 10%, black 90%, transparent);
              }
            `}} />
          </div>

        </aside>

      </main>
    </div>
  );
}
