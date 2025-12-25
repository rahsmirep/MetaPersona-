import express from 'express';
import mysql from 'mysql2/promise';
import bcrypt from 'bcrypt';
import dotenv from 'dotenv';
import cors from 'cors';

dotenv.config();

const app = express();
app.use(express.json());
app.use(cors());

const db = await mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

app.post('/signup', async (req, res) => {
  const { username, email, password } = req.body;
  if (!username || !email || !password) {
    return res.status(400).json({ error: 'All fields are required.' });
  }
  try {
    const [existing] = await db.query('SELECT id FROM users WHERE username = ? OR email = ?', [username, email]);
    if (existing.length > 0) {
      return res.status(409).json({ error: 'Username or email already exists.' });
    }
    const password_hash = await bcrypt.hash(password, 10);
    await db.query('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)', [username, email, password_hash]);
    res.status(201).json({ message: 'User created successfully.' });
  } catch (err) {
    res.status(500).json({ error: 'Server error.' });
  }
});

app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'All fields are required.' });
  }
  try {
    const [users] = await db.query('SELECT * FROM users WHERE username = ?', [username]);
    if (users.length === 0) {
      return res.status(401).json({ error: 'Invalid credentials.' });
    }
    const user = users[0];
    const match = await bcrypt.compare(password, user.password_hash);
    if (!match) {
      return res.status(401).json({ error: 'Invalid credentials.' });
    }
    res.json({ message: 'Login successful.' });
  } catch (err) {
    res.status(500).json({ error: 'Server error.' });
  }
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
