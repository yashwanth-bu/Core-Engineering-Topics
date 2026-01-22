PostgreSQL Driver + Express.

---

## 0️⃣ Prerequisites (quick check)

Before starting, you should know:

* Basic **JavaScript**
* Very basic **Node.js** (what `npm` is, how to run a file)

If you’re already using Express → you’re good to go.

---

## 1️⃣ What you’re actually learning (big picture)

```
Client (browser / frontend)
        ↓ HTTP requests
Express.js (Node backend)
        ↓ SQL queries
PostgreSQL (database)
```

Express:

* Handles routes (`/users`, `/login`, etc.)
* Talks to PostgreSQL
* Sends responses back to the client

---

## 2️⃣ Install PostgreSQL (local setup)

### 🔹 Install PostgreSQL

* Download from: [https://www.postgresql.org/download/](https://www.postgresql.org/download/)
* During installation:

  * Remember **username** (usually `postgres`)
  * Remember **password**
  * Default port: `5432`

### 🔹 Install pgAdmin (GUI tool)

pgAdmin lets you **see tables visually** instead of only typing SQL.

---

## 3️⃣ Learn PostgreSQL basics (VERY IMPORTANT FIRST)

Don’t touch Express yet. Learn **pure SQL** first.

### 🔹 Core SQL concepts (must-know)

Learn these in order:

1. **Databases**

```sql
CREATE DATABASE mydb;
```

2. **Tables**

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name TEXT,
  email TEXT UNIQUE,
  age INT
);
```

3. **Insert data**

```sql
INSERT INTO users (name, email, age)
VALUES ('John', 'john@email.com', 25);
```

4. **Read data**

```sql
SELECT * FROM users;
SELECT name, age FROM users WHERE age > 20;
```

5. **Update data**

```sql
UPDATE users SET age = 26 WHERE id = 1;
```

6. **Delete data**

```sql
DELETE FROM users WHERE id = 1;
```

👉 Spend **at least 2–3 days** practicing these.

📚 Beginner SQL resources:

* [https://sqlbolt.com](https://sqlbolt.com) (interactive & beginner-friendly)
* [https://www.postgresqltutorial.com](https://www.postgresqltutorial.com)

---

## 4️⃣ Create a basic Express project

```bash
mkdir express-postgres
cd express-postgres
npm init -y
npm install express pg
```

### 🔹 Basic Express server

```js
// index.js
const express = require("express");
const app = express();

app.use(express.json());

app.get("/", (req, res) => {
  res.send("Server running 🚀");
});

app.listen(3000, () => {
  console.log("Server running on port 3000");
});
```

Run:

```bash
node index.js
```

---

## 5️⃣ Connect Express to PostgreSQL

### 🔹 Create DB connection

```js
// db.js
const { Pool } = require("pg");

const pool = new Pool({
  user: "postgres",
  host: "localhost",
  database: "mydb",
  password: "your_password",
  port: 5432,
});

module.exports = pool;
```

---

## 6️⃣ First Express + PostgreSQL query

### 🔹 Get all users

```js
// index.js
const express = require("express");
const pool = require("./db");

const app = express();
app.use(express.json());

app.get("/users", async (req, res) => {
  try {
    const result = await pool.query("SELECT * FROM users");
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).send("Server error");
  }
});

app.listen(3000, () => console.log("Server running"));
```

Visit:

```
http://localhost:3000/users
```

🎉 You just connected Express to PostgreSQL!

---

## 7️⃣ Insert data from Express (POST request)

```js
app.post("/users", async (req, res) => {
  const { name, email, age } = req.body;

  try {
    const result = await pool.query(
      "INSERT INTO users (name, email, age) VALUES ($1, $2, $3) RETURNING *",
      [name, email, age]
    );

    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).send(err.message);
  }
});
```

### 🔹 Why `$1, $2, $3`?

✅ Prevents SQL injection
✅ Always use **parameterized queries**

---

## 8️⃣ CRUD pattern (very important)

Every backend follows this pattern:

| Action | HTTP   | SQL    |
| ------ | ------ | ------ |
| Create | POST   | INSERT |
| Read   | GET    | SELECT |
| Update | PUT    | UPDATE |
| Delete | DELETE | DELETE |

Once you understand this → backend dev becomes MUCH easier.

---

## 9️⃣ Folder structure (clean way)

```text
project/
 ├── db.js
 ├── index.js
 ├── routes/
 │    └── users.js
 └── controllers/
      └── usersController.js
```

---

PostgreSQL + Prisma + Express.

---

Perfect 👍
Here’s a **very beginner-friendly Prisma guide**, written assuming **no prior ORM experience** (but you already know some Python/SQL, which helps).

I’ll keep it **simple, step-by-step**, and explain *why* things work.

---

# 🌱 Prisma for Absolute Beginners (with Express + PostgreSQL)

## What is Prisma? (super simple)

Prisma is an **ORM** that lets you:

* Define tables as **models**
* Write **JavaScript instead of SQL**
* Automatically handle migrations

Think:

> **Prisma = SQLAlchemy (but simpler & more modern)**

---

## 1️⃣ Setup Project

```bash
mkdir prisma-demo
cd prisma-demo
npm init -y
npm install express prisma @prisma/client
npx prisma init
```

This creates:

```
prisma/
 └── schema.prisma
.env
```

---

## 2️⃣ Connect PostgreSQL

### `.env`

```env
DATABASE_URL="postgresql://postgres:YOUR_REAL_PASSWORD@localhost:5432/mydb"
```

📌 Same idea as SQLAlchemy connection string.

---

## 3️⃣ Prisma Schema (THIS IS IMPORTANT)

Open `prisma/schema.prisma`

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}
```

Now define a model 👇

---

## 4️⃣ Define Your First Model

```prisma
model User {
  id    Int    @id @default(autoincrement())
  name  String
  email String @unique
  age   Int
}
```

👉 This is your **table definition**
👉 Prisma will convert this into SQL

---

## 5️⃣ Create Table (Migration)

```bash
npx prisma migrate dev --name init
```

This:

* Creates tables
* Keeps migration history
* Similar to **Alembic**

---

## 6️⃣ Prisma Client (DB Access)

Create `prismaClient.js`

```js
const { PrismaClient } = require("@prisma/client")
const prisma = new PrismaClient()

module.exports = prisma
```

---

## 7️⃣ Use Prisma in Express

### `index.js`

```js
const express = require("express")
const prisma = require("./prismaClient")

const app = express()
app.use(express.json())
```

---

## 8️⃣ CRUD Operations (Core Learning)

### 🔹 CREATE (INSERT)

```js
app.post("/users", async (req, res) => {
  const { name, email, age } = req.body

  const user = await prisma.user.create({
    data: { name, email, age }
  })

  res.json(user)
})
```

---

### 🔹 READ (SELECT)

```js
app.get("/users", async (req, res) => {
  const users = await prisma.user.findMany()
  res.json(users)
})
```

---

### 🔹 READ ONE

```js
app.get("/users/:id", async (req, res) => {
  const user = await prisma.user.findUnique({
    where: { id: Number(req.params.id) }
  })

  res.json(user)
})
```

---

### 🔹 UPDATE

```js
app.put("/users/:id", async (req, res) => {
  const user = await prisma.user.update({
    where: { id: Number(req.params.id) },
    data: req.body
  })

  res.json(user)
})
```

---

### 🔹 DELETE

```js
app.delete("/users/:id", async (req, res) => {
  await prisma.user.delete({
    where: { id: Number(req.params.id) }
  })

  res.send("User deleted")
})
```

---

## 9️⃣ Filtering & Conditions (Very Important)

```js
const adults = await prisma.user.findMany({
  where: {
    age: { gt: 18 }
  }
})
```

### SQL Equivalent

```sql
SELECT * FROM users WHERE age > 18;
```

---

## 🔗 Relationships (Simple Example)

### One-to-Many (User → Posts)

```prisma
model User {
  id    Int    @id @default(autoincrement())
  name  String
  posts Post[]
}

model Post {
  id     Int
  title  String
  userId Int
  user   User @relation(fields: [userId], references: [id])

  @@id([id])
}
```

Fetch user with posts:

```js
const user = await prisma.user.findMany({
  include: { posts: true }
})
```

---

## 🧠 Prisma vs SQLAlchemy (Mental Map)

| SQLAlchemy      | Prisma         |
| --------------- | -------------- |
| Model class     | model          |
| session.add()   | create()       |
| session.query() | findMany()     |
| relationships   | relations      |
| alembic         | prisma migrate |

---

## ⚠️ Beginner Mistakes to Avoid

❌ Skipping SQL basics
❌ Writing raw SQL before learning Prisma
❌ Not using migrations
❌ Forgetting `await`

---


## ✅ Beginner-Friendly Fix (RECOMMENDED)

* You **created tables manually** (pgAdmin / SQL)
* Or reused an **existing database**
* Or ran Prisma before migrations existed

### 🔥 Option 1: Reset database (BEST for beginners)

Run:

```bash
npx prisma migrate reset
```

Then:

* Type `y` when asked
* Prisma will:

  * Drop all tables
  * Recreate them using your schema
  * Apply migrations correctly

✅ This is **100% safe in development**
❌ Never do this in production

---

## 🟢 After reset, run again:

```bash
npx prisma migrate dev --name init
```

You should now see:

```
Applying migration `init`
✔ Generated Prisma Client
```

🎉 Problem solved.

---

## ❗ If you want to KEEP existing tables (advanced)

For learning → **skip this**
But just for knowledge:

```bash
npx prisma db pull
npx prisma migrate dev
```

This tells Prisma:

> “Read the database first, then generate models.”

---

## 🧪 Quick sanity check

After success, run:

```bash
npx prisma studio
```

You should see your tables in a web UI 🎉

---

## 🛑 Important beginner rule (memorize this)

| Situation      | Command         |
| -------------- | --------------- |
| Learning / dev | `migrate reset` |
| New DB         | `migrate dev`   |
| Existing DB    | `db pull`       |
| View data      | `prisma studio` |

---

Let’s move to the **next important Prisma concepts**, with **clear explanations + real implementations**.

---

# 🚀 Next Prisma Concepts (Beginner → Intermediate)

We’ll cover **what you need in real projects**:

1️⃣ **Relations (deep understanding)**
2️⃣ **Pagination & Search**
3️⃣ **Validation & Error Handling**
4️⃣ **Transactions**
5️⃣ **Authentication-ready patterns**

---

## 1️⃣ Prisma Relations (MOST IMPORTANT)

### Example: User → Posts (One-to-Many)

#### `schema.prisma`

```prisma
model User {
  id    Int    @id @default(autoincrement())
  name  String
  email String @unique

  posts Post[]
}

model Post {
  id      Int    @id @default(autoincrement())
  title   String
  content String

  userId Int
  user   User @relation(fields: [userId], references: [id])
}
```

Run migration:

```bash
npx prisma migrate dev --name user_post
```

---

### Create User with Posts

```js
const user = await prisma.user.create({
  data: {
    name: "Alice",
    email: "alice@mail.com",
    posts: {
      create: [
        { title: "First post", content: "Hello" },
        { title: "Second post", content: "World" }
      ]
    }
  }
})
```

---

### Fetch User with Posts

```js
const users = await prisma.user.findMany({
  include: {
    posts: true
  }
})
```

📌 **Include = JOIN**

---

## 2️⃣ Pagination (Very Common in APIs)

### Limit + Offset

```js
app.get("/users", async (req, res) => {
  const page = Number(req.query.page) || 1
  const limit = 5

  const users = await prisma.user.findMany({
    skip: (page - 1) * limit,
    take: limit
  })

  res.json(users)
})
```

### SQL Equivalent

```sql
LIMIT 5 OFFSET 5;
```

---

## 3️⃣ Search & Filtering

### Search by name

```js
const users = await prisma.user.findMany({
  where: {
    name: {
      contains: "ali",
      mode: "insensitive"
    }
  }
})
```

### Multiple conditions

```js
const users = await prisma.user.findMany({
  where: {
    AND: [
      { age: { gt: 18 } },
      { email: { contains: "@gmail.com" } }
    ]
  }
})
```

---

## 4️⃣ Validation & Error Handling (IMPORTANT)

### Use try/catch

```js
app.post("/users", async (req, res) => {
  try {
    const user = await prisma.user.create({
      data: req.body
    })
    res.json(user)
  } catch (err) {
    if (err.code === "P2002") {
      return res.status(400).json({ error: "Email already exists" })
    }
    res.status(500).json({ error: "Server error" })
  }
})
```

### Common Prisma Errors

| Code  | Meaning           |
| ----- | ----------------- |
| P2002 | Unique constraint |
| P2025 | Record not found  |

---

## 5️⃣ Transactions (Atomic Operations)

> All succeed or all fail

### Example: Create User + Post

```js
await prisma.$transaction(async (tx) => {
  const user = await tx.user.create({
    data: { name: "Bob", email: "bob@mail.com" }
  })

  await tx.post.create({
    data: {
      title: "Hello",
      content: "Post content",
      userId: user.id
    }
  })
})
```

---

## 6️⃣ Soft Deletes (Real-World Pattern)

### Schema

```prisma
model User {
  id        Int      @id @default(autoincrement())
  name      String
  deletedAt DateTime?
}
```

### Query only active users

```js
const users = await prisma.user.findMany({
  where: { deletedAt: null }
})
```

---

## 7️⃣ Prisma Best Practices (VERY IMPORTANT)

### ✔️ Reuse Prisma Client

```js
global.prisma = global.prisma || new PrismaClient()
```

### ✔️ Separate Layers

```
routes → controllers → services → prisma
```

### ✔️ Never expose raw errors to client

---

## 8️⃣ When to Use Raw SQL (Advanced)

```js
await prisma.$queryRaw`
  SELECT * FROM "User" WHERE age > 18
`
```

Use only when:

* Performance critical
* Complex joins

---

Relations are **the heart of Prisma + PostgreSQL**, and understanding them deeply will make everything else easy.

I’ll go **step by step**, from **simple → advanced**, with **mental models**, **schemas**, **queries**, and **real-world patterns**.

---

# 🔗 Prisma Relations — Deep & Practical Guide

## 1️⃣ Relation Fundamentals (Mental Model)

Think in **SQL terms first**, Prisma just *expresses* it.

| Relation Type | SQL         | Prisma              |
| ------------- | ----------- | ------------------- |
| One-to-One    | FK + UNIQUE | `@relation`         |
| One-to-Many   | FK          | `[]`                |
| Many-to-Many  | Join table  | implicit / explicit |

---

## 2️⃣ One-to-Many (Most Common)

### Example: User → Posts

### Schema

```prisma
model User {
  id    Int    @id @default(autoincrement())
  name  String

  posts Post[]
}

model Post {
  id      Int    @id @default(autoincrement())
  title   String

  userId  Int
  user    User   @relation(fields: [userId], references: [id])
}
```

### What Prisma creates

```sql
ALTER TABLE "Post"
ADD CONSTRAINT fk_user
FOREIGN KEY ("userId") REFERENCES "User"(id);
```

---

### Create Post for Existing User

```js
await prisma.post.create({
  data: {
    title: "Hello",
    user: {
      connect: { id: 1 }
    }
  }
})
```

---

### Fetch Users with Posts

```js
await prisma.user.findMany({
  include: { posts: true }
})
```

---

## 3️⃣ One-to-One Relation

### Example: User → Profile

### Schema

```prisma
model User {
  id      Int      @id @default(autoincrement())
  email   String   @unique
  profile Profile?
}

model Profile {
  id      Int    @id @default(autoincrement())
  bio     String

  userId  Int    @unique
  user    User   @relation(fields: [userId], references: [id])
}
```

📌 `@unique` enforces **one-to-one**

---

### Create User with Profile

```js
await prisma.user.create({
  data: {
    email: "a@mail.com",
    profile: {
      create: { bio: "Backend dev" }
    }
  }
})
```

---

### Optional vs Required Relations

```prisma
profile Profile?   // optional
profile Profile    // required
```

---

## 4️⃣ Many-to-Many (Implicit)

### Example: Users ↔ Roles

### Schema (Implicit)

```prisma
model User {
  id    Int    @id @default(autoincrement())
  name  String
  roles Role[]
}

model Role {
  id    Int    @id @default(autoincrement())
  name  String
  users User[]
}
```

Prisma auto-creates:

```sql
_UserToRole
```

---

### Assign Role

```js
await prisma.user.update({
  where: { id: 1 },
  data: {
    roles: {
      connect: { id: 2 }
    }
  }
})
```

---

## 5️⃣ Many-to-Many (Explicit — REAL WORLD)

Use when you need:

* Extra fields
* Timestamps
* Status

---

### Example: Enrollment

```prisma
model User {
  id          Int          @id @default(autoincrement())
  enrollments Enrollment[]
}

model Course {
  id          Int          @id @default(autoincrement())
  title       String
  enrollments Enrollment[]
}

model Enrollment {
  userId   Int
  courseId Int
  joinedAt DateTime @default(now())

  user     User   @relation(fields: [userId], references: [id])
  course   Course @relation(fields: [courseId], references: [id])

  @@id([userId, courseId])
}
```

---

### Query Courses for User

```js
await prisma.user.findUnique({
  where: { id: 1 },
  include: {
    enrollments: {
      include: { course: true }
    }
  }
})
```

---

## 6️⃣ Relation Filtering (VERY IMPORTANT)

### Users with at least one post

```js
where: {
  posts: { some: {} }
}
```

### Users with NO posts

```js
posts: { none: {} }
```

### All related records must match

```js
posts: {
  every: { published: true }
}
```

---

## 7️⃣ Nested Writes (Create / Update)

### Create user + posts

```js
await prisma.user.create({
  data: {
    name: "Sam",
    posts: {
      create: [
        { title: "A" },
        { title: "B" }
      ]
    }
  }
})
```

---

### Update relations

```js
await prisma.user.update({
  where: { id: 1 },
  data: {
    posts: {
      disconnect: { id: 2 },
      connect: { id: 3 }
    }
  }
})
```

---

## 8️⃣ Cascade Deletes & Referential Actions

### Schema

```prisma
model Post {
  userId Int
  user   User @relation(
    fields: [userId],
    references: [id],
    onDelete: Cascade
  )
}
```

Now deleting a user deletes posts automatically.

---

## 9️⃣ Self-Relations (Advanced)

### Example: Followers

```prisma
model User {
  id          Int    @id @default(autoincrement())
  name        String

  followers   User[] @relation("Follows")
  following   User[] @relation("Follows")
}
```

Prisma creates a self join table.

---

## 🔟 Polymorphic Relations (Pattern)

Prisma doesn’t support polymorphism directly.

### Workaround

```prisma
model Comment {
  id        Int
  targetId  Int
  target    String // "Post" | "Video"
}
```

Handled at app level.

---

## 🧠 Common Relation Mistakes

❌ Forgetting `@unique` in one-to-one
❌ Using implicit many-to-many when you need metadata
❌ Not indexing foreign keys
❌ Over-using `include`

---

## 🎯 Relation Design Rules (Memorize)

1️⃣ One-to-many is default
2️⃣ Use explicit join tables in real apps
3️⃣ Index foreign keys
4️⃣ Prefer nested writes
5️⃣ Control deletes with `onDelete`

---

Excellent — this is **advanced, real-world Prisma knowledge** 🔥
Relation performance tuning is where many apps **slow down or break** if done wrong.

I’ll explain **WHY things get slow**, then **HOW to fix them**, with **Prisma + PostgreSQL best practices**.

---

# ⚡ Prisma Relation Performance Tuning (Deep Guide)

## 1️⃣ The #1 Enemy: Over-fetching Relations

### ❌ Bad (fetches EVERYTHING)

```js
await prisma.user.findMany({
  include: {
    posts: {
      include: {
        comments: {
          include: { author: true }
        }
      }
    }
  }
})
```

This explodes into:

* Large JOINs
* Huge payload
* Slow serialization

---

### ✅ Fix: Fetch Only What You Need

```js
await prisma.user.findMany({
  select: {
    id: true,
    name: true,
    posts: {
      select: {
        id: true,
        title: true
      }
    }
  }
})
```

📌 **Rule**: `select > include`

---

## 2️⃣ Index Foreign Keys (CRITICAL)

### ❌ Without index

```prisma
model Post {
  userId Int
}
```

### ✅ With index

```prisma
model Post {
  userId Int
  @@index([userId])
}
```

📌 Every relation column should be indexed.

---

## 3️⃣ Avoid N+1 (Again, but Deeper)

### ❌ Hidden N+1

```js
const users = await prisma.user.findMany()

await Promise.all(users.map(user =>
  prisma.post.count({ where: { userId: user.id } })
))
```

### ✅ Use `_count`

```js
await prisma.user.findMany({
  select: {
    id: true,
    name: true,
    _count: {
      select: { posts: true }
    }
  }
})
```

---

## 4️⃣ Separate Queries (YES, Sometimes Faster)

JOINs aren’t always best.

### ❌ Heavy JOIN

```js
include: { posts: true }
```

### ✅ Two optimized queries

```js
const users = await prisma.user.findMany({
  select: { id: true, name: true }
})

const posts = await prisma.post.findMany({
  where: { userId: { in: users.map(u => u.id) } }
})
```

📌 Especially useful for large relations.

---

## 5️⃣ Limit Related Records

### ❌ Load all posts

```js
include: { posts: true }
```

### ✅ Load latest 3

```js
include: {
  posts: {
    take: 3,
    orderBy: { createdAt: "desc" }
  }
}
```

---

## 6️⃣ Cursor Pagination on Relations

### Example: Paginated comments

```js
await prisma.post.findUnique({
  where: { id: postId },
  include: {
    comments: {
      take: 10,
      cursor: lastCommentId ? { id: lastCommentId } : undefined,
      skip: lastCommentId ? 1 : 0
    }
  }
})
```

---

## 7️⃣ Use `_count` Instead of Fetching

### ❌ Bad

```js
posts: true
```

### ✅ Good

```js
_count: {
  select: { posts: true }
}
```

---

## 8️⃣ Precompute with Denormalization

### Example: Post count stored on User

```prisma
model User {
  postCount Int @default(0)
}
```

Update inside transaction:

```js
await prisma.$transaction([
  prisma.post.create({ data }),
  prisma.user.update({
    where: { id: userId },
    data: { postCount: { increment: 1 } }
  })
])
```

📌 Massive speed gains for feeds.

---

## 9️⃣ Use Raw SQL for Heavy Relation Queries

### Example: Feed query

```js
await prisma.$queryRaw`
  SELECT p.*
  FROM "Post" p
  JOIN "Follow" f ON f.following_id = p.user_id
  WHERE f.follower_id = ${userId}
  ORDER BY p.created_at DESC
  LIMIT 20
`
```

Prisma relations here would be slower.

---

## 🔍 10️⃣ Measure with EXPLAIN ANALYZE

```sql
EXPLAIN ANALYZE
SELECT * FROM "Post" WHERE "userId" = 1;
```

Check:

* Seq Scan ❌
* Index Scan ✅

---

## 1️⃣1️⃣ Control Referential Actions

### ❌ Cascade on huge tables

```prisma
onDelete: Cascade
```

### ✅ Soft delete or manual cleanup

```prisma
deletedAt DateTime?
```

---

## 1️⃣2️⃣ Connection & Query Strategy

| Scenario        | Best Strategy      |
| --------------- | ------------------ |
| Small relations | include            |
| Large relations | separate queries   |
| Analytics       | raw SQL            |
| Feeds           | denormalized + SQL |

---

## 🧠 Golden Rules (Memorize These)

1️⃣ Index all foreign keys
2️⃣ `select` > `include`
3️⃣ Limit related records
4️⃣ Avoid deep nesting
5️⃣ Measure before optimizing

---

# Authentication (JWT + Prisma + Express)

This is **mandatory knowledge** for real-world backend work.

---

## 1️⃣ Auth Flow (Understand First)

```
User registers → password hashed → saved in DB
User logs in → password verified → JWT issued
JWT sent in headers → protected routes
```

---

## 2️⃣ Update Prisma User Model

```prisma
model User {
  id        Int      @id @default(autoincrement())
  name      String
  email     String   @unique
  password  String
  role      String   @default("USER")
  createdAt DateTime @default(now())
}
```

Run:

```bash
npx prisma migrate dev --name auth
```

---

## 3️⃣ Install Required Packages

```bash
npm install bcryptjs jsonwebtoken dotenv
```

---

## 4️⃣ User Registration (Signup)

```js
const bcrypt = require("bcryptjs")
const jwt = require("jsonwebtoken")

app.post("/auth/register", async (req, res) => {
  const { name, email, password } = req.body

  const hashedPassword = await bcrypt.hash(password, 10)

  const user = await prisma.user.create({
    data: {
      name,
      email,
      password: hashedPassword
    }
  })

  res.json({ message: "User created" })
})
```

---

## 5️⃣ User Login

```js
app.post("/auth/login", async (req, res) => {
  const { email, password } = req.body

  const user = await prisma.user.findUnique({
    where: { email }
  })

  if (!user) {
    return res.status(401).json({ error: "Invalid credentials" })
  }

  const valid = await bcrypt.compare(password, user.password)

  if (!valid) {
    return res.status(401).json({ error: "Invalid credentials" })
  }

  const token = jwt.sign(
    { userId: user.id, role: user.role },
    process.env.JWT_SECRET,
    { expiresIn: "1h" }
  )

  res.json({ token })
})
```

---

## 6️⃣ Auth Middleware (Protect Routes)

```js
const authMiddleware = (req, res, next) => {
  const token = req.headers.authorization?.split(" ")[1]

  if (!token) {
    return res.status(401).json({ error: "No token" })
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET)
    req.user = decoded
    next()
  } catch {
    res.status(401).json({ error: "Invalid token" })
  }
}
```

---

## 7️⃣ Protected Route Example

```js
app.get("/profile", authMiddleware, async (req, res) => {
  const user = await prisma.user.findUnique({
    where: { id: req.user.userId },
    select: { id: true, name: true, email: true }
  })

  res.json(user)
})
```

---

# 🔑 STEP 4 — Role-Based Access Control (RBAC)

### Admin-only Middleware

```js
const adminOnly = (req, res, next) => {
  if (req.user.role !== "ADMIN") {
    return res.status(403).json({ error: "Forbidden" })
  }
  next()
}
```

### Admin Route

```js
app.delete("/users/:id", authMiddleware, adminOnly, async (req, res) => {
  await prisma.user.delete({
    where: { id: Number(req.params.id) }
  })

  res.send("User deleted")
})
```

---

# 📄 STEP 5 — Many-to-Many Relations

### Example: Users ↔ Roles

```prisma
model User {
  id    Int    @id @default(autoincrement())
  name  String
  roles Role[]
}

model Role {
  id    Int    @id @default(autoincrement())
  name  String
  users User[]
}
```

Prisma auto-creates a join table ✨

---

### Assign Role

```js
await prisma.user.update({
  where: { id: 1 },
  data: {
    roles: {
      connect: { id: 1 }
    }
  }
})
```

---

# ⚡ STEP 6 — Performance Basics

### Select only needed fields

```js
const users = await prisma.user.findMany({
  select: { id: true, name: true }
})
```

### Indexes

```prisma
model User {
  email String @unique
  @@index([email])
}
```

---

# 🚀 Advanced Prisma (Indexes, Raw SQL, Optimization)

## 1️⃣ Indexes (VERY IMPORTANT for performance)

### ❓ Why indexes matter

Without an index:

* PostgreSQL scans the whole table (**slow**)
  With index:
* Uses a lookup structure (**fast**)

---

### 🔹 When to add indexes

Add indexes on:

* `email`
* `userId` (foreign keys)
* columns used in `WHERE`, `ORDER BY`

---

### 🔹 Prisma Index Example

```prisma
model User {
  id    Int    @id @default(autoincrement())
  email String @unique
  name  String

  @@index([name])
}
```

### Composite index

```prisma
@@index([email, name])
```

📌 Prisma → generates PostgreSQL `CREATE INDEX`

---

## 2️⃣ Analyze Queries (Think like Postgres)

### Enable query logs

```js
const prisma = new PrismaClient({
  log: ["query", "error", "warn"]
})
```

You’ll **see raw SQL Prisma generates** 👀
This is extremely valuable.

---

## 3️⃣ Select Less Data (Big Optimization)

❌ Bad

```js
await prisma.user.findMany()
```

✅ Good

```js
await prisma.user.findMany({
  select: {
    id: true,
    name: true
  }
})
```

Less data = faster response.

---

## 4️⃣ N+1 Problem (COMMON & DANGEROUS)

### ❌ Bad pattern

```js
const users = await prisma.user.findMany()

for (const user of users) {
  await prisma.post.findMany({
    where: { userId: user.id }
  })
}
```

### ✅ Correct

```js
await prisma.user.findMany({
  include: {
    posts: true
  }
})
```

One query instead of many.

---

## 5️⃣ Raw SQL (When ORM Is Not Enough)

### Use cases

* Complex joins
* Aggregations
* Reports
* Performance-critical queries

---

### Safe Raw SQL (IMPORTANT)

```js
const users = await prisma.$queryRaw`
  SELECT * FROM "User" WHERE age > ${18}
`
```

✔ Prevents SQL injection
❌ NEVER use string concatenation

---

### Unsafe (DON’T DO THIS)

```js
prisma.$queryRaw(`SELECT * FROM users WHERE age > ${age}`)
```

---

## 6️⃣ Aggregations (Counts, Averages)

### Prisma Aggregates

```js
const stats = await prisma.user.aggregate({
  _count: { id: true },
  _avg: { age: true },
  _max: { age: true }
})
```

---

### Raw SQL (faster for big data)

```js
await prisma.$queryRaw`
  SELECT COUNT(*) FROM "User"
`
```

---

## 7️⃣ Transactions (Advanced Pattern)

### Use transactions for consistency

```js
await prisma.$transaction([
  prisma.user.create({ data: {...} }),
  prisma.post.create({ data: {...} })
])
```

### When to use

* Payments
* Inventory
* Multiple dependent writes

---

## 8️⃣ Connection Pooling (Production MUST)

### PostgreSQL connection pool

Prisma uses pooling internally, but:

* Use **PgBouncer** in production
* Avoid serverless connection explosion

---

## 9️⃣ Pagination Optimization (Cursor-based)

### Offset pagination (slow for big tables)

```js
skip: 1000
```

### Cursor pagination (fast)

```js
await prisma.user.findMany({
  take: 10,
  cursor: { id: lastId },
  skip: 1
})
```

---

## 🔥 10️⃣ Database-Level Optimization (Pro Tips)

### Partial index

```sql
CREATE INDEX active_users_idx ON "User"(email)
WHERE deletedAt IS NULL;
```

### Use `EXPLAIN ANALYZE`

```sql
EXPLAIN ANALYZE SELECT * FROM "User" WHERE email = 'x';
```

---

## 11️⃣ When NOT to Use Prisma

Use raw SQL or another tool when:

* Heavy analytics
* Complex reporting
* OLAP workloads

Prisma is **OLTP-focused** (CRUD apps).

---

## 🧠 Prisma Performance Checklist

✅ Index frequently queried columns
✅ Use `select` instead of `include`
✅ Avoid N+1 queries
✅ Use cursor pagination
✅ Use raw SQL when needed

---

# 🧠 Advanced Prisma Querying (Deep Dive)

## 1️⃣ Advanced `where` Conditions

### AND / OR / NOT

```js
const users = await prisma.user.findMany({
  where: {
    OR: [
      { age: { gt: 30 } },
      { email: { contains: "@company.com" } }
    ],
    NOT: {
      name: "Admin"
    }
  }
})
```

### SQL equivalent

```sql
WHERE (age > 30 OR email LIKE '%@company.com%')
AND name != 'Admin'
```

---

## 2️⃣ IN / NOT IN Queries

```js
await prisma.user.findMany({
  where: {
    id: { in: [1, 2, 3] }
  }
})
```

```js
await prisma.user.findMany({
  where: {
    email: { notIn: ["a@mail.com", "b@mail.com"] }
  }
})
```

---

## 3️⃣ Date & Time Queries

```js
await prisma.user.findMany({
  where: {
    createdAt: {
      gte: new Date("2025-01-01"),
      lt: new Date("2026-01-01")
    }
  }
})
```

📌 Prisma uses **JS Date → Postgres timestamp**

---

## 4️⃣ Relation Filters (Very Powerful)

### Users who have posts

```js
await prisma.user.findMany({
  where: {
    posts: {
      some: {}   // EXISTS
    }
  }
})
```

### Users with NO posts

```js
await prisma.user.findMany({
  where: {
    posts: {
      none: {}
    }
  }
})
```

### Users with posts matching condition

```js
await prisma.user.findMany({
  where: {
    posts: {
      some: {
        title: { contains: "Prisma" }
      }
    }
  }
})
```

---

## 5️⃣ Deep Relation Filtering

```js
await prisma.user.findMany({
  where: {
    posts: {
      some: {
        comments: {
          some: {
            content: { contains: "great" }
          }
        }
      }
    }
  }
})
```

📌 Prisma builds **nested EXISTS queries**

---

## 6️⃣ Sorting (ORDER BY)

### Single field

```js
await prisma.user.findMany({
  orderBy: {
    createdAt: "desc"
  }
})
```

### Multiple fields

```js
orderBy: [
  { role: "asc" },
  { createdAt: "desc" }
]
```

---

## 7️⃣ Distinct Queries

```js
await prisma.user.findMany({
  distinct: ["email"]
})
```

📌 Useful for deduplication

---

## 8️⃣ Group By (Analytics)

```js
await prisma.user.groupBy({
  by: ["role"],
  _count: {
    _all: true
  }
})
```

### SQL

```sql
GROUP BY role;
```

---

## 9️⃣ Having Clause

```js
await prisma.user.groupBy({
  by: ["role"],
  _count: { _all: true },
  having: {
    _count: {
      _all: { gt: 5 }
    }
  }
})
```

---

## 🔟 JSON Queries (PostgreSQL JSONB)

### Schema

```prisma
model User {
  id     Int  @id @default(autoincrement())
  prefs  Json
}
```

### Query JSON

```js
await prisma.user.findMany({
  where: {
    prefs: {
      path: ["theme"],
      equals: "dark"
    }
  }
})
```

---

## 1️⃣1️⃣ Full-Text Search (Postgres)

### Raw SQL (recommended)

```js
await prisma.$queryRaw`
  SELECT *
  FROM "Post"
  WHERE to_tsvector(title || ' ' || content)
  @@ plainto_tsquery('prisma')
`
```

📌 Prisma does not abstract full-text well → use SQL

---

## 1️⃣2️⃣ Window Functions (Advanced SQL)

```js
await prisma.$queryRaw`
  SELECT *,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC)
  FROM "Post"
`
```

---

## 1️⃣3️⃣ Subqueries

```js
await prisma.$queryRaw`
  SELECT *
  FROM "User"
  WHERE id IN (
    SELECT user_id FROM "Post" GROUP BY user_id HAVING COUNT(*) > 5
  )
`
```

---

## 1️⃣4️⃣ Bulk Operations

### Bulk insert

```js
await prisma.user.createMany({
  data: users,
  skipDuplicates: true
})
```

### Bulk delete

```js
await prisma.user.deleteMany({
  where: { deletedAt: { not: null } }
})
```

---

## 1️⃣5️⃣ Increment / Decrement

```js
await prisma.post.update({
  where: { id: 1 },
  data: {
    views: { increment: 1 }
  }
})
```

---

## 1️⃣6️⃣ Conditional Updates

```js
await prisma.user.updateMany({
  where: { role: "USER" },
  data: { role: "MEMBER" }
})
```

---

## 🧠 Query Optimization Rules (Memorize These)

1️⃣ Filter early
2️⃣ Select less
3️⃣ Index filter fields
4️⃣ Avoid offset pagination
5️⃣ Use raw SQL for analytics

---
