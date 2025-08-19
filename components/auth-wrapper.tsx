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
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white border-b px-4 py-3 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Package className="h-5 w-5 text-green-500" />
            <span className="font-semibold">Order Breakdown Tool</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">Welcome, {currentUser}</span>
            <Button variant="outline" size="sm" onClick={handleSignOut}>
              Sign Out
            </Button>
          </div>
        </div>
        {React.cloneElement(children as React.ReactElement, { currentUser })}
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="bg-green-500 text-white text-center">
          <CardTitle className="flex items-center justify-center gap-2">
            <Package className="h-6 w-6" />
            Order Breakdown Tool
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <Tabs value={authTab} onValueChange={setAuthTab}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="signin" className="flex items-center gap-2">
                <LogIn className="h-4 w-4" />
                Sign In
              </TabsTrigger>
              <TabsTrigger value="signup" className="flex items-center gap-2">
                <UserPlus className="h-4 w-4" />
                Sign Up
              </TabsTrigger>
            </TabsList>

            <TabsContent value="signin" className="space-y-4 mt-6">
              <div className="space-y-2">
                <Label htmlFor="signInEmail">Email</Label>
                <Input
                  id="signInEmail"
                  type="email"
                  placeholder="Enter your email"
                  value={signInEmail}
                  onChange={(e) => setSignInEmail(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="signInPin">PIN</Label>
                <Input
                  id="signInPin"
                  type="password"
                  placeholder="Enter your PIN"
                  value={signInPin}
                  onChange={(e) => setSignInPin(e.target.value)}
                />
              </div>
              <Button onClick={handleSignIn} className="w-full">
                <LogIn className="h-4 w-4 mr-2" />
                Sign In
              </Button>
            </TabsContent>

            <TabsContent value="signup" className="space-y-4 mt-6">
              <div className="space-y-2">
                <Label htmlFor="signUpEmail">Email</Label>
                <Input
                  id="signUpEmail"
                  type="email"
                  placeholder="Enter your email"
                  value={signUpEmail}
                  onChange={(e) => setSignUpEmail(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="signUpPin">Create PIN</Label>
                <Input
                  id="signUpPin"
                  type="password"
                  placeholder="Create a PIN (min 4 characters)"
                  value={signUpPin}
                  onChange={(e) => setSignUpPin(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirmPin">Confirm PIN</Label>
                <Input
                  id="confirmPin"
                  type="password"
                  placeholder="Confirm your PIN"
                  value={confirmPin}
                  onChange={(e) => setConfirmPin(e.target.value)}
                />
              </div>
              <Button onClick={handleSignUp} className="w-full">
                <UserPlus className="h-4 w-4 mr-2" />
                Create Account
              </Button>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}
