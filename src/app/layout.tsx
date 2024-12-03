import type { Metadata } from "next";
import { Roboto } from "next/font/google";
import localFont from "next/font/local";
import "./globals.css";
import Navbar from "@/components/navbar";
import Footer from "@/components/footer";
import { Toaster } from "@/components/ui/toaster";
import { UserProvider } from "./contexts/user-context";
import DialogflowMessenger from "@/components/DialogflowMessenger";

const default_font = Roboto({
  weight: ["300", "500", "700"],
  subsets: ["latin"],
  style: ["normal", "italic"],
});

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "QuickDataProcessor",
  description: "An all-in-one data processing tool",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <UserProvider>
        <body
          className={
            `${default_font.className} ${geistSans.variable} ${geistMono.variable} antialiased` +
            "min-h-[80vh]"
          }
        >
          <Navbar />
          <DialogflowMessenger />
          <main className="flex-grow flex justify-center items-center">
            {children}
          </main>
          <Footer />
          <Toaster />
        </body>
      </UserProvider>
    </html>
  );
}
