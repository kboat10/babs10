"use client"

import React from "react"

import type { ReactNode } from "react"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { UserPlus, LogIn, Package } from "lucide-react"

interface User {
  email: string
  pin: string
  createdAt: string
}

interface AuthWrapperProps {
  children: ReactNode
}

export default function AuthWrapper({ children }: AuthWrapperProps) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [currentUser, setCurrentUser] = useState<string | null>(null)
  const [authTab, setAuthTab] = useState("signin")

  // Sign In Form
  const [signInEmail, setSignInEmail] = useState("")
  const [signInPin, setSignInPin] = useState("")

  // Sign Up Form
  const [signUpEmail, setSignUpEmail] = useState("")
  const [signUpPin, setSignUpPin] = useState("")
  const [confirmPin, setConfirmPin] = useState("")

  useEffect(() => {
    const savedAuth = localStorage.getItem("orderToolAuth")
    if (savedAuth) {
      try {
        const authData = JSON.parse(savedAuth)
        if (authData.isAuthenticated && authData.currentUser) {
          setIsAuthenticated(true)
          setCurrentUser(authData.currentUser)
        }
      } catch (error) {
        console.error("Error loading auth data:", error)
      }
    }
  }, [])

  const saveAuthState = (authenticated: boolean, user: string | null) => {
    const authData = {
      isAuthenticated: authenticated,
      currentUser: user,
      lastLogin: new Date().toISOString(),
    }
    localStorage.setItem("orderToolAuth", JSON.stringify(authData))
  }

  const handleSignUp = () => {
    if (!signUpEmail.trim() || !signUpPin.trim()) {
      alert("Please enter both email and PIN.")
      return
    }

    if (signUpPin !== confirmPin) {
      alert("PINs do not match.")
      return
    }

    if (signUpPin.length < 4) {
      alert("PIN must be at least 4 characters long.")
      return
    }

    // Check if user already exists
    const existingUsers = JSON.parse(localStorage.getItem("orderToolUsers") || "{}")
    if (existingUsers[signUpEmail]) {
      alert("User with this email already exists.")
      return
    }

    // Create new user
    const newUser: User = {
      email: signUpEmail.trim(),
      pin: signUpPin,
      createdAt: new Date().toISOString(),
    }

    const updatedUsers = {
      ...existingUsers,
      [signUpEmail]: newUser,
    }

    localStorage.setItem("orderToolUsers", JSON.stringify(updatedUsers))

    // Auto sign in after successful sign up
    setIsAuthenticated(true)
    setCurrentUser(signUpEmail)
    saveAuthState(true, signUpEmail)

    alert("Account created successfully!")
  }

  const handleSignIn = () => {
    if (!signInEmail.trim() || !signInPin.trim()) {
      alert("Please enter both email and PIN.")
      return
    }

    const existingUsers = JSON.parse(localStorage.getItem("orderToolUsers") || "{}")
    const user = existingUsers[signInEmail]

    if (!user) {
      alert("User not found. Please sign up first.")
      return
    }

    if (user.pin !== signInPin) {
      alert("Incorrect PIN.")
      return
    }

    setIsAuthenticated(true)
    setCurrentUser(signInEmail)
    saveAuthState(true, signInEmail)
  }

  const handleSignOut = () => {
    setIsAuthenticated(false)
    setCurrentUser(null)
    saveAuthState(false, null)
    setSignInEmail("")
    setSignInPin("")
  }

  if (isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <div className="bg-white/80 backdrop-blur-lg border-b border-blue-200/50 px-4 py-4 flex justify-between items-center shadow-xl shadow-blue-200/20">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Package className="h-7 w-7 text-blue-600 transform rotate-12 drop-shadow-lg" />
              <div className="absolute -inset-1 bg-blue-500/20 rounded-full blur-lg"></div>
            </div>
            <span className="font-bold text-xl bg-gradient-to-r from-blue-700 to-indigo-600 bg-clip-text text-transparent">
              Order Breakdown Tool
            </span>
          </div>
          <div className="flex items-center gap-4">
            <div className="px-4 py-2 bg-gradient-to-r from-blue-500/10 to-indigo-500/10 rounded-xl backdrop-blur-sm border border-blue-200/30">
              <span className="text-sm font-medium text-blue-700">Welcome, {currentUser}</span>
            </div>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleSignOut}
              className="border-blue-200 text-blue-700 hover:bg-blue-50 hover:border-blue-300 transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              Sign Out
            </Button>
          </div>
        </div>
        <div className="relative">
          {React.cloneElement(children as React.ReactElement, { currentUser })}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute top-10 left-10 w-72 h-72 bg-blue-400/20 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-10 right-10 w-96 h-96 bg-indigo-400/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-purple-400/10 rounded-full blur-3xl animate-pulse delay-500"></div>
      
      <Card className="w-full max-w-md relative backdrop-blur-xl bg-white/10 border border-white/20 shadow-2xl shadow-blue-900/50 transform hover:scale-105 transition-all duration-300">
        <CardHeader className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-600 rounded-t-lg"></div>
          <div className="absolute inset-0 bg-white/10 backdrop-blur-sm rounded-t-lg"></div>
          <CardTitle className="relative flex items-center justify-center gap-3 text-white text-center py-2">
            <div className="relative">
              <Package className="h-8 w-8 transform rotate-12 drop-shadow-lg" />
              <div className="absolute -inset-1 bg-white/30 rounded-full blur-lg"></div>
            </div>
            <span className="font-bold text-xl drop-shadow-lg">Order Breakdown Tool</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6 relative">
          <Tabs value={authTab} onValueChange={setAuthTab}>
            <TabsList className="grid w-full grid-cols-2 bg-blue-100/50 backdrop-blur-sm border border-blue-200/30">
              <TabsTrigger 
                value="signin" 
                className="flex items-center gap-2 data-[state=active]:bg-white data-[state=active]:text-blue-700 data-[state=active]:shadow-lg text-blue-600 font-medium"
              >
                <LogIn className="h-4 w-4" />
                Sign In
              </TabsTrigger>
              <TabsTrigger 
                value="signup" 
                className="flex items-center gap-2 data-[state=active]:bg-white data-[state=active]:text-blue-700 data-[state=active]:shadow-lg text-blue-600 font-medium"
              >
                <UserPlus className="h-4 w-4" />
                Sign Up
              </TabsTrigger>
            </TabsList>

            <TabsContent value="signin" className="space-y-6 mt-6">
              <div className="space-y-3">
                <Label htmlFor="signInEmail" className="text-blue-800 font-semibold">Email</Label>
                <Input
                  id="signInEmail"
                  type="email"
                  placeholder="Enter your email"
                  value={signInEmail}
                  onChange={(e) => setSignInEmail(e.target.value)}
                  className="bg-white/70 backdrop-blur-sm border-blue-200/50 focus:border-blue-400 focus:ring-blue-300/50 shadow-lg hover:shadow-xl transition-all duration-200"
                />
              </div>
              <div className="space-y-3">
                <Label htmlFor="signInPin" className="text-blue-800 font-semibold">PIN</Label>
                <Input
                  id="signInPin"
                  type="password"
                  placeholder="Enter your PIN"
                  value={signInPin}
                  onChange={(e) => setSignInPin(e.target.value)}
                  className="bg-white/70 backdrop-blur-sm border-blue-200/50 focus:border-blue-400 focus:ring-blue-300/50 shadow-lg hover:shadow-xl transition-all duration-200"
                />
              </div>
              <Button 
                onClick={handleSignIn} 
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold py-3 transform hover:scale-105 transition-all duration-200 shadow-xl hover:shadow-2xl"
              >
                <LogIn className="h-5 w-5 mr-2" />
                Sign In
              </Button>
            </TabsContent>

            <TabsContent value="signup" className="space-y-6 mt-6">
              <div className="space-y-3">
                <Label htmlFor="signUpEmail" className="text-blue-800 font-semibold">Email</Label>
                <Input
                  id="signUpEmail"
                  type="email"
                  placeholder="Enter your email"
                  value={signUpEmail}
                  onChange={(e) => setSignUpEmail(e.target.value)}
                  className="bg-white/70 backdrop-blur-sm border-blue-200/50 focus:border-blue-400 focus:ring-blue-300/50 shadow-lg hover:shadow-xl transition-all duration-200"
                />
              </div>
              <div className="space-y-3">
                <Label htmlFor="signUpPin" className="text-blue-800 font-semibold">Create PIN</Label>
                <Input
                  id="signUpPin"
                  type="password"
                  placeholder="Create a PIN (min 4 characters)"
                  value={signUpPin}
                  onChange={(e) => setSignUpPin(e.target.value)}
                  className="bg-white/70 backdrop-blur-sm border-blue-200/50 focus:border-blue-400 focus:ring-blue-300/50 shadow-lg hover:shadow-xl transition-all duration-200"
                />
              </div>
              <div className="space-y-3">
                <Label htmlFor="confirmPin" className="text-blue-800 font-semibold">Confirm PIN</Label>
                <Input
                  id="confirmPin"
                  type="password"
                  placeholder="Confirm your PIN"
                  value={confirmPin}
                  onChange={(e) => setConfirmPin(e.target.value)}
                  className="bg-white/70 backdrop-blur-sm border-blue-200/50 focus:border-blue-400 focus:ring-blue-300/50 shadow-lg hover:shadow-xl transition-all duration-200"
                />
              </div>
              <Button 
                onClick={handleSignUp} 
                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold py-3 transform hover:scale-105 transition-all duration-200 shadow-xl hover:shadow-2xl"
              >
                <UserPlus className="h-5 w-5 mr-2" />
                Create Account
              </Button>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}