// Vercel API handler for BABS10
export default function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // Handle different routes
  if (req.method === 'GET') {
    if (req.url === '/api/' || req.url === '/api') {
      res.status(200).json({ message: 'Hello World from BABS10 API - Vercel Edition' });
    } else if (req.url === '/api/health') {
      res.status(200).json({
        status: 'healthy',
        mongo_available: false,
        timestamp: new Date().toISOString(),
        platform: 'Vercel',
        customers: 6,
        users: 1
      });
    } else if (req.url === '/api/users') {
      res.status(200).json([{
        id: "68ddce3f-2a19-4ad8-b838-06198af3447e",
        email: "lynaboateng1@gmail.com",
        created_at: "2025-08-24T12:45:39.312433",
        updated_at: "2025-08-24T12:45:39.312438"
      }]);
    } else if (req.url.startsWith('/api/customers')) {
      const customers = [
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
      ];
      res.status(200).json(customers);
    } else {
      res.status(404).json({ error: 'Not found' });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}