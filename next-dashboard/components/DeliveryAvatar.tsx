"use client";

import { useState } from "react";

const messages = [
  "AI courier tip: click states on the Geographic map for local market drilldowns.",
  "Forecast note: the best holdout model reduced MAPE to 1.29%.",
  "Expansion hint: Stars are high-revenue, high-opportunity cities worth protecting.",
  "Health score tip: At Risk partners may need visibility, menu, or onboarding support.",
  "SQL Appendix: query outputs are precomputed, so the dashboard stays fast.",
];

function CourierIllustration() {
  return (
    <svg
      viewBox="0 0 200 118"
      aria-hidden="true"
      className="delivery-courier-svg h-[4.75rem] w-[7.75rem]"
    >
      <defs>
        <linearGradient id="scooter-body" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#FF9A5C" />
          <stop offset="55%" stopColor="#FF6B35" />
          <stop offset="100%" stopColor="#D84E1F" />
        </linearGradient>
        <linearGradient id="jacket" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#FF8A4A" />
          <stop offset="100%" stopColor="#E85A24" />
        </linearGradient>
        <linearGradient id="box-side" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#FF7A3D" />
          <stop offset="100%" stopColor="#FF6B35" />
        </linearGradient>
        <radialGradient id="headlight-glow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#FFF8E8" />
          <stop offset="70%" stopColor="#FFE08A" />
          <stop offset="100%" stopColor="#FFB347" />
        </radialGradient>
        <filter id="courier-shadow" x="-20%" y="-20%" width="140%" height="160%">
          <feDropShadow dx="0" dy="5" stdDeviation="4" floodColor="#000" floodOpacity="0.38" />
        </filter>
      </defs>

      <g filter="url(#courier-shadow)">
        <ellipse cx="98" cy="108" rx="58" ry="7" fill="#000" opacity="0.18" />

        <g>
          <circle cx="52" cy="96" r="13" fill="#1A1A22" />
          <circle cx="52" cy="96" r="9" fill="#2E2E38" />
          <circle cx="52" cy="96" r="4.5" fill="#55556A" />
        </g>
        <g>
          <circle cx="142" cy="96" r="13" fill="#1A1A22" />
          <circle cx="142" cy="96" r="9" fill="#2E2E38" />
          <circle cx="142" cy="96" r="4.5" fill="#55556A" />
        </g>

        <path
          d="M34 88c8-10 24-14 42-12 10 1 18 5 24 11l8 9H34z"
          fill="url(#scooter-body)"
        />
        <path d="M66 74h58c8 0 14 6 14 14v8H58v-14c0-5 4-8 8-8z" fill="url(#scooter-body)" />
        <path d="M122 66h24c6 0 11 5 11 11v19h-18l-17-30z" fill="#FF7A3D" />
        <rect x="126" y="52" width="30" height="24" rx="3" fill="url(#box-side)" />
        <rect x="129" y="55" width="24" height="18" rx="2" fill="#FF8F52" />
        <circle cx="141" cy="64" r="6.5" fill="#FFF" />
        <text x="141" y="67.5" textAnchor="middle" fontSize="9" fontWeight="900" fill="#FF6B35">
          S
        </text>

        <path d="M88 78h18v16H84c-2 0-4-2-4-4v-8c0-2 2-4 4-4h4z" fill="#1A1A22" />
        <path d="M92 70h14c4 0 7 3 7 7v8H88v-8c0-4 3-7 7-7z" fill="url(#jacket)" />
        <circle cx="99" cy="58" r="11" fill="#F2B48C" />
        <path d="M88 54c2-6 8-10 15-9 6 1 10 5 11 11l-12 3-14-5z" fill="#FF6B35" />
        <rect x="90" y="49" width="18" height="5" rx="2.5" fill="#FF8A4A" />
        <circle cx="95" cy="57" r="1.6" fill="#1A1A22" />
        <circle cx="104" cy="57" r="1.6" fill="#1A1A22" />
        <path d="M96 61c2 1.5 4 1.5 6 0" stroke="#C97A5D" strokeWidth="1.4" strokeLinecap="round" fill="none" />

        <path d="M86 66c-6-2-10 0-12 5" stroke="#F2B48C" strokeWidth="4" strokeLinecap="round" />
        <path d="M110 66c6-2 12 0 14 5" stroke="#F2B48C" strokeWidth="4" strokeLinecap="round" />
        <path d="M78 70h10M112 70h12" stroke="#ECECEA" strokeWidth="3" strokeLinecap="round" />

        <path d="M146 78h18c5 0 9 4 9 9v7h-16l-11-16z" fill="url(#scooter-body)" />
        <circle cx="168" cy="82" r="9" fill="url(#headlight-glow)" />
        <circle cx="168" cy="82" r="5.5" fill="#FFF6D8" />
        <path d="M160 74h8v18h-8z" fill="#FF8A4A" />
      </g>

      <path
        d="M18 44c10-8 22-12 36-10M24 30l8-4M26 38h10M22 48l9 3"
        stroke="#F2C94C"
        strokeWidth="2"
        strokeLinecap="round"
        opacity="0.75"
      />
    </svg>
  );
}

export function DeliveryAvatar() {
  const [messageIndex, setMessageIndex] = useState(0);
  const [open, setOpen] = useState(false);

  const nextMessage = () => {
    setOpen(true);
    setMessageIndex((current) => (current + 1) % messages.length);
  };

  return (
    <div className="pointer-events-none fixed bottom-3 left-40 right-4 z-40 h-24 overflow-hidden">
      <div className="delivery-avatar-track pointer-events-auto absolute bottom-0">
        <button
          type="button"
          onClick={nextMessage}
          className="delivery-courier-button group relative rounded-full border border-[rgba(255,107,53,0.35)] bg-[#101118]/88 px-2.5 py-1.5 shadow-2xl shadow-black/40 backdrop-blur transition hover:border-[var(--accent)]"
          aria-label="Swiggy AI courier assistant"
        >
          {open ? (
            <span className="absolute bottom-16 left-0 w-72 rounded-2xl border border-[var(--accent)] bg-[#101118]/95 p-3 text-left text-[11px] font-semibold leading-5 text-[var(--text-primary)] shadow-2xl shadow-black/50 backdrop-blur">
              <span className="block text-[var(--accent)]">Swiggy AI Courier</span>
              {messages[messageIndex]}
              <span
                role="button"
                tabIndex={0}
                onClick={(event) => {
                  event.stopPropagation();
                  setOpen(false);
                }}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    event.stopPropagation();
                    setOpen(false);
                  }
                }}
                className="absolute right-2 top-1 cursor-pointer text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                aria-label="Hide courier message"
              >
                x
              </span>
            </span>
          ) : null}

          <span className="delivery-courier-figure relative flex items-center">
            <CourierIllustration />
            <span className="absolute -right-1 -top-1 rounded-full border border-[var(--accent)] bg-[#101118]/90 px-1.5 py-0.5 text-[9px] font-black text-[var(--accent)] shadow-md">
              AI
            </span>
          </span>
        </button>
      </div>
    </div>
  );
}
