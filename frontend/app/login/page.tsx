'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function LoginPage() {
  const [isKannada, setIsKannada] = useState(false);
  const router = useRouter();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-[var(--color-page-bg)] flex flex-col items-center justify-center relative p-6">
      
      {/* Top Right Language Toggle */}
      <div className="absolute top-6 right-6 z-10">
        <button 
          onClick={() => setIsKannada(!isKannada)} 
          className="flex items-center gap-2 px-4 py-2 border border-[var(--color-line)] bg-white hover:bg-[var(--color-soft-card-2)] rounded-sm text-sm font-bold uppercase tracking-wider text-[var(--color-ksp-text)] transition-colors"
        >
          <span className="material-symbols-outlined text-[16px]">translate</span>
          <span>{isKannada ? 'ENGLISH' : 'ಕನ್ನಡ'}</span>
        </button>
      </div>

      {/* Login Container */}
      <div className="w-full max-w-[480px] bg-[var(--color-white-card)] border border-[var(--color-line)] p-10 rounded-sm shadow-xl relative overflow-hidden">
        
        {/* Wireframe design accents */}
        <div className="absolute top-0 left-0 w-full h-[4px] bg-black"></div>
        <div className="absolute top-4 right-4 text-[10px] font-mono text-[var(--color-muted-light)]">AUTH_SEC_1</div>
        
        <div className="flex flex-col items-center mb-10 mt-4">
          <div className="w-16 h-16 mb-6">
            <img src="/image copy.png" alt="KSP Logo" className="w-full h-full object-contain drop-shadow-sm opacity-90" />
          </div>
          <h1 className="text-2xl font-bold text-[var(--color-ksp-text)] text-center tracking-tight mb-2">
            {isKannada ? 'ಸುರಕ್ಷಿತ ಪ್ರವೇಶ ಗೇಟ್' : 'SECURE ACCESS GATE'}
          </h1>
          <p className="text-sm text-[var(--color-muted)] text-center font-mono uppercase tracking-widest">
            {isKannada ? 'ಗುಪ್ತಚರ ಆಜ್ಞೆ ಕನ್ಸೋಲ್' : 'INTELLIGENCE COMMAND CONSOLE'}
          </p>
        </div>

        <form onSubmit={handleLogin} className="flex flex-col gap-6">
          <div className="flex flex-col gap-2">
            <label className="text-[11px] font-bold text-[var(--color-ksp-text)] uppercase tracking-wider font-mono">
              {isKannada ? 'ಬ್ಯಾಡ್ಜ್ ಐಡಿ' : 'Badge ID'}
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-[18px] text-[var(--color-muted)]">badge</span>
              <input 
                type="text" 
                defaultValue="KSP-8834-AMOGH"
                readOnly
                className="w-full pl-10 pr-4 py-3 bg-[var(--color-page-bg)] border border-[var(--color-line)] text-[var(--color-ksp-text)] focus:outline-none focus:border-black font-mono transition-colors"
              />
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-[11px] font-bold text-[var(--color-ksp-text)] uppercase tracking-wider font-mono">
              {isKannada ? 'ಭದ್ರತಾ ಪಾಸ್ವರ್ಡ್' : 'Security Password'}
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-[18px] text-[var(--color-muted)]">lock</span>
              <input 
                type="password" 
                defaultValue="••••••••••••"
                readOnly
                className="w-full pl-10 pr-4 py-3 bg-[var(--color-page-bg)] border border-[var(--color-line)] text-[var(--color-ksp-text)] focus:outline-none focus:border-black font-mono tracking-widest transition-colors"
              />
            </div>
          </div>

          <div className="flex flex-col gap-4 mt-6">
            <button 
              type="submit"
              className="w-full py-4 bg-black text-white text-[13px] font-bold uppercase tracking-widest hover:bg-[var(--color-ksp-text)] transition-colors shadow-md shadow-black/10 flex justify-center items-center gap-2 group"
            >
              <span>{isKannada ? 'ಆಜ್ಞೆ ಕ್ಲಿಯರೆನ್ಸ್ ಪರಿಶೀಲಿಸಿ' : 'VERIFY COMMAND CLEARANCE'}</span>
              <span className="material-symbols-outlined text-[18px] group-hover:translate-x-1 transition-transform">login</span>
            </button>
            
            <Link 
              href="/"
              className="w-full py-3 bg-transparent border border-[var(--color-line)] text-[var(--color-ksp-text)] text-[12px] font-bold uppercase tracking-widest hover:bg-[var(--color-soft-card-2)] transition-colors flex justify-center items-center text-center"
            >
              {isKannada ? 'ರದ್ದುಗೊಳಿಸಿ ಮತ್ತು ಹಿಂತಿರುಗಿ' : 'CANCEL & RETURN'}
            </Link>
          </div>
        </form>

        <div className="mt-8 border-t border-[var(--color-line)] pt-4 flex justify-between items-center text-[10px] font-mono text-[var(--color-muted-light)]">
          <span>IP: 192.168.1.1</span>
          <span>NODE: SEC-ALPHA</span>
        </div>
      </div>
      
    </div>
  );
}
