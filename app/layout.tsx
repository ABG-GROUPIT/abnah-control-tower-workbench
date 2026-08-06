import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL(
    "https://abg-groupit.github.io/abnah-control-tower-workbench/",
  ),
  title: "ABNAH Control Tower Workbench",
  description:
    "A visual handover of ABNAH source reports, the lean Zoho Analytics model, governed calculations, forecasts, decision outputs and exact dashboard filter mappings.",
  openGraph: {
    title: "ABNAH Control Tower Workbench",
    description: "From source reports to filter-safe daily decisions.",
    images: [{ url: "/og.png", width: 1710, height: 912 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "ABNAH Control Tower Workbench",
    description: "From source reports to filter-safe daily decisions.",
    images: ["/og.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
