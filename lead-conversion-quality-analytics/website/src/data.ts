// Generated from ../data/exports by scripts/sync-analytics-data.mjs. Do not hand-edit.
export const months = [
  { month: "Apr", leads: 518, closed: 56, rate: 10.81, positive: 15.25, low: 8.42, high: 13.78 },
  { month: "May", leads: 580, closed: 37, rate: 6.38, positive: 10.17, low: 4.66, high: 8.67 },
  { month: "Jun", leads: 609, closed: 63, rate: 10.34, positive: 14.12, low: 8.17, high: 13.02 },
  { month: "Jul", leads: 532, closed: 33, rate: 6.20, positive: 9.21, low: 4.45, high: 8.58 },
  { month: "Aug", leads: 438, closed: 41, rate: 9.36, positive: 14.16, low: 6.98, high: 12.45 },
  { month: "Sep", leads: 344, closed: 15, rate: 4.36, positive: 16.86, low: 2.66, high: 7.07 }
];

export const dimensions = {
  "Ad group": [
    { segment: "Holding Tank - Debt", leads: 338, closed: 49, rate: 14.50, lift: 1.79, significant: true },
    { segment: "Consolidate", leads: 169, closed: 21, rate: 12.43, lift: 1.53, significant: false },
    { segment: "Debt", leads: 93, closed: 11, rate: 11.83, lift: 1.46, significant: false },
    { segment: "General Debt", leads: 130, closed: 13, rate: 10.00, lift: 1.23, significant: false },
    { segment: "Unknown", leads: 272, closed: 26, rate: 9.56, lift: 1.18, significant: false },
    { segment: "Debt Consolidation", leads: 195, closed: 17, rate: 8.72, lift: 1.07, significant: false },
    { segment: "How", leads: 115, closed: 10, rate: 8.70, lift: 1.07, significant: false },
    { segment: "Lower Payments", leads: 197, closed: 10, rate: 5.08, lift: 0.63, significant: false },
    { segment: "Credit Card Consolidation", leads: 84, closed: 4, rate: 4.76, lift: 0.59, significant: false },
    { segment: "Credit Card Debt - high volume", leads: 258, closed: 12, rate: 4.65, lift: 0.57, significant: false },
    { segment: "Student Debt", leads: 360, closed: 4, rate: 1.11, lift: 0.14, significant: true }
  ],
  "Debt level": [
    { segment: "70001-90000", leads: 131, closed: 18, rate: 13.74, lift: 1.69, significant: false },
    { segment: "10001-15000", leads: 291, closed: 34, rate: 11.68, lift: 1.44, significant: false },
    { segment: "90000-100000", leads: 90, closed: 9, rate: 10.00, lift: 1.23, significant: false },
    { segment: "50001-70000", leads: 245, closed: 22, rate: 8.98, lift: 1.11, significant: false },
    { segment: "20001-30000", leads: 456, closed: 40, rate: 8.77, lift: 1.08, significant: false },
    { segment: "15001-20000", leads: 408, closed: 35, rate: 8.58, lift: 1.06, significant: false },
    { segment: "30001-50000", leads: 496, closed: 39, rate: 7.86, lift: 0.97, significant: false },
    { segment: "7500-15000", leads: 271, closed: 19, rate: 7.01, lift: 0.86, significant: false },
    { segment: "7500-10000", leads: 442, closed: 22, rate: 4.98, lift: 0.61, significant: false },
    { segment: "More_than_100000", leads: 191, closed: 7, rate: 3.66, lift: 0.45, significant: false }
  ],
  "Partner": [
    { segment: "AdKnowledge", leads: 171, closed: 21, rate: 12.28, lift: 1.51, significant: false },
    { segment: "Call center", leads: 271, closed: 26, rate: 9.59, lift: 1.18, significant: false },
    { segment: "Yahoo", leads: 958, closed: 74, rate: 7.72, lift: 0.95, significant: false },
    { segment: "Google", leads: 1618, closed: 123, rate: 7.60, lift: 0.94, significant: false }
  ]
} as const;

export const scenarios = [
  { name: "Portfolio conversion target", affected: 3021, destination: 9.60, incremental: 46.00, total: 291, rate: 9.63, confidence: "Planning benchmark" },
  { name: "Observed ad-group mix test", affected: 344, destination: 14.50, incremental: 46.05, total: 291, rate: 9.63, confidence: "Directional hypothesis" },
  { name: "Conservative ad-group mix test", affected: 513, destination: 11.14, incremental: 46.00, total: 291, rate: 9.63, confidence: "Lower-bound hypothesis" }
];
