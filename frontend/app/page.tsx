'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function Home() {
  const [isKannada, setIsKannada] = useState(false);
  const [fontSizeLevel, setFontSizeLevel] = useState(0);

  const changeFontSize = (level: number) => {
    let newLevel = level === 0 ? 0 : fontSizeLevel + level;
    newLevel = Math.max(-2, Math.min(2, newLevel));
    setFontSizeLevel(newLevel);
    const newSize = 100 + (newLevel * 10);
    if (typeof document !== 'undefined') {
      document.documentElement.style.fontSize = `${newSize}%`;
    }
  };

  return (
    <>
      {/* Top Navigation Assembly */}
      <header className="relative z-50 shadow-md bg-white border-b border-[var(--color-line)]">
        <div className="bg-[var(--color-deep-black)] text-white w-full py-2">
          <div className="max-w-[1728px] mx-auto px-10 flex justify-between items-center text-[11px] font-bold tracking-wider font-label uppercase">
            <div className="flex items-center gap-4">
              <Link href="/login" className="hover:text-white/80 transition-colors text-white">
                {isKannada ? 'ಲಾಗಿನ್' : 'SIGN IN'}
              </Link>
              <div className="w-[1px] h-3 bg-white/30"></div>
              <button onClick={() => setIsKannada(!isKannada)} className="hover:text-white/80 transition-colors flex items-center gap-1 text-white">
                <span className="material-symbols-outlined text-[14px]">translate</span>
                <span>{isKannada ? 'ENGLISH' : 'ಕನ್ನಡ'}</span>
              </button>
            </div>

            <div className="flex items-center gap-1">
              <button onClick={() => changeFontSize(-1)} className="w-7 h-7 rounded border border-white/20 text-white flex items-center justify-center hover:bg-white/10 transition-colors">A-</button>
              <button onClick={() => changeFontSize(0)} className="w-7 h-7 rounded border border-white/20 text-white flex items-center justify-center hover:bg-white/10 transition-colors">A</button>
              <button onClick={() => changeFontSize(1)} className="w-7 h-7 rounded border border-white/20 text-white flex items-center justify-center hover:bg-white/10 transition-colors">A+</button>
            </div>
          </div>
        </div>

        <div className="bg-white w-full py-2 relative h-[110px]">
          <div className="max-w-[1728px] h-full mx-auto px-10 flex items-center justify-between relative">
            <div className="h-[90px] flex items-center shrink-0 relative z-10">
              <div className="w-12 h-12 rounded-full bg-black/5 flex items-center justify-center text-[var(--color-ksp-text)] font-bold text-xs">KSP</div>
            </div>

            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center justify-center pointer-events-none w-full z-10">
              <div className="flex items-center gap-4 pointer-events-auto">
                <div className="w-12 h-12 rounded-full bg-black text-white flex items-center justify-center font-bold text-sm shadow-sm shrink-0">
                  KSP
                </div>
                <div className="flex flex-col text-left hidden xl:flex">
                  <h1 className="text-[28px] font-bold text-[var(--color-ksp-text)] leading-tight tracking-tight">
                    {isKannada ? 'ಕರ್ನಾಟಕ ರಾಜ್ಯ ಪೊಲೀಸ್' : 'Karnataka State Police'}
                  </h1>
                  <h2 className="text-sm text-[var(--color-muted)]">
                    {isKannada ? 'ಕರ್ನಾಟಕ ಸರ್ಕಾರ' : 'Government of Karnataka'}
                  </h2>
                </div>
              </div>
            </div>

            <div className="h-[90px] flex items-center shrink-0 relative z-10 hidden md:flex">
              <div className="w-12 h-12 rounded-full bg-black/5 flex items-center justify-center text-[var(--color-ksp-text)] font-bold text-xs">GOVT</div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Workspace */}
      <main>
        {/* 1. Command Cockpit */}
        <section className="pt-20 px-10 max-w-[1728px] mx-auto flex flex-col items-center text-center relative overflow-visible bg-[var(--color-page-bg)] pb-20">
          <h1 className="text-[64px] text-balance max-w-4xl mb-6 text-[var(--color-ksp-text)] tracking-tighter font-bold">
            {isKannada ? 'ಕೆಎಸ್ಪಿ ಗುಪ್ತಚರ ಪೋರ್ಟಲ್' : 'KSP Intelligence Portal'}
          </h1>
          <p className="text-[18px] text-[var(--color-muted)] max-w-2xl mb-12">
            {isKannada ? 'ಅಧಿಕೃತ ಸಿಬ್ಬಂದಿಗೆ ಮಾತ್ರ ಪ್ರವೇಶ. ಪ್ರಕರಣ ನಿರ್ವಹಣೆ, ಲಿಂಕ್ ವಿಶ್ಲೇಷಣೆ ಮತ್ತು ಲೈವ್ ಯುದ್ಧತಂತ್ರದ ಗುಪ್ತಚರಕ್ಕಾಗಿ ಕೇಂದ್ರೀಕೃತ ಡ್ಯಾಶ್ಬೋರ್ಡ್.' : 'Authorized Personnel Access Only. Centralized dashboard for case management, link analysis, and live tactical intelligence.'}
          </p>

          <Link href="/login" className="group flex items-center gap-3 bg-black text-white px-8 py-4 rounded-full text-sm font-bold uppercase tracking-widest hover:bg-[var(--color-ksp-text)] transition-colors shadow-lg shadow-black/20 hover:scale-105 transform duration-300">
            <span>{isKannada ? 'ಇಂಟೆಲಿಜೆನ್ಸ್ ಡ್ಯಾಶ್ಬೋರ್ಡ್ಗೆ ಲಾಗಿನ್ ಮಾಡಿ' : 'LOGIN TO INTELLIGENCE DASHBOARD'}</span>
            <span className="material-symbols-outlined group-hover:translate-x-1 transition-transform">arrow_forward</span>
          </Link>

          {/* Embedded Global Search */}
          <div className="w-full max-w-[800px] mt-16 relative z-10">
            <div className="bg-[var(--color-white-card)] rounded-full shadow-[0_12px_40px_rgba(0,0,0,0.08)] p-3 flex items-center border border-[var(--color-line)]">
              <div className="pl-4 pr-2">
                <span className="material-symbols-outlined text-[var(--color-muted)] text-[28px]">search</span>
              </div>
              <input type="text"
                placeholder={isKannada ? 'ಜಾಗತಿಕ ಹುಡುಕಾಟ: ಎಫ್ಐಆರ್ ಗಳು, ನಾಗರಿಕರು, ಇಲಾಖೆಯ ಸುತ್ತೋಲೆಗಳು...' : 'Global Search: FIRs, Citizens, Department Circulars...'}
                className="w-full bg-transparent border-none focus:outline-none text-[var(--color-ksp-text)] text-[18px] placeholder:text-[var(--color-muted-light)] px-2 focus:ring-0" />
              <div className="flex items-center gap-2 pr-1">
                <button className="w-12 h-12 rounded-full hover:bg-[var(--color-soft-card-2)] flex items-center justify-center transition-colors border border-[var(--color-line)]">
                  <span className="material-symbols-outlined text-[#FF4B2B]">mic</span>
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* 2. Online Services Grid */}
        <section className="py-[120px] px-10 max-w-[1728px] mx-auto bg-[var(--color-page-bg)] border-t border-[var(--color-line)]">
          <h2 className="text-[40px] mb-12 font-bold tracking-tight text-[var(--color-ksp-text)]">
            {isKannada ? 'ತ್ವರಿತ ಲಿಂಕ್ಗಳು ಮತ್ತು ನಾಗರಿಕ ಸೇವೆಗಳು' : 'Quick Links & Citizen Services'}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <a href="#" className="bg-[var(--color-white-card)] p-6 rounded-[24px] border border-[var(--color-line)] shadow-sm hover:shadow-md transition-shadow group">
              <div className="w-12 h-12 rounded-full bg-[#E0EAFC] text-[#2B547E] flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined">description</span>
              </div>
              <h3 className="text-xl font-bold mb-2 text-[var(--color-ksp-text)]">
                {isKannada ? 'ಎಫ್ಐಆರ್ ಹುಡುಕಾಟ' : 'FIR Search'}
              </h3>
              <p className="text-[15px] text-[var(--color-muted)]">
                {isKannada ? 'ಪರಿಶೀಲಿಸಿದ ಎಫ್ಐಆರ್ ಪ್ರತಿಗಳನ್ನು ಡಿಜಿಟಲ್ ಆಗಿ ಪ್ರವೇಶಿಸಿ ಮತ್ತು ಡೌನ್ಲೋಡ್ ಮಾಡಿ.' : 'Access and download verified FIR copies digitally.'}
              </p>
            </a>
            <a href="#" className="bg-[var(--color-white-card)] p-6 rounded-[24px] border border-[var(--color-line)] shadow-sm hover:shadow-md transition-shadow group">
              <div className="w-12 h-12 rounded-full bg-[#FFE4D6] text-[#D84315] flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined">policy</span>
              </div>
              <h3 className="text-xl font-bold mb-2 text-[var(--color-ksp-text)]">
                {isKannada ? 'ಸೇವಾ ಸಿಂಧು' : 'Seva Sindhu'}
              </h3>
              <p className="text-[15px] text-[var(--color-muted)]">
                {isKannada ? 'ವಿವಿಧ ಸರ್ಕಾರಿ ಅನುಮತಿಗಳಿಗಾಗಿ ಸಂಯೋಜಿತ ಪೋರ್ಟಲ್.' : 'Integrated portal for various government clearances.'}
              </p>
            </a>
            <a href="#" className="bg-[var(--color-white-card)] p-6 rounded-[24px] border border-[var(--color-line)] shadow-sm hover:shadow-md transition-shadow group">
              <div className="w-12 h-12 rounded-full bg-[#F3E5F5] text-[#6A1B9A] flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined">report</span>
              </div>
              <h3 className="text-xl font-bold mb-2 text-[var(--color-ksp-text)]">
                {isKannada ? 'ಇ-ಲಾಸ್ಟ್ ವರದಿಗಳು' : 'e-Lost Reports'}
              </h3>
              <p className="text-[15px] text-[var(--color-muted)]">
                {isKannada ? 'ಠಾಣೆಗೆ ಭೇಟಿ ನೀಡದೆ ಕಳೆದುಹೋದ ವಸ್ತುಗಳನ್ನು ತಕ್ಷಣ ವರದಿ ಮಾಡಿ.' : 'Report lost articles instantly without visiting a station.'}
              </p>
            </a>
            <a href="#" className="bg-[var(--color-white-card)] p-6 rounded-[24px] border border-[var(--color-line)] shadow-sm hover:shadow-md transition-shadow group">
              <div className="w-12 h-12 rounded-full bg-[#E8F5E9] text-[#2E7D32] flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <span className="material-symbols-outlined">badge</span>
              </div>
              <h3 className="text-xl font-bold mb-2 text-[var(--color-ksp-text)]">
                {isKannada ? 'ನೇಮಕಾತಿ' : 'Recruitment'}
              </h3>
              <p className="text-[15px] text-[var(--color-muted)]">
                {isKannada ? 'ಚಾಲ್ತಿಯಲ್ಲಿರುವ ಪೊಲೀಸ್ ನೇಮಕಾತಿ ಡ್ರೈವ್ಗಳ ಇತ್ತೀಚಿನ ನವೀಕರಣಗಳು.' : 'Latest updates on ongoing police recruitment drives.'}
              </p>
            </a>
          </div>
        </section>

        {/* 3. Feature Showcase 01 */}
        <section className="py-[120px] px-10 max-w-[1728px] mx-auto bg-[var(--color-page-bg)] border-t border-[var(--color-line)]">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-32 items-center">
            <div className="lg:col-span-5 flex flex-col justify-center">
              <div className="inline-block px-3 py-1 bg-black text-white w-max rounded text-[10px] font-bold uppercase tracking-wider mb-8">
                {isKannada ? 'ಆಂತರಿಕ ವ್ಯವಸ್ಥೆ' : 'Internal System'}
              </div>
              <h3 className="text-[48px] leading-[1.1] mb-6 font-bold tracking-tight text-[var(--color-ksp-text)] text-balance">
                {isKannada ? 'ದ್ವಿಭಾಷಾ ಬುದ್ಧಿವಂತ RAG ಎಂಜಿನ್' : 'Bilingual Intelligent RAG Engine'}
              </h3>
              <p className="text-[18px] text-[var(--color-muted)] leading-relaxed">
                {isKannada ? 'ಇಂಗ್ಲಿಷ್ ಮತ್ತು ಕನ್ನಡದಾದ್ಯಂತ ಸಂಕೀರ್ಣ ಪ್ರಕರಣದ ಫೈಲ್ಗಳನ್ನು ತಕ್ಷಣವೇ ಪ್ರಶ್ನಿಸಿ. ಬುದ್ಧಿವಂತ ಎಂಜಿನ್ ನಿಖರವಾದ ತನಿಖಾ ಒಳನೋಟಗಳನ್ನು ಮೇಲ್ಮೈಗೆ ತರಲು ಐತಿಹಾಸಿಕ ದಾಖಲೆಗಳು ಮತ್ತು ಸಕ್ರಿಯ ವರದಿಗಳನ್ನು ಅಡ್ಡ-ಉಲ್ಲೇಖಿಸುತ್ತದೆ.' : 'Query complex case files across English and Kannada instantly. The intelligent engine cross-references historical records and active reports to surface precise investigative insights.'}
              </p>
            </div>
            <div className="lg:col-span-7">
              <div className="bg-[var(--color-panel-bg)] rounded-[40px] p-8 h-[600px] flex items-center justify-center relative overflow-hidden border border-[var(--color-line)] shadow-inner">
                <div className="w-full max-w-lg bg-[var(--color-white-card)] rounded-[24px] shadow-xl border border-[var(--color-line)] p-8 flex flex-col gap-8">
                  <div className="flex gap-4 items-start">
                    <div className="w-10 h-10 rounded-full bg-black shrink-0 flex items-center justify-center text-white font-bold text-[11px] shadow-sm">
                      INV
                    </div>
                    <div className="bg-[var(--color-soft-card-2)] p-5 rounded-2xl rounded-tl-none text-[15px] text-[var(--color-ksp-text)] border border-[var(--color-line)] shadow-sm">
                      {isKannada ? 'ಕಳೆದ 30 ದಿನಗಳಲ್ಲಿ ಎಚ್ಎಸ್ಆರ್ ಲೇಔಟ್ನಲ್ಲಿ ಇತ್ತೀಚಿನ ವಾಹನ ಕಳ್ಳತನದ ಮಾದರಿಗಳನ್ನು ಸಂಕ್ಷಿಪ್ತಗೊಳಿಸಿ.' : 'Summarize the recent vehicle theft patterns in HSR Layout over the last 30 days.'}
                    </div>
                  </div>
                  <div className="flex gap-4 items-start">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-[#FF416C] to-[#FF4B2B] shrink-0 flex items-center justify-center text-white shadow-md">
                      <span className="material-symbols-outlined text-[20px]">auto_awesome</span>
                    </div>
                    <div className="bg-[var(--color-page-bg)] p-5 rounded-2xl rounded-tr-none text-[15px] text-[var(--color-ksp-text)] border border-[var(--color-line)] flex flex-col gap-4 shadow-sm">
                      <p>
                        {isKannada ? 'ವಿಶ್ಲೇಷಣೆಯು ದ್ವಿಚಕ್ರ ವಾಹನಗಳನ್ನು ಒಳಗೊಂಡ 14 ಘಟನೆಗಳ ಸಮೂಹವನ್ನು ಸೂಚಿಸುತ್ತದೆ, ಪ್ರಾಥಮಿಕವಾಗಿ ಬೆಳಿಗ್ಗೆ 02:00 ಮತ್ತು 04:30 ರ ನಡುವೆ ಸಂಭವಿಸುತ್ತದೆ.' : 'Analysis indicates a cluster of 14 incidents involving two-wheelers, primarily occurring between 02:00 and 04:30 AM.'}
                      </p>
                      <div className="flex flex-wrap items-center gap-2 mt-2">
                        <span className="bg-green-100/50 text-green-800 border border-green-200 px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                          <span>{isKannada ? 'ಹೆಚ್ಚಿನ ವಿಶ್ವಾಸ' : 'HIGH CONFIDENCE'}</span>
                        </span>
                        <span className="bg-[var(--color-soft-card)] border border-[var(--color-line)] text-[var(--color-muted)] px-2 py-1 rounded text-[10px] font-mono">
                          FIR-2023-08-112
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Feature Showcase 02 */}
        <section className="py-[120px] px-10 max-w-[1728px] mx-auto bg-[var(--color-page-bg)]">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-32 items-center">
            <div className="lg:col-span-7 order-2 lg:order-1">
              <div className="bg-[var(--color-panel-bg)] rounded-[40px] p-8 h-[600px] flex items-center justify-center relative overflow-hidden border border-[var(--color-line)] shadow-inner">
                <div className="w-full h-full max-w-lg flex items-center justify-center">
                  <div className="w-full bg-[var(--color-white-card)] border-[1.5px] border-[var(--color-ksp-text)] p-10 rounded-2xl shadow-[12px_12px_0px_rgba(27,27,27,1)] flex flex-col justify-between">
                    <div className="flex justify-between items-start mb-14">
                      <span className="material-symbols-outlined text-[40px] text-[var(--color-ksp-text)]">hub</span>
                      <span className="font-mono text-xs text-[var(--color-ksp-text)] border border-[var(--color-ksp-text)] px-3 py-1.5 uppercase font-bold tracking-wider">
                        {isKannada ? 'ಲೈವ್ ಸ್ಟ್ರೀಮ್' : 'Live Stream'}
                      </span>
                    </div>
                    <div className="flex flex-col gap-3">
                      <p className="font-mono text-sm text-[var(--color-muted)] uppercase tracking-wider font-bold">
                        {isKannada ? 'ಸಕ್ರಿಯ ನೆಟ್ವರ್ಕ್ ಘಟಕಗಳು' : 'Active Network Entities'}
                      </p>
                      <p className="text-[72px] font-bold text-[var(--color-ksp-text)] leading-none tracking-tighter">
                        12,482
                      </p>
                    </div>
                    <div className="w-full h-[1.5px] bg-[var(--color-line)] my-8"></div>
                    <div className="grid grid-cols-3 gap-4">
                      <div className="flex flex-col gap-1">
                        <span className="font-mono text-[11px] text-[var(--color-muted)] uppercase font-bold tracking-wider">
                          {isKannada ? 'ನೋಡ್ಗಳು' : 'Nodes'}
                        </span>
                        <span className="font-bold text-[var(--color-ksp-text)] text-xl">4,291</span>
                      </div>
                      <div className="flex flex-col gap-1">
                        <span className="font-mono text-[11px] text-[var(--color-muted)] uppercase font-bold tracking-wider">
                          {isKannada ? 'ಅಂಚುಗಳು' : 'Edges'}
                        </span>
                        <span className="font-bold text-[var(--color-ksp-text)] text-xl">8,191</span>
                      </div>
                      <div className="flex flex-col gap-1">
                        <span className="font-mono text-[11px] text-[#FF4B2B] uppercase font-bold tracking-wider">
                          {isKannada ? 'ವೈಪರೀತ್ಯಗಳು' : 'Anomalies'}
                        </span>
                        <span className="font-bold text-[#FF4B2B] text-xl">14</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="lg:col-span-5 flex flex-col justify-center order-1 lg:order-2">
              <div className="inline-block px-3 py-1 bg-black text-white w-max rounded text-[10px] font-bold uppercase tracking-wider mb-8">
                {isKannada ? 'ಆಂತರಿಕ ವ್ಯವಸ್ಥೆ' : 'Internal System'}
              </div>
              <h3 className="text-[48px] leading-[1.1] mb-6 font-bold tracking-tight text-[var(--color-ksp-text)] text-balance">
                {isKannada ? 'ಸ್ವಾಯತ್ತ ನೆಟ್ವರ್ಕ್ ಲಿಂಕ್ ವಿಶ್ಲೇಷಣೆ' : 'Autonomous Network Link Analysis'}
              </h3>
              <p className="text-[18px] text-[var(--color-muted)] leading-relaxed">
                {isKannada ? 'ಶಂಕಿತರು, ವಾಹನಗಳು ಮತ್ತು ಸಂವಹನ ದಾಖಲೆಗಳ ನಡುವಿನ ಸಂಪರ್ಕಗಳನ್ನು ತಕ್ಷಣ ನಕ್ಷೆ ಮಾಡಿ. ನಮ್ಮ ಗ್ರಾಫ್ ಆರ್ಕಿಟೆಕ್ಚರ್ ಸ್ವಯಂಚಾಲಿತವಾಗಿ ಗುಪ್ತ ಸಂಬಂಧಗಳನ್ನು ಗುರುತಿಸುತ್ತದೆ, ಚದುರಿದ ಡೇಟಾವನ್ನು ಕ್ರಿಯಾಶೀಲ ಬುದ್ಧಿವಂತಿಕೆಯನ್ನಾಗಿ ಪರಿವರ್ತಿಸುತ್ತದೆ.' : 'Instantly map connections between suspects, vehicles, and communication records. Our graph architecture automatically identifies hidden affiliations, turning scattered data into actionable intelligence.'}
              </p>
            </div>
          </div>
        </section>

        {/* Workspace Pipelines */}
        <section className="py-[160px] px-10 max-w-[1728px] mx-auto bg-[var(--color-page-bg)] overflow-hidden relative border-t border-[var(--color-line)]">
          <h2 className="text-[48px] mb-16 font-bold tracking-tight text-[var(--color-ksp-text)] text-center">
            {isKannada ? 'ಕಾರ್ಯಾಚರಣೆಯ ಕಾರ್ಯಕ್ಷೇತ್ರಗಳು' : 'Operational Workspaces'}
          </h2>

          <div className="w-full flex gap-8 overflow-x-auto pb-12 snap-x snap-mandatory scrollbar-hide px-10">
            <div className="shrink-0 w-[420px] snap-center bg-[var(--color-white-card)] border border-[var(--color-line)] rounded-[32px] p-10 shadow-sm flex flex-col justify-between hover:shadow-xl transition-all duration-300 group">
              <div>
                <div className="inline-block px-4 py-1.5 bg-[#E0EAFC]/60 text-[#2B547E] border border-[#2B547E]/20 rounded text-[10px] font-bold uppercase tracking-wider mb-8">
                  {isKannada ? 'ಕೇಸ್ ಫೈಲ್ ಆರ್ಕೆಸ್ಟ್ರೇಟರ್' : 'Case File Orchestrator'}
                </div>
                <h4 className="text-[24px] font-bold mb-4 text-[var(--color-ksp-text)] leading-snug">
                  {isKannada ? 'ಡಿಜಿಟಲ್ ಕೇಸ್ ನಿರ್ವಹಣೆ' : 'Digital Case Management'}
                </h4>
                <p className="text-[15px] text-[var(--color-muted)] leading-relaxed">
                  {isKannada ? 'ಎಫ್ಐಆರ್ಗಳು, ಸಾಕ್ಷಿಗಳ ಹೇಳಿಕೆಗಳು ಮತ್ತು ಸಾಕ್ಷ್ಯಾಧಾರದ ದಾಖಲೆಗಳನ್ನು ಹೆಚ್ಚು ಸುರಕ್ಷಿತವಾದ ಎನ್ಕ್ಲೇವ್ನಲ್ಲಿ ಕೊನೆಯಿಂದ ಕೊನೆಯವರೆಗೆ ಡಿಜಿಟಲೀಕರಣಗೊಳಿಸುವುದು.' : 'End-to-end digitisation of FIRs, witness statements, and evidentiary documents in a highly secure enclave.'}
                </p>
              </div>
              <div className="mt-12 pt-6 border-t border-[var(--color-line)] flex justify-between items-center group-hover:border-[#1B1B1B] transition-colors cursor-pointer">
                <span className="text-[11px] font-bold text-[var(--color-ksp-text)] uppercase tracking-wider">
                  {isKannada ? 'ಕಾರ್ಯಕ್ಷೇತ್ರವನ್ನು ಪ್ರವೇಶಿಸಿ' : 'Access Workspace'}
                </span>
                <span className="material-symbols-outlined text-[var(--color-ksp-text)] group-hover:translate-x-1 transition-transform">arrow_forward</span>
              </div>
            </div>

            <div className="shrink-0 w-[420px] snap-center bg-[var(--color-white-card)] border border-[var(--color-line)] rounded-[32px] p-10 shadow-sm flex flex-col justify-between hover:shadow-xl transition-all duration-300 group">
              <div>
                <div className="inline-block px-4 py-1.5 bg-[#FFE4D6]/60 text-[#D84315] border border-[#D84315]/20 rounded text-[10px] font-bold uppercase tracking-wider mb-8">
                  {isKannada ? 'ಜಿಲ್ಲಾ ಹಾಟ್ಸ್ಪಾಟ್ ಲೆಡ್ಜರ್' : 'District Hotspot Ledger'}
                </div>
                <h4 className="text-[24px] font-bold mb-4 text-[var(--color-ksp-text)] leading-snug">
                  {isKannada ? 'ಮುನ್ಸೂಚಕ ಶಾಖ ನಕ್ಷೆಗಳು' : 'Predictive Heatmaps'}
                </h4>
                <p className="text-[15px] text-[var(--color-muted)] leading-relaxed">
                  {isKannada ? 'ಅಪರಾಧ ಸಾಂದ್ರತೆಯ ಭೌಗೋಳಿಕ ದೃಶ್ಯೀಕರಣ. ಗಸ್ತು ಅಗತ್ಯತೆಗಳನ್ನು ನಿರೀಕ್ಷಿಸಿ ಮತ್ತು ಸಂಪನ್ಮೂಲಗಳನ್ನು ಸಮರ್ಥವಾಗಿ ನಿಯೋಜಿಸಿ.' : 'Geospatial visualization of crime density. Anticipate patrol requirements and allocate resources efficiently.'}
                </p>
              </div>
              <div className="mt-12 pt-6 border-t border-[var(--color-line)] flex justify-between items-center group-hover:border-[#1B1B1B] transition-colors cursor-pointer">
                <span className="text-[11px] font-bold text-[var(--color-ksp-text)] uppercase tracking-wider">
                  {isKannada ? 'ಕಾರ್ಯಕ್ಷೇತ್ರವನ್ನು ಪ್ರವೇಶಿಸಿ' : 'Access Workspace'}
                </span>
                <span className="material-symbols-outlined text-[var(--color-ksp-text)] group-hover:translate-x-1 transition-transform">arrow_forward</span>
              </div>
            </div>

            <div className="shrink-0 w-[420px] snap-center bg-[var(--color-white-card)] border border-[var(--color-line)] rounded-[32px] p-10 shadow-sm flex flex-col justify-between hover:shadow-xl transition-all duration-300 group">
              <div>
                <div className="inline-block px-4 py-1.5 bg-[#F3E5F5]/60 text-[#6A1B9A] border border-[#6A1B9A]/20 rounded text-[10px] font-bold uppercase tracking-wider mb-8">
                  {isKannada ? 'ಆಡಿಟ್ ಟ್ರಯಲ್ ಲೆಡ್ಜರ್' : 'Audit Trail Ledger'}
                </div>
                <h4 className="text-[24px] font-bold mb-4 text-[var(--color-ksp-text)] leading-snug">
                  {isKannada ? 'ಬದಲಾಗದ ಲಾಗಿಂಗ್' : 'Immutable Logging'}
                </h4>
                <p className="text-[15px] text-[var(--color-muted)] leading-relaxed">
                  {isKannada ? 'ಹೊಣೆಗಾರಿಕೆಗಾಗಿ ಪ್ಲಾಟ್ಫಾರ್ಮ್ ಬಳಕೆ, ಡೇಟಾ ಪ್ರಶ್ನೆಗಳು ಮತ್ತು ಪ್ರವೇಶ ವಿನಂತಿಗಳ ಸಂಪೂರ್ಣ ಕ್ರಿಪ್ಟೋಗ್ರಾಫಿಕ್ ಟ್ರ್ಯಾಕಿಂಗ್.' : 'Complete cryptographic tracking of platform usage, data queries, and access requests for accountability.'}
                </p>
              </div>
              <div className="mt-12 pt-6 border-t border-[var(--color-line)] flex justify-between items-center group-hover:border-[#1B1B1B] transition-colors cursor-pointer">
                <span className="text-[11px] font-bold text-[var(--color-ksp-text)] uppercase tracking-wider">
                  {isKannada ? 'ಕಾರ್ಯಕ್ಷೇತ್ರವನ್ನು ಪ್ರವೇಶಿಸಿ' : 'Access Workspace'}
                </span>
                <span className="material-symbols-outlined text-[var(--color-ksp-text)] group-hover:translate-x-1 transition-transform">arrow_forward</span>
              </div>
            </div>
          </div>
        </section>

        {/* Clearance Tiers */}
        <section className="py-[160px] px-10 max-w-[1728px] mx-auto flex flex-col items-center bg-[var(--color-page-bg)] border-t border-[var(--color-line)]">
          <h2 className="text-[48px] mb-6 font-bold tracking-tight text-center text-[var(--color-ksp-text)]">
            {isKannada ? 'ಪಾತ್ರ-ಆಧಾರಿತ ಪ್ರವೇಶ ಪ್ರೋಟೋಕಾಲ್ಗಳು' : 'Role-Based Access Protocols'}
          </h2>
          <p className="text-[18px] text-[var(--color-muted)] text-center mb-20 max-w-2xl">
            {isKannada ? 'ಕಟ್ಟುನಿಟ್ಟಾದ ಸರಪಳಿ-ಕಸ್ಟಡಿ ಮತ್ತು ಡೇಟಾ ಸಮಗ್ರತೆಯನ್ನು ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಲು ಕ್ಲಿಯರೆನ್ಸ್ ಮಟ್ಟದಿಂದ ವಿಭಜಿತವಾದ ಸುರಕ್ಷಿತ ಪರಿಸರಗಳು.' : 'Secure environments partitioned by clearance level to ensure strict chain-of-custody and data integrity.'}
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-10 w-full max-w-[1100px] mx-auto">
            <div className="bg-[var(--color-white-card)] rounded-[40px] p-12 border border-[var(--color-line)] shadow-md flex flex-col">
              <div className="flex items-center gap-4 mb-10">
                <span className="material-symbols-outlined text-[var(--color-ksp-text)] text-[32px]">badge</span>
                <h3 className="text-[28px] font-bold text-[var(--color-ksp-text)]">
                  {isKannada ? 'ತನಿಖಾಧಿಕಾರಿ ಪ್ರವೇಶ' : 'Investigator Access'}
                </h3>
              </div>
              <div className="flex-grow space-y-5">
                <div className="flex gap-4 items-start">
                  <span className="material-symbols-outlined text-black text-[24px]">check_circle</span>
                  <span className="text-[15px] text-[var(--color-ksp-text)] pt-0.5">
                    {isKannada ? 'ನಿಲ್ದಾಣ ಮಟ್ಟದ ಪ್ರಕರಣದ ಡೇಟಾ ನಮೂದು' : 'Station-level case data entry'}
                  </span>
                </div>
                <div className="flex gap-4 items-start">
                  <span className="material-symbols-outlined text-black text-[24px]">check_circle</span>
                  <span className="text-[15px] text-[var(--color-ksp-text)] pt-0.5">
                    {isKannada ? 'ಅಧಿಕಾರ ವ್ಯಾಪ್ತಿಯಲ್ಲಿ ದ್ವಿಭಾಷಾ RAG ಪ್ರಶ್ನೆ' : 'Bilingual RAG query within jurisdiction'}
                  </span>
                </div>
                <div className="flex gap-4 items-start">
                  <span className="material-symbols-outlined text-black text-[24px]">check_circle</span>
                  <span className="text-[15px] text-[var(--color-ksp-text)] pt-0.5">
                    {isKannada ? 'ಪ್ರಮಾಣಿತ ಶಂಕಿತ ಪ್ರೊಫೈಲ್ ಉತ್ಪಾದನೆ' : 'Standard suspect profile generation'}
                  </span>
                </div>
                <div className="flex gap-4 items-start opacity-30 mt-8">
                  <span className="material-symbols-outlined text-[var(--color-muted)] text-[24px]">cancel</span>
                  <span className="text-[15px] text-[var(--color-ksp-text)] line-through pt-0.5">
                    {isKannada ? 'ಅಡ್ಡ-ಜಿಲ್ಲಾ ಗುಪ್ತಚರ ಮ್ಯಾಪಿಂಗ್' : 'Cross-district intelligence mapping'}
                  </span>
                </div>
                <div className="flex gap-4 items-start opacity-30">
                  <span className="material-symbols-outlined text-[var(--color-muted)] text-[24px]">cancel</span>
                  <span className="text-[15px] text-[var(--color-ksp-text)] line-through pt-0.5">
                    {isKannada ? 'ಸಿಸ್ಟಮ್-ವ್ಯಾಪಕ ಆಡಿಟ್ ಟ್ರಯಲ್ ಲಾಗ್ಗಳು' : 'System-wide audit trail logs'}
                  </span>
                </div>
              </div>
              <button className="mt-14 w-full py-4 rounded-full border-[1.5px] border-[var(--color-line)] text-[var(--color-ksp-text)] text-[13px] font-bold hover:bg-[var(--color-soft-card)] transition-colors uppercase tracking-wider">
                {isKannada ? 'ಪ್ರೋಟೋಕಾಲ್ಗಳನ್ನು ವೀಕ್ಷಿಸಿ' : 'View Protocols'}
              </button>
            </div>

            <div className="bg-black rounded-[40px] p-12 shadow-[0_24px_80px_rgba(0,0,0,0.3)] flex flex-col relative overflow-hidden">
              <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-gradient-to-bl from-white/10 to-transparent rounded-bl-full pointer-events-none"></div>

              <div className="flex justify-between items-start mb-10 relative z-10">
                <div className="flex items-center gap-4">
                  <span className="material-symbols-outlined text-white text-[32px]">admin_panel_settings</span>
                  <h3 className="text-[28px] font-bold text-white">
                    {isKannada ? 'ಕಮಾಂಡ್ ಪ್ರವೇಶ' : 'Command Access'}
                  </h3>
                </div>
                <span className="bg-white/20 border border-white/30 text-white px-3 py-1.5 rounded text-[10px] font-bold uppercase tracking-wider">
                  {isKannada ? 'ಎಸ್ಪಿ / ಡಿವೈಎಸ್ಪಿ' : 'SP / DySP'}
                </span>
              </div>

              <div className="flex-grow space-y-5 relative z-10">
                <div className="flex gap-4 items-start">
                  <span className="material-symbols-outlined text-[#FF416C] text-[24px]">check_circle</span>
                  <span className="text-[15px] text-white/90 pt-0.5">
                    {isKannada ? 'ಜಾಗತಿಕ ನೆಟ್ವರ್ಕ್ ಲಿಂಕ್ ವಿಶ್ಲೇಷಣೆ' : 'Global network link analysis'}
                  </span>
                </div>
                <div className="flex gap-4 items-start">
                  <span className="material-symbols-outlined text-[#FF416C] text-[24px]">check_circle</span>
                  <span className="text-[15px] text-white/90 pt-0.5">
                    {isKannada ? 'ರಾಜ್ಯಾದ್ಯಂತ ಗುಪ್ತಚರ ಶಾಖ ನಕ್ಷೆಗಳು' : 'State-wide intelligence heatmaps'}
                  </span>
                </div>
                <div className="flex gap-4 items-start">
                  <span className="material-symbols-outlined text-[#FF416C] text-[24px]">check_circle</span>
                  <span className="text-[15px] text-white/90 pt-0.5">
                    {isKannada ? 'ನೈಜ-ಸಮಯದ ಅಡ್ಡ-ಜಿಲ್ಲಾ ಎಚ್ಚರಿಕೆಗಳು' : 'Real-time cross-district alerts'}
                  </span>
                </div>
                <div className="flex gap-4 items-start">
                  <span className="material-symbols-outlined text-[#FF416C] text-[24px]">check_circle</span>
                  <span className="text-[15px] text-white/90 pt-0.5">
                    {isKannada ? 'ಮುನ್ಸೂಚಕ ನಿಯೋಜನೆ ಮಾಡ್ಯೂಲ್ಗಳು' : 'Predictive deployment modules'}
                  </span>
                </div>
                <div className="flex gap-4 items-start">
                  <span className="material-symbols-outlined text-[#FF416C] text-[24px]">check_circle</span>
                  <span className="text-[15px] text-white/90 pt-0.5">
                    {isKannada ? 'ಬದಲಾಗದ ಆಡಿಟ್ ಲೆಡ್ಜರ್ ಪ್ರವೇಶ' : 'Immutable audit ledger access'}
                  </span>
                </div>
              </div>
              <button className="mt-14 w-full py-4 rounded-full bg-white text-black text-[13px] font-bold hover:bg-[var(--color-page-bg)] transition-colors relative z-10 uppercase tracking-wider">
                {isKannada ? 'ತೆರವುಗೊಳಿಸಲು ವಿನಂತಿಸಿ' : 'Request Clearance'}
              </button>
            </div>
          </div>
        </section>

        {/* Operational FAQ Accordion */}
        <section className="py-[160px] px-10 max-w-[900px] mx-auto bg-[var(--color-page-bg)] border-t border-[var(--color-line)] mb-20">
          <h2 className="text-[48px] mb-16 font-bold tracking-tight text-[var(--color-ksp-text)] text-center">
            {isKannada ? 'ಕಾರ್ಯಾಚರಣೆಯ ನಿಯತಾಂಕಗಳು' : 'Operational Parameters'}
          </h2>

          <div className="border-t-[1.5px] border-[var(--color-line)]">
            <details className="group [&_summary::-webkit-details-marker]:hidden">
              <summary className="py-8 border-b-[1.5px] border-[var(--color-line)] flex justify-between items-center cursor-pointer list-none">
                <h4 className="text-xl font-bold text-[var(--color-ksp-text)] group-hover:text-black transition-colors pr-8">
                  {isKannada ? 'ಯಾವುದೇ ತನಿಖಾ ಡೇಟಾ ಭಾರತವನ್ನು ಬಿಡುತ್ತದೆಯೇ?' : 'Does any investigative data leave India?'}
                </h4>
                <span className="material-symbols-outlined text-[var(--color-ksp-text)] text-[24px] shrink-0 group-open:hidden">add</span>
                <span className="material-symbols-outlined text-[var(--color-ksp-text)] text-[24px] shrink-0 hidden group-open:block">remove</span>
              </summary>
              <div className="mt-6 pb-6 border-b-[1.5px] border-[var(--color-line)]">
                <p className="text-[18px] text-[var(--color-muted)] max-w-3xl">
                  {isKannada ? 'ಇಲ್ಲ. ಸಂಪೂರ್ಣ ಕೆಎಸ್ಪಿ ಇಂಟೆಲ್ ಆರ್ಕಿಟೆಕ್ಚರ್ ಅನ್ನು ಸಾರ್ವಭೌಮ, ಆನ್-ಪ್ರಿಮೈಸ್ ಮೂಲಸೌಕರ್ಯದಲ್ಲಿ ನಿಯೋಜಿಸಲಾಗಿದೆ. ಯಾವುದೇ ಬಾಹ್ಯ API ಗಳು ಅಥವಾ ವಿದೇಶಿ ಸರ್ವರ್ಗಳು ಡೇಟಾಸೆಟ್ನ ಯಾವುದೇ ಭಾಗವನ್ನು ಪ್ರಕ್ರಿಯೆಗೊಳಿಸುವುದಿಲ್ಲ.' : 'No. The entire KSP Intel architecture is deployed on sovereign, on-premise infrastructure. No external APIs or foreign servers process any part of the dataset.'}
                </p>
              </div>
            </details>

            <details className="group [&_summary::-webkit-details-marker]:hidden">
              <summary className="py-8 border-b-[1.5px] border-[var(--color-line)] flex justify-between items-center cursor-pointer list-none">
                <h4 className="text-xl font-bold text-[var(--color-ksp-text)] group-hover:text-black transition-colors pr-8">
                  {isKannada ? 'ದ್ವಿಭಾಷಾ ಇನ್ಪುಟ್ ಅನ್ನು ಸುರಕ್ಷಿತವಾಗಿ ಹೇಗೆ ಪ್ರಕ್ರಿಯೆಗೊಳಿಸಲಾಗುತ್ತದೆ?' : 'How is bilingual input processed securely?'}
                </h4>
                <span className="material-symbols-outlined text-[var(--color-ksp-text)] text-[24px] shrink-0 group-open:hidden">add</span>
                <span className="material-symbols-outlined text-[var(--color-ksp-text)] text-[24px] shrink-0 hidden group-open:block">remove</span>
              </summary>
              <div className="mt-6 pb-6 border-b-[1.5px] border-[var(--color-line)]">
                <p className="text-[18px] text-[var(--color-muted)] max-w-3xl">
                  {isKannada ? 'ಕನ್ನಡ-ಇಂಗ್ಲಿಷ್ ಕೋಡ್-ಸ್ವಿಚಿಂಗ್ ಮತ್ತು ಸ್ಥಳೀಯ ಕಾನೂನು ಜಾರಿ ಪರಿಭಾಷೆಗಾಗಿ ನಿರ್ದಿಷ್ಟವಾಗಿ ಟ್ಯೂನ್ ಮಾಡಲಾದ ಸ್ಥಳೀಯ ಎಸ್ಎಲ್ಎಂ (ಸಣ್ಣ ಭಾಷಾ ಮಾದರಿ) ಅನ್ನು ನಾವು ಬಳಸಿಕೊಳ್ಳುತ್ತೇವೆ.' : 'We utilize a localized SLM (Small Language Model) fine-tuned specifically for Kannada-English code-switching and local law enforcement terminology.'}
                </p>
              </div>
            </details>

            <details className="group [&_summary::-webkit-details-marker]:hidden">
              <summary className="py-8 border-b-[1.5px] border-[var(--color-line)] flex justify-between items-center cursor-pointer list-none">
                <h4 className="text-xl font-bold text-[var(--color-ksp-text)] group-hover:text-black transition-colors pr-8">
                  {isKannada ? 'ನಾವು ಪರಂಪರೆಯ ಎಫ್ಐಆರ್ ಡೇಟಾಬೇಸ್ಗಳನ್ನು ಸಂಯೋಜಿಸಬಹುದೇ?' : 'Can we integrate legacy FIR databases?'}
                </h4>
                <span className="material-symbols-outlined text-[var(--color-ksp-text)] text-[24px] shrink-0 group-open:hidden">add</span>
                <span className="material-symbols-outlined text-[var(--color-ksp-text)] text-[24px] shrink-0 hidden group-open:block">remove</span>
              </summary>
              <div className="mt-6 pb-6 border-b-[1.5px] border-[var(--color-line)]">
                <p className="text-[18px] text-[var(--color-muted)] max-w-3xl">
                  {isKannada ? 'ಹೌದು, ಪ್ಲಾಟ್ಫಾರ್ಮ್ 15 ವರ್ಷಗಳ ಅವಧಿಯ ರಚನೆಯಿಲ್ಲದ ಐತಿಹಾಸಿಕ ದಾಖಲೆಗಳನ್ನು ಸೇವಿಸಲು, ಸ್ವಚ್ಛಗೊಳಿಸಲು ಮತ್ತು ವೆಕ್ಟರೈಸ್ ಮಾಡಲು ವಿನ್ಯಾಸಗೊಳಿಸಲಾದ ಸ್ವಯಂಚಾಲಿತ ಇಟಿಎಲ್ ಪೈಪ್ಲೈನ್ಗಳನ್ನು ಒಳಗೊಂಡಿದೆ.' : 'Yes, the platform includes automated ETL pipelines designed to ingest, sanitize, and vectorize unstructured historical records spanning over 15 years.'}
                </p>
              </div>
            </details>

            <details className="group [&_summary::-webkit-details-marker]:hidden">
              <summary className="py-8 border-b-[1.5px] border-[var(--color-line)] flex justify-between items-center cursor-pointer list-none">
                <h4 className="text-xl font-bold text-[var(--color-ksp-text)] group-hover:text-black transition-colors pr-8">
                  {isKannada ? 'ನೋಡ್ ಸಂಪರ್ಕವನ್ನು ಕಳೆದುಕೊಂಡರೆ ಏನಾಗುತ್ತದೆ?' : 'What happens if a node loses connectivity?'}
                </h4>
                <span className="material-symbols-outlined text-[var(--color-ksp-text)] text-[24px] shrink-0 group-open:hidden">add</span>
                <span className="material-symbols-outlined text-[var(--color-ksp-text)] text-[24px] shrink-0 hidden group-open:block">remove</span>
              </summary>
              <div className="mt-6 pb-6 border-b-[1.5px] border-[var(--color-line)]">
                <p className="text-[18px] text-[var(--color-muted)] max-w-3xl">
                  {isKannada ? 'ಸಿಸ್ಟಮ್ ವಿಭಜಿತ ಆಫ್ಲೈನ್ ಕಾರ್ಯಗತಗೊಳಿಸುವಿಕೆಯನ್ನು ಬೆಂಬಲಿಸುತ್ತದೆ. ಫೀಲ್ಡ್ ಏಜೆಂಟ್ಗಳು ಸ್ಥಳೀಯವಾಗಿ ಎಂಟಿಟಿಗಳನ್ನು ಲಾಗ್ ಮಾಡುವುದನ್ನು ಮುಂದುವರಿಸಬಹುದು, ಸಂಪರ್ಕವನ್ನು ಮರುಸ್ಥಾಪಿಸಿದ ನಂತರ ಅದು ಸ್ವಯಂಚಾಲಿತವಾಗಿ ಎನ್ಕ್ರಿಪ್ಟ್ ಮಾಡುತ್ತದೆ ಮತ್ತು ಸಿಂಕ್ ಮಾಡುತ್ತದೆ.' : 'The system supports partitioned offline execution. Field agents can continue logging entities locally, which automatically encrypt and sync once connectivity is restored.'}
                </p>
              </div>
            </details>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-black text-white pt-32 pb-16 px-10 relative z-20">
        <div className="max-w-[1728px] mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-32 mb-32">
            <div className="flex flex-col gap-8">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full border border-[var(--color-line)]/20 flex items-center justify-center shrink-0 bg-[#F0EFEB]">
                  <img src="/app/image copy.png" alt="Govt Emblem" className="w-8 h-8 object-contain" />
                </div>
                <h3 className="font-bold text-lg leading-tight" dangerouslySetInnerHTML={{ __html: isKannada ? 'ಕರ್ನಾಟಕ<br/>ರಾಜ್ಯ ಪೊಲೀಸ್' : 'Karnataka<br/>State Police' }}></h3>
              </div>
              <p className="text-[15px] text-white/80 max-w-xs">
                {isKannada ? 'ಕರ್ನಾಟಕದಲ್ಲಿ ಆಧುನಿಕ ಕಾನೂನು ಜಾರಿಗಾಗಿ ಅಧಿಕೃತ ಗುಪ್ತಚರ ಮತ್ತು ಆಡಳಿತ ಪೋರ್ಟಲ್.' : 'The official intelligence and administrative portal for modern law enforcement in Karnataka.'}
              </p>
              <div className="flex gap-4">
                <a className="w-10 h-10 rounded-full border border-white/30 flex items-center justify-center hover:bg-white/20 transition-colors" href="#">
                  <span className="material-symbols-outlined text-[20px]">share</span>
                </a>
                <a className="w-10 h-10 rounded-full border border-white/30 flex items-center justify-center hover:bg-white/20 transition-colors" href="#">
                  <span className="material-symbols-outlined text-[20px]">public</span>
                </a>
              </div>
            </div>

            <div>
              <h4 className="text-[10px] font-bold text-white mb-6 uppercase tracking-widest font-label">
                {isKannada ? 'ಇಲಾಖೆ' : 'Department'}
              </h4>
              <ul className="flex flex-col gap-4">
                <li><a className="text-[15px] text-white/70 hover:text-white transition-colors" href="#">{isKannada ? 'ನಮ್ಮ ಬಗ್ಗೆ' : 'About Us'}</a></li>
                <li><a className="text-[15px] text-white/70 hover:text-white transition-colors" href="#">{isKannada ? 'ಆಡಳಿತ' : 'Administration'}</a></li>
                <li><a className="text-[15px] text-white/70 hover:text-white transition-colors" href="#">{isKannada ? 'ನಮ್ಮನ್ನು ಸಂಪರ್ಕಿಸಿ' : 'Contact Us'}</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-[10px] font-bold text-white mb-6 uppercase tracking-widest font-label">
                {isKannada ? 'ಪ್ರಮುಖ ಲಿಂಕ್ಗಳು' : 'Important Links'}
              </h4>
              <ul className="flex flex-col gap-4">
                <li><a className="text-[15px] text-white/70 hover:text-white transition-colors" href="#">{isKannada ? 'ಕರ್ನಾಟಕ ಸರ್ಕಾರದ ಅಧಿಕೃತ ಜಾಲತಾಣ' : 'Official Website of GoK'}</a></li>
                <li><a className="text-[15px] text-white/70 hover:text-white transition-colors" href="#">{isKannada ? 'ಟೆಂಡರ್ಗಳು - ಇ-ಪ್ರೊಕ್ಯೂರ್ಮೆಂಟ್' : 'Tenders - eProcurement'}</a></li>
                <li><a className="text-[15px] text-white/70 hover:text-white transition-colors" href="#">{isKannada ? 'ಆರ್.ಟಿ.ಐ' : 'RTI'}</a></li>
                <li><a className="text-[15px] text-white/70 hover:text-white transition-colors" href="#">{isKannada ? 'ಪೊಲೀಸ್ ಠಾಣೆ ಲೊಕೇಟರ್' : 'Police Station Locator'}</a></li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-white/20 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-[11px] font-bold text-white/70 font-label">© 2026 Karnataka State Police. All rights reserved.</p>
            <div className="flex gap-8">
              <a className="text-[11px] font-bold text-white/70 hover:text-white transition-colors font-label" href="#">{isKannada ? 'ಗೌಪ್ಯತಾ ನೀತಿ' : 'Privacy Policy'}</a>
              <a className="text-[11px] font-bold text-white/70 hover:text-white transition-colors font-label" href="#">{isKannada ? 'ಸೇವಾ ನಿಯಮಗಳು' : 'Terms of Service'}</a>
              <a className="text-[11px] font-bold text-white/70 hover:text-white transition-colors font-label" href="#">{isKannada ? 'ಪ್ರವೇಶಿಸುವಿಕೆ ಹೇಳಿಕೆ' : 'Accessibility Statement'}</a>
            </div>
          </div>
        </div>
      </footer>
    </>
  );
}


