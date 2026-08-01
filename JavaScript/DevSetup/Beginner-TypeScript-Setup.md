# **TypeScript Project Setup Guide for Node.js**

## **1. Install Node.js**

* Download and install Node.js from [https://nodejs.org](https://nodejs.org).
* Verify installation:

```bash
node -v
npm -v
```

---

## **2. Create Project Folder**

* Open terminal and run:

```bash
mkdir my-ts-project
cd my-ts-project
```

* Initialize npm to manage dependencies:

```bash
npm init -y
```

This creates a `package.json` file.

---

## **3. Install TypeScript**

* Install TypeScript locally in your project:

```bash
npm install typescript --save-dev
```

* Optional: Install Node type definitions (needed if you use Node modules like `fs` or `path`):

```bash
npm install -D @types/node
```

---

## **4. Configure TypeScript**

* Create `tsconfig.json` for compiler options:

```bash
npx tsc --init
```

* Replace default content with a clean Node.js configuration:

```json
{
  "compilerOptions": {
    "rootDir": "./src",               // source files folder
    "outDir": "./dist",               // compiled JS output folder
    "module": "commonjs",             // Node.js module system
    "target": "ES2020",               // modern JS version
    "strict": true,                   // enable strict type checking
    "esModuleInterop": true,          // allows import fs from 'fs'
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true,             // skip type checking for libraries
    "sourceMap": true                 // generate source maps for debugging
  },
  "include": ["src/**/*"]
}
```

---

## **5. Organize Project Structure**

* Create a `src` folder for all TypeScript files:

```
my-ts-project/
  src/
    main.ts
  tsconfig.json
  package.json
```

* **Example `main.ts`:**

```ts
const greeting: string = "Hello, TypeScript!";
console.log(greeting);
```

---

## **6. Compile TypeScript**

* Run the compiler:

```bash
npx tsc
```

* This creates a `dist` folder with compiled JavaScript:

```
dist/
  main.js
  main.js.map
```

---

## **7. Run Compiled JavaScript**

* Use Node.js to run the compiled file:

```bash
node dist/main.js
```

* Output:

```
Hello, TypeScript!
```

---

## **8. Optional: Add NPM Scripts**

* Edit `package.json` to add build and run scripts:

```json
"scripts": {
  "build": "tsc",
  "start": "node dist/main.js"
}
```

* Now you can run with:

```bash
npm run build   # compiles TS files
npm start       # runs compiled JS
```

---

## **9. Recommended Workflow**

1. Write TypeScript in `src/`.
2. Compile using `npm run build`.
3. Run with `npm start`.
4. Repeat as you develop.

---

## **10. Notes & Tips**

* Keep `src/` clean: only `.ts` files.
* Compiled JS goes to `dist/`.
* If using Node modules (fs, path), make sure `@types/node` is installed.
* For React projects, you’d enable `"jsx": "react-jsx"` in `tsconfig.json`.

---

This setup works for **any small-to-medium Node.js TypeScript project** and keeps your source files and compiled files organized.

---
