"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "@/hooks/use-toast";

export default function ContactPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Here you would typically send the form data to your backend
    console.log("Form submitted:", { name, email, subject, message });
    toast({
      title: "Message Sent",
      description: "We've received your message and will get back to you soon.",
    });
    // Reset form fields
    setName("");
    setEmail("");
    setSubject("");
    setMessage("");
  };

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <main className="flex-1">
        <section className="w-full py-12 md:py-24 lg:py-32">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center space-y-4 text-center">
              <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl">
                Contact Us
              </h1>
              <p className="mx-auto max-w-[700px] text-muted-foreground md:text-xl">
                We&apos;re here to help. Send us a message and we&apos;ll get
                back to you as soon as possible.
              </p>
            </div>
            <div className="mx-auto max-w-[500px] mt-12">
              <Card>
                <CardHeader>
                  <CardTitle>Send a Message</CardTitle>
                  <CardDescription>
                    Fill out the form below to get in touch with us.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmit}>
                    <div className="grid w-full items-center gap-4">
                      <div className="flex flex-col space-y-1.5">
                        <Label htmlFor="name">Name</Label>
                        <Input
                          id="name"
                          placeholder="Your name"
                          value={name}
                          onChange={(e) => setName(e.target.value)}
                          required
                        />
                      </div>
                      <div className="flex flex-col space-y-1.5">
                        <Label htmlFor="email">Email</Label>
                        <Input
                          id="email"
                          placeholder="Your email"
                          type="email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          required
                        />
                      </div>
                      <div className="flex flex-col space-y-1.5">
                        <Label htmlFor="subject">Subject</Label>
                        <Select
                          value={subject}
                          onValueChange={setSubject}
                          required
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select a subject" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="general">
                              General Inquiry
                            </SelectItem>
                            <SelectItem value="support">
                              Technical Support
                            </SelectItem>
                            <SelectItem value="billing">
                              Billing Question
                            </SelectItem>
                            <SelectItem value="feedback">Feedback</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="flex flex-col space-y-1.5">
                        <Label htmlFor="message">Message</Label>
                        <Textarea
                          id="message"
                          placeholder="Your message"
                          value={message}
                          onChange={(e) => setMessage(e.target.value)}
                          required
                        />
                      </div>
                    </div>
                    <CardFooter className="flex justify-between mt-4 px-0">
                      <Button type="submit" className="w-full">
                        Send Message
                      </Button>
                    </CardFooter>
                  </form>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
