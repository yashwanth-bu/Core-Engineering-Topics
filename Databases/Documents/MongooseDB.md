# 📘 Mongoose Beginner Guide

**From Connection to Core Features**

---

## 1️⃣ Connect to MongoDB

### What this does

* Connects Node.js app to MongoDB
* Creates database automatically if not exists

### How to connect

```js
const mongoose = require("mongoose");

mongoose
  .connect("mongodb://127.0.0.1:27017/myDatabase")
  .then(() => console.log("MongoDB Connected"))
  .catch(err => console.log(err));
```

📌 `myDatabase` will be created automatically.

---

## 2️⃣ Schema (Data Structure)

### What it gives

* Defines how data should look
* Prevents random data

### How to use

```js
const userSchema = new mongoose.Schema({
  name: String,
  age: Number,
  email: String
});
```

🧠 Schema = Blueprint of data.

---

## 3️⃣ Model (Collection Handler)

### What it gives

* Connects schema to database
* Gives CRUD methods

### How to use

```js
const User = mongoose.model("User", userSchema);
```

📌 MongoDB collection → `users`

---

## 4️⃣ Create Data (Insert)

### What it gives

* Save data to DB

```js
User.create({
  name: "John",
  age: 25,
  email: "john@gmail.com"
});
```

---

## 5️⃣ Read Data (Fetch)

### Fetch all

```js
User.find();
```

### Fetch one

```js
User.findOne({ name: "John" });
```

### Fetch by ID

```js
User.findById(id);
```

---

## 6️⃣ Update Data

### What it gives

* Modify existing documents

```js
User.updateOne(
  { name: "John" },
  { age: 26 }
);
```

OR

```js
User.findByIdAndUpdate(id, { age: 30 }, { new: true });
```

---

## 7️⃣ Delete Data

```js
User.deleteOne({ name: "John" });
```

OR

```js
User.findByIdAndDelete(id);
```

---

## 8️⃣ Validation (Data Protection)

### What it gives

* Blocks invalid data

```js
const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    minlength: 3
  },
  age: {
    type: Number,
    min: 18
  }
});
```

❌ Invalid data won’t be saved.

---

## 9️⃣ Default Values

```js
isActive: {
  type: Boolean,
  default: true
}
```

---

## 🔟 Middleware (Hooks)

### What it gives

* Run code before / after DB actions

```js
userSchema.pre("save", function (next) {
  console.log("User is about to be saved");
  next();
});
```

---

## 1️⃣1️⃣ Instance Methods

### What it gives

* Custom methods for documents

```js
userSchema.methods.greet = function () {
  return `Hello ${this.name}`;
};
```

Usage:

```js
const user = await User.findOne();
user.greet();
```

---

## 1️⃣2️⃣ Static Methods

### What it gives

* Custom model methods

```js
userSchema.statics.findAdults = function () {
  return this.find({ age: { $gte: 18 } });
};
```

Usage:

```js
User.findAdults();
```

---

## 1️⃣3️⃣ Relationships & Populate

### What it gives

* Connect collections

```js
const postSchema = new mongoose.Schema({
  title: String,
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "User"
  }
});
```

```js
Post.find().populate("user");
```

---

## 1️⃣4️⃣ Virtuals (Computed Fields)

```js
userSchema.virtual("isAdult").get(function () {
  return this.age >= 18;
});
```

📌 Not saved in DB.

---

## 1️⃣5️⃣ Indexes (Performance)

```js
email: {
  type: String,
  unique: true,
  index: true
}
```

---

## 1️⃣6️⃣ Pagination & Sorting

```js
User.find()
  .sort({ age: -1 })
  .limit(5)
  .skip(10);
```

---

## 🔥 Why Use Mongoose?

✔ Clean structure
✔ Validation
✔ Easy queries
✔ Middleware support
✔ Great with Express

---

## 🧠 Summary Table

| Feature    | Purpose       |
| ---------- | ------------- |
| connect    | DB connection |
| schema     | Data shape    |
| model      | DB operations |
| validation | Data safety   |
| middleware | Automation    |
| populate   | Relations     |
| indexes    | Speed         |

---

## 1️⃣7️⃣ Query Helpers (Cleaner Queries)

### What it gives

* Reusable query logic
* Cleaner, readable code

### How to use

```js
userSchema.query.active = function () {
  return this.where({ isActive: true });
};
```

### Usage

```js
User.find().active();
```

---

## 1️⃣8️⃣ Lean Queries (Performance Boost)

### What it gives

* Faster queries
* Returns plain JavaScript objects

### How to use

```js
User.find().lean();
```

📌 Use when you **don’t need methods or virtuals**.

---

## 1️⃣9️⃣ Timestamps (Auto createdAt / updatedAt)

### What it gives

* Automatically tracks time

### How to use

```js
const userSchema = new mongoose.Schema(
  {
    name: String
  },
  { timestamps: true }
);
```

MongoDB will store:

```js
createdAt
updatedAt
```

---

## 2️⃣0️⃣ Schema Options (Useful Ones)

### Common options

```js
const schema = new mongoose.Schema(
  {},
  {
    timestamps: true,
    versionKey: false,
    collection: "users"
  }
);
```

| Option     | Purpose     |
| ---------- | ----------- |
| timestamps | auto dates  |
| versionKey | removes __v |
| collection | custom name |

---

## 2️⃣1️⃣ Custom Validators

### What it gives

* Your own validation logic

```js
email: {
  type: String,
  validate: {
    validator: value => value.includes("@"),
    message: "Invalid email"
  }
}
```

---

## 2️⃣2️⃣ Enum (Allowed Values)

```js
role: {
  type: String,
  enum: ["user", "admin"],
  default: "user"
}
```

❌ Other values rejected.

---

## 2️⃣3️⃣ Embedded Documents (Subdocuments)

### What it gives

* Store nested objects

```js
const userSchema = new mongoose.Schema({
  name: String,
  address: {
    city: String,
    country: String
  }
});
```

OR array:

```js
addresses: [
  {
    city: String,
    country: String
  }
]
```

---

## 2️⃣4️⃣ One-to-Many Relationship

```js
const commentSchema = new mongoose.Schema({
  text: String,
  post: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "Post"
  }
});
```

```js
Comment.find().populate("post");
```

---

## 2️⃣5️⃣ Pre vs Post Hooks

### Pre

```js
userSchema.pre("save", function (next) {
  console.log("Before save");
  next();
});
```

### Post

```js
userSchema.post("save", function (doc) {
  console.log("After save", doc);
});
```

---

## 2️⃣6️⃣ Error Handling (Common Errors)

### Duplicate key error

```js
if (err.code === 11000) {
  console.log("Duplicate value");
}
```

### Validation error

```js
err.name === "ValidationError"
```

---

## 2️⃣7️⃣ Transactions (Advanced but Important)

### What it gives

* Multiple DB operations as one unit

```js
const session = await mongoose.startSession();
session.startTransaction();

try {
  await User.create([{ name: "A" }], { session });
  await Account.create([{ balance: 100 }], { session });

  await session.commitTransaction();
} catch (err) {
  await session.abortTransaction();
}
```

---

## 2️⃣8️⃣ Disconnect from MongoDB

```js
mongoose.connection.close();
```

---

## 2️⃣9️⃣ Project Folder Structure (Best Practice)

```txt
src/
 ├── models/
 │    └── user.model.js
 ├── controllers/
 ├── routes/
 ├── config/
 │    └── db.js
 └── app.js
```

---

## 3️⃣0️⃣ Mongoose vs MongoDB Driver

| Feature    | MongoDB | Mongoose |
| ---------- | ------- | -------- |
| Schema     | ❌       | ✅        |
| Validation | ❌       | ✅        |
| Middleware | ❌       | ✅        |
| Populate   | ❌       | ✅        |

---

## 🧠 Beginner Golden Rules

✅ Always define schema
✅ Use validation
✅ Use `lean()` for heavy reads
✅ Use `populate()` carefully
❌ Don’t overuse middleware

---

## 3️⃣1️⃣ Strict Mode (Control Extra Fields)

### What it gives

* Prevents unknown fields from being saved

### How to use

```js
const schema = new mongoose.Schema(
  {
    name: String
  },
  { strict: true }
);
```

❌ Extra fields ignored
✅ Keeps DB clean

---

## 3️⃣2️⃣ Strict Query

```js
mongoose.set("strictQuery", true);
```

Stops invalid query filters.

---

## 3️⃣3️⃣ Auto Increment (Common Use Case)

MongoDB doesn’t support auto-increment by default.

### Simple workaround

```js
const counterSchema = new mongoose.Schema({
  name: String,
  value: Number
});
```

Used in projects for order numbers.

---

## 3️⃣4️⃣ Select (Hide Fields)

### What it gives

* Hide sensitive data

```js
password: {
  type: String,
  select: false
}
```

```js
User.find(); // password excluded
```

---

## 3️⃣5️⃣ Alias (Field Nicknames)

```js
email: {
  type: String,
  alias: "mail"
}
```

```js
user.mail; // same as user.email
```

---

## 3️⃣6️⃣ Mixed Type (Flexible Fields)

```js
data: mongoose.Schema.Types.Mixed
```

Use when structure varies.

⚠️ Use carefully.

---

## 3️⃣7️⃣ Decimal128 (Money Values)

```js
price: mongoose.Schema.Types.Decimal128
```

Better precision than Number.

---

## 3️⃣8️⃣ Bulk Operations

### What it gives

* Faster mass updates

```js
User.insertMany([
  { name: "A" },
  { name: "B" }
]);
```

---

## 3️⃣9️⃣ Upsert (Update or Insert)

```js
User.updateOne(
  { email: "a@gmail.com" },
  { name: "Alex" },
  { upsert: true }
);
```

---

## 4️⃣0️⃣ Aggregation (Powerful Queries)

### What it gives

* Grouping, statistics, reports

```js
User.aggregate([
  { $match: { isActive: true } },
  { $group: { _id: "$role", count: { $sum: 1 } } }
]);
```

---

## 4️⃣1️⃣ Discriminators (Schema Inheritance)

### What it gives

* Multiple models from one base schema

```js
const options = { discriminatorKey: "type" };

const baseSchema = new mongoose.Schema(
  { name: String },
  options
);

const User = mongoose.model("User", baseSchema);
const Admin = User.discriminator("Admin", new mongoose.Schema({
  permissions: [String]
}));
```

---

## 4️⃣2️⃣ Change Streams (Real-Time Updates)

```js
User.watch().on("change", data => {
  console.log(data);
});
```

Used in:

* Notifications
* Live dashboards

---

## 4️⃣3️⃣ Connection Pooling

```js
mongoose.connect(uri, {
  maxPoolSize: 10
});
```

Improves performance in production.

---

## 4️⃣4️⃣ Read Preference

```js
mongoose.connect(uri, {
  readPreference: "secondaryPreferred"
});
```

Used in replica sets.

---

## 4️⃣5️⃣ Validation on Update

```js
User.findByIdAndUpdate(
  id,
  { age: 10 },
  { runValidators: true }
);
```

🚨 By default validators don’t run on updates.

---

## 4️⃣6️⃣ toJSON / toObject (Response Control)

```js
schema.set("toJSON", {
  transform: function (doc, ret) {
    delete ret.password;
    return ret;
  }
});
```

---

## 4️⃣7️⃣ Soft Delete (Industry Pattern)

```js
isDeleted: {
  type: Boolean,
  default: false
}
```

```js
User.find({ isDeleted: false });
```

---

## 4️⃣8️⃣ Global Plugins

### What it gives

* Reusable logic across schemas

```js
function softDelete(schema) {
  schema.add({ isDeleted: Boolean });
}
```

```js
schema.plugin(softDelete);
```

---

## 4️⃣9️⃣ Environment-based Config

```js
mongoose.connect(process.env.MONGO_URI);
```

Always use `.env`.

---

## 5️⃣0️⃣ Production Best Practices

✅ Use indexes
✅ Use `lean()`
✅ Handle errors
✅ Use connection pooling
❌ Don’t over-populate
❌ Don’t store huge arrays

---

## 🧠 REAL-WORLD USE CASES

| Feature        | Used for         |
| -------------- | ---------------- |
| Hooks          | password hashing |
| Populate       | user-posts       |
| Aggregation    | reports          |
| Discriminators | roles            |
| Soft delete    | data recovery    |

---

## 🔥 YOU NOW KNOW MONGOOSE 🔥

From:
✅ Connect → CRUD → Validation → Advanced → Production

---