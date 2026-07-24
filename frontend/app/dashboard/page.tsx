'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function DashboardPage() {
  const [isKannada, setIsKannada] = useState(false);
  const [sessionId, setSessionId] = useState('------');

  useEffect(() => {
    setSessionId(new Date().getTime().toString().slice(-6));
  }, []);

  return (
    <div className="min-h-screen bg-[var(--color-page-bg)] flex flex-col font-sans overflow-hidden">
      
      {/* Header Bar */}
      <header className="fixed top-0 left-0 right-0 z-50 h-[70px] bg-white border-b border-[var(--color-line)] flex items-center justify-between px-6 shadow-sm">
        <div className="flex items-center gap-3">
          <img src="/app/image copy.png" alt="KSP Crest" className="w-10 h-10 object-contain drop-shadow-sm" />
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
          <button 
            onClick={() => setIsKannada(!isKannada)} 
            className="flex items-center gap-2 px-3 py-1.5 border border-[var(--color-line)] bg-[var(--color-page-bg)] hover:bg-[var(--color-soft-card-2)] rounded-sm text-[11px] font-bold uppercase tracking-wider text-[var(--color-ksp-text)] transition-colors"
          >
            <span className="material-symbols-outlined text-[14px]">translate</span>
            <span>{isKannada ? 'ENG' : 'ಕನ್ನಡ'}</span>
          </button>
          
          <div className="w-[1px] h-4 bg-[var(--color-line)]"></div>
          
          <Link 
            href="/"
            className="flex items-center gap-2 px-3 py-1.5 bg-black text-white rounded-sm text-[11px] font-bold uppercase tracking-wider hover:bg-[var(--color-ksp-text)] transition-colors"
          >
            <span>{isKannada ? 'ಲಾಗ್ ಔಟ್' : 'LOGOUT'}</span>
            <span className="material-symbols-outlined text-[14px]">logout</span>
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
            
            <button className="flex items-center gap-3 px-3 py-3 bg-[var(--color-white-card)] border border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] text-[12px] font-bold text-[var(--color-ksp-text)] uppercase tracking-wider mb-1">
              <span className="material-symbols-outlined text-[18px]">radar</span>
              <span>{isKannada ? 'ಲೈವ್ ತನಿಖೆ' : 'Live Investigation'}</span>
            </button>
            
            <button className="flex items-center gap-3 px-3 py-3 bg-transparent border border-transparent hover:border-[var(--color-line)] hover:bg-white text-[12px] font-bold text-[var(--color-muted)] hover:text-[var(--color-ksp-text)] uppercase tracking-wider transition-colors mb-1">
              <span className="material-symbols-outlined text-[18px]">folder_open</span>
              <span>{isKannada ? 'ಕೇಸ್ ಡೈರೆಕ್ಟರಿ (ಎಫ್ಐಆರ್)' : 'Case Directory (FIR)'}</span>
            </button>
            
            <button className="flex items-center gap-3 px-3 py-3 bg-transparent border border-transparent hover:border-[var(--color-line)] hover:bg-white text-[12px] font-bold text-[var(--color-muted)] hover:text-[var(--color-ksp-text)] uppercase tracking-wider transition-colors mb-1">
              <span className="material-symbols-outlined text-[18px]">contact_page</span>
              <span>{isKannada ? 'ಶಂಕಿತ ಡೋಸಿಯರ್‌ಗಳು' : 'Suspect Dossiers'}</span>
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

        {/* Column 2: Center Core Workspace (55%) */}
        <section className="w-[55%] flex flex-col bg-[var(--color-page-bg)] relative">
          
          {/* Top subtle fade overlay */}
          <div className="absolute top-0 w-full h-8 bg-gradient-to-b from-[var(--color-page-bg)] to-transparent z-10 pointer-events-none"></div>
          
          {/* Chat Stream Area */}
          <div className="flex-1 overflow-y-auto p-8 pb-32 flex flex-col gap-6">
            
            <div className="flex gap-4 items-start max-w-[85%] animate-stream-in" style={{animationDelay: '100ms'}}>
              <div className="w-8 h-8 rounded-sm bg-[var(--color-white-card)] border border-[var(--color-line)] shrink-0 flex items-center justify-center">
                <span className="material-symbols-outlined text-[16px] text-black">person</span>
              </div>
              <div className="bg-[var(--color-white-card)] border border-[var(--color-line)] p-4 shadow-sm text-[14px] leading-relaxed">
                {isKannada ? 'ಬೆಳಗಾವಿ ಜಿಲ್ಲೆಯಲ್ಲಿ ಇತ್ತೀಚಿನ ಮಾದಕವಸ್ತು ಸಿಂಡಿಕೇಟ್ ಚಟುವಟಿಕೆಗಳನ್ನು ತೋರಿಸಿ.' : 'Show recent narcotics syndicates in Belagavi district.'}
              </div>
            </div>

            <div className="flex gap-4 items-start max-w-[90%] self-end flex-row-reverse animate-stream-in" style={{animationDelay: '300ms'}}>
              <div className="w-8 h-8 rounded-sm bg-black border border-black shrink-0 flex items-center justify-center">
                <span className="material-symbols-outlined text-[16px] text-[#FF4B2B]">auto_awesome</span>
              </div>
              <div className="bg-[var(--color-panel-bg)] border border-[var(--color-line)] p-4 shadow-sm flex flex-col gap-3">
                <p className="text-[14px] leading-relaxed">
                  {isKannada ? 'ಬೆಳಗಾವಿ ಸೆಕ್ಟರ್‌ನಲ್ಲಿ 3 ಸಂಭಾವ್ಯ ಸಿಂಡಿಕೇಟ್ ನೋಡ್‌ಗಳನ್ನು ವಿಶ್ಲೇಷಣೆ ಗುರುತಿಸಿದೆ. ನಿಪ್ಪಾಣಿ ಟೋಲ್ ಪ್ಲಾಜಾ ಬಳಿಯ ಸೆಲ್ ಟವರ್ ದತ್ತಾಂಶವು ಕಳ್ಳಸಾಗಣೆ ಮಾರ್ಗಗಳೊಂದಿಗೆ ಹೊಂದಿಕೆಯಾಗುವ ಅಸಹಜ ರಾತ್ರಿ ಸಮಯದ ಚಲನೆಯನ್ನು ತೋರಿಸುತ್ತದೆ.' : 'Analysis identified 3 probable syndicate nodes in Belagavi sector. Cell tower data near Nipani toll plaza shows anomalous night-time movement matching contraband routes.'}
                </p>
                <div className="flex flex-wrap gap-2 mt-1">
                  <div className="px-2 py-1 bg-white border border-[var(--color-line)] text-[10px] font-mono font-bold">CELL-ARRAY: NIP-442</div>
                  <div className="px-2 py-1 bg-white border border-[var(--color-line)] text-[10px] font-mono font-bold text-[#FF4B2B]">MATCH: 87%</div>
                </div>
              </div>
            </div>

          </div>

          {/* Command Entry Bar */}
          <div className="absolute bottom-0 w-full p-6 bg-gradient-to-t from-[var(--color-page-bg)] via-[var(--color-page-bg)] to-transparent">
            <div className="bg-white border-2 border-black p-2 flex items-center shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
              <span className="material-symbols-outlined text-[20px] text-[var(--color-muted)] px-3">terminal</span>
              <input 
                type="text" 
                defaultValue="Show recent narcotics syndicates in Belagavi district"
                className="flex-1 bg-transparent border-none outline-none text-[14px] font-mono focus:ring-0 px-2 text-[var(--color-ksp-text)]"
              />
              <button className="w-10 h-10 bg-black flex items-center justify-center ml-2 relative">
                <span className="absolute inset-0 border border-[#F97316] animate-mic-glow"></span>
                <span className="material-symbols-outlined text-[#F97316] relative z-10 text-[20px]">mic</span>
              </button>
            </div>
            <div className="flex gap-2 mt-3 pl-2">
              <button className="text-[10px] font-mono px-2 py-1 border border-[var(--color-line)] bg-white hover:bg-[var(--color-soft-card)] text-[var(--color-muted)] transition-colors">/query-suspects</button>
              <button className="text-[10px] font-mono px-2 py-1 border border-[var(--color-line)] bg-white hover:bg-[var(--color-soft-card)] text-[var(--color-muted)] transition-colors">/run-heatmap</button>
            </div>
          </div>
          
        </section>

        {/* Column 3: Telemetry/Matrix Panel (25%) */}
        <aside className="w-[25%] min-w-[300px] border-l border-[var(--color-line)] bg-[var(--color-white-card)] flex flex-col">
          
          {/* Top Half: Matrix Visualization */}
          <div className="h-[50%] border-b border-[var(--color-line)] p-6 flex flex-col relative overflow-hidden bg-[#0A0A0A]">
            <div className="flex justify-between items-center mb-6 relative z-10">
              <h3 className="text-[11px] font-mono font-bold text-white uppercase tracking-widest flex items-center gap-2">
                <span className="material-symbols-outlined text-[14px]">share</span>
                {isKannada ? 'ಮ್ಯಾಟ್ರಿಕ್ಸ್ ಟೆಲಿಮೆಟ್ರಿ' : 'Matrix Telemetry'}
              </h3>
              <span className="w-2 h-2 bg-green-500 animate-blink"></span>
            </div>
            
            <div className="flex-1 flex flex-col justify-center gap-4 relative z-10">
              <div className="flex justify-between items-end border-b border-white/20 pb-2">
                <span className="text-[10px] font-mono text-white/60">ACTIVE ENTITIES</span>
                <span className="text-[20px] font-bold text-white font-mono leading-none">4,291</span>
              </div>
              <div className="flex justify-between items-end border-b border-white/20 pb-2">
                <span className="text-[10px] font-mono text-white/60">IDENTIFIED EDGES</span>
                <span className="text-[20px] font-bold text-white font-mono leading-none">8,191</span>
              </div>
              
              <div className="mt-4 border border-[#FF4B2B] bg-[#FF4B2B]/10 p-3 flex justify-between items-center">
                <span className="text-[10px] font-mono text-[#FF4B2B] font-bold tracking-wider">CRITICAL CROSS-ANOMALIES</span>
                <span className="text-[24px] font-bold text-[#FF4B2B] leading-none">14</span>
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
              <span className="material-symbols-outlined text-[14px]">history</span>
              {isKannada ? 'ಲೈವ್ ಘಟನೆ ಫೀಡ್' : 'Live Incident Feed'}
            </h3>
            
            <div className="relative flex-1 overflow-hidden mask-image-vertical">
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
                
                {/* Duplicate for infinite scroll illusion */}
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
            
            {/* Custom CSS for mask image to fade out edges */}
            <style dangerouslySetInnerHTML={{__html: `
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


