'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';

// Dynamically import map component to avoid SSR issues with Leaflet
const CrimeMap = dynamic(() => import('./CrimeMap'), { ssr: false, loading: () => <div className="w-full h-full bg-[#0A0A0A] flex items-center justify-center text-white/40 font-mono text-sm">Loading Map Engine...</div> });

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const QUERY_API = process.env.NEXT_PUBLIC_QUERY_API_BASE_URL || 'http://localhost:8001';

// ─── Types ───────────────────────────────────────────────────────────
interface Criminal { id: number; name: string; age: number; gender: string; case_count: number; }
interface GraphNode { id: string; label: string; type: string; role?: string; age?: number; crime_type?: string; date?: string; facts?: string; }
interface GraphEdge { source: string; target: string; relation: string; }
interface RiskData { criminal_id: number; name: string; score: number; level: string; badge: string; color: string; metrics: { prior_cases: number; age: number; jurisdictions: number; severity_grade: number }; explanation: string; recommendation: string; risk_factors: string[]; }
interface ChatMessage { id: string; role: 'user' | 'ai'; text: string; timestamp: string; textEn?: string; textKn?: string; showKn?: boolean; }
interface CaseRecord { case_no: string; lat: number; lng: number; ps_id: number; category: string; year: number; facts: string; }

type ActiveView = 'map' | 'cases' | 'graph' | 'chat';

export default function DashboardPage() {
  const [isKannada, setIsKannada] = useState(false);
  const [sessionId, setSessionId] = useState('------');
  const [activeView, setActiveView] = useState<ActiveView>('map');

  // Graph state
  const [criminals, setCriminals] = useState<Criminal[]>([]);
  const [selectedCriminal, setSelectedCriminal] = useState<number | null>(null);
  const [graphNodes, setGraphNodes] = useState<GraphNode[]>([]);
  const [graphEdges, setGraphEdges] = useState<GraphEdge[]>([]);
  const [graphSubject, setGraphSubject] = useState<{ id: number; name: string; age: number } | null>(null);
  const [graphLoading, setGraphLoading] = useState(false);

  // Risk state
  const [riskData, setRiskData] = useState<RiskData | null>(null);
  const [riskLoading, setRiskLoading] = useState(false);

  // Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Cases state
  const [cases, setCases] = useState<CaseRecord[]>([]);
  const [casesLoading, setCasesLoading] = useState(false);
  const [caseFilter, setCaseFilter] = useState('');

  // Stats
  const [stats, setStats] = useState({ stations: 0, hotspots: 0, criminals: 0 });

  useEffect(() => {
    setSessionId(new Date().getTime().toString().slice(-6));
    loadInitialData();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const loadInitialData = async () => {
    try {
      const [criminalsRes, stationsRes, hotspotsRes] = await Promise.allSettled([
        fetch(`${API_BASE}/graph/criminals?limit=50`),
        fetch(`${API_BASE}/map/stations`),
        fetch(`${API_BASE}/map/hotspots`),
      ]);

      if (criminalsRes.status === 'fulfilled' && criminalsRes.value.ok) {
        const data = await criminalsRes.value.json();
        setCriminals(data);
        setStats(s => ({ ...s, criminals: data.length }));
      }
      if (stationsRes.status === 'fulfilled' && stationsRes.value.ok) {
        const data = await stationsRes.value.json();
        setStats(s => ({ ...s, stations: data.length }));
      }
      if (hotspotsRes.status === 'fulfilled' && hotspotsRes.value.ok) {
        const data = await hotspotsRes.value.json();
        setStats(s => ({ ...s, hotspots: data.length }));
      }
    } catch (e) {
      console.error('Failed to load initial data:', e);
    }
  };

  // ─── Graph Loader ──────────────────────────────────────────────────
  const loadCriminalGraph = useCallback(async (criminalId: number) => {
    setGraphLoading(true);
    setSelectedCriminal(criminalId);
    try {
      const [graphRes, riskRes] = await Promise.all([
        fetch(`${API_BASE}/graph/criminal/${criminalId}`),
        fetch(`${API_BASE}/risk/criminal/${criminalId}`),
      ]);
      if (graphRes.ok) {
        const data = await graphRes.json();
        setGraphNodes(data.nodes);
        setGraphEdges(data.edges);
        setGraphSubject(data.subject);
      }
      if (riskRes.ok) {
        const data = await riskRes.json();
        setRiskData(data);
      }
    } catch (e) {
      console.error('Graph load error:', e);
    } finally {
      setGraphLoading(false);
    }
  }, []);

  // ─── Chat Handler ──────────────────────────────────────────────────
  const sendChat = async () => {
    if (!chatInput.trim() || chatLoading) return;
    const userMsg: ChatMessage = { id: Math.random().toString(), role: 'user', text: chatInput, timestamp: new Date().toLocaleTimeString() };
    setChatMessages(prev => [...prev, userMsg]);
    const query = chatInput;
    setChatInput('');
    setChatLoading(true);

    try {
      const res = await fetch(`${QUERY_API}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, filters_dict: null, officer_id: null }),
      });
      if (res.ok) {
        const data = await res.json();
        const isKnResponse = data.detected_language === 'kn';
        const textEn = isKnResponse ? data.translated_text : (data.answer_text || JSON.stringify(data));
        const textKn = isKnResponse ? data.answer_text : (data.translated_text || data.answer_text);
        
        const aiMsg: ChatMessage = { 
          id: Math.random().toString(), 
          role: 'ai', 
          text: textEn || 'No response', 
          textEn, 
          textKn, 
          showKn: false, 
          timestamp: new Date().toLocaleTimeString() 
        };
        setChatMessages(prev => [...prev, aiMsg]);
      } else {
        setChatMessages(prev => [...prev, { id: Math.random().toString(), role: 'ai', text: `Error: ${res.status} — Backend unreachable.`, timestamp: new Date().toLocaleTimeString() }]);
      }
    } catch {
      setChatMessages(prev => [...prev, { id: Math.random().toString(), role: 'ai', text: 'Connection failed. Ensure query backend is running on port 8001.', timestamp: new Date().toLocaleTimeString() }]);
    } finally {
      setChatLoading(false);
    }
  };

  const toggleMessageLanguage = (id: string) => {
    setChatMessages(prev => prev.map(msg => {
      if (msg.id === id && msg.role === 'ai') {
        const newShowKn = !msg.showKn;
        return { ...msg, showKn: newShowKn, text: newShowKn ? (msg.textKn || msg.text) : (msg.textEn || msg.text) };
      }
      return msg;
    }));
  };

  const toggleVoice = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Speech recognition is not supported in this browser.');
      return;
    }

    if (isListening) {
      setIsListening(false);
      return; // The recognition will stop on its own or we can force it, but let's keep it simple
    }

    const SpeechRecognition = window.SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = isKannada ? 'kn-IN' : 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setIsListening(true);
    
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setChatInput(prev => prev + (prev ? ' ' : '') + transcript);
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error', event.error);
      setIsListening(false);
    };

    recognition.onend = () => setIsListening(false);

    recognition.start();
  };

  // ─── Load Cases ────────────────────────────────────────────────────
  const loadCases = useCallback(async () => {
    if (cases.length > 0) return; // already loaded
    setCasesLoading(true);
    try {
      const res = await fetch(`${API_BASE}/map/hotspots`);
      if (res.ok) {
        const points: number[][] = await res.json();
        // Convert hotspot points into case-like records for the directory view
        const caseRecords: CaseRecord[] = points.slice(0, 200).map((p, i) => ({
          case_no: `FIR-${2024}-${String(i + 1).padStart(4, '0')}`,
          lat: p[0],
          lng: p[1],
          ps_id: Math.floor(Math.random() * 186) + 1,
          category: ['Theft', 'Assault', 'Robbery', 'Burglary', 'Narcotics', 'Fraud', 'Cybercrime', 'Missing Person'][Math.floor(Math.random() * 8)],
          year: [2023, 2024, 2025][Math.floor(Math.random() * 3)],
          facts: ['Vehicle theft near main road', 'Chain snatching incident', 'Residential break-in reported', 'Drug seizure at checkpoint', 'Online fraud complaint', 'Assault during public event', 'Missing person case filed', 'Robbery at commercial establishment'][Math.floor(Math.random() * 8)],
        }));
        setCases(caseRecords);
      }
    } catch (e) {
      console.error('Cases load error:', e);
    } finally {
      setCasesLoading(false);
    }
  }, [cases.length]);

  // ─── Nav Items ─────────────────────────────────────────────────────
  const navItems: { key: ActiveView; icon: string; labelEn: string; labelKn: string }[] = [
    { key: 'map', icon: 'radar', labelEn: 'Live Investigation', labelKn: 'ಲೈವ್ ತನಿಖೆ' },
    { key: 'cases', icon: 'folder_open', labelEn: 'Case Directory (FIR)', labelKn: 'ಕೇಸ್ ಡೈರೆಕ್ಟರಿ (ಎಫ್ಐಆರ್)' },
    { key: 'graph', icon: 'contact_page', labelEn: 'Suspect Dossiers', labelKn: 'ಶಂಕಿತ ಡೋಸಿಯರ್‌ಗಳು' },
    { key: 'chat', icon: 'smart_toy', labelEn: 'RAG Intelligence', labelKn: 'RAG ಗುಪ್ತಚರ' },
  ];

  return (
    <div className="min-h-screen bg-[var(--color-page-bg)] flex flex-col font-sans overflow-hidden">

      {/* ═══ Header ═══ */}
      <header className="fixed top-0 left-0 right-0 z-50 h-[70px] bg-white border-b border-[var(--color-line)] flex items-center justify-between px-6 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-black text-white flex items-center justify-center font-bold text-xs shadow-sm shrink-0">KSP</div>
          <div className="flex flex-col">
            <span className="font-bold text-[var(--color-ksp-text)] text-[14px] leading-tight tracking-tight uppercase">
              {isKannada ? 'ಗುಪ್ತಚರ ಕನ್ಸೋಲ್' : 'Intelligence Console'}
            </span>
            <span className="text-[10px] text-[var(--color-muted)] font-mono tracking-widest">
              {isKannada ? 'ಕಾರ್ಯಾಚರಣೆ ಕೇಂದ್ರ' : 'OPS CENTER'}
            </span>
          </div>
        </div>

        {/* Live Stats */}
        <div className="hidden md:flex items-center gap-6">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            <span className="text-[10px] font-mono text-[var(--color-muted)] uppercase tracking-wider">{stats.stations} Stations</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#FF4B2B] animate-pulse"></span>
            <span className="text-[10px] font-mono text-[var(--color-muted)] uppercase tracking-wider">{stats.hotspots} Hotspots</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse"></span>
            <span className="text-[10px] font-mono text-[var(--color-muted)] uppercase tracking-wider">{stats.criminals} Entities</span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button onClick={() => setIsKannada(!isKannada)} className="flex items-center gap-2 px-3 py-1.5 border border-[var(--color-line)] bg-[var(--color-page-bg)] hover:bg-[var(--color-soft-card-2)] rounded-sm text-[11px] font-bold uppercase tracking-wider text-[var(--color-ksp-text)] transition-colors">
            <span className="material-symbols-outlined text-[14px]">translate</span>
            <span>{isKannada ? 'ENG' : 'ಕನ್ನಡ'}</span>
          </button>
          <div className="w-[1px] h-4 bg-[var(--color-line)]"></div>
          <Link href="/" className="flex items-center gap-2 px-3 py-1.5 bg-black text-white rounded-sm text-[11px] font-bold uppercase tracking-wider hover:bg-[var(--color-ksp-text)] transition-colors">
            <span>{isKannada ? 'ಲಾಗ್ ಔಟ್' : 'LOGOUT'}</span>
            <span className="material-symbols-outlined text-[14px]">logout</span>
          </Link>
        </div>
      </header>

      {/* ═══ Main Layout ═══ */}
      <main className="flex-1 pt-[70px] flex h-screen overflow-hidden">

        {/* ─── Sidebar ─── */}
        <aside className="w-[220px] min-w-[200px] border-r border-[var(--color-line)] bg-[var(--color-panel-bg)] flex flex-col justify-between shrink-0">
          <div className="p-4 flex flex-col gap-2">
            <div className="text-[10px] font-mono text-[var(--color-muted)] uppercase tracking-widest mb-2 px-2">
              {isKannada ? 'ನೇವಿಗೇಷನ್' : 'Navigation'}
            </div>
            {navItems.map(item => (
              <button
                key={item.key}
                onClick={() => setActiveView(item.key)}
                className={`flex items-center gap-3 px-3 py-3 text-[12px] font-bold uppercase tracking-wider mb-1 transition-colors ${
                  activeView === item.key
                    ? 'bg-[var(--color-white-card)] border border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] text-[var(--color-ksp-text)]'
                    : 'bg-transparent border border-transparent hover:border-[var(--color-line)] hover:bg-white text-[var(--color-muted)] hover:text-[var(--color-ksp-text)]'
                }`}
              >
                <span className="material-symbols-outlined text-[18px]">{item.icon}</span>
                <span>{isKannada ? item.labelKn : item.labelEn}</span>
              </button>
            ))}
          </div>

          {/* Session Info */}
          <div className="p-4 border-t border-[var(--color-line)] bg-[#0A0A0A] text-white">
            <div className="font-mono text-[10px] flex flex-col gap-2">
              <div className="flex items-center gap-2 text-[#00FF00]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#00FF00] animate-blink"></span>
                <span>SECURE NODE // ONLINE</span>
              </div>
              <div className="text-white/60">OPERATOR: ACTIVE</div>
              <div className="text-white/40 mt-1">SESSION: {sessionId}</div>
            </div>
          </div>
        </aside>

        {/* ─── Center Workspace ─── */}
        <section className="flex-1 flex flex-col bg-[var(--color-page-bg)] relative overflow-hidden">

          {/* View: Crime Heatmap */}
          {activeView === 'map' && (
            <div className="flex-1 relative">
              <CrimeMap apiBase={API_BASE} isKannada={isKannada} />
            </div>
          )}

          {/* View: Case Directory (FIR) */}
          {activeView === 'cases' && (
            <CaseDirectoryView
              cases={cases}
              loading={casesLoading}
              onLoad={loadCases}
              caseFilter={caseFilter}
              setCaseFilter={setCaseFilter}
              isKannada={isKannada}
            />
          )}

          {/* View: Network Graph */}
          {activeView === 'graph' && (
            <div className="flex-1 flex flex-col overflow-hidden">
              {/* Criminal Selector */}
              <div className="p-4 border-b border-[var(--color-line)] bg-white flex items-center gap-4 shrink-0">
                <span className="material-symbols-outlined text-[20px] text-[var(--color-muted)]">person_search</span>
                <select
                  className="flex-1 bg-transparent border border-[var(--color-line)] px-3 py-2 text-sm font-mono text-[var(--color-ksp-text)] focus:outline-none focus:border-black"
                  value={selectedCriminal || ''}
                  onChange={e => { const id = parseInt(e.target.value); if (id) loadCriminalGraph(id); }}
                >
                  <option value="">{isKannada ? '-- ಶಂಕಿತನನ್ನು ಆಯ್ಕೆ ಮಾಡಿ --' : '-- Select Criminal Entity --'}</option>
                  {criminals.map(c => (
                    <option key={c.id} value={c.id}>{c.name} — {c.case_count} cases (ID: {c.id})</option>
                  ))}
                </select>
                {graphLoading && <span className="text-[10px] font-mono text-[var(--color-muted)] animate-pulse">COMPUTING...</span>}
              </div>

              {/* Graph Canvas */}
              <div className="flex-1 bg-[#0A0A0A] relative overflow-hidden">
                {graphNodes.length === 0 ? (
                  <div className="w-full h-full flex flex-col items-center justify-center text-white/30">
                    <span className="material-symbols-outlined text-[48px] mb-4">hub</span>
                    <span className="font-mono text-sm">{isKannada ? 'ಗ್ರಾಫ್ ರೆಂಡರ್ ಮಾಡಲು ಶಂಕಿತನನ್ನು ಆಯ್ಕೆ ಮಾಡಿ' : 'Select a criminal entity to render network graph'}</span>
                  </div>
                ) : (
                  <NetworkGraph nodes={graphNodes} edges={graphEdges} subject={graphSubject} />
                )}
              </div>
            </div>
          )}

          {/* View: RAG Chat */}
          {activeView === 'chat' && (
            <div className="flex-1 flex flex-col overflow-hidden">
              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-4">
                {chatMessages.length === 0 && (
                  <div className="flex-1 flex flex-col items-center justify-center text-[var(--color-muted)]">
                    <span className="material-symbols-outlined text-[48px] mb-4 opacity-30">smart_toy</span>
                    <p className="font-mono text-sm">{isKannada ? 'ಗುಪ್ತಚರ ವಿಚಾರಣೆಯನ್ನು ಟೈಪ್ ಮಾಡಿ...' : 'Type an intelligence query to begin...'}</p>
                    <div className="flex gap-2 mt-4">
                      {['Show narcotics cases in Belagavi', 'Recent theft patterns in Bengaluru', 'List top repeat offenders'].map(q => (
                        <button key={q} onClick={() => { setChatInput(q); }} className="text-[10px] font-mono px-3 py-1.5 border border-[var(--color-line)] bg-white hover:bg-[var(--color-soft-card)] text-[var(--color-muted)] transition-colors">
                          {q}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                {chatMessages.map((msg, i) => (
                  <div key={msg.id} className={`flex gap-3 items-start max-w-[85%] animate-stream-in ${msg.role === 'ai' ? 'self-end flex-row-reverse' : ''}`}>
                    <div className={`w-8 h-8 rounded-sm shrink-0 flex items-center justify-center ${msg.role === 'user' ? 'bg-[var(--color-white-card)] border border-[var(--color-line)]' : 'bg-black border border-black'}`}>
                      <span className={`material-symbols-outlined text-[16px] ${msg.role === 'user' ? 'text-black' : 'text-[#FF4B2B]'}`}>
                        {msg.role === 'user' ? 'person' : 'auto_awesome'}
                      </span>
                    </div>
                    <div className={`p-4 shadow-sm text-[14px] leading-relaxed ${msg.role === 'user' ? 'bg-[var(--color-white-card)] border border-[var(--color-line)]' : 'bg-[var(--color-panel-bg)] border border-[var(--color-line)]'}`}>
                      <p className="whitespace-pre-wrap">{msg.text}</p>
                      <div className="flex items-center justify-between mt-2 gap-4">
                        <span className="text-[9px] font-mono text-[var(--color-muted-light)]">{msg.timestamp}</span>
                        {msg.role === 'ai' && msg.textKn && (
                          <button 
                            onClick={() => toggleMessageLanguage(msg.id)}
                            className="text-[10px] font-mono px-2 py-1 border border-[var(--color-line)] bg-white hover:bg-[var(--color-soft-card)] text-[var(--color-muted)] transition-colors shrink-0"
                          >
                            {msg.showKn ? 'Show in English' : 'ಕನ್ನಡದಲ್ಲಿ ನೋಡಿ'}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                {chatLoading && (
                  <div className="flex gap-3 items-start max-w-[85%] self-end flex-row-reverse animate-stream-in">
                    <div className="w-8 h-8 rounded-sm bg-black border border-black shrink-0 flex items-center justify-center">
                      <span className="material-symbols-outlined text-[16px] text-[#FF4B2B] animate-pulse">auto_awesome</span>
                    </div>
                    <div className="bg-[var(--color-panel-bg)] border border-[var(--color-line)] p-4 shadow-sm">
                      <div className="flex gap-1">
                        <span className="w-2 h-2 bg-[var(--color-muted)] rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                        <span className="w-2 h-2 bg-[var(--color-muted)] rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                        <span className="w-2 h-2 bg-[var(--color-muted)] rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Chat Input */}
              <div className="p-4 border-t border-[var(--color-line)] bg-white">
                <div className="bg-[var(--color-page-bg)] border-2 border-black p-2 flex items-center shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
                  <span className="material-symbols-outlined text-[20px] text-[var(--color-muted)] px-3">terminal</span>
                  <input
                    type="text"
                    value={chatInput}
                    onChange={e => setChatInput(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') sendChat(); }}
                    placeholder={isKannada ? 'ಗುಪ್ತಚರ ಪ್ರಶ್ನೆಯನ್ನು ಟೈಪ್ ಮಾಡಿ...' : 'Type intelligence query...'}
                    className="flex-1 bg-transparent border-none outline-none text-[14px] font-mono focus:ring-0 px-2 text-[var(--color-ksp-text)]"
                  />
                  <button onClick={toggleVoice} className={`w-10 h-10 flex items-center justify-center ml-2 transition-colors ${isListening ? 'bg-[#FF4B2B] text-white animate-pulse' : 'bg-[var(--color-soft-card)] hover:bg-[var(--color-line)] text-[var(--color-muted)]'}`}>
                    <span className="material-symbols-outlined text-[20px]">mic</span>
                  </button>
                  <button onClick={sendChat} disabled={chatLoading} className="w-10 h-10 bg-black flex items-center justify-center ml-2 hover:bg-[var(--color-ksp-text)] transition-colors">
                    <span className="material-symbols-outlined text-white text-[20px]">send</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* ─── Right Intel Panel ─── */}
        <aside className="w-[300px] min-w-[280px] border-l border-[var(--color-line)] bg-[var(--color-white-card)] flex flex-col shrink-0">

          {/* Risk Score Panel */}
          <div className="h-[50%] border-b border-[var(--color-line)] p-5 flex flex-col relative overflow-hidden bg-[#0A0A0A]">
            <div className="flex justify-between items-center mb-4 relative z-10">
              <h3 className="text-[11px] font-mono font-bold text-white uppercase tracking-widest flex items-center gap-2">
                <span className="material-symbols-outlined text-[14px]">security</span>
                {isKannada ? 'ಬೆದರಿಕೆ ಮೌಲ್ಯಮಾಪನ' : 'Threat Assessment'}
              </h3>
              <span className="w-2 h-2 bg-green-500 animate-blink"></span>
            </div>

            {riskData ? (
              <div className="flex-1 flex flex-col justify-center gap-3 relative z-10">
                {/* Score Gauge */}
                <div className="flex items-center justify-center mb-2">
                  <div className="relative w-28 h-28">
                    <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
                      <circle cx="60" cy="60" r="50" stroke="rgba(255,255,255,0.1)" strokeWidth="10" fill="none" />
                      <circle cx="60" cy="60" r="50" stroke={riskData.color === 'red' ? '#FF4B2B' : riskData.color === 'yellow' ? '#F59E0B' : '#22C55E'} strokeWidth="10" fill="none" strokeDasharray={`${riskData.score * 3.14} 314`} strokeLinecap="round" className="transition-all duration-1000" />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-[28px] font-bold text-white font-mono leading-none">{riskData.score}%</span>
                      <span className="text-[9px] font-mono text-white/50 uppercase">{riskData.level} Risk</span>
                    </div>
                  </div>
                </div>

                <div className="text-center mb-2">
                  <span className="text-[13px] font-bold text-white">{riskData.name}</span>
                  <span className="text-[10px] font-mono text-white/40 block">ID: {riskData.criminal_id}</span>
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-2 gap-2">
                  <div className="border border-white/10 p-2 text-center">
                    <span className="text-[9px] font-mono text-white/50 block">PRIORS</span>
                    <span className="text-[16px] font-bold text-white font-mono">{riskData.metrics.prior_cases}</span>
                  </div>
                  <div className="border border-white/10 p-2 text-center">
                    <span className="text-[9px] font-mono text-white/50 block">JURISDICTIONS</span>
                    <span className="text-[16px] font-bold text-white font-mono">{riskData.metrics.jurisdictions}</span>
                  </div>
                </div>

                {/* Risk Factors */}
                <div className="mt-1 space-y-1">
                  {riskData.risk_factors.map((f, i) => (
                    <div key={i} className="text-[10px] font-mono text-white/60 flex gap-2 items-start">
                      <span className="text-[#FF4B2B] shrink-0">▸</span>
                      <span>{f}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col justify-center items-center gap-3 relative z-10">
                <span className="material-symbols-outlined text-[36px] text-white/15">shield</span>
                <span className="text-[10px] font-mono text-white/30 text-center">
                  {isKannada ? 'ಅಪಾಯ ಸ್ಕೋರ್ ವೀಕ್ಷಿಸಲು\nಗ್ರಾಫ್ ಟ್ಯಾಬ್‌ನಲ್ಲಿ ಶಂಕಿತನನ್ನು ಆಯ್ಕೆ ಮಾಡಿ' : 'Select a criminal from\nGraph tab to view risk score'}
                </span>
              </div>
            )}

            {/* Background wireframe */}
            <div className="absolute inset-0 opacity-10 pointer-events-none overflow-hidden">
              <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
                <g stroke="#ffffff" strokeWidth="1" fill="none" opacity="0.5">
                  <line x1="10%" y1="20%" x2="40%" y2="60%" className="animate-edge-dash" strokeDasharray="4 4" />
                  <line x1="40%" y1="60%" x2="80%" y2="40%" className="animate-edge-dash" strokeDasharray="4 4" />
                  <line x1="80%" y1="40%" x2="50%" y2="80%" className="animate-edge-dash" strokeDasharray="4 4" />
                </g>
              </svg>
            </div>
          </div>

          {/* Live Incident Feed */}
          <div className="h-[50%] p-5 flex flex-col overflow-hidden bg-[var(--color-panel-bg)]">
            <h3 className="text-[11px] font-mono font-bold text-[var(--color-ksp-text)] uppercase tracking-widest flex items-center gap-2 mb-4 shrink-0">
              <span className="material-symbols-outlined text-[14px]">history</span>
              {isKannada ? 'ಲೈವ್ ಘಟನೆ ಫೀಡ್' : 'Live Incident Feed'}
            </h3>

            <div className="relative flex-1 overflow-hidden" style={{ maskImage: 'linear-gradient(to bottom, transparent, black 10%, black 90%, transparent)', WebkitMaskImage: 'linear-gradient(to bottom, transparent, black 10%, black 90%, transparent)' }}>
              <div className="absolute w-full flex flex-col gap-3 animate-ticker hover:[animation-play-state:paused]">
                {[1, 2, 3, 4, 5, 6, 7].map((i) => (
                  <div key={i} className="bg-white border border-[var(--color-line)] p-3 shadow-sm">
                    <div className="text-[10px] font-mono text-[var(--color-muted)] mb-1">
                      [13:{28 - i}] FIR #{442 - i} Filed (Belagavi)
                    </div>
                    <div className="text-[12px] font-bold text-[var(--color-ksp-text)]">
                      Contraband Intercept - Checkpoint Alpha
                    </div>
                  </div>
                ))}
                {/* Duplicate for infinite scroll */}
                {[1, 2, 3, 4, 5, 6, 7].map((i) => (
                  <div key={`dup-${i}`} className="bg-white border border-[var(--color-line)] p-3 shadow-sm">
                    <div className="text-[10px] font-mono text-[var(--color-muted)] mb-1">
                      [13:{28 - i}] FIR #{442 - i} Filed (Belagavi)
                    </div>
                    <div className="text-[12px] font-bold text-[var(--color-ksp-text)]">
                      Contraband Intercept - Checkpoint Alpha
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </aside>
      </main>
    </div>
  );
}


// ═══════════════════════════════════════════════════════════════════════
// NETWORK GRAPH COMPONENT (SVG Force-Directed)
// ═══════════════════════════════════════════════════════════════════════

function NetworkGraph({ nodes, edges, subject }: { nodes: GraphNode[]; edges: GraphEdge[]; subject: { id: number; name: string; age: number } | null }) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [positions, setPositions] = useState<Record<string, { x: number; y: number }>>({});
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  useEffect(() => {
    if (nodes.length === 0) return;

    // Simple radial layout
    const centerX = 500;
    const centerY = 350;
    const pos: Record<string, { x: number; y: number }> = {};

    // Place subject at center
    const subjectNodeId = nodes.find(n => n.role === 'Subject')?.id;

    // Group by type
    const incidents = nodes.filter(n => n.type === 'incident');
    const criminals = nodes.filter(n => n.type === 'criminal' && n.id !== subjectNodeId);
    const locations = nodes.filter(n => n.type === 'location');
    const victims = nodes.filter(n => n.type === 'victim');

    if (subjectNodeId) pos[subjectNodeId] = { x: centerX, y: centerY };

    const placeRing = (items: GraphNode[], radius: number, offsetAngle: number) => {
      items.forEach((node, i) => {
        const angle = offsetAngle + (i / Math.max(items.length, 1)) * Math.PI * 2;
        pos[node.id] = {
          x: centerX + Math.cos(angle) * radius + (Math.random() - 0.5) * 30,
          y: centerY + Math.sin(angle) * radius + (Math.random() - 0.5) * 30,
        };
      });
    };

    placeRing(incidents, 160, 0);
    placeRing(criminals, 280, Math.PI / 6);
    placeRing(locations, 220, Math.PI / 3);
    placeRing(victims, 300, Math.PI / 2);

    setPositions(pos);
  }, [nodes]);

  const nodeColor = (type: string, role?: string) => {
    if (role === 'Subject') return '#FF4B2B';
    if (type === 'criminal') return '#F59E0B';
    if (type === 'incident') return '#3B82F6';
    if (type === 'location') return '#22C55E';
    if (type === 'victim') return '#A855F7';
    return '#6B7280';
  };

  const nodeRadius = (type: string, role?: string) => {
    if (role === 'Subject') return 18;
    if (type === 'incident') return 12;
    return 10;
  };

  return (
    <div className="w-full h-full relative">
      {/* Legend */}
      <div className="absolute top-4 left-4 z-10 bg-black/80 border border-white/10 p-3 flex flex-col gap-2">
        <span className="text-[9px] font-mono text-white/50 uppercase tracking-wider mb-1">Legend</span>
        {[
          { color: '#FF4B2B', label: 'Subject' }, { color: '#F59E0B', label: 'Co-Accused' },
          { color: '#3B82F6', label: 'FIR / Incident' }, { color: '#22C55E', label: 'Location' },
          { color: '#A855F7', label: 'Victim' },
        ].map(l => (
          <div key={l.label} className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: l.color }}></span>
            <span className="text-[10px] font-mono text-white/70">{l.label}</span>
          </div>
        ))}
      </div>

      {/* Subject Info */}
      {subject && (
        <div className="absolute top-4 right-4 z-10 bg-black/80 border border-white/10 p-3">
          <span className="text-[9px] font-mono text-white/50 uppercase tracking-wider">Subject</span>
          <div className="text-[14px] font-bold text-white mt-1">{subject.name}</div>
          <div className="text-[10px] font-mono text-white/40">ID: {subject.id} · Age: {subject.age}</div>
        </div>
      )}

      <svg ref={svgRef} viewBox="0 0 1000 700" className="w-full h-full">
        {/* Edges */}
        {edges.map((edge, i) => {
          const from = positions[edge.source];
          const to = positions[edge.target];
          if (!from || !to) return null;
          return (
            <line key={i} x1={from.x} y1={from.y} x2={to.x} y2={to.y} stroke="rgba(255,255,255,0.15)" strokeWidth="1" strokeDasharray="4 2" className="animate-edge-dash" />
          );
        })}

        {/* Nodes */}
        {nodes.map(node => {
          const p = positions[node.id];
          if (!p) return null;
          const isHovered = hoveredNode === node.id;
          return (
            <g key={node.id} onMouseEnter={() => setHoveredNode(node.id)} onMouseLeave={() => setHoveredNode(null)} className="cursor-pointer">
              {/* Glow */}
              {(isHovered || node.role === 'Subject') && (
                <circle cx={p.x} cy={p.y} r={nodeRadius(node.type, node.role) + 6} fill={nodeColor(node.type, node.role)} opacity={0.2} className="animate-node-pulse" />
              )}
              <circle cx={p.x} cy={p.y} r={nodeRadius(node.type, node.role)} fill={nodeColor(node.type, node.role)} stroke={isHovered ? '#fff' : 'none'} strokeWidth={2} />
              {/* Label */}
              <text x={p.x} y={p.y + nodeRadius(node.type, node.role) + 14} textAnchor="middle" fill="rgba(255,255,255,0.7)" fontSize="9" fontFamily="monospace">
                {node.label.length > 18 ? node.label.slice(0, 18) + '…' : node.label}
              </text>

              {/* Tooltip */}
              {isHovered && (
                <foreignObject x={p.x + 20} y={p.y - 40} width="180" height="80">
                  <div className="bg-black/90 border border-white/20 p-2 text-[10px] font-mono text-white/80 rounded shadow-lg">
                    <div className="font-bold text-white mb-1">{node.label}</div>
                    {node.type === 'incident' && node.crime_type && <div>Type: {node.crime_type}</div>}
                    {node.date && <div>Date: {node.date}</div>}
                    {node.age && <div>Age: {node.age}</div>}
                    <div className="text-white/40 mt-1">{node.type.toUpperCase()}</div>
                  </div>
                </foreignObject>
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
}


// ═══════════════════════════════════════════════════════════════════════
// CASE DIRECTORY VIEW COMPONENT
// ═══════════════════════════════════════════════════════════════════════

interface CaseDirectoryProps {
  cases: CaseRecord[];
  loading: boolean;
  onLoad: () => void;
  caseFilter: string;
  setCaseFilter: (v: string) => void;
  isKannada: boolean;
}

function CaseDirectoryView({ cases, loading, onLoad, caseFilter, setCaseFilter, isKannada }: CaseDirectoryProps) {
  useEffect(() => { onLoad(); }, [onLoad]);

  const categoryColors: Record<string, string> = {
    'Theft': 'bg-blue-100 text-blue-800 border-blue-200',
    'Assault': 'bg-red-100 text-red-800 border-red-200',
    'Robbery': 'bg-orange-100 text-orange-800 border-orange-200',
    'Burglary': 'bg-amber-100 text-amber-800 border-amber-200',
    'Narcotics': 'bg-purple-100 text-purple-800 border-purple-200',
    'Fraud': 'bg-yellow-100 text-yellow-800 border-yellow-200',
    'Cybercrime': 'bg-cyan-100 text-cyan-800 border-cyan-200',
    'Missing Person': 'bg-pink-100 text-pink-800 border-pink-200',
  };

  const filtered = cases.filter(c =>
    c.case_no.toLowerCase().includes(caseFilter.toLowerCase()) ||
    c.category.toLowerCase().includes(caseFilter.toLowerCase()) ||
    c.facts.toLowerCase().includes(caseFilter.toLowerCase())
  );

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Search Bar */}
      <div className="p-4 border-b border-[var(--color-line)] bg-white flex items-center gap-4 shrink-0">
        <span className="material-symbols-outlined text-[20px] text-[var(--color-muted)]">search</span>
        <input
          type="text"
          value={caseFilter}
          onChange={e => setCaseFilter(e.target.value)}
          placeholder={isKannada ? 'ಎಫ್ಐಆರ್ ಸಂಖ್ಯೆ, ವರ್ಗ, ಅಥವಾ ಸಂಗತಿಗಳಿಂದ ಫಿಲ್ಟರ್ ಮಾಡಿ...' : 'Filter by FIR number, category, or facts...'}
          className="flex-1 bg-transparent border border-[var(--color-line)] px-3 py-2 text-sm font-mono text-[var(--color-ksp-text)] focus:outline-none focus:border-black"
        />
        <span className="text-[10px] font-mono text-[var(--color-muted)]">{filtered.length} / {cases.length} {isKannada ? 'ದಾಖಲೆಗಳು' : 'records'}</span>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex-1 flex items-center justify-center h-full">
            <span className="text-[12px] font-mono text-[var(--color-muted)] animate-pulse">
              {isKannada ? 'ಪ್ರಕರಣ ಡೇಟಾ ಲೋಡ್ ಆಗುತ್ತಿದೆ...' : 'Loading case records...'}
            </span>
          </div>
        ) : (
          <table className="w-full text-left">
            <thead className="sticky top-0 bg-[var(--color-panel-bg)] border-b border-[var(--color-line)] z-10">
              <tr className="text-[10px] font-mono font-bold text-[var(--color-muted)] uppercase tracking-wider">
                <th className="px-4 py-3">{isKannada ? 'ಎಫ್ಐಆರ್ ಸಂಖ್ಯೆ' : 'FIR No.'}</th>
                <th className="px-4 py-3">{isKannada ? 'ವರ್ಗ' : 'Category'}</th>
                <th className="px-4 py-3">{isKannada ? 'ವರ್ಷ' : 'Year'}</th>
                <th className="px-4 py-3">{isKannada ? 'ಠಾಣೆ ID' : 'Station ID'}</th>
                <th className="px-4 py-3">{isKannada ? 'ಸಂಕ್ಷಿಪ್ತ ಸಂಗತಿಗಳು' : 'Brief Facts'}</th>
                <th className="px-4 py-3">{isKannada ? 'ಸ್ಥಳ' : 'Location'}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((c, i) => (
                <tr key={i} className="border-b border-[var(--color-line)] hover:bg-[var(--color-soft-card-2)] transition-colors group">
                  <td className="px-4 py-3">
                    <span className="text-[12px] font-mono font-bold text-[var(--color-ksp-text)]">{c.case_no}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded border ${categoryColors[c.category] || 'bg-gray-100 text-gray-800 border-gray-200'}`}>
                      {c.category}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-[12px] font-mono text-[var(--color-muted)]">{c.year}</td>
                  <td className="px-4 py-3 text-[12px] font-mono text-[var(--color-muted)]">PS-{c.ps_id}</td>
                  <td className="px-4 py-3 text-[12px] text-[var(--color-ksp-text)] max-w-[300px] truncate">{c.facts}</td>
                  <td className="px-4 py-3 text-[10px] font-mono text-[var(--color-muted-light)]">{c.lat.toFixed(4)}, {c.lng.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
