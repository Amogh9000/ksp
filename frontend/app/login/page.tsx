'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

// ── Type shim for the Catalyst SDK global ───────────────────────────────────
declare global {
  interface Window {
    catalyst?: {
      auth: {
        signIn: (elementId: string, config?: Record<string, unknown>) => void;
      };
    };
  }
}

/** Dynamically injects a <script> tag and resolves when it has loaded. */
function loadScript(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve();
      return;
    }
    const el = document.createElement('script');
    el.src = src;
    el.async = false; // keep insertion order
    el.onload = () => resolve();
    el.onerror = () => reject(new Error(`[KSP Auth] Failed to load: ${src}`));
    document.head.appendChild(el);
  });
}

export default function LoginPage() {
  const [isKannada, setIsKannada] = useState(false);
  const [authError, setAuthError] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        // 1. Load the Catalyst Web SDK from Zoho CDN
        await loadScript(
          'https://static.zohocdn.com/catalyst/sdk/js/4.5.0/catalystWebSDK.js'
        );
        // 2. Load the Catalyst environment init script (served by Catalyst hosting)
        await loadScript('/__catalyst/sdk/init.js');

        // 3. Mount the auth iFrame into our container div
        if (window.catalyst?.auth) {
          window.catalyst.auth.signIn('loginDivElementId', {
            // After successful login, redirect to the dashboard
            service_url: '/app/dashboard/',
            // Custom CSS for the embedded login form
            css_url: '/app/css/embeddediframe.css',
            // Load forgot-password inside our iFrame shell (same div by default)
            is_customize_forgot_password: true,
            forgot_password_css_url: '/app/css/reset_password.css',
          });
        } else {
          // SDK loaded but catalyst global not set — likely running outside Catalyst hosting
          console.warn('[KSP Auth] Catalyst SDK loaded but `window.catalyst` is undefined. ' +
            'Auth iFrame only works when the app is hosted on Zoho Catalyst.');
          setAuthError(true);
        }
      } catch (err) {
        console.error(err);
        setAuthError(true);
      }
    })();
  }, []);

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
          AUTH_SEC_1
        </div>

        {/* ── Branding header ────────────────────────────────────────────── */}
        <div className="flex flex-col items-center mb-8 mt-4">
          <div className="w-16 h-16 mb-5">
            <img
              src="/app/image copy.png"
              alt="Karnataka State Police Logo"
              className="w-full h-full object-contain drop-shadow-sm opacity-90"
            />
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

        {/* ── Catalyst iFrame Mount Point ─────────────────────────────────
            The Catalyst SDK renders its login form (email + password + submit)
            as an iFrame inside this div. Our CSS at /css/embeddediframe.css
            styles it to match the KSP shell.
        ─────────────────────────────────────────────────────────────────── */}
        <div id="loginDivElementId" className="w-full min-h-[180px]" />

        {/* ── Dev-mode fallback (only shown outside Catalyst hosting) ────── */}
        {authError && (
          <div className="mt-4 p-4 border border-amber-300 bg-amber-50 text-amber-800 text-[12px] font-mono rounded-sm">
            <p className="font-bold uppercase tracking-wider mb-1">⚠ Local Dev Notice</p>
            <p>
              The Catalyst auth iFrame only initialises when the app is served from
              Zoho Catalyst Web Hosting. To test locally, deploy first or use the
              Catalyst local emulator.
            </p>
          </div>
        )}

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


