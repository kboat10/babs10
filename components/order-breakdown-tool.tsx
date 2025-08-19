"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { CalendarIcon } from "lucide-react"
import { Package, Users, CreditCard, AlertTriangle, FileText, Trash2, Plus, Save, Edit } from "lucide-react"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Calendar } from "@/components/ui/calendar"
import { format } from "date-fns"

interface Item {
  desc: string
  qty: string
  color: string
  size: string
  price: string
}

interface Order {
  id: string
  orderRef: string
  orderDate: string
  items: Item[]
  comments: string
  savedAt: string
}

interface Customer {
  id: string
  name: string
  moneyGiven: number
  totalSpent: number
  orders: Order[]
  lastUpdated: string
}

interface OrderBreakdownToolProps {
  currentUser?: string
}

export default function OrderBreakdownTool({ currentUser }: OrderBreakdownToolProps) {
  const [activeTab, setActiveTab] = useState("orders")
  const [editingOrderId, setEditingOrderId] = useState<string | null>(null)
  const [selectedCustomerId, setSelectedCustomerId] = useState("")
  const [newCustomerName, setNewCustomerName] = useState("")
  const [orderRef, setOrderRef] = useState("")
  const [orderDate, setOrderDate] = useState<Date | undefined>(new Date())
  const [items, setItems] = useState([{ desc: "", qty: "1", color: "", size: "", price: "0.00" }])
  const [comments, setComments] = useState("")
  const [isGenerateModalOpen, setIsGenerateModalOpen] = useState(false)
  const [selectedCustomer, setSelectedCustomer] = useState("current")
  const [customers, setCustomers] = useState<{ [key: string]: Customer }>({})
  const [breakdownFormat, setBreakdownFormat] = useState("simple")
  const [showBreakdown, setShowBreakdown] = useState(false)
  const [breakdownOutput, setBreakdownOutput] = useState("")
  const [selectedCustomerForTopUp, setSelectedCustomerForTopUp] = useState<string | null>(null)
  const [topUpAmount, setTopUpAmount] = useState("")
  const [selectedCustomerForRefund, setSelectedCustomerForRefund] = useState<string | null>(null)
  const [refundAmount, setRefundAmount] = useState("")
  const [refundSource, setRefundSource] = useState("")
  const [selectedCustomerForView, setSelectedCustomerForView] = useState<string | null>(null)
  const [selectedOrdersForDeletion, setSelectedOrdersForDeletion] = useState<{ [customerId: string]: string[] }>({})
  const [showDeleteOptions, setShowDeleteOptions] = useState<{ [customerId: string]: boolean }>({})
  const [newCustomerBalance, setNewCustomerBalance] = useState("")
  const [selectedOrders, setSelectedOrders] = useState<{ [customerId: string]: string[] }>({})

  const getStorageKey = () => {
    return currentUser ? `orderBreakdownData_${currentUser}` : "orderBreakdownData"
  }

  useEffect(() => {
    const savedData = localStorage.getItem(getStorageKey())
    if (savedData) {
      try {
        const parsedData = JSON.parse(savedData)
        console.log("[v0] Loading saved data for user:", currentUser, parsedData)
        setCustomers(parsedData.customers || {})
      } catch (error) {
        console.error("Error loading saved data:", error)
      }
    } else {
      console.log("[v0] No saved data found for user:", currentUser, "- starting fresh")
      setCustomers({})
    }
  }, [currentUser])

  useEffect(() => {
    const dataToSave = {
      customers,
      lastUpdated: new Date().toISOString(),
    }
    console.log("[v0] Saving data to localStorage for user:", currentUser, dataToSave)
    localStorage.setItem(getStorageKey(), JSON.stringify(dataToSave))
  }, [customers, currentUser])

  const checkInsufficientBalance = () => {
    const currentCustomer = getCurrentCustomer()
    if (!currentCustomer) return false

    const orderTotal = calculateTotal()
    const customerBalance = calculateCustomerBalance(currentCustomer)

    return orderTotal > customerBalance && orderTotal > 0
  }

  const getCurrentCustomer = () => {
    return selectedCustomerId ? customers[selectedCustomerId] : null
  }

  const calculateTotal = () => {
    return items.reduce((acc, item) => acc + Number.parseFloat(item.price), 0)
  }

  const calculateCustomerBalance = (customer: Customer) => {
    return customer.moneyGiven - customer.totalSpent
  }

  const updateItem = (index: number, key: string, value: string) => {
    const newItems = [...items]
    newItems[index][key] = value
    setItems(newItems)
  }

  const removeItem = (index: number) => {
    if (items.length === 1) return
    const newItems = [...items]
    newItems.splice(index, 1)
    setItems(newItems)
  }

  const addItem = () => {
    setItems([...items, { desc: "", qty: "1", color: "", size: "", price: "0.00" }])
  }

  const handleTopUp = () => {
    if (!selectedCustomerForTopUp || !topUpAmount) {
      alert("Please select a customer and enter an amount.")
      return
    }

    const amount = Number.parseFloat(topUpAmount)
    if (isNaN(amount) || amount <= 0) {
      alert("Please enter a valid amount.")
      return
    }

    setCustomers((prevCustomers) => {
      const existingCustomer = prevCustomers[selectedCustomerForTopUp]
      const updatedCustomer = {
        ...existingCustomer,
        moneyGiven: existingCustomer.moneyGiven + amount,
        lastUpdated: new Date().toLocaleString(),
      }
      console.log("[v0] Top-up processed:", {
        customerId: selectedCustomerForTopUp,
        amount,
        newBalance: updatedCustomer.moneyGiven,
      })
      return {
        ...prevCustomers,
        [selectedCustomerForTopUp]: updatedCustomer,
      }
    })

    setSelectedCustomerForTopUp(null)
    setTopUpAmount("")
    alert(`Successfully added $${amount.toFixed(2)} to the customer's account.`)
  }

  const handleRefund = () => {
    if (!selectedCustomerForRefund || !refundAmount || !refundSource) {
      alert("Please select a customer, enter an amount, and provide a source/reason.")
      return
    }

    const amount = Number.parseFloat(refundAmount)
    if (isNaN(amount) || amount <= 0) {
      alert("Please enter a valid refund amount.")
      return
    }

    setCustomers((prevCustomers) => {
      const existingCustomer = prevCustomers[selectedCustomerForRefund]
      const updatedCustomer = {
        ...existingCustomer,
        moneyGiven: existingCustomer.moneyGiven + amount,
        lastUpdated: new Date().toLocaleString(),
      }
      console.log("[v0] Refund processed:", {
        customerId: selectedCustomerForRefund,
        amount,
        source: refundSource,
        newBalance: updatedCustomer.moneyGiven,
      })
      return {
        ...prevCustomers,
        [selectedCustomerForRefund]: updatedCustomer,
      }
    })

    setSelectedCustomerForRefund(null)
    setRefundAmount("")
    setRefundSource("")
    alert(`Successfully refunded $${amount.toFixed(2)} to the customer's account.`)
  }

  const deleteSelectedOrders = (customerId: string) => {
    const customer = customers[customerId]
    if (!customer) return

    const orderIds = selectedOrders[customerId] || []

    if (orderIds.length === 0) {
      alert("Please select orders to delete")
      return
    }

    const orderText = orderIds.length === 1 ? "order" : "orders"
    if (confirm(`Are you sure you want to delete ${orderIds.length} ${orderText} for ${customer.name}?`)) {
      setCustomers((prevCustomers) => {
        const updatedCustomer = {
          ...customer,
          orders: customer.orders.filter((order) => !orderIds.includes(order.id)),
          totalSpent: customer.orders
            .filter((order) => !orderIds.includes(order.id))
            .reduce((sum, order) => sum + order.items.reduce((itemSum, item) => itemSum + Number(item.price), 0), 0),
        }

        return {
          ...prevCustomers,
          [customerId]: updatedCustomer,
        }
      })

      setSelectedOrders((prev) => ({ ...prev, [customerId]: [] }))
      setShowDeleteOptions((prev) => ({ ...prev, [customerId]: false }))
    }
  }

  const deleteAllOrders = (customerId: string) => {
    const customer = customers[customerId]
    if (!customer) return

    if (
      confirm(
        `Are you sure you want to delete ALL orders for ${customer.name}? This will keep the customer profile but remove all order history.`,
      )
    ) {
      setCustomers((prevCustomers) => ({
        ...prevCustomers,
        [customerId]: {
          ...customer,
          orders: [],
          totalSpent: 0,
        },
      }))

      setSelectedOrders((prev) => ({ ...prev, [customerId]: [] }))
      setShowDeleteOptions((prev) => ({ ...prev, [customerId]: false }))
    }
  }

  const toggleOrderSelection = (customerId: string, orderId: string) => {
    setSelectedOrdersForDeletion((prev) => {
      const currentSelections = prev[customerId] || []
      const isSelected = currentSelections.includes(orderId)

      return {
        ...prev,
        [customerId]: isSelected ? currentSelections.filter((id) => id !== orderId) : [...currentSelections, orderId],
      }
    })
  }

  const selectAllOrders = (customerId: string) => {
    const customer = customers[customerId]
    if (!customer) return

    setSelectedOrdersForDeletion((prev) => ({
      ...prev,
      [customerId]: customer.orders.map((order) => order.id),
    }))
  }

  const clearOrderSelection = (customerId: string) => {
    setSelectedOrdersForDeletion((prev) => ({
      ...prev,
      [customerId]: [],
    }))
  }

  const deleteCustomer = (customerId: string) => {
    if (confirm("Are you sure you want to delete this customer and all their data?")) {
      setCustomers((prevCustomers) => {
        const newCustomers = { ...prevCustomers }
        delete newCustomers[customerId]
        return newCustomers
      })
    }
  }

  const handleGenerateBreakdown = () => {
    let output = ""

    if (selectedCustomer === "current") {
      const orderTotal = calculateTotal()
      const customerBalance = getCurrentCustomer() ? calculateCustomerBalance(getCurrentCustomer()!) : 0

      if (breakdownFormat === "simple") {
        output = `Order Total: $${orderTotal.toFixed(2)}\n`
        if (getCurrentCustomer()) {
          output += `Customer Balance: $${customerBalance.toFixed(2)}\n`
          output += `Customer: ${getCurrentCustomer()!.name}\n`
        } else {
          output += "No customer selected.\n"
        }
        output += `Items:\n${items.map((item) => `${item.desc} - $${item.price}`).join("\n")}`
      } else {
        output = `ORDER BREAKDOWN\n\n`
        output += `Customer: ${getCurrentCustomer() ? getCurrentCustomer()!.name : "N/A"}\n`
        output += `Order Ref: ${orderRef || "N/A"}\n`
        output += `Order Date: ${orderDate}\n\n`
        output += `Items:\n`
        items.forEach((item, index) => {
          output += `${index + 1}. ${item.desc} - Qty: ${item.qty}, Color: ${item.color}, Size: ${item.size}, Price: $${item.price}\n`
        })
        output += `\nTotal: $${orderTotal.toFixed(2)}`
      }
    } else {
      const customer = customers[selectedCustomer]
      if (!customer) {
        alert("Customer not found.")
        return
      }

      if (!customer.orders || customer.orders.length === 0) {
        alert("No orders found for this customer.")
        return
      }

      const allItems = customer.orders.flatMap((order) => order.items)
      const totalAmount = allItems.reduce((acc, item) => acc + Number.parseFloat(item.price), 0)
      const customerBalance = calculateCustomerBalance(customer)

      if (breakdownFormat === "simple") {
        output = `Customer: ${customer.name}\n`
        output += `Total Orders: ${customer.orders.length}\n`
        output += `Customer Balance: $${customerBalance.toFixed(2)}\n`
        output += `Total Spent: $${totalAmount.toFixed(2)}\n\n`
        output += `All Items:\n${allItems.map((item) => `${item.desc} - $${item.price}`).join("\n")}`
      } else {
        output = `CUSTOMER ORDER BREAKDOWN\n\n`
        output += `Customer: ${customer.name}\n`
        output += `Total Orders: ${customer.orders.length}\n`
        output += `Customer Balance: $${customerBalance.toFixed(2)}\n`
        output += `Total Spent: $${totalAmount.toFixed(2)}\n\n`

        // Show all orders with their details
        customer.orders.forEach((order, orderIndex) => {
          output += `--- ORDER ${orderIndex + 1} ---\n`
          output += `Order Ref: ${order.orderRef || "N/A"}\n`
          output += `Order Date: ${order.orderDate}\n`
          output += `Items:\n`
          order.items.forEach((item, itemIndex) => {
            output += `  ${itemIndex + 1}. ${item.desc} - Qty: ${item.qty}, Color: ${item.color}, Size: ${item.size}, Price: $${item.price}\n`
          })
          const orderTotal = order.items.reduce((acc, item) => acc + Number.parseFloat(item.price), 0)
          output += `Order Total: $${orderTotal.toFixed(2)}\n\n`
        })

        output += `GRAND TOTAL: $${totalAmount.toFixed(2)}`
      }
    }

    setBreakdownOutput(output)
    setShowBreakdown(true)
    setIsGenerateModalOpen(false)
  }

  const createNewCustomer = () => {
    if (!newCustomerName.trim()) {
      alert("Please enter a customer name.")
      return
    }

    const customerId = crypto.randomUUID()
    const newCustomer: Customer = {
      id: customerId,
      name: newCustomerName.trim(),
      orders: [],
      moneyGiven: 0,
      totalSpent: 0,
      lastUpdated: new Date().toLocaleString(),
    }

    setCustomers((prev) => {
      const updated = { ...prev, [customerId]: newCustomer }
      console.log("[v0] Created new customer:", newCustomer)
      return updated
    })

    setNewCustomerName("")
    alert(`Customer "${newCustomer.name}" created successfully!`)
  }

  const saveProgress = () => {
    if (!selectedCustomerId) {
      alert("Please select a customer first.")
      return
    }

    const customer = customers[selectedCustomerId]
    if (!customer) {
      alert("Selected customer not found.")
      return
    }

    const orderId = editingOrderId || crypto.randomUUID()
    const orderTotal = calculateTotal()

    const orderData: Order = {
      id: orderId,
      orderRef,
      orderDate: orderDate ? format(orderDate, "yyyy-MM-dd") : "",
      items,
      comments,
      savedAt: new Date().toLocaleString(),
    }

    setCustomers((prevCustomers) => {
      const existingCustomer = prevCustomers[selectedCustomerId]
      const updatedOrders = editingOrderId
        ? existingCustomer.orders.map((order) => (order.id === editingOrderId ? orderData : order))
        : [...existingCustomer.orders, orderData]

      const newTotalSpent = editingOrderId ? existingCustomer.totalSpent : existingCustomer.totalSpent + orderTotal

      const updatedCustomer = {
        ...existingCustomer,
        orders: updatedOrders,
        totalSpent: newTotalSpent,
        lastUpdated: new Date().toLocaleString(),
      }

      console.log("[v0] Order saved:", {
        customerId: selectedCustomerId,
        orderId,
        orderTotal,
        isEdit: !!editingOrderId,
        newTotalSpent,
        orderCount: updatedOrders.length,
      })

      return {
        ...prevCustomers,
        [selectedCustomerId]: updatedCustomer,
      }
    })

    setOrderRef("")
    setOrderDate(new Date())
    setItems([{ desc: "", qty: "1", color: "", size: "", price: "0.00" }])
    setComments("")
    setEditingOrderId(null)

    alert("Order saved successfully!")
  }

  const clearForm = () => {
    setSelectedCustomerId("")
    setOrderRef("")
    setOrderDate(new Date())
    setItems([{ desc: "", qty: "1", color: "", size: "", price: "0.00" }])
    setComments("")
    setShowBreakdown(false)
    setBreakdownOutput("")
  }

  const loadCustomerOrder = (customerId: string) => {
    const customer = customers[customerId]
    setSelectedCustomerId(customer.id)
    if (!customer.orders || customer.orders.length === 0) {
      console.log("[v0] No orders found for customer:", customer.name)
      return
    }
    const latestOrder = customer.orders[customer.orders.length - 1]
    if (!latestOrder) {
      console.log("[v0] Latest order is undefined for customer:", customer.name)
      return
    }
    setOrderRef(latestOrder.orderRef || "")
    setOrderDate(latestOrder.orderDate ? new Date(latestOrder.orderDate) : undefined)
    setItems(latestOrder.items)
    setComments(latestOrder.comments || "")
  }

  const loadOrderForEditing = (customerId: string, orderId: string) => {
    const customer = customers[customerId]
    setSelectedCustomerId(customer.id)
    if (!customer.orders || customer.orders.length === 0) {
      console.log("[v0] No orders found for customer:", customer.name)
      return
    }
    const orderToEdit = customer.orders.find((order) => order.id === orderId)
    if (orderToEdit) {
      setEditingOrderId(orderId)
      setOrderRef(orderToEdit.orderRef || "")
      setOrderDate(orderToEdit.orderDate ? new Date(orderToEdit.orderDate) : undefined)
      setItems(orderToEdit.items)
      setComments(orderToEdit.comments || "")
      setActiveTab("orders")
    } else {
      console.log("[v0] Order not found:", orderId, "for customer:", customer.name)
    }
  }

  const sortedCustomers = Object.values(customers).sort((a, b) => a.name.localeCompare(b.name))

  const formatBalance = (balance: number) => {
    if (balance >= 0) {
      return `$${balance.toFixed(2)}`
    } else {
      return `Owes $${Math.abs(balance).toFixed(2)}`
    }
  }

  const cancelEdit = () => {
    setEditingOrderId(null)
    clearForm()
  }

  const createCustomer = () => {
    if (!newCustomerName.trim()) {
      alert("Please enter a customer name.")
      return
    }

    const initialBalance = Number.parseFloat(newCustomerBalance) || 0
    if (isNaN(initialBalance)) {
      alert("Please enter a valid initial balance.")
      return
    }

    const customerId = crypto.randomUUID()
    const newCustomer: Customer = {
      id: customerId,
      name: newCustomerName.trim(),
      orders: [],
      moneyGiven: initialBalance,
      totalSpent: 0,
      lastUpdated: new Date().toLocaleString(),
    }

    setCustomers((prev) => {
      const updated = { ...prev, [customerId]: newCustomer }
      console.log("[v0] Created new customer:", newCustomer)
      return updated
    })

    setNewCustomerName("")
    setNewCustomerBalance("")
    alert(`Customer "${newCustomer.name}" created successfully!`)
  }

  return (
    <div className="w-full max-w-7xl mx-auto p-3 sm:p-5">
      <Card className="overflow-hidden">
        <CardHeader className="bg-green-500 text-white text-center p-4 sm:p-6">
          <CardTitle className="flex items-center justify-center gap-2 text-lg sm:text-xl">
            <Package className="h-5 w-5 sm:h-6 sm:w-6" />
            Order Breakdown Tool
            {editingOrderId && <span className="text-xs sm:text-sm bg-orange-500 px-2 py-1 rounded">EDITING</span>}
          </CardTitle>
        </CardHeader>

        <CardContent className="p-3 sm:p-6">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2 h-auto">
              <TabsTrigger value="orders" className="flex items-center gap-1 sm:gap-2 p-2 sm:p-3 text-xs sm:text-sm">
                <Package className="h-3 w-3 sm:h-4 sm:w-4" />
                <span className="hidden xs:inline">Order Entry</span>
                <span className="xs:hidden">Orders</span>
              </TabsTrigger>
              <TabsTrigger value="customers" className="flex items-center gap-1 sm:gap-2 p-2 sm:p-3 text-xs sm:text-sm">
                <Users className="h-3 w-3 sm:h-4 sm:w-4" />
                <span className="hidden xs:inline">Customer Management</span>
                <span className="xs:hidden">Customers</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="orders" className="space-y-4 sm:space-y-6 mt-4 sm:mt-6">
              {/* Customer Selection Section */}
              <div className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="customerSelect" className="text-sm sm:text-base">
                      Customer
                    </Label>
                    <Select value={selectedCustomerId} onValueChange={setSelectedCustomerId}>
                      <SelectTrigger className="h-10 sm:h-11">
                        <SelectValue placeholder="Select a customer" />
                      </SelectTrigger>
                      <SelectContent>
                        {sortedCustomers.map((customer) => (
                          <SelectItem key={customer.id} value={customer.id}>
                            {customer.name} (Balance: {formatBalance(calculateCustomerBalance(customer))})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {sortedCustomers.length === 0 && (
                      <p className="text-sm text-muted-foreground">
                        No customers available. Create customers in the Customer Management tab.
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="orderRef" className="text-sm sm:text-base">
                      Order Ref
                    </Label>
                    <Input
                      id="orderRef"
                      placeholder="Optional order reference"
                      value={orderRef}
                      onChange={(e) => setOrderRef(e.target.value)}
                      className="h-10 sm:h-11"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label className="text-sm sm:text-base">Order Date</Label>
                    <div className="relative">
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button
                            variant="outline"
                            className="w-full justify-start text-left font-normal h-10 sm:h-11 bg-transparent"
                          >
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            {orderDate ? format(orderDate, "PPP") : <span>Pick a date</span>}
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0" align="start">
                          <Calendar mode="single" selected={orderDate} onSelect={setOrderDate} initialFocus />
                        </PopoverContent>
                      </Popover>
                    </div>
                  </div>
                </div>

                {getCurrentCustomer() && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 sm:p-4">
                    <h4 className="font-semibold text-blue-800 flex items-center gap-2 text-sm sm:text-base mb-3">
                      <CreditCard className="h-4 w-4" />
                      {getCurrentCustomer()!.name}'s Account Balance
                    </h4>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 text-xs sm:text-sm">
                      <div className="flex justify-between sm:block">
                        <span className="text-blue-600">Money Given:</span>
                        <div className="font-semibold">${getCurrentCustomer()!.moneyGiven.toFixed(2)}</div>
                      </div>
                      <div className="flex justify-between sm:block">
                        <span className="text-blue-600">Total Spent:</span>
                        <div className="font-semibold">${getCurrentCustomer()!.totalSpent.toFixed(2)}</div>
                      </div>
                      <div className="flex justify-between sm:block">
                        <span className="text-blue-600">Balance:</span>
                        <div
                          className={`font-bold ${calculateCustomerBalance(getCurrentCustomer()!) >= 0 ? "text-green-600" : "text-red-600"}`}
                        >
                          {formatBalance(calculateCustomerBalance(getCurrentCustomer()!))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {checkInsufficientBalance() && (
                  <Alert className="border-orange-200 bg-orange-50">
                    <AlertTriangle className="h-4 w-4 text-orange-600" />
                    <AlertDescription className="text-orange-800">
                      <strong>Amount Owed:</strong> This customer will owe $
                      {(calculateTotal() - calculateCustomerBalance(getCurrentCustomer()!)).toFixed(2)} after this
                      order. Current balance: {formatBalance(calculateCustomerBalance(getCurrentCustomer()!))} | Order
                      total: ${calculateTotal().toFixed(2)}
                    </AlertDescription>
                  </Alert>
                )}
              </div>

              <div className="space-y-4 sm:space-y-6">
                <Card>
                  <CardHeader className="pb-3 sm:pb-4">
                    <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
                      <Package className="h-4 w-4 sm:h-5 sm:w-5" />
                      Items Ordered
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="hidden lg:grid grid-cols-12 gap-2 text-sm font-medium text-muted-foreground px-2">
                      <div className="col-span-4">Item Description</div>
                      <div className="col-span-1">Qty*</div>
                      <div className="col-span-2">Color</div>
                      <div className="col-span-2">Size/Notes</div>
                      <div className="col-span-2">Total Price ($)</div>
                      <div className="col-span-1"></div>
                    </div>
                    <div className="text-xs text-muted-foreground px-2">
                      *Quantity is for reference only - enter the total price including taxes/fees
                    </div>

                    {items.map((item, index) => (
                      <div key={index} className="border rounded-lg p-3 sm:p-4">
                        <div className="lg:hidden space-y-3">
                          <div className="space-y-2">
                            <Label className="text-xs text-muted-foreground">Item Description</Label>
                            <Input
                              placeholder="Item description"
                              value={item.desc}
                              onChange={(e) => updateItem(index, "desc", e.target.value)}
                              className="h-9"
                            />
                          </div>
                          <div className="grid grid-cols-2 gap-3">
                            <div className="space-y-2">
                              <Label className="text-xs text-muted-foreground">Qty</Label>
                              <Input
                                type="number"
                                placeholder="1"
                                value={item.qty}
                                onChange={(e) => updateItem(index, "qty", e.target.value)}
                                className="h-9"
                              />
                            </div>
                            <div className="space-y-2">
                              <Label className="text-xs text-muted-foreground">Total Price ($)</Label>
                              <Input
                                type="number"
                                step="0.01"
                                placeholder="0.00"
                                value={item.price}
                                onChange={(e) => updateItem(index, "price", e.target.value)}
                                className="h-9"
                              />
                            </div>
                          </div>
                          <div className="grid grid-cols-2 gap-3">
                            <div className="space-y-2">
                              <Label className="text-xs text-muted-foreground">Color</Label>
                              <Input
                                placeholder="Color"
                                value={item.color}
                                onChange={(e) => updateItem(index, "color", e.target.value)}
                                className="h-9"
                              />
                            </div>
                            <div className="space-y-2">
                              <Label className="text-xs text-muted-foreground">Size/Notes</Label>
                              <Input
                                placeholder="Size/Notes"
                                value={item.size}
                                onChange={(e) => updateItem(index, "size", e.target.value)}
                                className="h-9"
                              />
                            </div>
                          </div>
                          <div className="flex justify-end">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => removeItem(index)}
                              className="text-red-600 hover:text-red-700 h-8"
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>

                        <div className="hidden lg:grid grid-cols-12 gap-2 items-center">
                          <div className="col-span-4">
                            <Input
                              placeholder="Item description"
                              value={item.desc}
                              onChange={(e) => updateItem(index, "desc", e.target.value)}
                            />
                          </div>
                          <div className="col-span-1">
                            <Input
                              type="number"
                              placeholder="1"
                              value={item.qty}
                              onChange={(e) => updateItem(index, "qty", e.target.value)}
                            />
                          </div>
                          <div className="col-span-2">
                            <Input
                              placeholder="Color"
                              value={item.color}
                              onChange={(e) => updateItem(index, "color", e.target.value)}
                            />
                          </div>
                          <div className="col-span-2">
                            <Input
                              placeholder="Size/Notes"
                              value={item.size}
                              onChange={(e) => updateItem(index, "size", e.target.value)}
                            />
                          </div>
                          <div className="col-span-2">
                            <Input
                              type="number"
                              step="0.01"
                              placeholder="0.00"
                              value={item.price}
                              onChange={(e) => updateItem(index, "price", e.target.value)}
                            />
                          </div>
                          <div className="col-span-1">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => removeItem(index)}
                              className="text-red-600 hover:text-red-700"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}

                    <Button
                      variant="outline"
                      onClick={addItem}
                      className="w-full h-10 sm:h-11 border-dashed bg-transparent"
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Add Item
                    </Button>
                  </CardContent>

                  <div className="border-t pt-6 space-y-4">
                    <div className="flex justify-end">
                      <div className="text-right">
                        <div className="text-2xl sm:text-3xl font-bold text-green-600">
                          TOTAL: ${calculateTotal().toFixed(2)}
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="comments" className="text-sm sm:text-base flex items-center gap-2">
                        <FileText className="h-4 w-4" />
                        Comments
                      </Label>
                      <Textarea
                        id="comments"
                        placeholder="Add any notes or comments about this order..."
                        value={comments}
                        onChange={(e) => setComments(e.target.value)}
                        className="min-h-[80px] resize-none"
                      />
                    </div>

                    <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 pt-4 sm:pt-6">
                      <Button
                        onClick={saveProgress}
                        disabled={!selectedCustomerId || items.length === 0}
                        className="flex-1 h-11 sm:h-12 text-sm sm:text-base bg-orange-500 hover:bg-orange-600"
                      >
                        <Save className="h-4 w-4 mr-2" />
                        Save Progress
                      </Button>
                      <Button
                        onClick={() => setIsGenerateModalOpen(true)}
                        disabled={!selectedCustomerId}
                        className="flex-1 h-11 sm:h-12 text-sm sm:text-base bg-blue-500 hover:bg-blue-600"
                      >
                        <FileText className="h-4 w-4 mr-2" />
                        Generate Breakdown
                      </Button>
                      <Button
                        variant="outline"
                        onClick={clearForm}
                        className="flex-1 h-11 sm:h-12 text-sm sm:text-base bg-transparent"
                      >
                        Clear All
                      </Button>
                    </div>
                  </div>
                </Card>

                {Object.keys(customers).length > 0 && (
                  <Card>
                    <CardHeader className="pb-3 sm:pb-4">
                      <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
                        <FileText className="h-4 w-4 sm:h-5 sm:w-5" />
                        Saved Orders in Progress
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {sortedCustomers.map((customer) => (
                        <div key={customer.id} className="border rounded-lg p-4">
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                            <div>
                              <h3 className="text-lg font-semibold">{customer.name}</h3>
                              <p className="text-sm text-muted-foreground">
                                {customer.orders.length} order{customer.orders.length !== 1 ? "s" : ""} • Total spent: $
                                {customer.totalSpent.toFixed(2)} • Last updated: {customer.lastUpdated}
                              </p>
                            </div>
                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => loadCustomerOrder(customer.id)}
                                className="bg-green-500 hover:bg-green-600 text-white border-green-500"
                              >
                                Load Latest
                              </Button>
                              <Button
                                variant="destructive"
                                size="sm"
                                onClick={() =>
                                  setShowDeleteOptions((prev) => ({ ...prev, [customer.id]: !prev[customer.id] }))
                                }
                              >
                                Delete
                              </Button>
                            </div>
                          </div>

                          {showDeleteOptions[customer.id] && (
                            <div className="bg-gray-50 p-4 rounded-lg space-y-3">
                              <div className="flex flex-wrap gap-2">
                                {customer.orders.map((order) => (
                                  <label key={order.id} className="flex items-center space-x-2 text-sm">
                                    <input
                                      type="checkbox"
                                      checked={selectedOrders[customer.id]?.includes(order.id) || false}
                                      onChange={(e) => {
                                        const isChecked = e.target.checked
                                        setSelectedOrders((prev) => {
                                          const customerSelections = prev[customer.id] || []
                                          if (isChecked) {
                                            return { ...prev, [customer.id]: [...customerSelections, order.id] }
                                          } else {
                                            return {
                                              ...prev,
                                              [customer.id]: customerSelections.filter((id) => id !== order.id),
                                            }
                                          }
                                        })
                                      }}
                                      className="rounded"
                                    />
                                    <span>
                                      Order #{order.orderRef || order.id.slice(-4)} - {order.date} -{" "}
                                      {order.items.length} items
                                    </span>
                                  </label>
                                ))}
                              </div>
                              <div className="flex gap-2 pt-2">
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => {
                                    const allOrderIds = customer.orders.map((order) => order.id)
                                    setSelectedOrders((prev) => ({ ...prev, [customer.id]: allOrderIds }))
                                  }}
                                >
                                  Select All
                                </Button>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => setSelectedOrders((prev) => ({ ...prev, [customer.id]: [] }))}
                                >
                                  Clear Selection
                                </Button>
                                <Button
                                  size="sm"
                                  variant="destructive"
                                  onClick={() => deleteSelectedOrders(customer.id)}
                                  disabled={!selectedOrders[customer.id]?.length}
                                >
                                  Delete Selected ({selectedOrders[customer.id]?.length || 0})
                                </Button>
                                <Button size="sm" variant="destructive" onClick={() => deleteAllOrders(customer.id)}>
                                  Delete All Orders
                                </Button>
                              </div>
                            </div>
                          )}

                          <div className="space-y-2 mt-4">
                            {customer.orders.map((order) => (
                              <div
                                key={order.id}
                                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                              >
                                <span className="text-sm">
                                  Order #{order.orderRef || order.id.slice(-4)} - {order.date} - {order.items.length}{" "}
                                  items
                                </span>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => loadOrderForEditing(customer.id, order.id)}
                                >
                                  <Edit className="h-4 w-4" />
                                  Edit
                                </Button>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                )}
              </div>
            </TabsContent>

            <TabsContent value="customers" className="space-y-4 sm:space-y-6 mt-4 sm:mt-6">
              <h2 className="text-xl sm:text-2xl font-bold flex items-center gap-2">
                <Users className="h-5 w-5 sm:h-6 sm:w-6" />
                Customer Management
              </h2>

              <Card>
                <CardHeader className="pb-3 sm:pb-4">
                  <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
                    <Plus className="h-4 w-4 sm:h-5 sm:w-5" />
                    Add New Customer
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label className="text-sm sm:text-base">Customer Name:</Label>
                    <Input
                      placeholder="Enter customer name"
                      value={newCustomerName}
                      onChange={(e) => setNewCustomerName(e.target.value)}
                      className="h-10 sm:h-11"
                    />
                  </div>
                  <Button
                    onClick={createNewCustomer}
                    disabled={!newCustomerName.trim()}
                    className="w-full sm:w-auto h-10 sm:h-11 bg-green-500 hover:bg-green-600"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Create Customer
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3 sm:pb-4">
                  <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
                    <CreditCard className="h-4 w-4 sm:h-5 sm:w-5" />
                    View Customer Balance
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label className="text-sm sm:text-base">Select Customer:</Label>
                    <Select value={selectedCustomerForView || ""} onValueChange={setSelectedCustomerForView}>
                      <SelectTrigger className="h-10 sm:h-11">
                        <SelectValue placeholder="Choose a customer" />
                      </SelectTrigger>
                      <SelectContent>
                        {sortedCustomers.map((customer) => (
                          <SelectItem key={customer.id} value={customer.id}>
                            {customer.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  {selectedCustomerForView && customers[selectedCustomerForView] && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h4 className="font-semibold text-blue-800 mb-3">
                        {customers[selectedCustomerForView].name}'s Account
                      </h4>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
                        <div>
                          <span className="text-blue-600">Money Given:</span>
                          <div className="font-semibold">
                            ${customers[selectedCustomerForView].moneyGiven.toFixed(2)}
                          </div>
                        </div>
                        <div>
                          <span className="text-blue-600">Total Spent:</span>
                          <div className="font-semibold">
                            ${customers[selectedCustomerForView].totalSpent.toFixed(2)}
                          </div>
                        </div>
                        <div>
                          <span className="text-blue-600">Balance:</span>
                          <div
                            className={`font-bold ${calculateCustomerBalance(customers[selectedCustomerForView]) >= 0 ? "text-green-600" : "text-red-600"}`}
                          >
                            {formatBalance(calculateCustomerBalance(customers[selectedCustomerForView]))}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3 sm:pb-4">
                  <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
                    <CreditCard className="h-4 w-4 sm:h-5 sm:w-5" />
                    Customer Top-Up
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                    <div className="space-y-2">
                      <Label className="text-sm sm:text-base">Select Customer:</Label>
                      <Select value={selectedCustomerForTopUp || ""} onValueChange={setSelectedCustomerForTopUp}>
                        <SelectTrigger className="h-10 sm:h-11">
                          <SelectValue placeholder="Choose a customer" />
                        </SelectTrigger>
                        <SelectContent>
                          {sortedCustomers.map((customer) => (
                            <SelectItem key={customer.id} value={customer.id}>
                              {customer.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label className="text-sm sm:text-base">Amount to Add:</Label>
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="0.00"
                        value={topUpAmount}
                        onChange={(e) => setTopUpAmount(e.target.value)}
                        className="h-10 sm:h-11"
                      />
                    </div>
                  </div>
                  <Button
                    onClick={handleTopUp}
                    disabled={!selectedCustomerForTopUp || !topUpAmount}
                    className="w-full sm:w-auto h-10 sm:h-11 bg-green-500 hover:bg-green-600"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Money to Account
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3 sm:pb-4">
                  <CardTitle className="flex items-center gap-2 text-base sm:text-lg">Process Refund</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                    <div className="space-y-2">
                      <Label className="text-sm sm:text-base">Select Customer:</Label>
                      <Select value={selectedCustomerForRefund || ""} onValueChange={setSelectedCustomerForRefund}>
                        <SelectTrigger className="h-10 sm:h-11">
                          <SelectValue placeholder="Choose a customer" />
                        </SelectTrigger>
                        <SelectContent>
                          {sortedCustomers.map((customer) => (
                            <SelectItem key={customer.id} value={customer.id}>
                              {customer.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label className="text-sm sm:text-base">Refund Amount:</Label>
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="0.00"
                        value={refundAmount}
                        onChange={(e) => setRefundAmount(e.target.value)}
                        className="h-10 sm:h-11"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-sm sm:text-base">Refund Source/Reason:</Label>
                    <Textarea
                      placeholder="e.g., Order #123 - Blue dress return, Damaged item refund, etc."
                      value={refundSource}
                      onChange={(e) => setRefundSource(e.target.value)}
                      className="min-h-[60px] resize-none"
                    />
                  </div>
                  <p className="text-sm text-muted-foreground">
                    This amount will be added to the customer's account balance
                  </p>
                  <Button
                    onClick={handleRefund}
                    disabled={!selectedCustomerForRefund || !refundAmount || !refundSource}
                    className="w-full sm:w-auto h-10 sm:h-11 bg-red-400 hover:bg-red-500"
                  >
                    Process Refund
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {isGenerateModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Generate Breakdown</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Select Customer:</Label>
                <Select value={selectedCustomer} onValueChange={setSelectedCustomer}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="current">Current Order</SelectItem>
                    {sortedCustomers.map((customer) => (
                      <SelectItem key={customer.id} value={customer.id}>
                        {customer.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Format:</Label>
                <Select value={breakdownFormat} onValueChange={setBreakdownFormat}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="simple">Simple</SelectItem>
                    <SelectItem value="detailed">Detailed</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex gap-2">
                <Button onClick={handleGenerateBreakdown} className="flex-1">
                  Generate
                </Button>
                <Button variant="outline" onClick={() => setIsGenerateModalOpen(false)} className="flex-1">
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {showBreakdown && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-2xl max-h-[80vh] overflow-hidden">
            <CardHeader>
              <CardTitle>Order Breakdown</CardTitle>
            </CardHeader>
            <CardContent className="overflow-y-auto">
              <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded border">{breakdownOutput}</pre>
              <div className="flex gap-2 mt-4">
                <Button onClick={() => navigator.clipboard.writeText(breakdownOutput)} className="flex-1">
                  Copy to Clipboard
                </Button>
                <Button variant="outline" onClick={() => setShowBreakdown(false)} className="flex-1">
                  Close
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

export { OrderBreakdownTool }
