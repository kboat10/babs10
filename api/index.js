// Vercel Serverless API for BABS10
// This replaces the Render backend with a more reliable solution

const express = require('express');
const cors = require('cors');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// In-memory storage (persists between requests in Vercel)
let users = [];
let customers = [];

// Initialize with your data
if (users.length === 0) {
  // Add your user
  users.push({
    id: "68ddce3f-2a19-4ad8-b838-06198af3447e",
    email: "lynaboateng1@gmail.com",
    created_at: "2025-08-24T12:45:39.312433",
    updated_at: "2025-08-24T12:45:39.312438"
  });

  // Add your customers
  customers.push(
    {
      id: "7213e9d9-e6f7-4e83-b0cb-6cb621cc8aa5",
      name: "Grandma",
      money_given: 0.0,
      total_spent: 0.0,
      orders: [],
      created_at: "2025-08-24T12:50:34.792413",
      updated_at: "2025-08-24T12:50:34.792417"
    },
    {
      id: "18945c54-e3f0-4f17-9484-e6e961317a45",
      name: "Kwasi",
      money_given: 700.0,
      total_spent: 750.38,
      orders: [
        {
          id: "e518c755-0716-4e93-9d59-03fbd36146db",
          orderRef: "",
          orderDate: "2025-08-21",
          items: [
            {
              desc: "Amazon 1",
              qty: "1",
              color: "",
              size: "",
              price: "60.94"
            },
            {
              desc: "Amazon 2",
              qty: "1",
              color: "",
              size: "",
              price: "50.44"
            }
          ],
          comments: "",
          savedAt: "8/21/2025, 2:23:11 AM"
        }
      ],
      created_at: "2025-08-24T12:50:34.792413",
      updated_at: "2025-08-24T12:50:34.792417"
    },
    {
      id: "d0a3f0e6-d2f1-4d65-8ac8-1ad69371f683",
      name: "Theresa/Kwaku",
      money_given: 4500.0,
      total_spent: 2589.3999999999996,
      orders: [],
      created_at: "2025-08-24T12:50:34.792413",
      updated_at: "2025-08-24T12:50:34.792417"
    },
    {
      id: "7e318b3e-28ec-4bd6-82c6-f7092fd11411",
      name: "Sheila",
      money_given: 0.0,
      total_spent: 0.0,
      orders: [],
      created_at: "2025-08-24T12:50:34.792413",
      updated_at: "2025-08-24T12:50:34.792417"
    },
    {
      id: "c013f845-fe54-4656-ba00-791e99d3b4c5",
      name: "Titi School",
      money_given: 0.0,
      total_spent: 0.0,
      orders: [],
      created_at: "2025-08-24T12:50:34.792413",
      updated_at: "2025-08-24T12:50:34.792417"
    },
    {
      id: "5321926e-1720-4204-955b-ef9687010a00",
      name: "Uncle K",
      money_given: 0.0,
      total_spent: 0.0,
      orders: [],
      created_at: "2025-08-24T12:50:34.792413",
      updated_at: "2025-08-24T12:50:34.792417"
    }
  );
}

// Routes
app.get('/', (req, res) => {
  res.json({ message: 'Hello World from BABS10 API - Vercel Edition' });
});

app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    mongo_available: false,
    timestamp: new Date().toISOString(),
    platform: 'Vercel',
    customers: customers.length,
    users: users.length
  });
});

// Users endpoints
app.get('/users', (req, res) => {
  res.json(users);
});

app.post('/users', (req, res) => {
  const { email, pin } = req.body;
  const newUser = {
    id: Date.now().toString(),
    email,
    pin,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };
  users.push(newUser);
  res.status(201).json(newUser);
});

// Customers endpoints
app.get('/customers', (req, res) => {
  const { user_id } = req.query;
  if (user_id) {
    const userCustomers = customers.filter(c => c.user_id === user_id);
    res.json(userCustomers);
  } else {
    res.json(customers);
  }
});

app.post('/customers', (req, res) => {
  const { name, money_given, total_spent, orders } = req.body;
  const { user_id } = req.query;
  
  const newCustomer = {
    id: Date.now().toString(),
    name,
    money_given: money_given || 0.0,
    total_spent: total_spent || 0.0,
    orders: orders || [],
    user_id,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };
  
  customers.push(newCustomer);
  res.status(201).json(newCustomer);
});

// Export for Vercel
module.exports = app;
