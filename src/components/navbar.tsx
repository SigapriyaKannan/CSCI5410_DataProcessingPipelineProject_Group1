"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useContext } from "react";
import { UserContext } from "@/app/contexts/user-context";
import { Avatar, AvatarFallback } from "./ui/avatar";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "./ui/tooltip";

export default function Navbar() {
  const { user, logout } = useContext(UserContext);

  const navItems = [
    { name: "Home", href: "/" },
    { name: "DP1", href: "/dataprocessing/1" },
    { name: "DP2", href: "/dataprocessing/2" },
    { name: "DP3", href: "/dataprocessing/3" },
  ];

  if (user && user.role === "Agent") {
    navItems.push({ name: "Dashboard", href: "/admin/dashboard" });
  }

  return (
    <nav className="bg-background border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex-shrink-0">
            <Link href="/" className="text-2xl font-bold text-primary">
              QuickDataPro
            </Link>
          </div>
          <div className="flex items-center space-x-4">
            {navItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className="text-sm font-medium text-muted-foreground hover:text-primary"
              >
                {item.name}
              </Link>
            ))}
            {user ? (
              // User is logged in
              <>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger>
                      <Avatar className="hover:outline hover:outline-2 hover:outline-black hover:cursor-pointer">
                        <AvatarFallback>
                          {user.email[0].toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                    </TooltipTrigger>
                    <TooltipContent className="bg-primary">
                      <p>{`logged in as ${user.email}`}</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                <Button variant="destructive" onClick={logout}>
                  Logout
                </Button>
              </>
            ) : (
              // User is not logged in
              <>
                <Button variant="ghost" asChild>
                  <Link href="/login">Log in</Link>
                </Button>
                <Button asChild>
                  <Link href="/signup">Sign up</Link>
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
