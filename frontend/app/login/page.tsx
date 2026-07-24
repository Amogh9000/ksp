'use client';

import { useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';

export default function LoginPage() {
  const [isKannada, setIsKannada] = useState(false);
  const [badgeNo, setBadgeNo] = useState('KSP-80492');
  const [password, setPassword] = useState('••••••••••••');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      window.location.href = '/dashboard';
    }, 400);
  };

  return (
    <div className="min-h-screen bg-[var(--color-page-bg)] flex flex-col items-center justify-center relative p-6">

      {/* ── Language Toggle ──────────────────────────────────────────────── */}
      <div className="absolute top-6 right-6 z-10">
        <button
          onClick={() => setIsKannada(!isKannada)}
          className="flex items-center gap-2 px-4 py-2 border border-[var(--color-line)] bg-white hover:bg-[var(--color-soft-card-2)] rounded-sm text-sm font-bold uppercase tracking-wider text-[var(--color-ksp-text)] transition-colors"
        >
          <span className="material-symbols-outlined text-[16px]">translate</span>
          <span>{isKannada ? 'ENGLISH' : 'ಕನ್ನಡ'}</span>
        </button>
      </div>

      {/* ── Login Card ───────────────────────────────────────────────────── */}
      <div className="w-full max-w-[480px] bg-[var(--color-white-card)] border border-[var(--color-line)] px-10 pt-10 pb-8 rounded-sm shadow-xl relative overflow-hidden">

        {/* Accent bar + label */}
        <div className="absolute top-0 left-0 w-full h-[4px] bg-black" />
        <div className="absolute top-4 right-4 text-[10px] font-mono text-[var(--color-muted-light)]">
          DEV_BYPASS_ENABLED
        </div>

        {/* ── Branding header ────────────────────────────────────────────── */}
        <div className="flex flex-col items-center mb-8 mt-4">
          <div className="w-14 h-14 mb-5 rounded-full bg-black text-white flex items-center justify-center font-bold text-base shadow-sm">
            KSP
          </div>
          <h1 className="text-2xl font-bold text-[var(--color-ksp-text)] text-center tracking-tight mb-1">
            {isKannada ? 'ಸುರಕ್ಷಿತ ಪ್ರವೇಶ ಗೇಟ್' : 'SECURE ACCESS GATE'}
          </h1>
          <p className="text-[11px] text-[var(--color-muted)] text-center font-mono uppercase tracking-widest">
            {isKannada ? 'ಗುಪ್ತಚರ ಆಜ್ಞೆ ಕನ್ಸೋಲ್' : 'INTELLIGENCE COMMAND CONSOLE'}
          </p>
        </div>

        {/* ── Divider ────────────────────────────────────────────────────── */}
        <div className="border-t border-[var(--color-line)] mb-6" />

        {/* ── Interactive Dev Login Form ──────────────────────────────────── */}
        <form onSubmit={handleLogin} className="flex flex-col gap-4">
          <div>
            <label className="block text-[11px] font-mono uppercase tracking-wider font-bold text-[var(--color-ksp-text)] mb-1">
              {isKannada ? 'ಅಧಿಕಾರಿ ಬ್ಯಾಡ್ಜ್ ಸಂಖ್ಯಾ / ಐಡಿ' : 'OFFICER BADGE / ID'}
            </label>
            <input
              type="text"
              value={badgeNo}
              onChange={(e) => setBadgeNo(e.target.value)}
              className="w-full px-3 py-2 border border-[var(--color-line)] bg-white rounded-sm text-sm text-[var(--color-ksp-text)] font-mono focus:outline-none focus:border-black"
              required
            />
          </div>

          <div>
            <label className="block text-[11px] font-mono uppercase tracking-wider font-bold text-[var(--color-ksp-text)] mb-1">
              {isKannada ? 'ಪಾಸ್ವರ್ಡ್' : 'PASSWORD'}
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-[var(--color-line)] bg-white rounded-sm text-sm text-[var(--color-ksp-text)] font-mono focus:outline-none focus:border-black"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="mt-2 w-full py-3 bg-black text-white rounded-sm text-xs font-bold font-mono uppercase tracking-widest hover:bg-[var(--color-ksp-text)] transition-colors flex items-center justify-center gap-2 shadow-md"
          >
            {isLoading ? (
              <span>{isKannada ? 'ಪರಿಶೀಲಿಸಲಾಗುತ್ತಿದೆ...' : 'AUTHENTICATING...'}</span>
            ) : (
              <>
                <span>{isKannada ? 'ಲಾಗಿನ್ ಮಾಡಿ (ಪ್ರವೇಶಿಸಿ)' : 'AUTHENTICATE & ENTER'}</span>
                <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
              </>
            )}
          </button>
        </form>

        <div className="mt-4 p-3 border border-emerald-300 bg-emerald-50 text-emerald-900 text-[11px] font-mono rounded-sm flex items-center justify-between">
          <span>⚡ Dev Mode Bypass Active</span>
          <Link
            href="/dashboard"
            className="px-2 py-1 bg-emerald-700 text-white rounded text-[10px] font-bold uppercase tracking-wider hover:bg-emerald-800 transition-colors"
          >
            Direct RAG →
          </Link>
        </div>

        {/* ── Footer strip ───────────────────────────────────────────────── */}
        <div className="mt-8 border-t border-[var(--color-line)] pt-4 flex justify-between items-center text-[10px] font-mono text-[var(--color-muted-light)]">
          <span>KSP · CONVERSATIONAL AI PLATFORM</span>
          <span>NODE: SEC-ALPHA</span>
        </div>
      </div>

      {/* ── Cancel link ──────────────────────────────────────────────────── */}
      <div className="mt-5">
        <Link
          href="/"
          className="text-[11px] font-mono uppercase tracking-widest text-[var(--color-muted)] hover:text-[var(--color-ksp-text)] transition-colors"
        >
          ← {isKannada ? 'ರದ್ದುಗೊಳಿಸಿ ಮತ್ತು ಹಿಂತಿರುಗಿ' : 'CANCEL & RETURN'}
        </Link>
      </div>

    </div>
  );
}


