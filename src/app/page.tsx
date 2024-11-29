'use client'

import Link from "next/link";
import { useState } from "react";
import { ArrowRight, Upload, Bot, FileText, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function HomePage() {

  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const toggleDropdown = () => setIsDropdownOpen(!isDropdownOpen);

  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative py-32 lg:py-36 bg-background">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col items-center space-y-4 text-center">
            <h1 className="text-3xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl">
              QuickDataPro
            </h1>
            <p className="mx-auto max-w-[700px] text-muted-foreground text-lg sm:text-xl">
              Powerful data processing at your fingertips. Transform your CSV,
              TXT, and JSON files instantly.
            </p>
            <div className="relative mt-8">
              <Button
                size="lg"
                className="flex items-center"
                onClick={toggleDropdown}
              >
                Try Now <ChevronDown className="ml-2 h-4 w-4" />
              </Button>
              {isDropdownOpen && (
                <div className="absolute top-12 left-0 w-48 bg-white border rounded-md shadow-md z-10">
                  <ul className="py-2">
                    <li>
                      <Link
                        href="/dataprocessing/1"
                        className="block px-4 py-2 hover:bg-gray-100"
                      >
                        Json To CSV
                      </Link>
                    </li>
                    <li>
                      <Link
                        href="/dataprocessing/2"
                        className="block px-4 py-2 hover:bg-gray-100"
                      >
                        Text To Entities
                      </Link>
                    </li>
                    <li>
                      <Link
                        href="/dataprocessing/3"
                        className="block px-4 py-2 hover:bg-gray-100"
                      >
                        Word Cloud
                      </Link>
                    </li>
                  </ul>
                </div>
              )}
            </div>
            <div className="mt-4">
              <Button variant="outline" size="lg" asChild>
                <Link href="/signup">
                  Register <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-muted">
        <div className="container px-4 md:px-6">
          <h2 className="text-3xl font-bold tracking-tighter text-center mb-12">
            Key Features
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="bg-background">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Upload className="h-6 w-6 mr-2" />
                  Quick Processing
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Process CSV, TXT, and JSON files instantly. Start with 2 free
                  files.
                </p>
              </CardContent>
            </Card>
            <Card className="bg-background">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Bot className="h-6 w-6 mr-2" />
                  Virtual Assistant
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Get instant help with our AI-powered virtual assistant.
                </p>
              </CardContent>
            </Card>
            <Card className="bg-background">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="h-6 w-6 mr-2" />
                  Unlimited Access
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Registered users enjoy unlimited file processing and advanced
                  features.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* User Types Section */}
      <section className="py-24">
        <div className="container px-4 md:px-6">
          <h2 className="text-3xl font-bold tracking-tighter text-center mb-12">
            Choose Your Access Level
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card>
              <CardHeader>
                <CardTitle>Guest Access</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li>Process up to 2 files</li>
                  <li>Basic virtual assistant</li>
                  <li>View public feedback</li>
                </ul>
              </CardContent>
            </Card>
            <Card className="border-primary">
              <CardHeader>
                <CardTitle>Registered User</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li>Unlimited file processing</li>
                  <li>Advanced virtual assistant</li>
                  <li>Processing history</li>
                  <li>Agent support</li>
                </ul>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>QDP Agent</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li>User management</li>
                  <li>Service control</li>
                  <li>Customer support</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-muted">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col items-center space-y-4 text-center">
            <h2 className="text-3xl font-bold tracking-tighter">
              Ready to Get Started?
            </h2>
            <p className="mx-auto max-w-[600px] text-muted-foreground text-lg">
              Join thousands of users who trust QuickDataPro for their data
              processing needs.
            </p>
            <Button size="lg" asChild className="mt-4">
              <Link href="/signup">
                Create Free Account <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}
